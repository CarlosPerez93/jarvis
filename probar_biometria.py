import os
import sys
import time
import pyaudio
import numpy as np
from src.core.voice_auth import VoiceAuthenticator, extract_features

# Forzar CWD en el directorio del proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DEVICE_INDEX = 1  # ID del micrófono configurado en Jarvis
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024

def record_audio(duration: float = 2.0) -> np.ndarray:
    """Graba audio del micrófono durante la duración especificada con ganancia x15."""
    p = pyaudio.PyAudio()
    
    print("\n  🎤  Preparando micrófono real (ID: {})...".format(DEVICE_INDEX))
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
        print("  ❌  No se pudo abrir el micrófono (ID: {}): {}".format(DEVICE_INDEX, e))
        p.terminate()
        sys.exit(1)
        
    print("  🔴  GRABANDO AHORA... ¡Decí 'Hey Jarvis'!")
    frames = []
    
    total_chunks = int(SAMPLE_RATE / CHUNK_SIZE * duration)
    for i in range(total_chunks):
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        frames.append(np.frombuffer(data, dtype=np.int16))
        # Mostrar barra de progreso
        progress = int((i + 1) / total_chunks * 20)
        bar = "█" * progress + "░" * (20 - progress)
        print("      [{}] {:.1f}s / {:.1f}s".format(bar, ((i+1)/total_chunks)*duration, duration), end="\r")
        
    print("\n  ⏹️  Grabación finalizada.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    audio = np.concatenate(frames)
    # Aplicar ganancia del 15x idéntica a la del pipeline de producción
    audio_gained = np.clip(audio.astype(np.float32) * 15.0, -32768, 32767).astype(np.int16)
    return audio_gained

def main():
    print("="*60)
    print("  🧪  DIAGNÓSTICO Y CALIBRACIÓN DE BIOMETRÍA VOCAL (v3.2)")
    print("="*60)
    
    authenticator = VoiceAuthenticator()
    
    if not authenticator.is_trained or authenticator.model is None:
        print("\n  ⚠️  [ALERTA] No se encontró una firma de voz entrenada.")
        print("  Para usar este script, primero debés enrolar tu voz corriendo:")
        print("      python enrolar.py")
        print("\n  Saliendo...")
        sys.exit(1)
        
    print("\n  Firma de voz cargada correctamente.")
    print("  Umbral configurado (AUDIO_AUTH_THRESHOLD): {:.2f}".format(authenticator.threshold))
    print("  Presioná ENTER cuando estés listo para grabar tu prueba...")
    input()
    
    audio = record_audio()
    features = extract_features(audio).reshape(1, -1)
    
    try:
        prediction = authenticator.model.predict(features)[0]
        probabilities = authenticator.model.predict_proba(features)[0]
        user_prob = probabilities[1]
        
        print("\n" + "-"*50)
        print("  📊  RESULTADOS DEL ANÁLISIS DE VOZ:")
        print("-"*50)
        print("  - Probabilidad de ser CARLOS:  {:.2%}".format(user_prob))
        print("  - Umbral de Aprobación Mínima: {:.2%}".format(authenticator.threshold))
        
        if prediction == 1 and user_prob >= authenticator.threshold:
            print("\n  ✅  [ACCESO AUTORIZADO]: La voz coincide perfectamente con Carlos.")
            print("      ¡Estás calibrado de forma espectacular, loco!")
        else:
            print("\n  ❌  [ACCESO DENEGADO]: Firma vocal rechazada.")
            if user_prob >= 0.70:
                print("      Estuviste cerca ({:.2%}). Tal vez haya ruido de fondo o estés hablando".format(user_prob))
                print("      muy lejos. Podés bajar levemente el umbral en tu archivo `.env`:")
                print("      Ejemplo: AUDIO_AUTH_THRESHOLD = {:.2f}".format(user_prob - 0.05))
            else:
                print("      La probabilidad es muy baja ({:.2%}). Si sos vos, te recomiendo".format(user_prob))
                print("      volver a enrolar tu voz corriendo: python enrolar.py")
        print("="*60 + "\n")
        
    except Exception as e:
        print("  ❌  Error durante la predicción matemática SVM: {}".format(e))

if __name__ == "__main__":
    main()
