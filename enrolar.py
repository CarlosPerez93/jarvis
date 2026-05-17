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
    print("  🎤  SISTEMA DE ENROLAMIENTO BIOMÉTRICO DE JARVIS 3.0")
    print("="*60)
    print("¡Qué hacés, Carlos! Vamos a registrar tu huella de voz.")
    print("Para entrenar el modelo de forma ultra-precisa, vamos a hacer:")
    print("  1. 5 grabaciones tuyas diciendo exactamente 'Hey Jarvis'.")
    print("  2. 3 grabaciones de control diciendo otras palabras aleatorias.")
    print("  3. 1 grabación de 5 segundos en silencio absoluto (ruido de fondo).")
    print("\n¡Dale, ponete las pilas y empecemos!")
    
    positive_features = []
    negative_features = []
    
    # --- 1. MUESTRAS POSITIVAS (Carlos diciendo Hey Jarvis) ---
    print("\n--- PASO 1: Grabación de muestras positivas ---")
    for idx in range(1, 6):
        prompt = f"Decí alegremente 'Hey Jarvis' (Muestra {idx}/5)"
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
        
    # --- 3. MUESTRAS NEGATIVAS - Ruido Ambiente (Silencio) ---
    print("\n--- PASO 3: Grabación de ruido ambiente ---")
    audio_noise = record_audio(duration=5.0, prompt="Quedate en silencio absoluto (registrando el ruido de tu habitación)")
    # Troceamos el audio largo de 5s en fragmentos de 2s para generar varias muestras de ruido
    step = 32000 # 2 segundos
    for start_idx in range(0, len(audio_noise) - step + 1, step // 2):
        clip = audio_noise[start_idx : start_idx + step]
        features = extract_features(clip)
        negative_features.append(features)
        
    print("  ✅  Ruido ambiente registrado y procesado.")
    
    # --- 4. AUMENTACIÓN DE DATOS (DATA AUGMENTATION) ---
    print("\n🔮  Aplicando aumento de datos matemático para expandir el dataset...")
    
    # Creamos un conjunto de datos grande añadiendo ruido blanco Gaussiano sutil a los vectores
    X = []
    y = []
    
    # Aumentar muestras positivas (Carlos)
    for feats in positive_features:
        X.append(feats)
        y.append(1) # Carlos
        for _ in range(15):  # Generamos 15 variantes sintéticas por muestra
            noise = np.random.normal(0, 0.015, feats.shape)
            X.append(feats + noise)
            y.append(1)
            
    # Aumentar muestras negativas (Control y Ruido)
    for feats in negative_features:
        X.append(feats)
        y.append(0) # No es Carlos / No es el comando
        for _ in range(15):
            noise = np.random.normal(0, 0.015, feats.shape)
            X.append(feats + noise)
            y.append(0)
            
    print(f"📊  Dataset expandido: {y.count(1)} muestras positivas y {y.count(0)} muestras negativas.")
    
    # --- 5. ENTRENAMIENTO ---
    print("\n🤖  Entrenando el modelo Support Vector Machine (SVM) local...")
    authenticator = VoiceAuthenticator()
    authenticator.train_and_save(X, y)
    
    print("\n" + "="*60)
    print("  🎉  ¡SISTEMA BIOMÉTRICO BIEN CONFIGURADO!")
    print("="*60)
    print("Tu firma de voz fue guardada de forma segura.")
    print("Ahora Jarvis solo responderá cuando él detecte tu timbre de voz exclusivo.")
    print("Reiniciá Jarvis si ya está corriendo para que cargue tu firma nueva. ¡A rockear!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
