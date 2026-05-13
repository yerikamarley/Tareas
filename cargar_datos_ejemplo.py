from database import init_db, create_task, create_subtask, add_comment

init_db()

examples = [
    {
        "title": "Despliegue de apuntamiento Enterritorio",
        "description": "Coordinar y ejecutar el despliegue del apuntamiento. Actualmente depende de información del cliente.",
        "category": "Despliegues",
        "important": True,
        "urgent": True,
        "status": "En espera",
        "blocker_type": "Pendiente cliente",
        "dependency": "Cliente Enterritorio",
        "start_date": "2026-05-12",
        "due_date": "2026-05-15",
        "next_action": "Hacer seguimiento al cliente solicitando la información pendiente.",
        "progress": 25,
    },
    {
        "title": "Revisión de ANS proveedor RPost",
        "description": "Validar indicadores, compensaciones y puntos no penalizables.",
        "category": "ANS / SLA",
        "important": True,
        "urgent": False,
        "status": "En proceso",
        "blocker_type": "Pendiente información",
        "dependency": "Anexo contractual",
        "start_date": "2026-05-12",
        "due_date": "2026-05-20",
        "next_action": "Solicitar anexo actualizado para validación.",
        "progress": 40,
    },
    {
        "title": "Informe ejecutivo de gestión de problemas",
        "description": "Preparar indicadores y hallazgos para presentación ejecutiva.",
        "category": "Reportes",
        "important": True,
        "urgent": True,
        "status": "Sin iniciar",
        "blocker_type": "Sin bloqueo",
        "dependency": "",
        "start_date": "2026-05-12",
        "due_date": "2026-05-14",
        "next_action": "Consolidar datos de casos e incidentes.",
        "progress": 0,
    },
]

for item in examples:
    task_id = create_task(item)
    if "apuntamiento" in item["title"].lower():
        create_subtask(task_id, "Solicitar información al cliente", "En espera")
        create_subtask(task_id, "Validar datos técnicos", "Sin iniciar")
        create_subtask(task_id, "Coordinar ventana", "Sin iniciar")
        create_subtask(task_id, "Ejecutar despliegue", "Sin iniciar")
        add_comment(task_id, "Se crea tarea inicial. Queda detenida por información pendiente del cliente.")

print("Datos de ejemplo creados.")
