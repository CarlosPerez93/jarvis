"""
Script de prueba para las herramientas de navegación de Jarvis.
"""
import sys
import os

# Asegurar que el directorio raíz del proyecto está en el PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.navigation import buscar_en_mapa, trazar_ruta

def run_tests():
    print("=" * 60)
    print("PROBANDO HERRAMIENTAS DE NAVEGACION (GPS)")
    print("=" * 60)
    
    print("\n1. Probando buscar_en_mapa('parking')...")
    res1 = buscar_en_mapa("parking")
    print(f"Respuesta: {res1}")
    
    print("\n2. Probando trazar_ruta('Aeropuerto El Dorado')...")
    res2 = trazar_ruta("Aeropuerto El Dorado")
    print(f"Respuesta: {res2}")
    
    print("\nPruebas completadas. Se deberian haber abierto dos pestanas del navegador con Google Maps.")

if __name__ == "__main__":
    run_tests()
