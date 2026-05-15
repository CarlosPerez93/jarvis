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


def abrir_programa(nombre_programa: str) -> str:
    """
    Abre cualquier programa del sistema por su nombre o ejecutable (ej: winword, excel, chrome, calc, notepad).
    Usa esta herramienta cuando el usuario pida abrir una aplicación que no sea el entorno de trabajo por defecto.
    """
    print(f"  💻  Ejecutando: abrir_programa({nombre_programa})...")
    try:
        # En Windows, el comando 'start' lanza programas si están en el PATH o registrados
        subprocess.run(["cmd", "/c", "start", nombre_programa], check=True)
        return f"Programa {nombre_programa} abierto correctamente."
    except Exception as e:
        return f"Error al intentar abrir el programa {nombre_programa}: {e}"


def subir_volumen() -> str:
    """
    Sube el volumen del sistema un 20 por ciento.
    Usa esta herramienta cuando el usuario pida subir el volumen o que se escuche más fuerte.
    """
    print("  🔊  Ejecutando: subir_volumen...")
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        current = volume.GetMasterVolumeLevelScalar()
        new_level = min(1.0, current + 0.2)
        volume.SetMasterVolumeLevelScalar(new_level, None)

        return f"Volumen subido al {int(new_level * 100)}%."
    except Exception as e:
        return f"Error al subir el volumen: {e}"


def bajar_volumen() -> str:
    """
    Baja el volumen del sistema un 20 por ciento.
    Usa esta herramienta cuando el usuario pida bajar el volumen o que se escuche más despacio.
    """
    print("  🔉  Ejecutando: bajar_volumen...")
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        current = volume.GetMasterVolumeLevelScalar()
        new_level = max(0.0, current - 0.2)
        volume.SetMasterVolumeLevelScalar(new_level, None)

        return f"Volumen bajado al {int(new_level * 100)}%."
    except Exception as e:
        return f"Error al bajar el volumen: {e}"


def establecer_volumen(porcentaje: int) -> str:
    """
    Establece el volumen del sistema al porcentaje indicado (0 a 100).
    Usa esta herramienta cuando el usuario pida poner el volumen a un nivel específico.
    """
    print(f"  🔊  Ejecutando: establecer_volumen({porcentaje})...")
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        level = max(0.0, min(1.0, porcentaje / 100.0))
        volume.SetMasterVolumeLevelScalar(level, None)

        return f"Volumen establecido al {int(level * 100)}%."
    except Exception as e:
        return f"Error al establecer el volumen: {e}"


def silenciar_volumen() -> str:
    """
    Silencia o activa el sonido del sistema (toggle mute).
    Usa esta herramienta cuando el usuario pida silenciar o quitar el mute.
    """
    print("  🔇  Ejecutando: silenciar_volumen...")
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        is_muted = volume.GetMute()
        volume.SetMute(not is_muted, None)

        return "Sonido activado." if is_muted else "Sistema silenciado."
    except Exception as e:
        return f"Error al cambiar el mute: {e}"
