---
name: python-components
description: >
  Establece las buenas prácticas para la creación de nuevos componentes (módulos en core y herramientas en tools) en Jarvis, integrando el estándar de python-solid.
  Trigger: Al crear o modificar archivos de Python en src/core/ o src/tools/, agregar nuevas herramientas de sistema, o refactorizar motores lógicos.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

Usar esta skill SIEMPRE que se diseñe, cree o modifique un componente en la base de código de Jarvis. Esto incluye:
- **Core Components:** Nuevos motores (ej: reconocimiento facial, integración IoT, procesamiento de voz) en `src/core/`.
- **System Tools:** Nuevas herramientas expuestas a Gemini para el control del sistema (ej: volumen, apps, winget) en `src/tools/system/`.

---

## Critical Patterns

Al crear un componente, es **obligatorio** cumplir con los principios SOLID definidos en la skill [python-solid](file:///c:/Projects/jarvis/.agent/skills/python-solid.md) y seguir estas reglas específicas:

### 1. Desacoplamiento Absoluto (DIP & SRP)
* **Constructor Limpio:** Un componente de `core` NUNCA debe instanciar sus propias dependencias complejas (como micrófonos, reproductores de audio o clientes API) en el constructor. Deben ser pasadas como argumentos para permitir inyección de dependencias y mockeo en pruebas.
* **Separación de I/O y Lógica:** La lógica de cálculo o decisión debe estar aislada de la entrada/salida física (micrófono, parlantes, red). 

### 2. Resiliencia y Degradación Progresiva (Graceful Degradation)
* **Bypass de Fallos:** Si un componente depende de un archivo local (como un archivo de pesos de machine learning, o credenciales opcionales) y este no existe, el componente **no debe hacer colapsar a Jarvis**. Debe implementar un *bypass* automático o fallback seguro e informar una advertencia visible en la consola.
* **Timeout Controlado:** Toda llamada a APIs externas o raspado web debe incluir obligatoriamente un `timeout` (máximo 5 segundos) para no congelar el loop de diálogo principal de Jarvis.

### 3. Registro Centralizado de Tools
* Toda nueva herramienta debe registrarse en `src/tools/__init__.py` agregándola a la lista maestra `TOOLS_LIST`.
* **Docstrings en Español:** El docstring de la función de la herramienta debe estar escrito en español y ser sumamente descriptivo, ya que Gemini lo utiliza directamente en el motor de *Function Calling* para entender cuándo y cómo invocarlo.

### 4. Tipado Estricto de Datos
* No se permiten parámetros sin tipo o retornos implícitos. Se deben usar los tipos nativos de Python y el módulo `typing` cuando sea necesario.
* Nombres de clases y métodos en **Inglés**. Logs del sistema, strings de respuesta y locuciones TTS en **Español Rioplatense** (voseo).

---

## Code Examples

### 1. Estructura Correcta de un Core Component (DIP, SRP y Fallback)

```python
import os
import numpy as np
from typing import Optional
from src.core.tts import TTSProvider # Dependencia abstracta o inyectada

class SignalProcessor:
    """
    [SRP] Hace una sola cosa: procesa señales de audio.
    [DIP] Recibe las dependencias necesarias por parámetro.
    """
    def __init__(self, tts: TTSProvider, model_path: Optional[str] = None) -> None:
        self.tts = tts
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), "default.model")
        self.is_ready = False
        self.load_model()

    def load_model(self) -> None:
        """Carga el modelo de forma resiliente (Graceful Degradation)."""
        if os.path.exists(self.model_path):
            # Lógica de carga
            self.is_ready = True
        else:
            # Fallback seguro con aviso en consola
            self.is_ready = False
            print(f"  ⚠️  [PROCESSOR] Modelo no encontrado en {self.model_path}. Ejecutando en modo Bypass.")

    def process(self, audio_data: np.ndarray) -> bool:
        """Procesa datos y devuelve un resultado tipado estrictamente."""
        if not self.is_ready:
            # Comportamiento degradado
            return True
            
        # Lógica de procesamiento real
        return True
```

### 2. Estructura Correcta de una Tool (Function Calling + Fallback)

```python
import subprocess
from typing import str

def controlar_dispositivo(accion: str) -> str:
    """
    [Function Calling] Docstring descriptivo en español para Gemini.
    Controla un dispositivo externo mediante línea de comandos.
    """
    print(f"  ⚙️  Ejecutando control de dispositivo: {accion}...")
    
    # [Fallback y validaciones de seguridad]
    if accion not in ["encender", "apagar"]:
        return "Acción no permitida. Solo podés encender o apagar el dispositivo."
        
    try:
        # Comando controlado
        subprocess.Popen(f'echo {accion}', shell=True)
        return f"Dispositivo configurado en modo: {accion}."
    except Exception as e:
        print(f"  ❌  Error en control de dispositivo: {e}")
        return "Tuve un problema al intentar controlar el dispositivo."
```

---

## Commands

Para validar la sintaxis y tipos estáticos de los nuevos componentes antes de integrarlos:

```bash
# Validar tipos con mypy si está configurado en el entorno
.venv\Scripts\mypy src/

# Ejecutar pruebas unitarias locales (si existen en el proyecto)
.venv\Scripts\python.exe -m unittest discover tests/
```

---

## Resources

- **SOLID Rules:** Ver [python-solid.md](file:///c:/Projects/jarvis/.agent/skills/python-solid.md) para los fundamentos de arquitectura aplicados a Python.
- **Tools Registry:** Ver [__init__.py](file:///c:/Projects/jarvis/src/tools/__init__.py) para inyectar nuevas herramientas en la lista maestra.
