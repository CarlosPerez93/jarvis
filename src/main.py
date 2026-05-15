import sys
import time
from src.core.dialogue import DialogueManager
from src.core.wakeword import WakeWordDetector


def main():
    print("=" * 60)
    print("  🦾  JARVIS 3.0 INICIALIZANDO SISTEMAS...")
    print("=" * 60)

    try:
        dialogue_manager = DialogueManager()
        # El detector se crea una sola vez con baja sensibilidad para mics débiles
        wakeword = WakeWordDetector(sensitivity=0.25, device_index=1)
    except Exception as e:
        print(f"\n  ❌  Error de inicialización: {e}")
        sys.exit(1)

    print("\n  🎤  Sistemas online. Di 'Hey Jarvis' para activarme. (Ctrl+C para salir)")
    print("-" * 60)

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
                    print(f"  ❌  Error durante la interacción: {e}")
                finally:
                    # 4. Volvemos a modo escucha (start_stream se llama dentro de listen_for_wakeword)
                    time.sleep(0.3)
                    print("\n  👂  Volviendo a modo espera...\n")

    except KeyboardInterrupt:
        print("\n\n  Desconectando sistemas. Hasta luego, señor Carlos. 👋")
        wakeword.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    main()
