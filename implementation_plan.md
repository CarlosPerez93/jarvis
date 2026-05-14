# Arquitectura Jarvis 2.0 y Comandos de Voz

Pasar de un script que detecta aplausos a un asistente interactivo que hace preguntas y confirma requiere un rediseño total. No podemos seguir metiendo todo en un solo archivo `bienvenido_jarvis.py` porque terminaríamos con un "código espagueti" inmanejable.

## User Review Required

> [!CAUTION]
> **Cambio de Paradigma:** Para reconocer voz (y no solo ruidos como el aplauso), vamos a necesitar la librería `SpeechRecognition` y `PyAudio`. En Windows, a veces `PyAudio` tira algún error de instalación si no tenés los binarios correctos, pero lo solucionamos fácil. ¿Estás de acuerdo con sumar estas dependencias para que Jarvis pueda "escuchar" palabras?

## Open Questions

> [!IMPORTANT]
> 1. **Comandos:** Además de la secuencia de bienvenida, ¿qué otros comandos exactos querés agregar en esta primera fase? (Ej: "abrir navegador", "reproducir música", "apagar sistema").
> 2. **Flujo de Confirmación:** Cuando le decís algo a Jarvis, la idea es que responda: *"Entendido, voy a abrir el navegador. ¿Confirma?"*, y espere un "sí" o "no". ¿Es correcto este flujo?

## Proposed Changes

### 1. Definición de Skills y Reglas
#### [NEW] .agent/skills/python-solid.md
- Documentaremos las reglas de arquitectura para este proyecto: Tipado estricto (`mypy`), interfaces, Single Responsibility (cada clase hace una sola cosa), y Dependency Injection.

### 2. Refactorización SOLID
Vamos a demoler el `bienvenido_jarvis.py` y armar una estructura de carpetas (Clean Architecture):

#### [NEW] src/core/audio.py
- Manejará la entrada cruda del micrófono y el `SpeechRecognition` (STT - Speech to Text).
#### [NEW] src/core/tts.py
- Envolverá a `pyttsx3`. Su única responsabilidad es hablar.
#### [NEW] src/core/dialogue.py
- El "cerebro" interactivo. Orquesta el flujo: Pregunta -> Escucha -> Pide confirmación -> Ejecuta.
#### [NEW] src/commands/base.py
- Una interfaz base (`Command`) que obliga a implementar un método `execute()`.
#### [NEW] src/commands/welcome.py
- La secuencia actual que abre Claude, Cursor y YouTube, implementando la interfaz `Command`.
#### [NEW] src/main.py
- El punto de entrada que inicializa las dependencias y arranca el loop de escucha.

### 3. Integración de Reconocimiento de Voz
- Modificaremos la lógica para que después del aplauso (o al iniciar), Jarvis diga: *"¿Qué desea hacer, Carlos?"*.
- Jarvis quedará escuchando, procesará el texto usando Google Speech Recognition (o Sphinx para offline), buscará el comando asociado y pedirá confirmación antes de dispararlo.

## Verification Plan
1. Crear la estructura de carpetas y clases vacías.
2. Migrar la lógica actual (TTS y apertura de ventanas) a las nuevas clases.
3. Instalar `SpeechRecognition`.
4. Ejecutar el `main.py` interactivo.
5. Hablarle por micrófono: *"Abre el entorno de trabajo"* -> Jarvis: *"¿Confirma entorno de trabajo?"* -> *"Sí"*.
