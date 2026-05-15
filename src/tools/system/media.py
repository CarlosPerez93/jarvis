"""
Herramientas para el control de medios y reproducción.
"""
import webbrowser

def reproducir_musica(busqueda: str) -> str:
    """Busca y reproduce música en YouTube."""
    print(f"  🎵  Buscando música: {busqueda}...")
    url = f"https://www.youtube.com/results?search_query={busqueda.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Buscando '{busqueda}' en YouTube."
