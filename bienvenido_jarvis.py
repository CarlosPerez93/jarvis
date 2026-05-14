#!/usr/bin/env python3
"""
Double-clap welcome script for Señor Tatay.

Detects 2 claps → voz AI dice bienvenido → abre YouTube → Claude + Cursor lado a lado.

Dependencias:
    pip install sounddevice numpy pyttsx3

Uso:
    python bienvenido_tatay.py
"""

import os
import sys
import time
import threading
import subprocess
import webbrowser

import numpy as np
import sounddevice as sd
import pyttsx3

# ──────────────────────────────────────────────────────────────────────────────
#  Configuración
# ──────────────────────────────────────────────────────────────────────────────
SAMPLE_RATE    = 44100
BLOCK_SIZE     = int(SAMPLE_RATE * 0.05)   # 50 ms por bloque
THRESHOLD      = 0.20     # RMS mínimo para contar como aplauso  ← ajusta si falla
COOLDOWN       = 0.1    # segundos de pausa mínima entre aplausos
DOUBLE_WINDOW  = 2.0     # ventana de tiempo para el segundo aplauso

YOUTUBE_URL    = "https://www.youtube.com/watch?v=yEASFhtzSMQ&list=RDyEASFhtzSMQ&start_radio=1"
MENSAJE        = "Bienvenido a casa, señor Carlos."
NEW_PROJECT    = os.path.expanduser("~/Desktop/nuevo_proyecto")

# ──────────────────────────────────────────────────────────────────────────────
#  Estado global
# ──────────────────────────────────────────────────────────────────────────────
clap_times: list[float] = []
triggered = False
lock = threading.Lock()


# ──────────────────────────────────────────────────────────────────────────────
#  Detección de aplausos
# ──────────────────────────────────────────────────────────────────────────────
def audio_callback(indata, frames, time_info, status):
    global triggered, clap_times

    if status:
        print(f"Error de audio: {status}", flush=True)

    if triggered:
        return

    rms = float(np.sqrt(np.mean(indata ** 2)))
    now = time.time()

    # Medidor de ruido en vivo para debug (se sobreescribe en la misma línea)
    print(f"  🎙️ Nivel de ruido (RMS): {rms:.4f} | Threshold: {THRESHOLD} ", end='\r', flush=True)

    if rms > THRESHOLD:
        with lock:
            # Ignora si estamos en el cooldown del aplauso anterior
            if clap_times and (now - clap_times[-1]) < COOLDOWN:
                return

            clap_times.append(now)
            # Limpia aplausos fuera de la ventana
            clap_times = [t for t in clap_times if now - t <= DOUBLE_WINDOW]

            count = len(clap_times)
            print(f"  👏  Aplauso {count}/2  (RMS={rms:.3f})")

            if count >= 2:
                triggered = True
                clap_times = []
                threading.Thread(target=secuencia_bienvenida, daemon=True).start()


# ──────────────────────────────────────────────────────────────────────────────
#  Secuencia de bienvenida
# ──────────────────────────────────────────────────────────────────────────────
def secuencia_bienvenida():
    print("\n🚀  Iniciando secuencia de bienvenida…\n")

    hablar(MENSAJE)
    abrir_youtube()
    abrir_apps_lado_a_lado()

    print("\n✅  Secuencia completada.\n")


def hablar(texto: str):
    """TTS local con pyttsx3 (SAPI5 en Windows)."""
    print(f"  🔊  Diciendo: «{texto}»")

    engine = pyttsx3.init()
    voices = engine.getProperty("voices")

    # Busca voz en español
    esp = [v for v in voices if "es" in v.id.lower() or "spanish" in v.name.lower()]
    if esp:
        engine.setProperty("voice", esp[0].id)
        print(f"     Voz seleccionada: {esp[0].name}")
    else:
        print("     Usando voz por defecto (no se encontró voz en español)")

    engine.setProperty("rate", 148)
    engine.say(texto)
    engine.runAndWait()


def abrir_youtube():
    print(f"  🎵  Abriendo YouTube…")
    webbrowser.open(YOUTUBE_URL)
    time.sleep(1.2)  # deja que el navegador cargue antes de seguir


def abrir_apps_lado_a_lado():
    sw, sh = obtener_resolucion_pantalla()
    mitad = sw // 2

    # Asegura que existe la carpeta del nuevo proyecto
    os.makedirs(NEW_PROJECT, exist_ok=True)

    # ── Abre Claude ──────────────────────────────────────────────────────────
    print("  🤖  Abriendo Claude…")
    claude_path = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Claude\Claude.exe")
    if os.path.exists(claude_path):
        subprocess.Popen([claude_path])
    else:
        print("     Claude no encontrado en ruta por defecto.")
    time.sleep(2.0)

    # ── Abre Cursor con nuevo proyecto ───────────────────────────────────────
    print("  💻  Abriendo Cursor…")
    cursor_cmd = encontrar_cursor()
    if cursor_cmd:
        subprocess.Popen([cursor_cmd, NEW_PROJECT])
    else:
        print("     Cursor no encontrado.")
    time.sleep(2.0)

    # ── Coloca ventanas lado a lado ──────────────────────────────────────────
    print("  🪟  Organizando ventanas…")
    try:
        # pyrefly: ignore [missing-import]
        import pygetwindow as gw
        
        # Buscar ventana de Claude
        claude_windows = gw.getWindowsWithTitle('Claude')
        if claude_windows:
            cw = claude_windows[0]
            if cw.isMinimized: cw.restore()
            cw.moveTo(0, 0)
            cw.resizeTo(mitad, sh)
            
        # Buscar ventana de Cursor
        cursor_windows = gw.getWindowsWithTitle('Cursor')
        if cursor_windows:
            curw = cursor_windows[0]
            if curw.isMinimized: curw.restore()
            curw.moveTo(mitad, 0)
            curw.resizeTo(mitad, sh)
    except ImportError:
        print("     'pygetwindow' no está instalado. Instalalo con 'pip install pygetwindow' para acomodar las ventanas.")


# ──────────────────────────────────────────────────────────────────────────────
#  Utilidades
# ──────────────────────────────────────────────────────────────────────────────
def obtener_resolucion_pantalla() -> tuple[int, int]:
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    except Exception:
        return 1920, 1080


def encontrar_cursor():
    """Devuelve la ruta del CLI de Cursor si está disponible."""
    cursor_path = os.path.expandvars(r"%LOCALAPPDATA%\Programs\cursor\Cursor.exe")
    if os.path.isfile(cursor_path):
        return cursor_path
    # Intenta por PATH
    result = subprocess.run(["where", "cursor"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.splitlines()[0].strip()
    return None


# ──────────────────────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    global triggered

    print("=" * 55)
    print("  🎤  Escuchando aplausos… (Ctrl+C para salir)")
    print(f"  Umbral actual: {THRESHOLD}  (ajusta THRESHOLD si falla)")
    print("=" * 55)

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            dtype="float32",
            callback=audio_callback,
        ):
            while True:
                time.sleep(0.1)
                if triggered:
                    # Espera a que la secuencia acabe y vuelve a escuchar
                    time.sleep(8)
                    triggered = False
                    print("\n👂  Escuchando de nuevo…\n")
    except KeyboardInterrupt:
        print("\n\nHasta luego! 👋")
        sys.exit(0)


if __name__ == "__main__":
    main()
