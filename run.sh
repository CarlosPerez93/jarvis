#!/bin/bash

# Si no está activado, activarlo
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activando entorno virtual..."
    source .venv/Scripts/activate
fi

python -m src.main
