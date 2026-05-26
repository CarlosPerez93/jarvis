'''src/core/ui_bridge.py — Puente Python ↔ JavaScript via pywebview (desktop nativo)'''
import os
import json
import threading
import webview

# Ruta absoluta al directorio de la UI
UI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui'))

# Referencia global a la ventana de pywebview (thread-safe via GIL)
_window: webview.Window | None = None
_ready_event = threading.Event()


# ═══════════════════════════════════════════════
#  JS API — Métodos que JavaScript puede llamar
# ═══════════════════════════════════════════════

class JarvisApi:
    """API expuesta al frontend. JS llama via window.pywebview.api.method()"""

    def ui_ready(self) -> None:
        """Called from JavaScript when the UI has finished its boot sequence."""
        print("[UI] Front‑end reports ready")
        _ready_event.set()


# ═══════════════════════════════════════════════
#  INIT & START
# ═══════════════════════════════════════════════

_api = JarvisApi()


def init_ui() -> None:
    """Crea la ventana de pywebview con la UI de Jarvis.
    Debe llamarse una vez desde main antes de start_ui().
    """
    global _window
    html_path = os.path.join(UI_DIR, 'index.html')

    _window = webview.create_window(
        title='J.A.R.V.I.S. 4.0',
        url=html_path,
        js_api=_api,
        width=1200,
        height=800,
        frameless=False,
        easy_drag=True,
        background_color='#040a0e',
        text_select=False,
    )


def _wrapped_background_task(task):
    """Espera a que el frontend levante antes de arrancar el backend."""
    _ready_event.wait(timeout=10.0)
    if not _ready_event.is_set():
        print("[UI] ⚠️  Timeout esperando al frontend. Continuando de todos modos...")
    task()


def start_ui(background_task) -> None:
    """Inicia pywebview en el hilo principal (requerido por Windows/macOS).
    El background_task (wakeword/diálogo) corre en un hilo secundario manejado por pywebview.
    """
    webview.start(_wrapped_background_task, background_task, debug=False)


# ═══════════════════════════════════════════════
#  HELPERS — Backend pushea datos al frontend
# ═══════════════════════════════════════════════

def _eval_js(js_code: str) -> None:
    """Ejecuta JavaScript en la ventana de forma thread-safe.
    Silencia errores si la ventana no está lista o fue cerrada.
    """
    if _window is not None:
        try:
            _window.evaluate_js(js_code)
        except Exception:
            pass


def _escape_js_string(value: str) -> str:
    """Escapa una string para inyectar de forma segura en JavaScript."""
    return json.dumps(value)


def update_status(text: str, color: str = "#00ff00") -> None:
    """Update the status label in the HUD.
    Calls the JavaScript function `updateStatus` exposed in app.js.
    """
    _eval_js(f"updateStatus({_escape_js_string(text)}, {_escape_js_string(color)})")


def add_chat_message(sender: str, message: str) -> None:
    """Add a new chat line to the communication log."""
    _eval_js(f"addChatMessage({_escape_js_string(sender)}, {_escape_js_string(message)})")


def update_biometrics(score: float, threshold: float) -> None:
    """Refresh the biometric progress arc."""
    _eval_js(f"updateBiometrics({score}, {threshold})")


def update_waveform(data_array: list) -> None:
    """Push a new waveform data array to the canvas."""
    _eval_js(f"updateWaveform({json.dumps(data_array)})")


def update_footer(key: str, value: str) -> None:
    """Update a footer item (e.g., model, key, auth)."""
    _eval_js(f"updateFooter({_escape_js_string(key)}, {_escape_js_string(value)})")
