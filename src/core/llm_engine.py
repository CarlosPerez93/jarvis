import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import warnings

# Suprimir warnings innecesarios
warnings.filterwarnings("ignore", category=FutureWarning)

# Cargar variables de entorno desde .env
load_dotenv()


class LLMEngine:
    def __init__(self, tools_list: list = None) -> None:
        self.tools_list = tools_list if tools_list else []

        # 1. Obtener todas las keys disponibles (GEMINI_API_KEY, GEMINI_API_KEY_1, GEMINI_API_KEY_2...)
        self.api_keys = []

        base_key = os.getenv("GEMINI_API_KEY")
        if base_key and base_key != "tu_clave_aca":
            self.api_keys.append(base_key)

        for i in range(1, 10):
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if key and key != "tu_clave_aca":
                self.api_keys.append(key)

        if not self.api_keys:
            raise ValueError("❌ No se encontró ninguna GEMINI_API_KEY en el archivo .env")

        self.current_key_idx = 0

        # 2. Modelos de respaldo en cascada (del más potente/limitado al más libre)
        self.models_cascade = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        self.current_model_idx = 0

        self.system_instruction = (
            "Eres Jarvis, un asistente virtual avanzado que corre en el escritorio de Windows de Carlos. "
            "Sos eficiente, amable y tenés una personalidad cálida y natural. "
            "Respondé siempre en español rioplatense, como si fueras un asistente personal de confianza. "
            "Si Carlos te pide que abras un programa (Word, Excel, Chrome, etc), usa la herramienta 'abrir_programa'. "
            "Si te pide que suba o baje el volumen, usa las herramientas de volumen. "
            "Si te pide la hora o el clima, usa las herramientas correspondientes. "
            "Si te pide poesía, cuentos, chistes o cantar, hacelo con gusto y creatividad. "
            "Cuando te busque información que no sabés, usá la herramienta de búsqueda web. "
            "Respondé de forma breve y conversacional. No hagas listas largas ni explicaciones innecesarias."
        )

        # 3. Inicializar el cliente y la sesión de chat
        self._init_client()

    def _init_client(self, history=None):
        """Inicializa el cliente y la sesión de chat con el modelo y la key actuales."""
        model_name = self.models_cascade[self.current_model_idx]

        self.client = genai.Client(api_key=self.api_keys[self.current_key_idx])

        # Configuración con herramientas personalizadas + Google Search
        tools_config = list(self.tools_list) if self.tools_list else []
        # Agregar Google Search como herramienta integrada
        tools_config.append(types.Tool(google_search=types.GoogleSearch()))

        self.chat_config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            tools=tools_config,
        )

        self.chat = self.client.chats.create(
            model=model_name,
            config=self.chat_config,
            history=history if history else [],
        )

        print(f"  🤖  Motor de IA conectado: {model_name} (Key #{self.current_key_idx + 1})")

    def _rotate_fallback(self) -> bool:
        """
        Intenta rotar al siguiente modelo disponible o a la siguiente API Key.
        Retorna True si logró encontrar un respaldo, False si se agotó todo.
        """
        historial_actual = self.chat.get_history() if hasattr(self.chat, 'get_history') else []

        # Intentamos pasar al siguiente modelo con la misma Key
        if self.current_model_idx + 1 < len(self.models_cascade):
            self.current_model_idx += 1
            print(f"  ⚠️  Cuota agotada. Saltando a: {self.models_cascade[self.current_model_idx]}...")
            self._init_client(history=historial_actual)
            return True

        # Si no hay más modelos, pasamos a la siguiente API Key
        if self.current_key_idx + 1 < len(self.api_keys):
            self.current_key_idx += 1
            self.current_model_idx = 0
            print(f"  ⚠️  Llave agotada. Pasando a Key #{self.current_key_idx + 1}...")
            self._init_client(history=historial_actual)
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

                # La nueva SDK expone function_calls directamente
                if response.function_calls:
                    tool_calls = list(response.function_calls)

                if response.text:
                    text_response = response.text

                return text_response.strip(), tool_calls

            except Exception as e:
                error_str = str(e).lower()
                # Detectar errores de cuota/recursos agotados
                if "resource" in error_str and "exhausted" in error_str or "429" in error_str or "quota" in error_str:
                    if self._rotate_fallback():
                        continue
                    else:
                        return "Lo siento, me he quedado sin tokens en todos mis modelos de respaldo.", []

                # Otros errores
                print(f"  ❌  Error de IA: {e}")
                return "Tuve un error interno al conectar con mi red neuronal.", []
