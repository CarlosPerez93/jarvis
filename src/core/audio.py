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
        # Lower threshold for normal speech
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = True

        # Silence threshold (pause) default 2.0s
        self.recognizer.pause_threshold = float(os.getenv("AUDIO_PAUSE_THRESHOLD", "2.0"))

        print("[INFO] Inicializando micrófono y ajustando ruido ambiente...")
        # Force microphone index 1
        self.microphone = sr.Microphone(device_index=1)
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
        print("[OK] Micrófono listo.")

    def listen(self, timeout: int = 5, phrase_time_limit: int | None = None) -> str | None:
        """Escucha el micrófono y devuelve el texto transcrito."""
        if phrase_time_limit is None:
            env_limit = os.getenv("AUDIO_PHRASE_TIME_LIMIT", "None")
            phrase_time_limit = None if env_limit == "None" else int(env_limit)

        print("\n[LISTEN] Te escucho...")
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            print("[PROCESSING] Entendiendo...")
            # Use Google Web Speech API (free)
            text = self.recognizer.recognize_google(audio, language="es-AR")
            print(f"[USER] Tú: «{text}»")
            return text
        except sr.WaitTimeoutError:
            print("[SILENCE]")
            return None
        except sr.UnknownValueError:
            print("[ERROR] No entendí lo que dijiste")
            return None
        except Exception as e:
            print(f"[ERROR] Error de audio: {e}")
            return None
