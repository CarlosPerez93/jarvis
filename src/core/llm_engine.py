import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
# pyrefly: ignore [missing-import]
from google.api_core import exceptions
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import warnings

# Suprimir el warning de deprecación para no ensuciar la consola
warnings.filterwarnings("ignore", category=FutureWarning)

# Cargar variables de entorno desde .env
load_dotenv()

class LLMEngine:
    def __init__(self, tools_list: list = None) -> None:
        self.tools_list = tools_list if tools_list else []
        
        # 1. Obtener todas las keys disponibles dinámicamente (GEMINI_API_KEY, GEMINI_API_KEY_1, GEMINI_API_KEY_2...)
        self.api_keys = []
        
        # Primero revisamos la llave estándar
        base_key = os.getenv("GEMINI_API_KEY")
        if base_key and base_key != "tu_clave_aca":
            self.api_keys.append(base_key)
            
        # Luego revisamos llaves extra numeradas
        for i in range(1, 10):
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if key and key != "tu_clave_aca":
                self.api_keys.append(key)
                
        if not self.api_keys:
            raise ValueError("❌ No se encontró ninguna GEMINI_API_KEY en el archivo .env")

        self.current_key_idx = 0
        genai.configure(api_key=self.api_keys[self.current_key_idx])
        
        # 2. Modelos de respaldo en cascada (del más potente/limitado al más libre)
        self.models_cascade = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        self.current_model_idx = 0
        
        self.system_instruction = (
            "Eres Jarvis, un asistente virtual avanzado que corre en el escritorio de Windows de Carlos. "
            "Sos eficiente, amable y tenés una voz femenina y natural. "
            "Si Carlos te pide que abras un programa (Word, Excel, Chrome, etc), usa la herramienta 'abrir_programa' infiriendo el nombre corto del ejecutable o la app. "
            "Si te pide poesía, cuentos, chistes o cantar, hacelo con gusto y creatividad, sin limitaciones. "
            "Para conversaciones normales, respondé de forma conversacional y natural."
        )
        
        # Iniciar la primera sesión
        self._init_chat()

    def _init_chat(self, history=None):
        """Inicializa el chat con el modelo y la key actuales, preservando la memoria si existe."""
        model_name = self.models_cascade[self.current_model_idx]
        self.model = genai.GenerativeModel(
            model_name=model_name,
            tools=self.tools_list,
            system_instruction=self.system_instruction
        )
        # Cargamos el historial previo si venimos de un modelo que se quedó sin cuota
        self.chat = self.model.start_chat(history=history if history else [])
        print(f"  🤖  Motor de IA conectado: {model_name} (Key #{self.current_key_idx + 1})")

    def _rotate_fallback(self) -> bool:
        """
        Intenta rotar al siguiente modelo disponible o a la siguiente API Key.
        Retorna True si logró encontrar un respaldo, False si se agotó todo.
        """
        historial_actual = self.chat.history
        
        # Intentamos pasar al siguiente modelo con la misma Key
        if self.current_model_idx + 1 < len(self.models_cascade):
            self.current_model_idx += 1
            print(f"  ⚠️  Cuota agotada. Saltando a modelo de respaldo: {self.models_cascade[self.current_model_idx]}...")
            self._init_chat(history=historial_actual)
            return True
            
        # Si no hay más modelos, pasamos a la siguiente API Key y reseteamos el modelo al más potente
        if self.current_key_idx + 1 < len(self.api_keys):
            self.current_key_idx += 1
            self.current_model_idx = 0
            genai.configure(api_key=self.api_keys[self.current_key_idx])
            print(f"  ⚠️  Llave agotada. Pasando a la API Key de repuesto #{self.current_key_idx + 1}...")
            self._init_chat(history=historial_actual)
            return True
            
        return False

    def send_message(self, text: str) -> tuple[str, list]:
        """
        Envía el mensaje del usuario al LLM. Implementa reintentos en caso de límite de tokens.
        """
        print("  🧠  Jarvis está pensando...")
        
        while True:
            try:
                response = self.chat.send_message(text)
                
                tool_calls = []
                text_response = ""
                
                for part in response.parts:
                    if part.function_call:
                        tool_calls.append(part.function_call)
                    if part.text:
                        text_response += part.text + " "

                return text_response.strip(), tool_calls

            except exceptions.ResourceExhausted:
                # Si explotó el límite de tokens, intentamos rotar de modelo/llave
                if self._rotate_fallback():
                    continue # Volvemos al inicio del while True para reintentar con el nuevo modelo
                else:
                    return "Lo siento, me he quedado sin tokens en todos mis modelos de respaldo.", []
                    
            except Exception as e:
                # Otros errores (internet, parseo, etc)
                print(f"  ❌  Error de IA: {e}")
                return "Tuve un error interno al conectar con mi red neuronal.", []
