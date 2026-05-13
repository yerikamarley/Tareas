# Gestora de Tareas

Aplicacion Streamlit para gestionar tareas, subtareas, comentarios, prioridades, bloqueos y exportacion a CSV.

## Archivos importantes

- `streamlit_app.py`: entrada recomendada para Streamlit Community Cloud.
- `app.py`: aplicacion principal.
- `database.py`: funciones de SQLite.
- `requirements.txt`: dependencias de Python para Cloud.
- `tareas.db`: base local. No debe subirse a GitHub si contiene datos reales.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Tambien puedes ejecutar:

```bash
streamlit run app.py
```

## Desplegar sin afectar tu data

1. Verifica que `tareas.db` tenga respaldo en `backups/`.
2. No subas `tareas.db`, `backups/` ni `__pycache__/`.
3. En Streamlit Cloud usa `streamlit_app.py` como main file path.
4. Si Cloud muestra errores viejos, entra en Manage app y usa Reboot app.

Si `tareas.db` o `__pycache__` ya aparecen en GitHub, quitalos del seguimiento sin borrarlos de tu PC:

```bash
git rm --cached tareas.db
git rm -r --cached __pycache__
git add .gitignore README.md streamlit_app.py app.py requirements.txt database.py utils.py cargar_datos_ejemplo.py
git commit -m "Preparar despliegue limpio"
git push
```

Si tu terminal no reconoce `git`, haz lo mismo desde VS Code Source Control o GitHub Desktop: elimina `tareas.db` y `__pycache__` del repositorio remoto, pero conserva esos archivos en tu carpeta local.

## Persistencia

SQLite local funciona bien en tu computador. En Streamlit Community Cloud, los archivos locales no son almacenamiento permanente garantizado. Para datos reales en produccion, usa una base externa o exporta respaldos con frecuencia.
