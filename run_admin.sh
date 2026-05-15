#!/bin/bash

# Script de arranque para Jarvis 3.0 (Ultra-Robusto)
# Este script evita dependencias externas para funcionar en entornos mínimos

# 1. Asegurar PATH para comandos básicos en Windows/GitBash
export PATH="/bin:/usr/bin:/c/Windows/system32:/c/Windows:$PATH"

# 2. Obtener ruta del script sin usar 'dirname'
SCRIPT_DIR="$(pwd)"
cd "$SCRIPT_DIR"

function is_admin() {
    net session > /dev/null 2>&1
    return $?
}

if ! is_admin; then
    echo "  🛡️  Jarvis necesita permisos de Administrador."
    echo "  🔓  Pidiendo elevación..."
    
    WIN_DIR=$(pwd -W)
    # Buscamos la ruta del ejecutable de bash actual
    WIN_BASH=$(where bash.exe | head -n 1)
    if [ -z "$WIN_BASH" ]; then
        WIN_BASH="bash.exe" # Fallback al PATH
    fi
    
    powershell.exe -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', \"cd '$WIN_DIR'; & '$WIN_BASH' '$0'\" -Verb runAs"
    exit
fi

echo "============================================================"
echo "  🦾  JARVIS 3.0 - MODO ADMINISTRADOR ACTIVADO"
echo "  📂  Carpeta: $SCRIPT_DIR"
echo "============================================================"

# 3. Configurar el PATH de Python
export PYTHONPATH="."

# 4. Ejecutar usando el Python del entorno virtual directamente (sin activate)
VENV_PYTHON="./.venv/Scripts/python.exe"

if [ -f "$VENV_PYTHON" ]; then
    echo "  🐍  Usando entorno virtual: .venv"
    "$VENV_PYTHON" -m src.main
else
    echo "  ⚠️  No se encontró .venv, intentando con python global..."
    python -m src.main
fi

# Pausa en caso de error
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Jarvis se cerró con un error."
    echo "Presione ENTER para salir..."
    read
fi
