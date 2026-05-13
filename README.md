

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
