"""
Herramientas para la gestión de aplicaciones y procesos del sistema.
"""
import os
import subprocess

# Mapeo de nombres comunes a ejecutables reales de Windows
APP_MAPPING = {
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "bloc de notas": "notepad",
    "notas": "notepad",
    "calculadora": "calc",
    "navegador": "start chrome", # O msedge
    "chrome": "chrome",
    "edge": "msedge",
    "spotify": "spotify",
    "discord": "discord",
    "visual studio code": "code",
    "vscode": "code",
    "code": "code"
}

def abrir_programa(nombre_programa: str) -> str:
    """
    Intenta abrir un programa por su nombre.
    Usa un mapeo interno para nombres comunes y el comando 'start' de Windows.
    """
    nombre_clean = nombre_programa.lower().strip()
    print(f"  🚀  Intentando abrir: {nombre_clean}...")
    
    # 1. Buscar en el mapeo inteligente
    ejecutable = APP_MAPPING.get(nombre_clean, nombre_clean)
    
    try:
        # 2. Intentar con el comando 'start' de Windows (es el más robusto para apps registradas)
        # Usamos shell=True para que reconozca los comandos internos de CMD
        cmd = f"start {ejecutable}"
        subprocess.Popen(cmd, shell=True)
        return f"Abriendo {nombre_programa}."
    except Exception:
        try:
            # 3. Fallback a os.startfile si lo anterior falla
            os.startfile(ejecutable)
            return f"Abriendo {nombre_programa}."
        except Exception as e:
            print(f"  ⚠️  Error al abrir {nombre_clean}: {e}")
            return f"No pude encontrar '{nombre_programa}'. Verificá si está instalado o probá con otro nombre."

def cerrar_proceso(nombre_proceso: str) -> str:
    """Fuerza el cierre de un proceso (ej: 'Spotify.exe')."""
    print(f"  🛑  Cerrando: {nombre_proceso}...")
    try:
        if not nombre_proceso.lower().endswith(".exe"):
            nombre_proceso += ".exe"
        
        # Mapeo inverso para cerrar (si el usuario dice 'Word', cerramos 'winword.exe')
        nombre_clean = nombre_proceso.replace(".exe", "").lower()
        if nombre_clean in APP_MAPPING:
            nombre_proceso = APP_MAPPING[nombre_clean] + ".exe"

        cmd = f'taskkill /F /IM "{nombre_proceso}" /T'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = process.communicate()
        
        if process.returncode == 0:
            return f"Proceso {nombre_proceso} cerrado."
        return f"No pude cerrar {nombre_proceso}. Error: {stderr[:50]}"
    except Exception as e:
        return f"Error al cerrar proceso: {e}"

def abrir_entorno_trabajo() -> str:
    """Abre el conjunto de herramientas de desarrollo del usuario."""
    print("  💻  Abriendo entorno de trabajo...")
    # Podés personalizar esto con lo que más uses
    programas = ["code", "chrome", "spotify"] 
    for p in programas:
        abrir_programa(p)
    return "Entorno de trabajo desplegado."
