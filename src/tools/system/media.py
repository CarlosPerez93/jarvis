"""
Herramientas para el control de medios y reproducción.
"""
import subprocess
import urllib.request
import urllib.parse
import re

def reproducir_musica(busqueda: str) -> str:
    """Busca en YouTube y reproduce automáticamente el primer resultado encontrado."""
    print(f"  🎵  Buscando música: {busqueda}...")
    
    # Intentamos obtener el primer resultado de YouTube de forma limpia
    query_encoded = urllib.parse.quote(busqueda)
    url_busqueda = f"https://www.youtube.com/results?search_query={query_encoded}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(url_busqueda, headers=headers)
        # Timeout corto de 4 segundos para que el asistente no se quede colgado
        with urllib.request.urlopen(req, timeout=4) as response:
            html = response.read().decode('utf-8')
            # Buscamos enlaces de video tradicionales: /watch?v=XXXXXXXXXXX
            matches = re.findall(r'/watch\?v=[a-zA-Z0-9_-]{11}', html)
            
            if matches:
                # Deduplicamos manteniendo el orden original
                unique_matches = []
                for m in matches:
                    if m not in unique_matches:
                        unique_matches.append(m)
                
                # El primer match único suele ser el video correcto
                video_url = f"https://www.youtube.com{unique_matches[0]}"
                print(f"  🚀  ¡Primer resultado encontrado!: {video_url}")
                subprocess.Popen(f'start "" "{video_url}"', shell=True)
                return f"¡De una! Ahí te puse a reproducir el primer resultado de '{busqueda}' en YouTube."
    except Exception as e:
        print(f"  ⚠️  No se pudo resolver el primer resultado directo ({e}). Usando página de búsqueda.")
    
    # Fallback robusto: abrir la página de búsqueda completa si el raspado directo falla
    try:
        subprocess.Popen(f'start "" "{url_busqueda}"', shell=True)
        return f"Busqué '{busqueda}' en YouTube para vos. Elegí el video que prefieras."
    except Exception as e:
        print(f"  ⚠️  Error al abrir YouTube: {e}")
        return f"Tuve un problema al intentar abrir YouTube, pero lo podés buscar como '{busqueda}'."


