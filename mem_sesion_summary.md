### mem_session_summary:

**Goal**
Transformar el script rígido de Jarvis en una arquitectura modular SOLID (Jarvis 2.0) integrando reconocimiento de voz (STT) crudo y un LLM (Gemini) mediante Function Calling para crear un agente conversacional interactivo.

**Instructions**
Se estableció el estándar de Arquitectura Limpia (SOLID) y tipado estricto en Python a través del skill .agent/skills/python-solid.md.
El flujo conversacional debe mantener el sistema de confirmación ("User-in-the-loop") antes de que el LLM ejecute acciones en el sistema operativo.

**Discoveries**
El diseño monolítico de bienvenido_jarvis.py era insostenible para agregar IA, lo que motivó el refactor hacia inyección de dependencias (src/main.py como entrypoint) y componentes atómicos (audio.py, tts.py, llm_engine.py, dialogue.py).
google-generativeai y SpeechRecognition son las herramientas ideales para este caso de uso en Python nativo en Windows.

**Accomplished**
- Creada toda la estructura de directorios src/.
- Implementado cliente Gemini LLM con soporte para Tools/Function Calling.
- Refactorizados los comandos legacy (abrir cursor/claude, abrir youtube) como herramientas dinámicas en system_tools.py.
- Generado archivo .env.example y documentadas las instrucciones para la API Key de Gemini.

**Next Steps**
- El usuario debe obtener y configurar su GEMINI_API_KEY en el archivo .env.
- Probar el nuevo entrypoint python -m src.main.
- Validar y afinar la calidad del micrófono (SpeechRecognition noise adjustment) si fuera necesario.

**Relevant Files**
- src/main.py — Nuevo punto de entrada de la aplicación.
- src/core/dialogue.py — El orquestador central que une audio, voz y el LLM.
- .agent/skills/python-solid.md — Reglas de negocio y arquitectura para futuras ampliaciones del agente.