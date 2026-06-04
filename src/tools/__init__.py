"""
Registro central de todas las herramientas inyectables en Gemini.
"""
# Herramientas de Sistema (Refactorizadas SOLID)
from .system.apps import abrir_programa, abrir_entorno_trabajo, cerrar_proceso
from .system.volume import subir_volumen, bajar_volumen, establecer_volumen, silenciar_volumen
from .system.software import instalar_programa, desinstalar_programa
from .system.media import reproducir_musica
from .system.session import finalizar_sesion

# Herramientas de Información
from .info_tools import obtener_hora, obtener_clima, investigar_en_internet, leer_registro_ia

# Herramientas de Navegación (GPS)
from .navigation import buscar_en_mapa, trazar_ruta

# Lista maestra de herramientas para inyectar en Gemini
TOOLS_LIST = [
    # Aplicaciones y Procesos
    abrir_programa,
    abrir_entorno_trabajo,
    cerrar_proceso,
    
    # Software (Winget)
    instalar_programa,
    desinstalar_programa,
    
    # Multimedia
    reproducir_musica,
    
    # Volumen
    subir_volumen,
    bajar_volumen,
    establecer_volumen,
    silenciar_volumen,
    
    # Sesión
    finalizar_sesion,
    
    # Información
    obtener_hora,
    obtener_clima,
    investigar_en_internet,
    leer_registro_ia,
    
    # Navegación y Mapas
    buscar_en_mapa,
    trazar_ruta,
]
