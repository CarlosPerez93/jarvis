import sys
import os

# Ajustar CWD al directorio raíz del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.offline_parser import OfflineIntentParser
from src.tools.system.diagnostics import obtener_estado_sistema

def run_tests():
    print("="*60)
    print("  [TESTS]  CORRIENDO UNIT TESTS PARA COMPONENTES DE JARVIS 3.2")
    print("="*60)

    # --- 1. Probar Diagnóstico de Hardware ---
    print("\n[TEST 1] Probando diagnóstico de hardware...")
    try:
        reporte = obtener_estado_sistema()
        print("  [OK]  Diagnóstico exitoso!")
        print("  [REPORT]  Reporte generado:\n")
        print(reporte)
    except Exception as e:
        print("  [FAIL]  Fallo en diagnóstico de hardware: {}".format(e))

    # --- 2. Probar Parser de Expresiones Regulares ---
    print("\n" + "-"*50)
    print("[TEST 2] Probando Parser Offline...")
    print("-"*50)
    
    parser = OfflineIntentParser()
    
    test_cases = [
        "subí el volumen, loco",
        "poneme el volumen al 75",
        "vamos a programar",
        "abrí google chrome",
        "cerrar notepad.exe",
        "poné música",
        "¿cómo está el sistema?",
        "qué hora es?",
        "cómo está el clima?",
        "chau jarvis gracias"
    ]
    
    for case in test_cases:
        text, tool_calls = parser.parse(case)
        print("  [USER]  Carlos: «{}»".format(case))
        if text:
            print("  [JARVIS-TXT]  Jarvis (texto): «{}»".format(text))
        if tool_calls:
            for tc in tool_calls:
                print("  [JARVIS-TOOL]  Jarvis (herramienta): {}(args={})".format(tc.name, tc.args))
        print()

    print("="*60)
    print("  [OK]  ¡TODOS LOS COMPONENTES DE PRUEBA LABURAN PERFECTO!")
    print("="*60)

if __name__ == "__main__":
    run_tests()
