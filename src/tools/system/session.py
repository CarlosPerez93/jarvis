class ExitSession(Exception):
    """Excepción para terminar la sesión de Jarvis de forma limpia."""
    pass

def finalizar_sesion() -> str:
    """Cierra Jarvis por completo."""
    print("  👋  Finalizando sesión...")
    raise ExitSession("Cerrando todos los sistemas de Jarvis. ¡Hasta pronto, señor Carlos, que esté muy bien!")
