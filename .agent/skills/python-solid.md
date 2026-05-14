# Reglas de Arquitectura: Python SOLID

Estas son las reglas fundamentales para mantener la base de código de Jarvis limpia, escalable y mantenible.

## 1. Clean Architecture y Capas
El proyecto está dividido en capas con responsabilidades únicas:
- `src/core/`: Componentes base del sistema (Motor LLM, Motor TTS, Captura de Audio). No conocen la lógica de negocio ni las herramientas específicas.
- `src/tools/`: Herramientas específicas que el LLM puede invocar (Function Calling). Ej: `OpenAppTool`, `SearchWebTool`.
- `src/commands/`: Lógica de comandos rígidos legacy (si los hubiera) o implementaciones de interfaces de negocio.
- `src/main.py`: Punto de entrada (Entry Point). Es el único lugar donde se deben instanciar las dependencias concretas y armar el grafo de inyección (Dependency Injection).

## 2. Principios SOLID
- **Single Responsibility (SRP):** Cada clase debe hacer *una sola cosa*. Si una clase escucha audio y además llama al LLM, está violando SRP. Separalas: `AudioListener` y `LLMEngine`.
- **Open/Closed (OCP):** Las entidades deben estar abiertas a la extensión pero cerradas a la modificación. Si queremos agregar una nueva herramienta para que Jarvis controle las luces de la casa, NO debemos modificar `LLMEngine`, sino crear una nueva clase `LightControlTool` que implemente la interfaz requerida por el motor.
- **Dependency Inversion (DIP):** Los módulos de alto nivel no deben depender de los de bajo nivel. Ambos deben depender de abstracciones. Pasá las dependencias por el constructor (ej: `def __init__(self, tts_engine: TTSProvider):`).

## 3. Tipado Estricto
- Todo el código debe estar tipado. Usar `mypy` como estándar mental.
- Ejemplo correcto: `def escuchar(self, timeout: int = 5) -> str | None:`
- Evitar el uso de `Any` salvo que sea estrictamente necesario.

## 4. Manejo de Secretos
- Nunca hardcodear API Keys. Usar `python-dotenv` y leerlas desde `os.getenv()`.

## 5. Idioma y Nomenclatura
- Nombres de clases y métodos en **Inglés** (ej: `AudioListener`, `speak()`).
- Respuestas de la IA, logs para el usuario y strings de TTS en **Español**.
