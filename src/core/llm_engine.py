import os
import warnings
import time
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=FutureWarning)
load_dotenv()

class LLMEngine:
    def __init__(self, tools_list: list = None) -> None:
        self.tools_list = tools_list if tools_list else []
        self.api_keys = []
        
        # Cargar llaves del .env
        base_key = os.getenv("GEMINI_API_KEY")
        if base_key: self.api_keys.append(base_key.strip())
        for i in range(1, 10):
            k = os.getenv(f"GEMINI_API_KEY_{i}")
            if k: self.api_keys.append(k.strip())
            
        if not self.api_keys:
            raise ValueError("No se encontraron API Keys en el .env")
            
        print(f"  🔑  Sistema de llaves listo: {len(self.api_keys)} llaves cargadas.")
        
        self.current_key_idx = 0
        # 2. Modelos de respaldo en cascada (Nombres reales de 2026)
        self.models_cascade = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
        self.current_model_idx = 0
        
        self.system_instruction = (
            "Eres Jarvis, asistente de Carlos. Responde siempre en español con acento y modismos de Colombia (tono ejecutivo paisa profesional, natural y amable). "
            "Eres eficiente, culto y respetuoso. Usa las herramientas para controlar la PC. "
            "Si el usuario pide información que no tienes, usa 'investigar_en_internet'."
        )
        
        self._init_client()

    def _init_client(self):
        """Configura el cliente con la combinación actual de Key y Modelo."""
        try:
            key = self.api_keys[self.current_key_idx]
            model = self.models_cascade[self.current_model_idx]
            
            self.client = genai.Client(api_key=key)
            self.chat = self.client.chats.create(
                model=model,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=self.tools_list
                )
            )
            print(f"  🧠  Cerebro conectado: {model} (Llave #{self.current_key_idx + 1})")
        except Exception as e:
            print(f"  ❌  Error al inicializar cliente: {e}")

    def _rotate_fallback(self) -> bool:
        """Prueba la siguiente llave. Si no hay más, prueba el siguiente modelo."""
        if self.current_key_idx < len(self.api_keys) - 1:
            self.current_key_idx += 1
            self._init_client()
            return True
        elif self.current_model_idx < len(self.models_cascade) - 1:
            self.current_model_idx += 1
            self.current_key_idx = 0
            self._init_client()
            return True
        return False

    def send_message(self, text: str) -> tuple[str, list]:
        """Envía mensaje y maneja reintentos por cuota/errores."""
        intentos = 0
        max_intentos = len(self.api_keys) * len(self.models_cascade)
        
        while intentos < max_intentos:
            try:
                response = self.chat.send_message(text)
                
                tool_calls = []
                if response.function_calls:
                    tool_calls = list(response.function_calls)
                
                return (response.text or "").strip(), tool_calls
                
            except Exception as e:
                err = str(e).lower()
                intentos += 1
                
                # Rotar llave ante cualquier error (cuota, formato, expiración, inválida, etc.)
                print(f"  ⚠️  Llave #{self.current_key_idx + 1} falló: {e}. Rotando...")
                if self._rotate_fallback():
                    time.sleep(1) # Esperar un segundo para no saturar
                    continue
                
                print(f"  ❌  Error en comunicación: {e}")
                return "Tuve un problema al procesar eso. ¿Podés repetir?", []
        
        return "Lo siento Carlos, todas mis redes neuronales están saturadas ahora mismo.", []
