'''src/core/ui_bridge.py'''
import eel
import os

# Ensure Eel can find the UI folder (relative to project root)
UI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui'))

# Initialize Eel (this will be called from main)

def init_eel():
    """Initialize Eel with the UI directory.
    Should be called once before starting the UI.
    """
    eel.init(UI_DIR)

def start_ui():
    """Start the Eel UI non‑blocking.
    Returns the thread running the UI event loop.
    """
    # Using block=False allows Python to continue execution.
    # Explicitly bind to port 8000 to guarantee the server is always accessible there.
    eel.start('index.html', port=8000, size=(1200, 800), block=False)
    # Le damos tiempo al hilo del servidor de Eel para bindear el puerto 8000
    # y levantar el servidor Bottle antes de que el hilo principal se bloquee.
    eel.sleep(2.0)

# -------------------------------------------------
# Functions that the front‑end (app.js) can call.
# -------------------------------------------------
@eel.expose
def ui_ready():
    """Called from JavaScript when the UI has finished its boot sequence."""
    print("[UI] Front‑end reports ready")

# -------------------------------------------------
# Helper functions for the back‑end to push updates to the UI.
# -------------------------------------------------
def update_status(text: str, color: str = "#00ff00"):
    """Update the status label in the HUD.
    Calls the JavaScript function `updateStatus` exposed in app.js.
    """
    eel.updateStatus(text, color)

def add_chat_message(sender: str, message: str):
    """Add a new chat line to the communication log."""
    eel.addChatMessage(sender, message)

def update_biometrics(score: float, threshold: float):
    """Refresh the biometric progress bar."""
    eel.updateBiometrics(score, threshold)

def update_waveform(data_array):
    """Push a new waveform data array to the canvas."""
    eel.updateWaveform(data_array)

def update_footer(key: str, value: str):
    """Update a footer item (e.g., model, key, auth)."""
    eel.updateFooter(key, value)

# Optional: expose helpers to allow Python code to call them via `ui_bridge.update_status` etc.
# The backend imports this module and calls the functions directly.
