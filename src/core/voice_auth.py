import os
import pickle
import random
import numpy as np
from sklearn.svm import SVC
from src.core.ui_bridge import update_biometrics

MODEL_PATH = os.path.join(os.path.dirname(__file__), "voice_model.pkl")

def get_mel_filterbank(num_filters: int, fft_size: int, sample_rate: int) -> np.ndarray:
    """Genera una matriz de filtros Mel estándar."""
    low_mel = 0
    # Formula estándar de escala Mel
    high_mel = 2595 * np.log10(1 + (sample_rate / 2) / 700)
    mel_points = np.linspace(low_mel, high_mel, num_filters + 2)
    hz_points = 700 * (10**(mel_points / 2595) - 1)
    
    bin_indices = np.floor((fft_size + 1) * hz_points / sample_rate).astype(int)
    
    filters = np.zeros((num_filters, fft_size // 2 + 1))
    for i in range(1, num_filters + 1):
        # Aseguramos no dividir por cero en los extremos
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

def extract_features(audio_data: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
    """
    Extrae un vector de 40 características (promedio y varianza de 20 bancos Mel)
    a partir de una señal de audio de 16kHz de forma súper liviana y determinista.
    """
    # Si viene en float32/int16, normalizamos a float entre -1.0 y 1.0
    if audio_data.dtype == np.int16:
        audio = audio_data.astype(np.float32) / 32768.0
    else:
        audio = audio_data.astype(np.float32)
        
    # Parámetros estándar de STFT
    frame_size = 512
    hop_size = 256
    
    # Ventana de Hann para suavizar bordes de frames
    window = np.hanning(frame_size)
    
    # Bancos de filtros Mel (20 filtros)
    mel_filters = get_mel_filterbank(num_filters=20, fft_size=frame_size, sample_rate=sample_rate)
    
    # Procesar por frames
    num_frames = (len(audio) - frame_size) // hop_size + 1
    if num_frames <= 0:
        # En caso de audio extremadamente corto, rellenamos con ceros
        return np.zeros(40, dtype=np.float32)
        
    frame_energies = []
    
    for i in range(num_frames):
        start = i * hop_size
        frame = audio[start : start + frame_size] * window
        
        # FFT magnitud
        fft_mag = np.abs(np.fft.rfft(frame))
        
        # Filtro Mel
        mel_energy = np.dot(mel_filters, fft_mag)
        
        # Logaritmo para comprimir rango dinámico (similar a decibelios)
        log_mel_energy = np.log(mel_energy + 1e-10)
        frame_energies.append(log_mel_energy)
        
    frame_energies = np.array(frame_energies) # Shape: (num_frames, 20)
    
    # Estadísticas para independencia temporal (promedio y desviación estándar)
    means = np.mean(frame_energies, axis=0)
    stds = np.std(frame_energies, axis=0)
    
    # Vector de 40 características
    feature_vector = np.concatenate([means, stds])
    return feature_vector


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
        """Entrena un clasificador SVM (RBF) y lo guarda en disco."""
        X = np.array(x_train)
        y = np.array(y_train)
        
        # Entrenamos SVM con RBF kernel y probabilidad habilitada
        svm = SVC(kernel="rbf", C=10.0, gamma="scale", probability=True, random_state=42)
        svm.fit(X, y)
        
        # Guardar modelo
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(svm, f)
            
        self.model = svm
        self.is_trained = True
        print(f"  🎉  [BIOMETRÍA] ¡Modelo entrenado y guardado con éxito en '{MODEL_PATH}'!")
