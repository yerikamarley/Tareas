import sys
from pathlib import Path

# Agregar la carpeta gestora_tareas_yerika al path para importar los módulos
sys.path.insert(0, str(Path(__file__).parent / "gestora_tareas_yerika"))

# Importar y ejecutar la aplicación principal
from app import *
