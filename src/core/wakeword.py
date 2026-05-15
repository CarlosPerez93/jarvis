import numpy as np
import pyaudio
from openwakeword.model import Model


class WakeWordDetector:
    """Detector de wakeword con ganancia extrema para micrófonos de bajo volumen."""

    def __init__(self, sensitivity: float = 0.15, device_index: int = 1) -> None:
        self.sensitivity = sensitivity
        self.device_index = device_index
        self.sample_rate = 16000
        self.chunk_size = 1280 

        print(f"  🧠  Cargando modelos... (Mic ID: {self.device_index})")
        self.model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")

        self.audio = pyaudio.PyAudio()
        self.stream = None
        print(f"  ✅  Calibrado para volumen bajo (Umbral: {self.sensitivity})")

    def start_stream(self):
        if not self.stream:
            try:
                self.stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=self.device_index,
                    frames_per_buffer=self.chunk_size,
                )
            except Exception as e:
                print(f"  ❌  Error de apertura: {e}")

    def stop_stream(self):
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None

    def listen_for_wakeword(self) -> bool:
        self.start_stream()
        if not self.stream: return False

        print("  👂  Escuchando... (Hablale normal a la laptop)")
        try:
            while True:
                audio_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)

                # GANANCIA EXTREMA (x15.0) para compensar el mic Intel
                audio_array = np.clip(audio_array.astype(np.float32) * 15.0, -32768, 32767).astype(np.int16)

                # Procesar
                self.model.predict(audio_array)

                # Verificar
                for model_name, score in self.model.prediction_buffer.items():
                    current_score = score[-1]
                    
                    # Ver el score en tiempo real si hay algo de ruido
                    if current_score > 0.05:
                        print(f"  📊  Nivel de coincidencia: {current_score:.2f} (Objetivo: {self.sensitivity})   ", end='\r')

                    if current_score > self.sensitivity:
                        print(f"\n  🚀  ¡DETECTADO! (Score: {current_score:.2f})")
                        self.model.reset()
                        return True
        except KeyboardInterrupt:
            return False

    def cleanup(self):
        self.stop_stream()
        if self.audio:
            self.audio.terminate()
