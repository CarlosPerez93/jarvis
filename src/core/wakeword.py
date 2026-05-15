import numpy as np
import pyaudio
from openwakeword.model import Model


class WakeWordDetector:
    """Detector de wakeword usando openWakeWord (gratis, sin API key, 100% local)."""

    def __init__(self, sensitivity: float = 0.5) -> None:
        self.sensitivity = sensitivity
        self.sample_rate = 16000
        self.chunk_size = 1280  # 80ms de audio a 16kHz (requerido por openWakeWord)

        print("  🧠  Cargando modelo de wakeword...")
        self.model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")

        self.audio = pyaudio.PyAudio()
        self.stream = None
        print("  ✅  Wakeword 'Hey Jarvis' listo.")

    def listen_for_wakeword(self) -> bool:
        """
        Escucha continuamente hasta detectar 'Hey Jarvis'.
        Retorna True cuando lo detecta.
        """
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )

        try:
            while True:
                audio_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)

                # Procesar el frame de audio
                prediction = self.model.predict(audio_array)

                # Verificar si se detectó el wakeword
                for model_name, score in self.model.prediction_buffer.items():
                    current_score = score[-1]  # Última predicción
                    if current_score > self.sensitivity:
                        self.model.reset()
                        return True

        except KeyboardInterrupt:
            return False
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

    def cleanup(self):
        """Liberar recursos de audio."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
