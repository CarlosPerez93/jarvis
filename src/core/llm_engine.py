import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import warnings

# Suprimir el warning de deprecación para no ensuciar la consola
warnings.filterwarnings("ignore", category=FutureWarning)

# Cargar variables de entorno desde .env
load_dotenv()

class LLMEngine:
    def __init__(self, tools_list: list = None) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "tu_api_key_aqui":
            raise ValueError("❌ No se encontró la GEMINI_API_KEY en el archivo .env")
        
        genai.configure(api_key=api_key)
        
        # Inicializamos el modelo con la instrucción de sistema y las herramientas
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=tools_list if tools_list else [],
            system_instruction=(
                "Eres Jarvis, un asistente virtual avanzado que corre en el escritorio de Windows de Carlos. "
                "Sos eficiente, amable y tenés una voz femenina y natural. "
                "Si Carlos te pide que abras un programa (Word, Excel, Chrome, etc), usa la herramienta 'abrir_programa' infiriendo el nombre corto del ejecutable o la app. "
                "Si te pide poesía, cuentos, chistes o cantar, hacelo con gusto y creatividad, sin limitaciones. "
                "Para conversaciones normales, respondé de forma conversacional y natural."
            )
        )
        # Usamos disable_automatic_function_calling porque nosotros manejaremos la ejecución y confirmación manual
        self.chat = self.model.start_chat()

    def send_message(self, text: str) -> tuple[str, list]:
        """
        Envía el mensaje del usuario al LLM.
        Retorna la respuesta de texto (si la hay) y una lista de llamadas a herramientas (function_calls).
        """
        print("  🧠  Jarvis está pensando...")
        response = self.chat.send_message(text)
        
        tool_calls = []
        text_response = ""
        
        for part in response.parts:
            if part.function_call:
                tool_calls.append(part.function_call)
            if part.text:
                text_response += part.text + " "

        return text_response.strip(), tool_calls
