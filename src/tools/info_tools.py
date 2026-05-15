import datetime
import urllib.request
import json
import os
from google import genai
from google.genai import types

def obtener_hora() -> str:
    ahora = datetime.datetime.now()
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"Son las {ahora.strftime('%H:%M')} del {dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month - 1]} de {ahora.year}."

def obtener_clima(ciudad: str) -> str:
    try:
        url = f"https://wttr.in/{ciudad}?format=j1&lang=es"
        req = urllib.request.Request(url, headers={"User-Agent": "Jarvis/3.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
        current = data["current_condition"][0]
        return f"En {ciudad} el clima es {current.get('lang_es', [{}])[0].get('value', 'despejado')} con {current['temp_C']}°C."
    except:
        return f"No pude obtener el clima de {ciudad}."

def investigar_en_internet(consulta: str) -> str:
    """Busca en Google usando rotación de llaves si es necesario."""
    print(f"  🔍  Investigando: «{consulta}»...")
    
    # Recolectar todas las llaves posibles
    keys = []
    base_key = os.getenv("GEMINI_API_KEY")
    if base_key: keys.append(base_key.strip())
    for i in range(1, 5):
        k = os.getenv(f"GEMINI_API_KEY_{i}")
        if k: keys.append(k.strip())
        
    for idx, api_key in enumerate(keys):
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=consulta,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            return response.text
        except Exception as e:
            print(f"  ⚠️  Llave #{idx+1} falló en búsqueda: {str(e)[:50]}...")
            continue
            
    return "No pude realizar la búsqueda. Parece que todas mis llaves de internet están agotadas."
