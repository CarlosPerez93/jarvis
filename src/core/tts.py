import os
import asyncio
# pyrefly: ignore [missing-import]
import edge_tts
# pyrefly: ignore [missing-import]
import pygame

class TTSProvider:
    def __init__(self) -> None:
        # Inicializamos el mixer de audio de pygame
        pygame.mixer.init()

    def speak(self, text: str) -> None:
        # 1. Imprimir la respuesta en consola
        print(f"  🔊  Jarvis: «{text}»")
        
        # 2. Limpiar Markdown para no confundir al motor TTS
        clean_text = text.replace("*", "").replace("#", "").replace("_", "").replace("`", "").strip()
        
        # 3. Generar y reproducir el audio con voces neuronales
        try:
            temp_file = "temp_voice.mp3"
            
            # Función asíncrona para generar el archivo mp3
            async def _generate_audio():
                # Usamos a Elvira (voz femenina natural de España)
                communicate = edge_tts.Communicate(clean_text, "es-ES-ElviraNeural", rate="+5%")
                await communicate.save(temp_file)
                
            # Ejecutamos la generación de forma bloqueante
            asyncio.run(_generate_audio())
            
            # Cargamos y reproducimos el mp3
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Esperamos a que termine de hablar
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            # Liberamos el archivo para poder borrarlo
            pygame.mixer.music.unload()
            
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
        except Exception as e:
            print(f"  ❌  Error del parlante neuronal: {e}")
