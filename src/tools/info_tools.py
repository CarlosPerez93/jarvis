import datetime
import urllib.request
import json


def obtener_hora() -> str:
    """
    Devuelve la fecha y hora actual del sistema.
    Usa esta herramienta cuando el usuario pregunte qué hora es, qué día es, o la fecha actual.
    """
    print("  🕐  Ejecutando: obtener_hora...")
    ahora = datetime.datetime.now()

    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    dia_semana = dias[ahora.weekday()]
    mes = meses[ahora.month - 1]
    hora = ahora.strftime("%H:%M")

    return f"Son las {hora} del {dia_semana} {ahora.day} de {mes} de {ahora.year}."


def obtener_clima(ciudad: str) -> str:
    """
    Obtiene el clima actual de una ciudad usando la API gratuita wttr.in (no requiere key).
    Usa esta herramienta cuando el usuario pregunte por el clima o el tiempo en algún lugar.
    """
    print(f"  🌤️  Ejecutando: obtener_clima({ciudad})...")
    try:
        url = f"https://wttr.in/{ciudad}?format=j1&lang=es"
        req = urllib.request.Request(url, headers={"User-Agent": "Jarvis/3.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())

        current = data["current_condition"][0]
        temp = current["temp_C"]
        feels = current["FeelsLikeC"]
        humidity = current["humidity"]
        desc = current.get("lang_es", [{}])
        desc_text = desc[0].get("value", current.get("weatherDesc", [{}])[0].get("value", "")) if desc else ""

        return (
            f"En {ciudad}: {desc_text}, {temp}°C (sensación térmica {feels}°C), "
            f"humedad del {humidity}%."
        )
    except Exception as e:
        return f"No pude obtener el clima de {ciudad}: {e}"
