# 🦾 Jarvis 3.0 - Asistente Conversacional IA

> **Nota Histórica:** Esta es la **Versión 3.0** del proyecto. Este repositorio parte originalmente de la versión 1.0 creada por **Rafa Tatay**, la cual era un script lineal diseñado para macOS que ejecutaba acciones rígidas tras detectar dos aplausos. En la versión 2.0, el proyecto fue reescrito usando Arquitectura Limpia para Windows. En esta versión 3.0, se migró a la nueva SDK de Google (`google-genai`), se reemplazaron los aplausos por un wakeword inteligente ("Hey Jarvis"), y se agregaron herramientas nuevas de control del sistema.

## ¿Qué hace?
Jarvis es un asistente de escritorio con voz neural que:
1. **Espera en silencio:** Detecta el wakeword **"Hey Jarvis"** usando IA local (openWakeWord).
2. **Te saluda naturalmente:** Con frases variadas y sin pausas innecesarias.
3. **Interactúa por Voz:** Te escucha usando tu micrófono (`SpeechRecognition`).
4. **Piensa con IA:** Procesa tu comando usando **Gemini** para entender tu intención real.
5. **Ejecuta herramientas:** Abre apps, controla volumen, consulta el clima, busca en la web.
6. **Busca en Google:** Usa Google Search integrado para responder preguntas que no sabe.

## Herramientas disponibles
| Herramienta | Descripción | Ejemplo de voz |
|---|---|---|
| `abrir_programa` | Abre cualquier app del sistema | "Abrí Chrome" |
| `abrir_entorno_trabajo` | Abre Claude + Cursor lado a lado | "Vamos a programar" |
| `reproducir_musica` | Abre YouTube con música | "Poné música" |
| `subir_volumen` | Sube el volumen 20% | "Subí el volumen" |
| `bajar_volumen` | Baja el volumen 20% | "Bajá el volumen" |
| `establecer_volumen` | Pone el volumen al nivel indicado | "Poné el volumen al 50" |
| `silenciar_volumen` | Toggle mute/unmute | "Silenciá el sonido" |
| `obtener_hora` | Dice la hora y fecha actual | "¿Qué hora es?" |
| `obtener_clima` | Consulta el clima de una ciudad | "¿Cómo está el clima en Madrid?" |
| **Google Search** | Busca información en la web | "¿Quién ganó el mundial 2022?" |

## Arquitectura
El proyecto sigue principios SOLID con arquitectura limpia:
- `src/main.py`: Punto de entrada y loop de wakeword.
- `src/core/`: Componentes atómicos (Cerebro LLM, Orejas STT, Boca TTS, Detector Wakeword).
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
   pip install google-genai python-dotenv SpeechRecognition pyaudio edge-tts pygame openwakeword onnxruntime pycaw comtypes pygetwindow
   ```

3. **Configurar la API Key:**
   - Renombrá el archivo `.env.example` a `.env`.
   - Pegá tu API Key principal de Google AI Studio (`GEMINI_API_KEY=tu_clave_aca`).
   - *(Opcional)* Si agotás tus peticiones, podés agregar más claves de respaldo como `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`. Jarvis saltará automáticamente entre modelos y claves.

## Uso

Asegurate de tener el entorno virtual activado y ejecutá:

```bash
python -m src.main
```

Cuando Jarvis arranque, simplemente decí **"Hey Jarvis"** y hablale naturalmente.

> **Tip:** Si el wakeword se activa demasiado fácil, subí la sensibilidad en `main.py` (ej: `0.7`). Si no te escucha, bajala (ej: `0.3`).
