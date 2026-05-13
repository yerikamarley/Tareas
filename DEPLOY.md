# Checklist de redespliegue

## Antes de subir

- `requirements.txt` debe estar en la raiz.
- `streamlit_app.py` debe estar en la raiz.
- `tareas.db` debe quedarse local, no en GitHub.
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
3. Si sigue mostrando un error anterior, usa Manage app -> Reboot app.
4. Si el error menciona una libreria faltante, revisa que `requirements.txt` este en GitHub.
