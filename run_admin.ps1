# Script de arranque inteligente para Jarvis 3.0
# Chequea permisos de Administrador y auto-eleva si es necesario

$currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "  🛡️  Jarvis necesita permisos de Administrador para controlar el sistema." -ForegroundColor Yellow
    Write-Host "  🔓  Pidiendo elevación de privilegios..." -ForegroundColor Cyan
    Start-Process powershell -Verb runAs -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-File", "$PSCommandPath"
    exit
}

# Si ya somos admin, procedemos
Clear-Host
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  🦾  JARVIS 3.0 - MODO ADMINISTRADOR ACTIVADO" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

# Activar entorno virtual si existe
if (Test-Path ".venv\Scripts\Activate.ps1") {
    . .venv\Scripts\Activate.ps1
}

# Ejecutar Jarvis con el PATH configurado
$env:PYTHONPATH = "."
python -m src.main
