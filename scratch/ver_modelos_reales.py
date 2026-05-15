import os
from google import genai
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

def list_my_models():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("--- MODELOS DISPONIBLES EN TU CUENTA ---")
    try:
        # Listamos los modelos soportados para generar contenido
        for model in client.models.list():
            if "generateContent" in model.supported_generation_methods:
                print(f"ID: {model.name} (DisplayName: {model.display_name})")
    except Exception as e:
        print(f"Error al listar modelos: {e}")

if __name__ == "__main__":
    list_my_models()
