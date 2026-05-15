"""
Herramientas para instalar y desinstalar software mediante Winget.
"""
import subprocess

def instalar_programa(nombre_programa: str) -> str:
    """Instala un programa usando Winget."""
    print(f"  📥  Instalando: {nombre_programa}...")
    try:
        cmd = f'winget install "{nombre_programa}" --silent --accept-source-agreements --accept-package-agreements'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = process.communicate()
        
        if process.returncode == 0:
            return f"Instalación de {nombre_programa} completada."
        return f"Error en instalación: {stderr[:100]}"
    except Exception as e:
        return f"Fallo al instalar: {e}"

def desinstalar_programa(nombre_programa: str) -> str:
    """Desinstala un programa usando Winget."""
    print(f"  🗑️  Desinstalando: {nombre_programa}...")
    try:
        cmd = f'winget uninstall "{nombre_programa}" --silent --accept-source-agreements'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = process.communicate()
        
        if process.returncode == 0:
            return f"Desinstalación de {nombre_programa} completada."
        return f"Error al desinstalar: {stderr[:100]}"
    except Exception as e:
        return f"Fallo al desinstalar: {e}"
