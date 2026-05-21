"""
Módulo de navegación y mapas para Jarvis.
"""
import webbrowser
import urllib.parse

def buscar_en_mapa(consulta: str) -> str:
    """
    Busca un lugar, tienda, parking o punto de interés en el mapa de Google usando el navegador.
    
    Args:
        consulta: El nombre del lugar, tipo de negocio o establecimiento a buscar (ej: 'parking', 'supermercado', 'restaurante').
        
    Returns:
        Mensaje confirmando la búsqueda realizada.
    """
    consulta_encoded = urllib.parse.quote(consulta)
    url = f"https://www.google.com/maps/search/?api=1&query={consulta_encoded}"
    webbrowser.open(url)
    return f"Perfecto, Carlos. He abierto el navegador buscando '{consulta}' en el mapa."

def trazar_ruta(destino: str) -> str:
    """
    Trazar una ruta o indicaciones desde la ubicación actual hasta un destino en el mapa de Google usando el navegador.
    
    Args:
        destino: La dirección, ciudad o nombre del sitio de destino al que se desea llegar (ej: 'Aeropuerto El Dorado', 'Medellín').
        
    Returns:
        Mensaje confirmando el inicio del cálculo de la ruta.
    """
    destino_encoded = urllib.parse.quote(destino)
    url = f"https://www.google.com/maps/dir/?api=1&destination={destino_encoded}"
    webbrowser.open(url)
    return f"De una, Carlos. Ya tracé la ruta hacia '{destino}' en el mapa."
