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
        wakeword = WakeWordDetector(sensitivity=0.5)
    except Exception as e:
        print(f"\n  ❌  Error de inicialización: {e}")
        sys.exit(1)

    print("\n  🎤  Sistemas online. Di 'Hey Jarvis' para activarme. (Ctrl+C para salir)")
    print("-" * 60)

    try:
        while True:
            # Esperar por el wakeword "Hey Jarvis"
            detected = wakeword.listen_for_wakeword()

            if detected:
                print("\n\n  🚀  ¡Wakeword detectado!")
                try:
                    dialogue_manager.run_interaction()
                except Exception as e:
                    print(f"  ❌  Error de sistema: {e}")
                finally:
                    time.sleep(0.5)
                    print("\n  👂  Volviendo a modo espera...\n")

    except KeyboardInterrupt:
        print("\n\n  Desconectando sistemas. Hasta luego, señor Carlos. 👋")
        wakeword.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    main()
