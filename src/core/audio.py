# pyrefly: ignore [missing-import]
import speech_recognition as sr

class AudioListener:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        # Puedes jugar con estos valores si el ambiente es ruidoso
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

        print("  🎤  Inicializando micrófono y ajustando ruido ambiente...")
        self.microphone = sr.Microphone()
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
        print("  ✅  Micrófono listo.")

    def listen(self, timeout: int = 5, phrase_time_limit: int = 15) -> str | None:
        """Escucha el micrófono y devuelve el texto transcrito."""
        print("\n  🎙️  Te escucho...")
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            print("  ⏳  Entendiendo...")
            # Usamos Google Web Speech API (es gratis y no requiere key para uso básico)
            text = self.recognizer.recognize_google(audio, language="es-AR")
            print(f"  👤  Tú: «{text}»")
            return text
        except sr.WaitTimeoutError:
            print("  (Silencio)")
            return None
        except sr.UnknownValueError:
            print("  (No entendí lo que dijiste)")
            return None
        except Exception as e:
            print(f"  ❌  Error de audio: {e}")
            return None
