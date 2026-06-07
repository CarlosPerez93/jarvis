def cerrar_busqueda() -> str:
    """Cierra todos los modales de búsqueda de la pantalla."""
    from src.core.ui_bridge import close_search
    close_search()
    return "He cerrado todos los resultados de búsqueda."

def minimizar_busqueda() -> str:
    """Minimiza los resultados de búsqueda y los guarda para restaurarlos después."""
    from src.core.ui_bridge import minimize_search
    minimize_search()
    return "He minimizado los resultados. Puede pedirme que los restaure cuando desee."

def restaurar_busqueda() -> str:
    """Restaura los resultados de búsqueda minimizados previamente."""
    from src.core.ui_bridge import restore_search
    restore_search()
    return "He restaurado los resultados de búsqueda."
