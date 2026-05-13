# Checklist de redespliegue

## Antes de subir

- `requirements.txt` debe estar en la raiz.
- `streamlit_app.py` debe estar en la raiz.
- `tareas.db` debe quedarse local, no en GitHub.
- `seed_tareas.db` se puede subir si quieres ver una copia de tus datos en Cloud.
- `backups/` debe quedarse local, no en GitHub.
- `__pycache__/` debe quedarse fuera de GitHub.

## En VS Code

1. Abre Source Control.
2. Asegurate de incluir estos archivos:
   - `.gitignore`
   - `README.md`
   - `DEPLOY.md`
   - `streamlit_app.py`
   - `app.py`
   - `seed_tareas.db` si quieres que Cloud arranque con una copia de tu data
   - `requirements.txt`
   - `database.py`
   - `utils.py`
   - `cargar_datos_ejemplo.py`
3. No incluyas `tareas.db`, `backups/` ni `__pycache__/`.
4. Escribe el commit: `Preparar despliegue limpio`.
5. Haz Commit y Push.

## En Streamlit Cloud

1. App settings o Deploy settings.
2. Main file path: `streamlit_app.py`.
3. Python version: `3.12`.
4. Si la app ya fue creada con otra version de Python, elimina esa app en Streamlit Cloud y creala de nuevo con Python `3.12`; un simple reboot no siempre cambia Python.
5. Si sigue mostrando un error anterior, usa Manage app -> Reboot app.
6. Si el error menciona una libreria faltante, revisa que `requirements.txt` este en GitHub.

## Senal de instalacion lenta

Si los logs dicen `Using Python 3.14` y luego `Downloading pandas...tar.gz` o `Installing build dependencies`, Cloud esta compilando paquetes desde fuente. Para esta app conviene Python `3.12`, porque las dependencias fijadas en `requirements.txt` tienen mejor compatibilidad ahi.
