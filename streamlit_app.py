import sys
import os
from pathlib import Path

# Cambiar al directorio de la app
os.chdir(Path(__file__).parent / "gestora_tareas_yerika")
sys.path.insert(0, str(Path(__file__).parent / "gestora_tareas_yerika"))

# Ejecutar la aplicación principal
exec(open("app.py").read())
