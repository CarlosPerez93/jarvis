import random
import time
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

        # Saludos variados
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
        """Mantiene una conversación fluida hasta que el usuario deja de hablar."""
        # 1. Saludo inicial (solo la primera vez)
        print("  📢  Saludando...")
        greeting = random.choice(self._greetings)
        self.tts.speak(greeting)

        continuar_charla = True
        
        while continuar_charla:
            # 2. Escuchar comando
            print("  👂  Escuchando...")
            # Dejamos que el AudioListener maneje los límites dinámicamente desde el .env
            user_text = self.audio.listen(timeout=5)
            
            if not user_text:
                print("  🤫  Silencio detectado. Volviendo a modo espera.")
                # Opcional: Jarvis puede despedirse o simplemente quedar en silencio
                # self.tts.speak("Cualquier cosa avisame.")
                continuar_charla = False
                continue

            # 3. Pensar
            print(f"  🧠  Procesando: «{user_text}»")
            text_response, tool_calls = self.llm.send_message(user_text)

            # 4. Responder texto
            if text_response:
                print(f"  🗣️  Jarvis: {text_response}")
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
                            # Si no hubo respuesta de texto previa, decimos el resultado de la herramienta
                            if not text_response:
                                self.tts.speak(result_msg)
                        except Exception as e:
                            print(f"  ❌  Error en herramienta {func_name}: {e}")
                            self.tts.speak("Tuve un problema al realizar esa acción.")
                    else:
                        self.tts.speak(f"No conozco la herramienta {func_name}.")

            # 6. Decidir si seguimos (heurística simple: si la respuesta termina en '?' o es corta)
            # Por ahora, simplemente intentamos escuchar UNA VEZ MÁS siempre.
            # Si el usuario quiere terminar, suele decir "gracias" o quedarse en silencio.
            if any(bye in user_text.lower() for bye in ["gracias", "chau", "adiós", "nada más"]):
                print("  👋  Despedida detectada.")
                continuar_charla = False
                
            print("  ⏳  Esperando por si tenés algo más que decir...")
            # Pequeña pausa visual
