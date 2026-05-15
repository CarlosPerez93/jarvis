import random
from .audio import AudioListener
from .tts import TTSProvider
from .llm_engine import LLMEngine
from src.tools import TOOLS_LIST


class DialogueManager:
    def __init__(self) -> None:
        self.audio = AudioListener()
        self.tts = TTSProvider()
        self.llm = LLMEngine(tools_list=TOOLS_LIST)

        # Mapear nombres de las funciones a sus objetos en memoria
        self.tools_map = {tool.__name__: tool for tool in TOOLS_LIST}

        # Saludos variados para que suene más natural
        self._greetings = [
            "¿Qué necesitás, Carlos?",
            "Acá estoy. ¿En qué te ayudo?",
            "Te escucho, Carlos.",
            "A tus órdenes. ¿Qué hacemos?",
            "Presente. ¿Qué se te ofrece?",
            "Dime, Carlos.",
        ]

    def run_interaction(self) -> None:
        """Ejecuta un ciclo completo de interacción: saludo → escuchar → pensar → responder/ejecutar."""
        # 1. Saludo natural y variado
        greeting = random.choice(self._greetings)
        self.tts.speak(greeting)

        # 2. Escuchamos el comando de voz
        user_text = self.audio.listen(timeout=8, phrase_time_limit=15)
        if not user_text:
            self.tts.speak("No te escuché. Decime 'Hey Jarvis' cuando necesites algo.")
            return

        # 3. Pasamos el texto al Cerebro (Gemini)
        text_response, tool_calls = self.llm.send_message(user_text)

        # 4. Si Gemini respondió con texto (charla, info, etc.)
        if text_response:
            self.tts.speak(text_response)

        # 5. Si Gemini decidió usar herramientas, las ejecutamos directamente (sin confirmación)
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.name
                if func_name in self.tools_map:
                    kwargs = dict(tool_call.args) if hasattr(tool_call, "args") and tool_call.args else {}
                    try:
                        result_msg = self.tools_map[func_name](**kwargs)
                        # Solo hablar el resultado si no hubo respuesta de texto ya
                        if not text_response:
                            self.tts.speak(result_msg)
                    except Exception as e:
                        print(f"  ❌  Error al ejecutar {func_name}: {e}")
                        self.tts.speak("Ocurrió un error al ejecutar esa acción.")
                else:
                    self.tts.speak(f"No conozco la herramienta {func_name}.")
