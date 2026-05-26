---
name: jarvis-architecture
description: >
  Define la arquitectura de alto nivel de Jarvis, flujo de datos, inyección de dependencias y reglas de modularidad para mantener un código limpio y altamente escalable.
  Trigger: Al crear nuevas herramientas, modificar el puente de UI, agregar componentes lógicos, o cambiar la inicialización del sistema en main.py.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## Overview

J.A.R.V.I.S. está diseñado siguiendo principios de Arquitectura Limpia (Clean Architecture) e Inversión de Dependencias (Dependency Injection), con un flujo claro entre Motores (Core), Lógica (Dialogue) y Presentación (UI).

---

## Capas y Responsabilidades

### 1. `src/main.py` (Composition Root)
Es el único lugar donde se instancian los objetos concretos. Es responsable del arranque del sistema, el enlazamiento de dependencias (DI) y la gestión del ciclo de vida global.
- **Regla:** Ningún motor ni componente debe instanciar dependencias complejas internamente.

### 2. `src/core/` (Engines & Services)
Contiene los motores independientes que proveen capacidades base:
- `audio.py` / `tts.py`: Motores de I/O de audio.
- `voice_auth.py`: Autenticación biométrica (MFCC + SVM).
- `wakeword.py`: Detección en tiempo real de "Hey Jarvis".
- `llm_engine.py`: Conexión con Gemini y manejo de LLM fallback.
- `ui_bridge.py`: El puente de comunicación thread-safe hacia el frontend (pywebview).
- **Regla:** Los motores son "ciegos", no conocen sobre herramientas específicas ni sobre la lógica del diálogo.

### 3. `src/tools/` (Agentic Tools)
Funciones de utilidad inyectadas en Gemini para Function Calling.
- **Regla:** Cada tool debe hacer UNA sola cosa (SRP). Deben ser expuestas vía `__init__.py` en el registro `TOOLS_LIST`.
- **Submódulos:** `system/` (interacción local), `info_tools.py` (web/API), `navigation.py` (GPS).

### 4. `src/ui/` (Presentation Layer)
Frontend HTML/CSS/JS renderizado nativamente vía `pywebview`.
- **Regla:** Comunicación estrictamente a través de `ui_bridge.py`.
- **Regla:** Python expone API llamando `window.evaluate_js()`. JS interactúa con Python a través de `window.pywebview.api`.

---

## Data Flow (El ciclo de vida)

1. **Boot**: `main.py` lanza el servidor pywebview en un hilo (daemon thread) y luego entra al loop del micrófono principal.
2. **Wakeword**: `WakeWordDetector` escucha en modo streaming. Cuando detecta el wakeword (y autentica la biometría vocal), cede el control.
3. **Diálogo**: `DialogueManager` toma el control. Saluda, escucha un comando, se lo envía a `LLMEngine`.
4. **Ejecución**: Si Gemini decide invocar una tool, se ejecuta localmente.
5. **Feedabck**: Cada paso genera actualizaciones enviadas por `ui_bridge.py` al Canvas UI de forma asíncrona.
6. **Retorno**: Termina la interacción y vuelve al loop de wakeword.

---

## Patrones Obligatorios

1. **Thread-Safety con pywebview**:
   Todo llamado desde Python para modificar la UI debe usar constructores como `window.evaluate_js()` asegurándose de capturar posibles excepciones si la UI no está lista.

2. **Graceful Degradation**:
   Los sistemas deben poder operar sin internet o sin modelos entrenados. (Ej: Fallback a TTS local si falla el neural TTS, Bypass biométrico si no hay archivo `.pkl`).

3. **Inyección de Dependencias (DIP)**:
   Si `VoiceAuthenticator` necesita hacer TTS, se le pasa la instancia de TTS en el constructor. No se importa y se inicializa adentro.

---

## Anti-patrones Prohibidos

- **Blocking en el Main Thread**: Operaciones de red prolongadas deben tener un `timeout` agresivo para no congelar la captación del micrófono.
- **Eel u otros servidores Web**: Todo migró a `pywebview`. No usar frameworks basados en servidor local WebSocket.
- **Variables Globales de Estado**: El estado del diálogo debe vivir en el Manager. (Excepto el Singleton de la ventana del UI Bridge, por limitaciones de pywebview).
- **Hardcodeo de Keys**: Todo va en `.env` (API Keys, umbrales de sensibilidad de audio, etc.).
