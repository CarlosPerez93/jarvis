import re

class SimulatedToolCall:
    """Simula una llamada a función del SDK de Gemini para mantener compatibilidad en diálogo."""
    def __init__(self, name: str, args: dict = None):
        self.name = name
        self.args = args or {}

class OfflineIntentParser:
    """
    Parser ligero basado en expresiones regulares para detectar y ejecutar
    herramientas locales del sistema cuando Jarvis no tiene conexión a internet.
    """
    def __init__(self) -> None:
        pass

    def parse(self, text: str) -> tuple[str, list]:
        """
        Analiza el texto de Carlos y devuelve un text_response y una lista de tool_calls simulados.
        """
        text_lower = text.lower().strip()
        
        # 1. Volumen Establecer (Ej: "poné el volumen al 50", "volumen 80")
        match_vol_set = re.search(r'(?:volumen al|volumen en|volumen|poner volumen al)\s*(\d+)', text_lower)
        if match_vol_set:
            try:
                nivel = int(match_vol_set.group(1))
                return "Configurando el volumen al {}% Carlos.".format(nivel), [
                    SimulatedToolCall("establecer_volumen", {"nivel": nivel})
                ]
            except ValueError:
                pass

        # 2. Volumen Subir
        if any(x in text_lower for x in ["subir volumen", "subi volumen", "subí el volumen", "mas volumen", "más volumen", "subilo", "subí"]):
            return "Subiendo el volumen.", [SimulatedToolCall("subir_volumen")]

        # 3. Volumen Bajar
        if any(x in text_lower for x in ["bajar volumen", "baja volumen", "bajá el volumen", "menos volumen", "bajalo", "bajá"]):
            return "Bajando el volumen.", [SimulatedToolCall("bajar_volumen")]

        # 4. Volumen Silenciar/Toggle
        if any(x in text_lower for x in ["silenciar", "silencia", "silenciá", "mutear", "muteá", "desmutear", "activar sonido", "sacar silencio"]):
            return "Cambiando estado de silencio.", [SimulatedToolCall("silenciar_volumen")]

        # 5. Abrir Entorno de Trabajo ("vamos a programar", "entorno de trabajo")
        if any(x in text_lower for x in ["vamos a programar", "entorno de trabajo", "abrir entorno", "modo programar"]):
            return "Preparando el entorno Carlos. Abriendo Claude y Cursor en paralelo.", [
                SimulatedToolCall("abrir_entorno_trabajo")
            ]

        # 6. Abrir Programa genérico (Ej: "abrí Chrome", "abrir bloc de notas")
        match_abrir = re.search(r'(?:abrir|abri|abrí|ejecutar)\s+(.+)', text_lower)
        if match_abrir:
            programa = match_abrir.group(1).strip()
            return "Abriendo el programa {} en este instante.".format(programa), [
                SimulatedToolCall("abrir_programa", {"nombre_programa": programa})
            ]

        # 7. Cerrar Proceso genérico (Ej: "cerrá Chrome", "cerrar notepad")
        match_cerrar = re.search(r'(?:cerrar|cerra|cerrá|matar|mata)\s+(.+)', text_lower)
        if match_cerrar:
            proceso = match_cerrar.group(1).strip()
            return "Cerrando el proceso {} de forma segura.".format(proceso), [
                SimulatedToolCall("cerrar_proceso", {"nombre_proceso": proceso})
            ]

        # 8. Reproducir música (Ej: "poné música", "reproducir música")
        if any(x in text_lower for x in ["musica", "música", "reproducir música", "pone musica", "poné música"]):
            return "Abriendo YouTube para meter ritmo.", [SimulatedToolCall("reproducir_musica")]

        # 9. Diagnóstico de sistema (Ej: "cómo está el sistema", "diagnóstico de pc", "estado de hardware")
        if any(x in text_lower for x in ["sistema", "hardware", "cpu", "memoria", "diagnostico", "diagnóstico", "cómo está la pc", "como esta la pc"]):
            return "", [SimulatedToolCall("obtener_estado_sistema")]

        # 10. Obtener Hora/Fecha
        if any(x in text_lower for x in ["hora", "qué hora es", "que hora es", "fecha", "día", "dia"]):
            return "", [SimulatedToolCall("obtener_hora")]

        # 11. Obtener Clima ( offline, reportamos que requiere red)
        if any(x in text_lower for x in ["clima", "temperatura", "frío", "calor", "llueve"]):
            return "Carlos, estoy en modo offline y no puedo conectarme a internet para ver el clima de afuera. Pero si mirás por la ventana seguro te das una idea.", []

        # 12. Finalizar Sesión
        if any(x in text_lower for x in ["finalizar sesion", "finalizar sesión", "apagar jarvis"]):
            return "Desconectando sistemas Carlos. Nos vemos luego.", [SimulatedToolCall("finalizar_sesion")]

        # Despedidas generales en modo offline
        if any(x in text_lower for x in ["gracias", "chau", "adiós", "nada más"]):
            return "De nada Carlos. Quedo por acá esperando en modo offline.", []

        # Fallback por defecto en offline
        return "Che Carlos, estoy sin conexión y no logré interpretar ese comando a nivel local. Recordá que en offline puedo abrir/cerrar apps, controlar volumen, darte la hora o hacer diagnósticos del sistema.", []
