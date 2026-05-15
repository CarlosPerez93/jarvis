"""
Registro central de todas las herramientas inyectables en Gemini.
"""
from src.tools.system_tools import (
    abrir_entorno_trabajo,
    reproducir_musica,
    abrir_programa,
    subir_volumen,
    bajar_volumen,
    establecer_volumen,
    silenciar_volumen,
)
from src.tools.info_tools import (
    obtener_hora,
    obtener_clima,
    investigar_en_internet,
)

# Lista maestra de herramientas para inyectar en Gemini
TOOLS_LIST = [
    # Sistema
    abrir_entorno_trabajo,
    reproducir_musica,
    abrir_programa,
    # Volumen
    subir_volumen,
    bajar_volumen,
    establecer_volumen,
    silenciar_volumen,
    # Información
    obtener_hora,
    obtener_clima,
    investigar_en_internet, # <--- Nueva herramienta de búsqueda
]
