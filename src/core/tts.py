import os
import re
import asyncio
import edge_tts
import pygame


class TTSProvider:
    def __init__(self) -> None:
        # Inicializamos el mixer de audio de pygame
        pygame.mixer.init()
        self._temp_counter = 0

    def speak(self, text: str) -> None:
        """Sintetiza y reproduce texto con voz neural, oración por oración para menor latencia."""
        # Imprimir la respuesta completa en consola
        print(f"  🔊  Jarvis: «{text}»")

        # Limpiar Markdown para no confundir al motor TTS
        clean_text = text.replace("*", "").replace("#", "").replace("_", "").replace("`", "").strip()

        if not clean_text:
            return

        # Dividir en oraciones para responder más rápido (streaming por oración)
        sentences = self._split_sentences(clean_text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 2:
                continue
            self._speak_chunk(sentence)

    def _split_sentences(self, text: str) -> list[str]:
        """Divide el texto en oraciones usando puntuación como separador."""
        # Dividir por . ! ? pero mantener el separador
        parts = re.split(r'(?<=[.!?])\s+', text)
        # Si el texto no tiene puntuación, devolver como una sola pieza
        if len(parts) <= 1:
            return [text]
        return parts

    def _speak_chunk(self, text: str) -> None:
        """Genera y reproduce un fragmento de audio."""
        try:
            self._temp_counter += 1
            temp_file = f"temp_voice_{self._temp_counter % 2}.mp3"

            # Función asíncrona para generar el archivo mp3
            async def _generate_audio():
                # Usamos a Elvira (voz femenina natural de España)
                communicate = edge_tts.Communicate(text, "es-ES-ElviraNeural", rate="+10%")
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
