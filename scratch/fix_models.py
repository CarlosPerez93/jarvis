import openwakeword
import os

print("Intentando descargar todos los modelos oficiales...")
try:
    # Esta es la forma oficial de bajar los modelos que le faltan
    openwakeword.utils.download_models()
    print("Descarga finalizada.")
    
    # Listar que hay ahora en la carpeta
    model_dir = os.path.join(os.path.dirname(openwakeword.__file__), "resources", "models")
    if os.path.exists(model_dir):
        print(f"Modelos disponibles en {model_dir}:")
        for f in os.listdir(model_dir):
            print(f" - {f}")
    else:
        print("La carpeta de modelos sigue sin existir.")
except Exception as e:
    print(f"Error: {e}")
