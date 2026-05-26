import os
import sys
import time
import pyaudio
import numpy as np
from src.core.voice_auth import VoiceAuthenticator, extract_features

# Forzar CWD en el directorio del proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DEVICE_INDEX = 1  # ID del micrófono real configurado en Jarvis
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024

def record_audio(duration: float, prompt: str) -> np.ndarray:
    """Graba audio del micrófono durante la duración especificada con ganancia extrema."""
    p = pyaudio.PyAudio()

    print("\n" + "="*50)
    print(f"  🎙️  Instrucción: {prompt}")
    print("  ENTER para empezar a grabar...")
    input()

    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            input_device_index=DEVICE_INDEX,
            frames_per_buffer=CHUNK_SIZE
        )
    except Exception as e:
        print(f"  ❌  No se pudo abrir el micrófono (ID: {DEVICE_INDEX}): {e}")
        p.terminate()
        sys.exit(1)

    print("  🔴  GRABANDO... ¡HABLA AHORA!")
    frames = []

    # Barra de progreso visual simple
    total_chunks = int(SAMPLE_RATE / CHUNK_SIZE * duration)
    for i in range(total_chunks):
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        frames.append(np.frombuffer(data, dtype=np.int16))
        # Dibujar barra
        progress = int((i + 1) / total_chunks * 20)
        bar = "█" * progress + "░" * (20 - progress)
        print(f"      [{bar}] {((i+1)/total_chunks)*duration:.1f}s / {duration:.1f}s", end="\r")

    print("\n  ⏹️  Grabación finalizada.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    audio = np.concatenate(frames)
    # GANANCIA EXTREMA (x15.0) para coincidir idénticamente con el flujo de audio de wakeword.py
    audio_gained = np.clip(audio.astype(np.float32) * 15.0, -32768, 32767).astype(np.int16)
    return audio_gained

def main():
    print("="*60)
    print("  🎤  SISTEMA DE ENROLAMIENTO BIOMÉTRICO DE JARVIS 4.0")
    print("="*60)
    print("¡Qué hacés, Carlos! Vamos a registrar tu huella de voz.")
    print("Para entrenar el modelo MFCC de forma ultra-precisa, vamos a hacer:")
    print("  1. 8 grabaciones tuyas diciendo exactamente 'Hey Jarvis'.")
    print("  2. 3 grabaciones de control diciendo otras palabras aleatorias.")
    print("  3. 3 grabaciones de variabilidad (susurros, lejos del mic, voz forzada).")
    print("  4. 1 grabación de 5 segundos en silencio absoluto (ruido de fondo).")
    print("\n¡Dale, ponete las pilas y empecemos!")

    positive_features = []
    negative_features = []

    # --- 1. MUESTRAS POSITIVAS (Carlos diciendo Hey Jarvis) ---
    print("\n--- PASO 1: Grabación de muestras positivas (8 muestras) ---")
    print("Variá un poco la entonación y distancia al mic entre muestras.")
    positive_prompts = [
        "Decí 'Hey Jarvis' con tu tono normal (Muestra 1/8)",
        "Decí 'Hey Jarvis' un poco más fuerte (Muestra 2/8)",
        "Decí 'Hey Jarvis' un poco más suave (Muestra 3/8)",
        "Decí 'Hey Jarvis' con tono natural (Muestra 4/8)",
        "Decí 'Hey Jarvis' alejándote un poquito del mic (Muestra 5/8)",
        "Decí 'Hey Jarvis' acercándote bien al mic (Muestra 6/8)",
        "Decí 'Hey Jarvis' con tono serio (Muestra 7/8)",
        "Decí 'Hey Jarvis' con tono relajado (Muestra 8/8)",
    ]
    for idx, prompt in enumerate(positive_prompts, 1):
        audio = record_audio(duration=2.0, prompt=prompt)
        features = extract_features(audio)
        positive_features.append(features)
        print(f"  ✅  Muestra {idx} registrada correctamente.")
        time.sleep(0.5)

    # --- 2. MUESTRAS NEGATIVAS - Palabras de Control (Carlos diciendo otras cosas) ---
    print("\n--- PASO 2: Grabación de palabras de control ---")
    print("Esto es fundamental para que Jarvis no se active con CUALQUIER sonido tuyo.")
    control_words = [
        "Decí palabras aleatorias como: 'Hola, buenas tardes, cómo va'",
        "Decí palabras de control como: 'temperatura, volumen, clima, apagar'",
        "Decí una frase cualquiera como: 'hoy está lindo el día para programar'"
    ]

    for idx, prompt in enumerate(control_words, 1):
        audio = record_audio(duration=2.0, prompt=prompt)
        features = extract_features(audio)
        negative_features.append(features)
        print(f"  ✅  Palabra de control {idx} registrada.")
        time.sleep(0.5)

    # --- 3. MUESTRAS NEGATIVAS - Variabilidad Adversaria ---
    print("\n--- PASO 3: Grabación de variabilidad adversaria ---")
    print("Estas muestras ayudan al modelo a NO confundirse con voces distorsionadas.")
    adversarial_prompts = [
        "Susurrá 'Hey Jarvis' lo más bajo que puedas",
        "Decí 'Hey Jarvis' tapándote un poco la boca con la mano",
        "Decí 'Hey Jarvis' alejándote bastante del mic (1 metro aprox)",
    ]

    for idx, prompt in enumerate(adversarial_prompts, 1):
        audio = record_audio(duration=2.0, prompt=prompt)
        features = extract_features(audio)
        # Estas van como NEGATIVAS para que el modelo no acepte voces distorsionadas
        negative_features.append(features)
        print(f"  ✅  Muestra adversaria {idx} registrada.")
        time.sleep(0.5)

    # --- 4. MUESTRAS NEGATIVAS - Ruido Ambiente (Silencio) ---
    print("\n--- PASO 4: Grabación de ruido ambiente ---")
    audio_noise = record_audio(duration=5.0, prompt="Quedate en silencio absoluto (registrando el ruido de tu habitación)")
    # Troceamos el audio largo de 5s en fragmentos de 2s para generar varias muestras de ruido
    step = 32000 # 2 segundos
    for start_idx in range(0, len(audio_noise) - step + 1, step // 2):
        clip = audio_noise[start_idx : start_idx + step]
        features = extract_features(clip)
        negative_features.append(features)

    print("  ✅  Ruido ambiente registrado y procesado.")

    # --- 5. AUMENTACIÓN DE DATOS (DATA AUGMENTATION MEJORADA) ---
    print("\n🔮  Aplicando aumento de datos avanzado para expandir el dataset...")

    X = []
    y = []

    # Aumentar muestras positivas (Carlos)
    for feats in positive_features:
        X.append(feats)
        y.append(1) # Carlos

        # Ruido Gaussiano con varianza escalonada (20 variantes por muestra)
        for i in range(20):
            noise_scale = 0.01 + (i / 20) * 0.03  # De 0.01 a 0.04 progresivo
            noise = np.random.normal(0, noise_scale, feats.shape)
            X.append(feats + noise)
            y.append(1)

        # Perturbación de scale (simula variación de volumen/distancia)
        for _ in range(5):
            scale = np.random.uniform(0.9, 1.1)
            X.append(feats * scale)
            y.append(1)

    # Aumentar muestras negativas (Control, Adversarial y Ruido)
    for feats in negative_features:
        X.append(feats)
        y.append(0) # No es Carlos / No es el comando
        for i in range(20):
            noise_scale = 0.01 + (i / 20) * 0.03
            noise = np.random.normal(0, noise_scale, feats.shape)
            X.append(feats + noise)
            y.append(0)

        for _ in range(5):
            scale = np.random.uniform(0.9, 1.1)
            X.append(feats * scale)
            y.append(0)

    print(f"📊  Dataset expandido: {y.count(1)} muestras positivas y {y.count(0)} muestras negativas.")

    # --- 6. ENTRENAMIENTO ---
    print("\n🤖  Entrenando el modelo SVM con features MFCC+Deltas+CMVN (78 dimensiones)...")
    authenticator = VoiceAuthenticator()
    authenticator.train_and_save(X, y)

    print("\n" + "="*60)
    print("  🎉  ¡SISTEMA BIOMÉTRICO v4.0 BIEN CONFIGURADO!")
    print("="*60)
    print("Tu firma de voz fue guardada de forma segura.")
    print("Ahora Jarvis solo responderá cuando él detecte tu timbre de voz exclusivo.")
    print("Pipeline: Pre-emphasis → MFCC → Deltas → CMVN → SVM (78 features)")
    print("Reiniciá Jarvis si ya está corriendo para que cargue tu firma nueva. ¡A rockear!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
