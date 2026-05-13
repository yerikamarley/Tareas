

## Requisitos

- Python 3.10 o superior

## Instalación

Abre una terminal dentro de la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
streamlit run app.py
```

## Despliegue seguro en Streamlit Community Cloud

- Usa `streamlit_app.py` como archivo principal del despliegue, o `app.py` si lo configuras manualmente.
- No subas tu `tareas.db` real a GitHub si contiene datos personales. La app puede crear una base nueva vacia en el despliegue.
- Antes de publicar, saca la base local del seguimiento de Git sin borrarla de tu carpeta:

```bash
git rm --cached tareas.db
git rm -r --cached __pycache__
git add .gitignore streamlit_app.py README.md
git commit -m "Preparar despliegue seguro de Streamlit"
git push
```

Nota: Streamlit Community Cloud no garantiza persistencia de archivos locales. Para conservar datos reales en produccion, usa una base externa o guarda/exporta respaldos regularmente.

## Funcionalidades incluidas

- Crear tareas
- Clasificar por importante y urgente
- Prioridad automática
- Estados: Sin iniciar, En proceso, En espera, Finalizado
- Bloqueos por cliente, proveedor, infraestructura, aprobación, información u otra área
- Dashboard con métricas
- Tablero Kanban
- Gestión de subtareas
- Comentarios tipo bitácora
- Edición rápida de tareas
- Exportación a CSV

## Base de datos

La aplicación crea automáticamente el archivo `tareas.db` al ejecutarse.
