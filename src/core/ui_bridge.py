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

    def trigger_action(self, action: str) -> None:
        """Llamado desde JS cuando el usuario hace clic en una opción del FAB."""
        print(f"[UI] Front-end disparó acción: {action}")
        if action == "train_voice":
            print("\n[UI] Inicializando modo de entrenamiento interactivo...")
            # Aquí podríamos emitir un evento a DialogueManager
            # o simplemente ejecutar enrolar.py en una nueva terminal
            import subprocess
            try:
                subprocess.Popen(["cmd.exe", "/c", "start", "python", "enrolar.py"])
            except Exception as e:
                print(f"[ERROR] No se pudo lanzar el entrenamiento: {e}")


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

def show_modal(title: str, content: str, modal_type: str = 'action', auto_close_ms: int = None) -> None:
    """Shows a modal in the UI.
    If auto_close_ms is provided, it will close automatically after that time.
    """
    auto_close_arg = str(auto_close_ms) if auto_close_ms else 'null'
    js_code = f"showModal({_escape_js_string(title)}, {_escape_js_string(content)}, {_escape_js_string(modal_type)}, {auto_close_arg})"
    _eval_js(js_code)

def show_search_results(query: str, results: list) -> None:
    """Shows multiple modals for search results."""
    _eval_js(f"showSearchResults({_escape_js_string(query)}, {json.dumps(results)})")

def close_search() -> None:
    """Cierra todos los modales de búsqueda."""
    _eval_js("closeAllSearchModals()")

def minimize_search() -> None:
    """Minimiza los modales de búsqueda."""
    _eval_js("minimizeSearchModals()")

def restore_search() -> None:
    """Restaura los modales de búsqueda."""
    _eval_js("restoreSearchModals()")
