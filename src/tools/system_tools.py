import os
import time
import subprocess
import webbrowser

def abrir_entorno_trabajo() -> str:
    """
    Abre las herramientas de desarrollo de Carlos: Cursor y Claude, y las organiza lado a lado en la pantalla.
    Usa esta herramienta cuando el usuario pida programar, trabajar o abrir el entorno.
    """
    print("  💻  Ejecutando: abrir_entorno_trabajo...")
    
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    sw = user32.GetSystemMetrics(0)
    sh = user32.GetSystemMetrics(1)
    mitad = sw // 2

    # Abre Claude
    claude_path = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Claude\Claude.exe")
    if os.path.exists(claude_path):
        subprocess.Popen([claude_path])
    
    # Abre Cursor
    cursor_path = os.path.expandvars(r"%LOCALAPPDATA%\Programs\cursor\Cursor.exe")
    new_project = os.path.expanduser("~/Desktop/nuevo_proyecto")
    os.makedirs(new_project, exist_ok=True)
    if os.path.exists(cursor_path):
        subprocess.Popen([cursor_path, new_project])
    else:
        # Intenta por PATH
        subprocess.run(["cmd", "/c", "start", "cursor", new_project])
        
    time.sleep(2.0)
    
    try:
        # pyrefly: ignore [missing-import]
        import pygetwindow as gw
        
        claude_windows = gw.getWindowsWithTitle('Claude')
        if claude_windows:
            cw = claude_windows[0]
            if cw.isMinimized: cw.restore()
            cw.moveTo(0, 0)
            cw.resizeTo(mitad, sh)
            
        cursor_windows = gw.getWindowsWithTitle('Cursor')
        if cursor_windows:
            curw = cursor_windows[0]
            if curw.isMinimized: curw.restore()
            curw.moveTo(mitad, 0)
            curw.resizeTo(mitad, sh)
    except Exception as e:
        print(f"  ❌  Error organizando ventanas: {e}")

    return "Entorno de trabajo abierto correctamente lado a lado."


def reproducir_musica() -> str:
    """
    Abre YouTube y reproduce una lista de música predefinida para Carlos.
    Usa esta herramienta cuando el usuario pida música.
    """
    print("  🎵  Ejecutando: reproducir_musica...")
    youtube_url = "https://www.youtube.com/watch?v=yEASFhtzSMQ&list=RDyEASFhtzSMQ&start_radio=1"
    webbrowser.open(youtube_url)
    return "Música reproduciéndose en YouTube."

# Lista de herramientas para inyectar en Gemini
TOOLS_LIST = [abrir_entorno_trabajo, reproducir_musica]
