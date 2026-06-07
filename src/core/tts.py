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
        self.local_engine.setProperty('rate', 198) # Velocidad natural a 148 wpm

    def speak(self, text: str, interrupt_callback=None) -> bool:
        """Sintetiza y reproduce texto. Retorna True si fue interrumpido."""
        print(f"  🔊  Jarvis: «{text}»")
        
        clean_text = text.replace("*", "").replace("#", "").replace("_", "").replace("`", "").strip()
        if not clean_text:
            return False

        sentences = self._split_sentences(clean_text)

        for sentence in sentences:
            if interrupt_callback and interrupt_callback():
                return True
                
            sentence = sentence.strip()
            if not sentence or len(sentence) < 2:
                continue
            
            # Intentar con voz neural (Edge-TTS)
            success, interrupted = self._speak_chunk_neural(sentence, interrupt_callback)
            
            if interrupted:
                return True
                
            # Si falla (por internet o red), usar voz local
            if not success:
                self._speak_local(sentence)
                
        return False

    def _split_sentences(self, text: str) -> list[str]:
        parts = re.split(r'(?<=[.!?])\s+', text)
        return parts if len(parts) > 1 else [text]

    def _speak_chunk_neural(self, text: str, interrupt_callback=None) -> tuple[bool, bool]:
        """Intenta reproducir con voz neural. Retorna (success, interrupted)."""
        try:
            self._temp_counter += 1
            temp_file = f"temp_voice_{self._temp_counter % 2}.mp3"

            async def _generate_audio():
                communicate = edge_tts.Communicate(text, "es-MX-JorgeNeural", rate="+0%")
                await communicate.save(temp_file)

            asyncio.run(_generate_audio())

            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if interrupt_callback and interrupt_callback():
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    if os.path.exists(temp_file):
                        try: os.remove(temp_file)
                        except: pass
                    return True, True
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
            if os.path.exists(temp_file):
                try: os.remove(temp_file)
                except: pass
            
            return True, False
        except Exception as e:
            print(f"  ⚠️  Falla de red neural: Usando voz de respaldo local...")
            return False, False

    def _speak_local(self, text: str):
        """Reproduce texto usando el motor de voz de Windows (SAPI5)."""
        try:
            self.local_engine.say(text)
            self.local_engine.runAndWait()
        except Exception as e:
            print(f"  ❌  Error crítico en TTS local: {e}")
