import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_my_models():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("--- MODELOS DISPONIBLES EN TU CUENTA ---")
    try:
        # Imprimimos todo lo que nos devuelva para ver la estructura
        models = client.models.list()
        for m in models:
            print(f"Name: {m.name}")
    except Exception as e:
        print(f"Error al listar modelos: {e}")

if __name__ == "__main__":
    list_my_models()
