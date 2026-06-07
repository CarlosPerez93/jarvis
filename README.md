# 🦾 Jarvis 4.0 - Asistente Conversacional IA

> **Nota Histórica y Evolución:** El proyecto sigue un ciclo de desarrollo iterativo registrado minuciosamente. Parte de la v1.0 creada por **Rafa Tatay** (macOS, aplausos) y ha evolucionado bajo una arquitectura robusta:
> - **v1.0 (Registro [v1](file:///c:/Projects/jarvis/registros_ia/implementation_plans/v1_migracion_windows_tts_y_tools.md)):** Migración inicial a Windows y Clean Architecture (SOLID), reemplazando la rigidez original por un flujo de diálogo dinámico y TTS de red neuronal.
> - **v2.0 (Registro [v2](file:///c:/Projects/jarvis/registros_ia/implementation_plans/v2_fallback_de_agentes.md)):** Resiliencia multicapa. Integración de fallback inteligente a voces locales y rotación de modelos si falla internet o la API.
> - **v3.0 (Registro [v3](file:///c:/Projects/jarvis/registros_ia/implementation_plans/v3_jarvis_3_evolucion_mayor.md)):** **Evolución Mayor**. Migración completa a la nueva SDK `google-genai`, reemplazo de aplausos por wakeword "Hey Jarvis" 100% local (openWakeWord) y Google Search integrado.
> - **v3.1 (Registro [v4](file:///c:/Projects/jarvis/registros_ia/implementation_plans/v4_pauta_silencio_inteligente.md)):** **Oído Inteligente**. Implementación de "Pauta de Silencio Inteligente" con umbral dinámico de espera (2.0s por defecto) y remoción de límites de tiempo para permitir la elaboración de ideas complejas sin cortes.
> - **v3.2 (Registro [v5](file:///c:/Projects/jarvis/registros_ia/implementation_plans/v5_consolidacion_sistemas.md)):** **Consolidación de Sistemas**. Biometría vocal básica, modo offline autónomo, diagnóstico Iron-Man y UI con Eel.
> - **v4.0 (Actual):** **Desktop Nativo y Alta Biometría**. Migración de UI a `pywebview` (aplicación de escritorio nativa, thread-safe). Motor biométrico reescrito con estándar industrial MFCC. HUD dinámico con caché multisesión (burbujas) y fallback automático de imágenes generadas por IA. Feedback vocal asíncrono para eliminar latencia percibida.


## ¿Qué hace?
Jarvis es un asistente de escritorio con voz neural que:
1. **Espera en silencio:** Detecta el wakeword **"Hey Jarvis"** usando IA local (openWakeWord).
2. **Verifica tu identidad:** Autenticación biométrica vocal con firma de voz SVM antes de responder.
3. **Te saluda naturalmente:** Con frases variadas y sin pausas innecesarias.
4. **Interactúa por Voz:** Te escucha usando tu micrófono (`SpeechRecognition`).
5. **Piensa con IA:** Procesa tu comando usando **Gemini** para entender tu intención real.
6. **Ejecuta herramientas:** Abre/cierra apps, controla volumen, consulta el clima, diagnostica el hardware, navega mapas, instala software.
7. **Busca en Google:** Usa Google Search integrado para responder preguntas que no sabe.
8. **Funciona offline:** Si se pierde la conexión o se agotan las API keys, activa un parser local de intenciones para comandos críticos.

## Funcionalidades Avanzadas

### Red Neuronal Resiliente
Soporte para hasta 10 llaves API de respaldo. Jarvis rota automáticamente entre llaves y modelos (`Gemini 2.5 Flash`, `2.0 Flash`, `Flash-Latest`) si se agota la cuota o falla el servidor. El historial de conversación se preserva íntegramente entre rotaciones gracias a un buffer circular en memoria.

### Biometría Vocal Avanzada (MFCC)
Autenticación basada en firma de voz usando **SVM Balanceado** entrenado con un pipeline industrial: 78 características (13 MFCCs, 13 Deltas, 13 Delta-Deltas, con sus medias y varianzas) y normalización CMVN. Soporte para enrolamiento interactivo con muestras posicionales, palabras de control, variabilidad adversaria y ruido ambiente, más data augmentation exhaustiva.

### Oído Biónico
Ganancia de audio optimizada (x15.0) mediante procesamiento de señales en tiempo real, permitiendo que Jarvis te escuche perfecto incluso con micrófonos integrados de bajo volumen.

### Voz Híbrida Inteligente
Utiliza voces neurales de alta calidad (`Edge-TTS`) con un sistema de fallback automático a voces locales (`SAPI5/pyttsx3`) si se pierde la conexión a internet.

### Pauta de Silencio Inteligente
Umbral de silencio dinámico (`AUDIO_PAUSE_THRESHOLD` de 2.0s por defecto) y límite de frase ajustable (`AUDIO_PHRASE_TIME_LIMIT` libre), garantizando que Jarvis no te corte a mitad de una idea compleja.

### Modo Offline Autónomo
Parser local de intenciones (`OfflineIntentParser`) basado en expresiones regulares rápidas en español rioplatense para comandos críticos del sistema (abrir/cerrar apps, volumen, hora, diagnóstico de hardware) cuando no hay conexión a internet.

### Diagnóstico de Hardware (Iron-Man)
Telemetría en tiempo real de CPU, RAM, disco y batería con personalidad rioplatense. Usa `psutil` si está disponible, con fallbacks nativos de Windows vía WMIC.

### Interfaz Gráfica Nativa Avanzada (HUD)
Aplicación de escritorio nativa renderizada vía **pywebview** (cero dependencias de servidores web). Muestra un orbe animado en Canvas 2D, indicadores de estado en tiempo real, y soporte para modales enriquecidos.
- **Caché Multisesión de Búsquedas:** Agrupa y minimiza búsquedas activas en "burbujas" visuales interactivas, permitiendo retomar contextos previos sin sobreescribir resultados.
- **Imágenes Contextuales (AI Fallback):** Integración con Pollinations AI para generar instantáneamente imágenes de fondo fotográficas en tarjetas de resultados web.
- **Feedback Vocal Pre-Ejecución:** Jarvis informa auditivamente cada acción antes de congelarse a procesar, eliminando la latencia percibida.


## Herramientas disponibles
| Herramienta | Descripción | Ejemplo de voz |
|---|---|---|
| `abrir_programa` | Abre cualquier app del sistema | "Abrí Chrome" |
| `abrir_entorno_trabajo` | Abre Claude + Cursor lado a lado | "Vamos a programar" |
| `cerrar_proceso` | Cierra un proceso por nombre | "Cerrá el Notepad" |
| `instalar_programa` | Instala software vía Winget | "Instalá VLC" |
| `desinstalar_programa` | Desinstala software vía Winget | "Desinstalá VLC" |
| `reproducir_musica` | Abre YouTube con música | "Poné música" |
| `subir_volumen` | Sube el volumen 20% | "Subí el volumen" |
| `bajar_volumen` | Baja el volumen 20% | "Bajá el volumen" |
| `establecer_volumen` | Pone el volumen al nivel indicado | "Poné el volumen al 50" |
| `silenciar_volumen` | Toggle mute/unmute | "Silenciá el sonido" |
| `obtener_hora` | Dice la hora y fecha actual | "¿Qué hora es?" |
| `obtener_clima` | Consulta el clima de una ciudad | "¿Cómo está el clima en Madrid?" |
| `investigar_en_internet` | Realiza una investigación profunda en la web | "Busca quién ganó el Oscar este año" |
| `cerrar_busqueda` | Cierra todas las tarjetas de búsqueda activas | "Cierra la búsqueda" |
| `minimizar_busqueda` | Minimiza la búsqueda a una burbuja en el HUD | "Limpia la pantalla" |
| `restaurar_busqueda` | Restaura la última sesión de búsqueda minimizada | "Abre la búsqueda que tenías ahí" |
| `obtener_estado_sistema` | Diagnóstico de CPU, RAM, disco y batería | "¿Cómo está el sistema?" |
| `buscar_en_mapa` | Busca un lugar o negocio en Google Maps | "Buscá un parking cerca" |
| `trazar_ruta` | Traza una ruta en Google Maps | "¿Cómo llego al aeropuerto?" |
| `finalizar_sesion` | Cierra Jarvis de forma limpia | "Chau Jarvis" |

## Arquitectura
El proyecto sigue principios SOLID con arquitectura limpia:

```
jarvis/
├── src/
│   ├── main.py                  # Punto de entrada y loop de wakeword
│   ├── core/                    # Componentes atómicos
│   │   ├── dialogue.py          # Orquestador de conversación (online/offline)
│   │   ├── llm_engine.py        # Cerebro LLM (Gemini) con rotación de llaves
│   │   ├── audio.py             # Orejas STT (SpeechRecognition)
│   │   ├── tts.py               # Boca TTS (Edge-TTS + fallback SAPI5)
│   │   ├── wakeword.py          # Detector de wakeword (openWakeWord)
│   │   ├── voice_auth.py        # Biometría vocal (SVM + Mel features)
│   │   ├── offline_parser.py    # Parser local de intenciones (modo offline)
│   │   └── ui_bridge.py         # Puente de comunicación asíncrona con la UI (pywebview)
│   ├── tools/                   # Herramientas de sistema inyectables en Gemini
│   │   ├── __init__.py          # Registro central y TOOLS_LIST
│   │   ├── info_tools.py        # Hora, clima, investigación web
│   │   ├── navigation.py        # Mapas y rutas (Google Maps)
│   │   └── system/              # Herramientas de hardware y sistema
│   │       ├── apps.py          # Abrir/cerrar aplicaciones
│   │       ├── volume.py        # Control de volumen (pycaw)
│   │       ├── media.py         # Reproducción de música
│   │       ├── software.py      # Instalar/desinstalar vía Winget
│   │       ├── diagnostics.py   # Telemetría de hardware
│   │       └── session.py       # Finalización de sesión
│   └── ui/                      # Frontend HTML/CSS/JS (renderizado nativo por pywebview)
│       ├── index.html           # Estructura HTML
│       ├── styles.css           # Estilos y animaciones
│       └── app.js               # Orbe animado, boot sequence, HUD
├── enrolar.py                   # Script de enrolamiento biométrico vocal
├── probar_biometria.py          # Script de diagnóstico y calibración de voz
├── run.sh                       # Lanzador para Git Bash / WSL
├── run.bat                      # Lanzador para CMD de Windows
├── .env                         # Configuración de API keys y parámetros
└── registros_ia/                # Historial de desarrollo por versión
    ├── implementation_plans/
    ├── walkthroughs/
    └── tasks/
```

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
   pip install google-genai python-dotenv SpeechRecognition pyaudio edge-tts pygame openwakeword onnxruntime pycaw comtypes pygetwindow pyttsx3 scikit-learn pywebview
   ```
   > **Opcional:** `pip install psutil` para telemetría de hardware precisa. Sin `psutil`, Jarvis usa fallbacks nativos de Windows (WMIC).

3. **Configurar la API Key:**
   - Renombrá el archivo `.env.example` a `.env`.
   - Pegá tu API Key principal de Google AI Studio (`GEMINI_API_KEY=tu_clave_aca`).
   - Jarvis soporta múltiples llaves para evitar límites de cuota: `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, etc.

4. **Variables de entorno disponibles:**

   | Variable | Default | Descripción |
   |---|---|---|
   | `GEMINI_API_KEY` | — | Llave principal de Google AI Studio |
   | `GEMINI_API_KEY_1..N` | — | Llaves de respaldo para rotación automática |
   | `MIC_DEVICE_INDEX` | `1` | ID del micrófono (usar `scratch/list_audio_devices.py`) |
   | `WAKEWORD_SENSITIVITY` | `0.3` | Sensibilidad del wakeword (0.1–1.0) |
   | `AUDIO_PAUSE_THRESHOLD` | `2.0` | Segundos de silencio antes de cortar la grabación |
   | `AUDIO_PHRASE_TIME_LIMIT` | `None` | Duración máxima de frase (`None` = sin límite) |
   | `AUDIO_AUTH_THRESHOLD` | `0.85` | Umbral de confianza biométrica (0.0–1.0) |


## Uso

Asegurate de tener el entorno virtual activado y ejecutá:

```bash
# Opción 1: Script lanzador (recomendado, activa el venv automáticamente)
./run.sh          # Git Bash / WSL
run.bat           # CMD de Windows

# Opción 2: Manual
python -m src.main
```

## Biometría Vocal

Para usar la biometría de voz, primero **entrená tu firma vocal**:

```bash
python enrolar.py
```

El script te guía paso a paso por un proceso de 4 fases para capturar la huella espectral de tu voz:
1. **8 grabaciones** diciendo "Hey Jarvis" (variando tono y distancia).
2. **3 grabaciones** de palabras de control (para evitar falsos positivos).
3. **3 grabaciones** adversarias (susurros y voz tapada).
4. **1 grabación** de 5 segundos en silencio absoluto (ruido de la habitación).

El modelo SVM entrenado se guarda en `src/core/voice_model.pkl`.

Luego, podés verificar la configuración con:

```bash
python probar_biometria.py
```

El script mostrará la probabilidad de coincidencia y te indicará si el acceso está autorizado. Podés ajustar el umbral en el archivo `.env` mediante la variable `AUDIO_AUTH_THRESHOLD` (default: `0.85`).

Cuando Jarvis arranque, simplemente decí **"Hey Jarvis"** y hablale naturalmente.

> **Tip:** Jarvis está optimizado para escucharte de lejos gracias al boost de ganancia (x15.0). Si sentís que se activa solo por ruidos de fondo, podés subir la sensibilidad del wakeword en el `.env` (`WAKEWORD_SENSITIVITY`).

---
*Jarvis 4.0 - Desarrollado con pasión para una automatización total.*
