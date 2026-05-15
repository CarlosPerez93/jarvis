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
            "¿Qué necesitás?",
            "Acá estoy. ¿En qué te ayudo?",
            "Te escucho.",
            "A tus órdenes. ¿Qué hacemos?",
            "Presente. ¿Qué se te ofrece?",
            "Dime.",
            "Si.",
            ]

    def run_interaction(self) -> None:
        """Ejecuta un ciclo completo de interacción: saludo → escuchar → pensar → responder/ejecutar."""
        # 1. Saludo
        print("  📢  Saludando...")
        greeting = random.choice(self._greetings)
        self.tts.speak(greeting)

        # 2. Escuchar
        print("  👂  Abriendo escucha de voz...")
        user_text = self.audio.listen(timeout=7, phrase_time_limit=12)
        
        if not user_text:
            print("  🤫  No se detectó habla.")
            self.tts.speak("No te escuché. Decime 'Hey Jarvis' cuando necesites algo.")
            return

        # 3. Pensar
        print(f"  🧠  Procesando con Gemini: «{user_text}»")
        text_response, tool_calls = self.llm.send_message(user_text)

        # 4. Responder texto
        if text_response:
            print("  🗣️  Generando respuesta de voz...")
            self.tts.speak(text_response)

        # 5. Ejecutar herramientas
        if tool_calls:
            print(f"  🛠️  Ejecutando {len(tool_calls)} herramientas...")
            for tool_call in tool_calls:
                func_name = tool_call.name
                if func_name in self.tools_map:
                    kwargs = dict(tool_call.args) if hasattr(tool_call, "args") and tool_call.args else {}
                    try:
                        print(f"  ⚙️  Llamando a {func_name}...")
                        result_msg = self.tools_map[func_name](**kwargs)
                        if not text_response:
                            self.tts.speak(result_msg)
                    except Exception as e:
                        print(f"  ❌  Error en herramienta {func_name}: {e}")
                        self.tts.speak("Tuve un problema al realizar esa acción.")
                else:
                    self.tts.speak(f"No conozco la herramienta {func_name}.")
