import os
import pickle
import random
import numpy as np
from sklearn.svm import SVC
from src.core.ui_bridge import update_biometrics

MODEL_PATH = os.path.join(os.path.dirname(__file__), "voice_model.pkl")

# ══════════════════════════════════════════════
#  FEATURE EXTRACTION — MFCC + Deltas + CMVN
# ══════════════════════════════════════════════

NUM_MFCC = 13         # Número de coeficientes MFCC a retener
NUM_MEL_FILTERS = 26  # Bancos de filtros Mel (estándar para speech)
FRAME_SIZE = 512
HOP_SIZE = 256
PRE_EMPHASIS_COEFF = 0.97
DELTA_N = 2           # Ventana de regresión para deltas


def get_mel_filterbank(num_filters: int, fft_size: int, sample_rate: int) -> np.ndarray:
    """Genera una matriz de filtros Mel triangulares estándar."""
    low_mel = 0
    high_mel = 2595 * np.log10(1 + (sample_rate / 2) / 700)
    mel_points = np.linspace(low_mel, high_mel, num_filters + 2)
    hz_points = 700 * (10**(mel_points / 2595) - 1)

    bin_indices = np.floor((fft_size + 1) * hz_points / sample_rate).astype(int)

    filters = np.zeros((num_filters, fft_size // 2 + 1))
    for i in range(1, num_filters + 1):
        left = bin_indices[i - 1]
        center = bin_indices[i]
        right = bin_indices[i + 1]

        if center > left:
            for j in range(left, center):
                filters[i - 1, j] = (j - left) / (center - left)
        if right > center:
            for j in range(center, right):
                filters[i - 1, j] = (right - j) / (right - center)

    return filters


def compute_dct_matrix(num_ceps: int, num_filters: int) -> np.ndarray:
    """
    Genera la matriz DCT tipo-II para transformar log-Mel energies en MFCCs.
    Decorrelaciona las bandas de filtro y concentra la energía en pocos coeficientes.
    """
    dct_matrix = np.zeros((num_ceps, num_filters))
    for k in range(num_ceps):
        for n in range(num_filters):
            dct_matrix[k, n] = np.cos(np.pi * k * (2 * n + 1) / (2 * num_filters))
    # Normalización ortogonal
    dct_matrix[0, :] *= 1.0 / np.sqrt(num_filters)
    dct_matrix[1:, :] *= np.sqrt(2.0 / num_filters)
    return dct_matrix


def compute_deltas(features: np.ndarray, N: int = DELTA_N) -> np.ndarray:
    """
    Calcula coeficientes delta (derivada temporal) usando regresión sobre ventana de ±N frames.
    Fórmula: d_t = Σ(n * (c_{t+n} - c_{t-n})) / (2 * Σ(n²))  para n=1..N
    """
    num_frames, num_features = features.shape
    denominator = 2 * sum(n * n for n in range(1, N + 1))
    deltas = np.zeros_like(features)

    # Pad con réplica de bordes (no con ceros, que introducen artefactos)
    padded = np.pad(features, ((N, N), (0, 0)), mode='edge')

    for t in range(num_frames):
        delta_sum = np.zeros(num_features)
        for n in range(1, N + 1):
            delta_sum += n * (padded[t + N + n] - padded[t + N - n])
        deltas[t] = delta_sum / denominator

    return deltas


def apply_cmvn(features: np.ndarray) -> np.ndarray:
    """
    Cepstral Mean and Variance Normalization (CMVN).
    Normaliza cada coeficiente por su media y varianza a lo largo del tiempo.
    Compensa variaciones de micrófono y ambiente entre sesiones.
    """
    mean = np.mean(features, axis=0)
    std = np.std(features, axis=0)
    # Evitar división por cero en coeficientes constantes
    std[std < 1e-10] = 1e-10
    return (features - mean) / std


def extract_features(audio_data: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
    """
    Extrae un vector de 78 características para verificación de hablante:
      - 13 MFCC (means + stds) = 26
      - 13 Delta (means + stds) = 26
      - 13 Delta-Delta (means + stds) = 26
      Total: 78 features

    Pipeline: Pre-emphasis → Framing → Hamming → FFT → Mel → Log → DCT → CMVN → Deltas
    """
    # 1. Normalizar a float [-1.0, 1.0]
    if audio_data.dtype == np.int16:
        audio = audio_data.astype(np.float32) / 32768.0
    else:
        audio = audio_data.astype(np.float32)

    # 2. Pre-emphasis: amplifica frecuencias altas que distinguen hablantes
    audio = np.append(audio[0], audio[1:] - PRE_EMPHASIS_COEFF * audio[:-1])

    # 3. Framing con ventana de Hamming (estándar en speech processing)
    window = np.hamming(FRAME_SIZE)
    num_frames = (len(audio) - FRAME_SIZE) // HOP_SIZE + 1

    if num_frames <= 0:
        return np.zeros(78, dtype=np.float32)

    # 4. Mel filterbank (26 filtros)
    mel_filters = get_mel_filterbank(
        num_filters=NUM_MEL_FILTERS,
        fft_size=FRAME_SIZE,
        sample_rate=sample_rate
    )

    # 5. DCT matrix para MFCC (13 coeficientes de 26 filtros)
    dct_matrix = compute_dct_matrix(NUM_MFCC, NUM_MEL_FILTERS)

    # 6. Procesar por frames: STFT → Mel → Log → DCT = MFCC
    mfcc_frames = []
    for i in range(num_frames):
        start = i * HOP_SIZE
        frame = audio[start: start + FRAME_SIZE] * window

        # FFT magnitud al cuadrado (power spectrum)
        power_spectrum = np.abs(np.fft.rfft(frame)) ** 2

        # Mel filterbank
        mel_energy = np.dot(mel_filters, power_spectrum)

        # Log (comprimir rango dinámico)
        log_mel = np.log(mel_energy + 1e-10)

        # DCT → MFCC (13 coeficientes decorrelados)
        mfcc = np.dot(dct_matrix, log_mel)
        mfcc_frames.append(mfcc)

    mfcc_frames = np.array(mfcc_frames)  # Shape: (num_frames, 13)

    # 7. CMVN — normaliza para compensar variaciones de canal/micrófono
    mfcc_frames = apply_cmvn(mfcc_frames)

    # 8. Deltas (velocidad de cambio espectral)
    deltas = compute_deltas(mfcc_frames)

    # 9. Delta-Deltas (aceleración de cambio espectral)
    delta_deltas = compute_deltas(deltas)

    # 10. Estadísticas temporales: mean + std de cada coeficiente
    mfcc_means = np.mean(mfcc_frames, axis=0)
    mfcc_stds = np.std(mfcc_frames, axis=0)
    delta_means = np.mean(deltas, axis=0)
    delta_stds = np.std(deltas, axis=0)
    dd_means = np.mean(delta_deltas, axis=0)
    dd_stds = np.std(delta_deltas, axis=0)

    # Vector final: 78 features (13*2 MFCC + 13*2 Delta + 13*2 DeltaDelta)
    feature_vector = np.concatenate([
        mfcc_means, mfcc_stds,
        delta_means, delta_stds,
        dd_means, dd_stds
    ])

    return feature_vector.astype(np.float32)


# ══════════════════════════════════════════════
#  VOICE AUTHENTICATOR
# ══════════════════════════════════════════════

class VoiceAuthenticator:
    """Maneja la carga del modelo de firma vocal y la validación en tiempo real."""

    def __init__(self, threshold: float = None, tts=None) -> None:
        if threshold is None:
            from dotenv import load_dotenv
            load_dotenv()
            self.threshold = float(os.getenv("AUDIO_AUTH_THRESHOLD", "0.85"))
        else:
            self.threshold = threshold
        self.model = None
        self.is_trained = False
        self.tts = tts
        self.load_model()

        # Mensajes naturales de rechazo en tono profesional colombiano paisa
        self._rejection_messages = [
            "Lo siento, pero esa no parece ser su firma de voz. Acceso denegado.",
            "No logré reconocer su voz, señor Carlos. No puedo permitirle el acceso.",
            "Disculpe, pero su firma de voz no coincide con la del señor Carlos.",
            "Acceso denegado. La firma de voz no corresponde con la autorizada.",
        ]

    def load_model(self) -> None:
        """Carga el modelo guardado si existe."""
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                self.is_trained = True
                print("  🔒  [BIOMETRÍA] Modelo de firma vocal cargado con éxito.")
            except Exception as e:
                print(f"  ⚠️  [BIOMETRÍA] Error al cargar el modelo de voz: {e}")
                self.is_trained = False
        else:
            self.is_trained = False

    def verify_speaker(self, audio_clip: np.ndarray) -> bool:
        """
        Verifica si el fragmento de audio pertenece al usuario autorizado.
        Si no hay modelo cargado (modo bypass inicial), retorna True.
        """
        if not self.is_trained or self.model is None:
            # Bypass inicial con aviso
            print("\n  ⚠️  [BIOMETRÍA] ADVERTENCIA: Firma de voz no entrenada. Jarvis responderá a cualquiera.")
            print("      Corré 'python enrolar.py' en la terminal para activar la biometría vocal.\n")
            return True

        features = extract_features(audio_clip).reshape(1, -1)

        # Predecir clase y probabilidad
        try:
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            # La clase 1 representa al usuario legítimo (Carlos)
            user_prob = probabilities[1]

            print(f"  📊  [BIOMETRÍA] Probabilidad de Carlos: {user_prob:.4f} (Umbral: {self.threshold})")

            # PUSH TO UI
            try:
                update_biometrics(user_prob, self.threshold)
            except Exception:
                pass

            if prediction == 1 and user_prob >= self.threshold:
                print("  ✅  [BIOMETRÍA] Usuario AUTENTICADO correctamente.")
                return True
            else:
                msg = random.choice(self._rejection_messages)
                print(f"  ❌  [BIOMETRÍA] Acceso DENEGADO: {msg}")
                if self.tts:
                    self.tts.speak(msg)
                return False
        except Exception as e:
            print(f"  ⚠️  [BIOMETRÍA] Error durante la predicción: {e}. Acceso denegado por seguridad.")
            return False

    def train_and_save(self, x_train: list, y_train: list) -> None:
        """Entrena un clasificador SVM (RBF) con class_weight balanceado y lo guarda en disco."""
        X = np.array(x_train)
        y = np.array(y_train)

        # SVM con RBF kernel, probabilidad habilitada, y class_weight balanced
        # para compensar desbalance entre muestras positivas/negativas
        svm = SVC(
            kernel="rbf",
            C=10.0,
            gamma="scale",
            probability=True,
            class_weight="balanced",
            random_state=42
        )
        svm.fit(X, y)

        # Guardar modelo
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(svm, f)

        self.model = svm
        self.is_trained = True
        print(f"  🎉  [BIOMETRÍA] ¡Modelo entrenado y guardado con éxito en '{MODEL_PATH}'!")
