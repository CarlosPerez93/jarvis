import pyaudio

def list_devices():
    p = pyaudio.PyAudio()
    print("\n--- DISPOSITIVOS DE AUDIO DETECTADOS ---")
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        device = p.get_device_info_by_host_api_device_index(0, i)
        if device.get('maxInputChannels') > 0:
            print(f"ID {i}: {device.get('name')} (Canales de entrada: {device.get('maxInputChannels')})")
    
    print("----------------------------------------\n")
    p.terminate()

if __name__ == "__main__":
    list_devices()
