# pyrefly: ignore [missing-import]
import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
import speech_recognition as sr

load_dotenv()

class AudioListener:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        # Bajamos el umbral para que sea más sensible al habla normal
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = True

        # Configuración del umbral de silencio (pauta de finalización)
        # Default de 2.0 segundos para no cortar al usuario mientras elabora ideas largas.
        self.recognizer.pause_threshold = float(os.getenv("AUDIO_PAUSE_THRESHOLD", "2.0"))

        print("  🎤  Inicializando micrófono y ajustando ruido ambiente...")
        # Forzamos el ID 1 que es el micrófono real detectado
        self.microphone = sr.Microphone(device_index=1)
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
        print("  ✅  Micrófono listo.")

    def listen(self, timeout: int = 5, phrase_time_limit: int | None = None) -> str | None:
        """Escucha el micrófono y devuelve el texto transcrito."""
        # Si no se especifica phrase_time_limit de forma explícita, leemos del .env (default None = sin límite de tiempo por frase)
        if phrase_time_limit is None:
            env_limit = os.getenv("AUDIO_PHRASE_TIME_LIMIT", "None")
            phrase_time_limit = None if env_limit == "None" else int(env_limit)

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
