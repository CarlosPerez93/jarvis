import os
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Cargar variables desde el archivo .env en el directorio del script
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
for m in client.models.list():
    print(m.name)
