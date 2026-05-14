# 🦾 Jarvis 2.0 - Asistente Conversacional IA

> **Nota Histórica:** Esta es la **Versión 2.0** del proyecto. Este repositorio parte originalmente de la versión 1.0 creada por **Rafa Tatay**, la cual era un script lineal diseñado para macOS que ejecutaba acciones rígidas tras detectar dos aplausos. En esta versión 2.0, el proyecto ha sido reescrito desde cero utilizando **Arquitectura Limpia (SOLID)** para Windows, integrando un motor LLM conversacional (Gemini), reconocimiento de voz continuo y ejecución dinámica de herramientas.

## ¿Qué hace?
Jarvis es un asistente de escritorio "User-in-the-loop" que:
1. **Espera en silencio:** Detecta 2 aplausos a través del micrófono para despertar.
2. **Interactúa por Voz:** Te saluda y te escucha usando tu micrófono (`SpeechRecognition`).
3. **Piensa con Inteligencia Artificial:** Procesa tu comando usando **Gemini 2.5 Flash** para entender tu intención real (no responde a comandos rígidos, podés hablarle natural).
4. **Ejecuta Herramientas (Function Calling):** Si le pedís que abra tu entorno de trabajo (Claude + Cursor) o que ponga música, Gemini "llama" a la herramienta correspondiente en Python.
5. **Confirma antes de actuar:** Jarvis te pregunta en voz alta si confirmás la acción antes de tocar algo en tu sistema.

## Arquitectura
El proyecto fue refactorizado siguiendo principios SOLID:
- `src/main.py`: Punto de entrada y loop de detección de audio de bajo nivel.
- `src/core/`: Componentes atómicos (Cerebro LLM, Orejas STT, Boca TTS).
- `src/tools/`: Herramientas de sistema inyectables en Gemini.

## Instalación

1. **Clonar y crear el entorno:**
   ```bash
   git clone https://github.com/CarlosPerez93/jarvis.git
   cd jarvis
   python -m venv .venv
   source .venv/Scripts/activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install SpeechRecognition pyaudio google-genai google-generativeai python-dotenv numpy sounddevice pyttsx3 pywin32 pygetwindow
   ```

3. **Configurar la API Key:**
   - Renombrá el archivo `.env.example` a `.env`.
   - Pegá tu API Key principal de Google AI Studio (`GEMINI_API_KEY=tu_clave_aca`).
   - *(Opcional)* Si agotás tus peticiones, podés agregar más claves de respaldo como `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`. Jarvis saltará automáticamente entre modelos y claves si se queda sin tokens, manteniendo el historial de la charla.

## Uso

Asegurate de tener el entorno virtual activado y ejecutá:

```bash
python -m src.main
```

> **Tip:** Si el entorno es muy ruidoso y se activa solo, ajustá la constante `THRESHOLD` en `src/main.py` a un número más alto (ej: `0.30`). Si tenés que aplaudir muy fuerte para que te escuche, bajalo a `0.10`.
