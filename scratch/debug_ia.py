import os
from google import genai
from google.genai import types
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

def test_everything():
    keys = []
    base_key = os.getenv("GEMINI_API_KEY")
    if base_key: keys.append(base_key.strip())
    for i in range(1, 4):
        k = os.getenv(f"GEMINI_API_KEY_{i}")
        if k: keys.append(k.strip())
    
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    
    print("--- DIAGNOSTICO DE RED NEURONAL ---")
    print(f"Llaves encontradas: {len(keys)}")
    
    for idx, key in enumerate(keys):
        print(f"\n--- Probando Key #{idx+1} ({key[:8]}...) ---")
        try:
            client = genai.Client(api_key=key)
            for model in models:
                try:
                    print(f"  Modelo {model}: ", end="", flush=True)
                    response = client.models.generate_content(
                        model=model,
                        contents="Hola, responde OK."
                    )
                    print(f"OK (Respuesta: {response.text.strip()})")
                except Exception as em:
                    print(f"ERROR: {em}")
        except Exception as ek:
            print(f"ERROR DE CLIENTE: {ek}")

if __name__ == "__main__":
    test_everything()
