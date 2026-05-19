# Gestora de Tareas

Aplicacion Streamlit para gestionar tareas, subtareas, comentarios, prioridades, bloqueos y exportacion a CSV.

## Archivos importantes

- `streamlit_app.py`: entrada recomendada para Streamlit Community Cloud.
- `app.py`: aplicacion principal.
- `database.py`: funciones de SQLite.
- `requirements.txt`: dependencias de Python para Cloud.
- `tareas.db`: base local. No debe subirse a GitHub si contiene datos reales.
- `seed_tareas.db`: copia opcional para que Cloud arranque con datos iniciales.

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
4. En Advanced settings selecciona Python `3.12`.
5. Si Cloud muestra errores viejos, entra en Manage app y usa Reboot app.

Si quieres ver una copia de tu data en Cloud, sube `seed_tareas.db`. La app copiara esa semilla a `tareas.db` cuando el servidor arranque sin datos. No es persistencia real: los cambios hechos en Cloud pueden perderse al reiniciar o redesplegar.

Si `tareas.db` o `__pycache__` ya aparecen en GitHub, quitalos del seguimiento sin borrarlos de tu PC:

```bash
git rm --cached tareas.db
git rm -r --cached __pycache__
git add .gitignore README.md streamlit_app.py app.py requirements.txt database.py utils.py cargar_datos_ejemplo.py
git commit -m "Preparar despliegue limpio"
git push
```

