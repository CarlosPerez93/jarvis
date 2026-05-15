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

## Funcionalidades Avanzadas de la v3.0
- **Red Neuronal Resiliente:** Soporte para hasta 10 llaves API de respaldo. Jarvis rota automáticamente entre llaves y modelos (`Gemini 2.5 Flash`, `2.0 Flash`, `Flash-Latest`) si se agota la cuota o falla el servidor.
- **Oído Biónico:** Ganancia de audio optimizada (x15.0) mediante procesamiento de señales en tiempo real, permitiendo que Jarvis te escuche perfecto incluso con micrófonos integrados de bajo volumen.
- **Voz Híbrida Inteligente:** Utiliza voces neurales de alta calidad (`Edge-TTS`) con un sistema de fallback automático a voces locales (`SAPI5/pyttsx3`) si se pierde la conexión a internet.
- **Investigación Autónoma:** Herramienta de búsqueda web mejorada que gestiona sus propias cuotas y llaves para garantizar que siempre tengas información actualizada.

## Herramientas disponibles
| Herramienta | Descripción | Ejemplo de voz |
|---|---|---|
| `abrir_programa` | Abre cualquier app del sistema | "Abrí Chrome" |
| `abrir_entorno_trabajo` | Abre Claude + Cursor lado a lado | "Vamos a programar" |
| `reproducir_musica` | Abre YouTube con música | "Poné música" |
| `subir_volumen` | Sube el volumen 20% | "Subí el volumen" |
| `bajar_volumen` | Baja el volumen 20% | "Subí el volumen" |
| `establecer_volumen` | Pone el volumen al nivel indicado | "Poné el volumen al 50" |
| `silenciar_volumen` | Toggle mute/unmute | "Silenciá el sonido" |
| `obtener_hora` | Dice la hora y fecha actual | "¿Qué hora es?" |
| `obtener_clima` | Consulta el clima de una ciudad | "¿Cómo está el clima en Madrid?" |
| `investigar_en_internet` | Realiza una investigación profunda en la web | "Busca quién ganó el Oscar este año" |

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
   pip install google-genai python-dotenv SpeechRecognition pyaudio edge-tts pygame openwakeword onnxruntime pycaw comtypes pygetwindow pyttsx3
   ```

3. **Configurar la API Key:**
   - Renombrá el archivo `.env.example` a `.env`.
   - Pegá tu API Key principal de Google AI Studio (`GEMINI_API_KEY=tu_clave_aca`).
   - Jarvis soporta múltiples llaves para evitar límites de cuota: `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, etc.

## Uso

Asegurate de tener el entorno virtual activado y ejecutá:

```bash
python -m src.main
```

Cuando Jarvis arranque, simplemente decí **"Hey Jarvis"** y hablale naturalmente.

> **Tip:** Jarvis está optimizado para escucharte de lejos gracias al boost de ganancia. Si sentís que se activa solo por ruidos de fondo, podés subir la sensibilidad en el `.env` o en `main.py`.

---
*Jarvis 3.0 - Desarrollado con pasión para una automatización total.*
