import os
import re
import asyncio
# pyrefly: ignore [missing-import]
import edge_tts
# pyrefly: ignore [missing-import]
import pygame
import pyttsx3 # Fallback local


class TTSProvider:
    def __init__(self) -> None:
        pygame.mixer.init()
        self._temp_counter = 0
        
        # Inicializar el motor local de Windows por si falla el neural
        self.local_engine = pyttsx3.init()
        self.local_engine.setProperty('rate', 148) # Velocidad natural a 148 wpm

    def speak(self, text: str) -> None:
        """Sintetiza y reproduce texto. Si falla la red, usa voz local."""
        print(f"  🔊  Jarvis: «{text}»")
        
        clean_text = text.replace("*", "").replace("#", "").replace("_", "").replace("`", "").strip()
        if not clean_text:
            return

        sentences = self._split_sentences(clean_text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 2:
                continue
            
            # Intentar con voz neural (Edge-TTS)
            success = self._speak_chunk_neural(sentence)
            
            # Si falla (por internet o red), usar voz local
            if not success:
                self._speak_local(sentence)

    def _split_sentences(self, text: str) -> list[str]:
        parts = re.split(r'(?<=[.!?])\s+', text)
        return parts if len(parts) > 1 else [text]

    def _speak_chunk_neural(self, text: str) -> bool:
        """Intenta reproducir con voz neural. Retorna True si tuvo éxito."""
        try:
            self._temp_counter += 1
            temp_file = f"temp_voice_{self._temp_counter % 2}.mp3"

            async def _generate_audio():
                communicate = edge_tts.Communicate(text, "es-CO-GonzaloNeural", rate="+0%")
                await communicate.save(temp_file)

            asyncio.run(_generate_audio())

            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return True
        except Exception as e:
            print(f"  ⚠️  Falla de red neural: Usando voz de respaldo local...")
            return False

    def _speak_local(self, text: str):
        """Reproduce texto usando el motor de voz de Windows (SAPI5)."""
        try:
            self.local_engine.say(text)
            self.local_engine.runAndWait()
        except Exception as e:
            print(f"  ❌  Error crítico en TTS local: {e}")
