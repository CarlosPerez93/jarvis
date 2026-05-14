import pyttsx3
import pythoncom

class TTSProvider:
    def __init__(self) -> None:
        pass

    def speak(self, text: str) -> None:
        # 1. Imprimir la respuesta
        print(f"  🔊  Jarvis: «{text}»")
        
        # 2. Limpiar Markdown (asteriscos, numerales, etc) que confunden al motor de Windows
        clean_text = text.replace("*", "").replace("#", "").replace("_", "").replace("`", "").strip()
        
        # 3. Inicializar el motor on-the-fly para esquivar el infame bug de 'runAndWait' de pyttsx3
        try:
            # Requisito para inicializar un motor COM en algunos entornos
            pythoncom.CoInitialize() 
            
            engine = pyttsx3.init()
            
            # Buscar voz en español
            voices = engine.getProperty("voices")
            esp = [v for v in voices if "es" in v.id.lower() or "spanish" in v.name.lower()]
            if esp:
                engine.setProperty("voice", esp[0].id)
            engine.setProperty("rate", 148)
            
            # Hablar
            engine.say(clean_text)
            engine.runAndWait()
            
            # Limpiar memoria del motor COM para la próxima vez
            del engine
            
        except Exception as e:
            print(f"  ❌  Error del parlante (SAPI5): {e}")
