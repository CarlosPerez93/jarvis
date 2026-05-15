"""
Herramientas para controlar el ciclo de vida de la aplicación.
"""
import os
import signal

def finalizar_sesion() -> str:
    """Cierra Jarvis por completo."""
    print("  👋  Finalizando sesión...")
    # Matamos el proceso actual
    os.kill(os.getpid(), signal.SIGTERM)
    return "Cerrando sistemas. ¡Hasta pronto!"
