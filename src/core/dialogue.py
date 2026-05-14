import sys
from .audio import AudioListener
from .tts import TTSProvider
from .llm_engine import LLMEngine
from src.tools.system_tools import TOOLS_LIST

class DialogueManager:
    def __init__(self) -> None:
        self.audio = AudioListener()
        self.tts = TTSProvider()
        self.llm = LLMEngine(tools_list=TOOLS_LIST)
        
        # Mapear nombres de las funciones a sus objetos en memoria
        self.tools_map = {tool.__name__: tool for tool in TOOLS_LIST}

    def run_interaction(self) -> None:
        self.tts.speak("¿Qué desea hacer, Carlos?")
        
        # 1. Escuchamos el comando de voz
        user_text = self.audio.listen(timeout=10, phrase_time_limit=15)
        if not user_text:
            return 
            
        # 2. Pasamos el texto al Cerebro (Gemini)
        text_response, tool_calls = self.llm.send_message(user_text)
        
        # 3. Si Gemini decidió responder con charla (Ej: "La capital de Francia es París")
        if text_response:
            self.tts.speak(text_response)
            
        # 4. Si Gemini decidió que hay que usar una herramienta (Ej: abrir apps)
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.name
                
                # Pedimos confirmación antes de ejecutar código
                self.tts.speak(f"Comprendido. Me dispongo a ejecutar: {func_name.replace('_', ' ')}. ¿Confirma la acción?")
                
                confirm_text = self.audio.listen(timeout=5, phrase_time_limit=5)
                
                # Palabras clave de confirmación afirmativa
                afirmaciones = ["sí", "si", "claro", "dale", "ok", "obvio", "confirmo", "por supuesto", "adelante"]
                
                if confirm_text and any(word in confirm_text.lower() for word in afirmaciones):
                    self.tts.speak("Ejecutando de inmediato, señor.")
                    
                    # Invocamos la función real en Python
                    if func_name in self.tools_map:
                        kwargs = {k: v for k, v in tool_call.args.items()} if hasattr(tool_call, "args") else {}
                        try:
                            result_msg = self.tools_map[func_name](**kwargs)
                            self.tts.speak(result_msg)
                        except Exception as e:
                            print(f"Error interno al ejecutar {func_name}: {e}")
                            self.tts.speak("Ocurrió un error al intentar abrir el programa.")
                    else:
                        self.tts.speak("Lo siento, esa herramienta no existe en mi base de datos.")
                else:
                    self.tts.speak("Acción abortada.")
