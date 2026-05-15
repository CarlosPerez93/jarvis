import pyaudio
import wave
import numpy as np

def test_mic():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    DEVICE_INDEX = 1 # El que vimos que era el mic real
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "test_mic_output.wav"

    p = pyaudio.PyAudio()

    print(f"--- INICIANDO TEST DE MICRÓFONO (ID: {DEVICE_INDEX}) ---")
    print(f"Grabando {RECORD_SECONDS} segundos... ¡Hablale fuerte al mic!")

    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=DEVICE_INDEX,
                        frames_per_buffer=CHUNK)

        frames = []
        max_vol = 0

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            
            # Calcular volumen instantaneo
            audio_data = np.frombuffer(data, dtype=np.int16)
            vol = np.abs(audio_data).mean()
            if vol > max_vol: max_vol = vol
            
            # Barra de progreso visual simple
            bar = "#" * int(vol / 100)
            print(f"Volumen: [{bar:50}] {vol:.2f}", end='\r')

        print("\n\nGrabación terminada.")
        stream.stop_stream()
        stream.close()
        p.terminate()

        print(f"Volumen máximo detectado: {max_vol:.2f}")
        
        if max_vol < 10:
            print("❌ RESULTADO: Silencio casi absoluto. El dispositivo ID 1 NO está mandando audio.")
        else:
            print("✅ RESULTADO: Se detectó señal de audio.")

        # Guardar para que el usuario pueda escucharlo si quiere
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"Archivo guardado como: {WAVE_OUTPUT_FILENAME}")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    test_mic()
