"""
Herramientas para el control del volumen del sistema.
"""
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
# pyrefly: ignore [missing-import]
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def _get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def subir_volumen() -> str:
    """Sube el volumen del sistema un 20%."""
    print("  🔊  Subiendo volumen...")
    try:
        volume = _get_volume_interface()
        current = volume.GetMasterVolumeLevelScalar()
        new_level = min(1.0, current + 0.2)
        volume.SetMasterVolumeLevelScalar(new_level, None)
        return f"Volumen subido al {int(new_level * 100)}%."
    except Exception as e:
        return f"Error al subir el volumen: {e}"

def bajar_volumen() -> str:
    """Baja el volumen del sistema un 20%."""
    print("  🔉  Bajando volumen...")
    try:
        volume = _get_volume_interface()
        current = volume.GetMasterVolumeLevelScalar()
        new_level = max(0.0, current - 0.2)
        volume.SetMasterVolumeLevelScalar(new_level, None)
        return f"Volumen bajado al {int(new_level * 100)}%."
    except Exception as e:
        return f"Error al bajar el volumen: {e}"

def establecer_volumen(porcentaje: int) -> str:
    """Establece el volumen al nivel indicado (0-100)."""
    print(f"  🔊  Estableciendo volumen al {porcentaje}%...")
    try:
        volume = _get_volume_interface()
        level = max(0.0, min(1.0, porcentaje / 100.0))
        volume.SetMasterVolumeLevelScalar(level, None)
        return f"Volumen establecido al {int(level * 100)}%."
    except Exception as e:
        return f"Error al establecer el volumen: {e}"

def silenciar_volumen() -> str:
    """Alterna el silencio (mute) del sistema."""
    print("  🔇  Cambiando estado de silencio...")
    try:
        volume = _get_volume_interface()
        is_muted = volume.GetMute()
        volume.SetMute(not is_muted, None)
        return "Sonido activado." if is_muted else "Sistema silenciado."
    except Exception as e:
        return f"Error al cambiar el mute: {e}"
