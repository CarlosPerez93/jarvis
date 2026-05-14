import time
import numpy as np
import sounddevice as sd
import sys
import threading
from src.core.dialogue import DialogueManager

# ──────────────────────────────────────────────────────────────────────────────
# Configuración del detector de aplausos
# ──────────────────────────────────────────────────────────────────────────────
SAMPLE_RATE    = 44100
BLOCK_SIZE     = int(SAMPLE_RATE * 0.05)
THRESHOLD      = 0.10
COOLDOWN       = 0.1
DOUBLE_WINDOW  = 2.0

clap_times = []
triggered = False
lock = threading.Lock()
dialogue_manager = None

def audio_callback(indata, frames, time_info, status):
    """Callback rápido y crudo para detectar los picos (aplausos)."""
    global triggered, clap_times
    if triggered:
        return

    rms = float(np.sqrt(np.mean(indata ** 2)))
    now = time.time()
    
    # Imprime en la misma línea sin llenar la consola
    print(f"  🎙️ Esperando aplausos (RMS): {rms:.4f} ", end='\r', flush=True)

    if rms > THRESHOLD:
        with lock:
            if clap_times and (now - clap_times[-1]) < COOLDOWN:
                return

            clap_times.append(now)
            clap_times = [t for t in clap_times if now - t <= DOUBLE_WINDOW]
            count = len(clap_times)

            if count >= 2:
                triggered = True
                clap_times = []
                # En lugar de usar un thread, dejamos que el bucle principal lo maneje
                # para evitar que Windows bloquee el motor de voz (SAPI5) por cruce de hilos.

def iniciar_interaccion():
    global triggered
    print("\n\n🚀  Secuencia de activación iniciada...")
    try:
        dialogue_manager.run_interaction()
    except Exception as e:
        print(f"  ❌  Error de sistema: {e}")
    finally:
        time.sleep(1)
        print("\n👂  Volviendo a modo espera silencioso…\n")
        triggered = False

def main():
    global dialogue_manager
    print("=" * 60)
    print("  🦾  JARVIS 2.0 INICIALIZANDO REDES NEURALES...")
    print("=" * 60)
    
    try:
        # Acá se arma el grafo de inyección de dependencias
        dialogue_manager = DialogueManager()
    except ValueError as e:
        print(f"\n{e}")
        sys.exit(1)

    print("\n  🎤  Sistemas online. Esperando comando por aplauso... (Ctrl+C para salir)")
    print(f"  Umbral de detección: {THRESHOLD}")
    print("-" * 60)

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            dtype="float32",
            callback=audio_callback,
        ):
            while True:
                time.sleep(0.1)
                if triggered:
                    iniciar_interaccion()
    except KeyboardInterrupt:
        print("\n\nDesconectando sistemas. Hasta luego, señor Carlos. 👋")
        sys.exit(0)

if __name__ == "__main__":
    main()
