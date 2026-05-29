import sys
import io

# Force stdout and stderr to use UTF-8 on Windows to prevent charmap codec errors
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True, write_through=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True, write_through=True)

import time
from src.core.dialogue import DialogueManager
from src.core.wakeword import WakeWordDetector
from src.core.ui_bridge import init_ui, start_ui, update_status, update_footer


def run_jarvis():
    try:
        # Initialize core components
        dialogue_manager = DialogueManager()
        # El detector se crea una sola vez con baja sensibilidad para mics débiles
        wakeword = WakeWordDetector(sensitivity=0.1, device_index=1, tts=dialogue_manager.tts)
    except Exception as e:
        print(f"\n  [ERROR] Error de inicialización del core: {e}")
        return

    print("\n  [SYS]  Ejecutando secuencia de arranque...")
    try:
        dialogue_manager.tts.speak("Iniciando protocolos principales de sistema.")
        time.sleep(0.2)
        dialogue_manager.tts.speak("Cargando motor de procesamiento de lenguaje natural y redes neuronales.")
        time.sleep(0.2)
        dialogue_manager.tts.speak("Sistemas biométricos, telemetría e interfaz de usuario en línea.")
        time.sleep(0.2)
        dialogue_manager.tts.speak("Todos los sistemas están operativos. A su entera disposición, señor Carlos.")
    except Exception as e:
        print(f"  [ERROR] Falla en la voz de arranque: {e}")

    print("\n  [MIC]  Sistemas online. Di 'Hey Jarvis' para activarme. (Ctrl+C para salir)")
    print("-" * 60)

    # Push system details to footer
    try:
        update_status("READY", "#00ff00")
        update_footer("status", "READY")
        update_footer("model", "gemini-2.5-flash")
        update_footer("key", "Key #1")
        update_footer("auth", "BIOMETRICS ON" if wakeword.authenticator.is_trained else "BYPASS MODE")
    except Exception:
        pass

    try:
        while True:
            # 1. Esperar por el wakeword
            detected = wakeword.listen_for_wakeword()

            if detected:
                try:
                    # 2. Soltamos el mic inmediatamente para el diálogo
                    wakeword.stop_stream()

                    # 3. Corremos la interacción
                    dialogue_manager.run_interaction()

                except Exception as e:
                    print(f"  [ERROR] Error durante la interacción: {e}")
                finally:
                    # 4. Volvemos a modo escucha (start_stream se llama dentro de listen_for_wakeword)
                    time.sleep(0.3)
                    print("\n  [INFO]  Volviendo a modo espera...\n")

    except KeyboardInterrupt:
        print("\n\n  Desconectando sistemas. Hasta luego, señor Carlos. [BYE]")
        wakeword.cleanup()
        import os
        os._exit(0)


def main():
    print("=" * 60)
    print("  JARVIS 4.0 INICIALIZANDO SISTEMAS...")
    print("=" * 60)

    try:
        # Initialize UI first (non‑blocking start)
        init_ui()
        # start_ui blocks the main thread and runs run_jarvis in background
        start_ui(run_jarvis)
    except Exception as e:
        print(f"\n  [ERROR] Error de inicialización: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
