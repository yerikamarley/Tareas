from datetime import date, datetime

CATEGORIES = [
    "Gestión de Problemas",
    "Incidentes",
    "Casos",
    "ANS / SLA",
    "Reportes",
    "Implementaciones",
    "Despliegues",
    "Proveedores",
    "Reuniones",
    "Mejoras internas",
    "Personal",
    "Otro",
]

STATUSES = [
    "Sin iniciar",
    "En proceso",
    "En espera",
    "Finalizado",
]

BLOCKER_TYPES = [
    "Sin bloqueo",
    "Pendiente cliente",
    "Pendiente proveedor",
    "Pendiente infraestructura",
    "Pendiente aprobación",
    "Pendiente información",
    "Pendiente otra área",
]

PRIORITY_ORDER = {
    "Crítica": 1,
    "Alta": 2,
    "Media": 3,
    "Baja": 4,
}


def priority_badge(priority: str) -> str:
    badges = {
        "Crítica": "🔴 Crítica",
        "Alta": "🟠 Alta",
        "Media": "🟡 Media",
        "Baja": "⚪ Baja",
    }
    return badges.get(priority, priority)


def status_badge(status: str) -> str:
    badges = {
        "Sin iniciar": "📝 Sin iniciar",
        "En proceso": "🚀 En proceso",
        "En espera": "⏸️ En espera",
        "Finalizado": "✅ Finalizado",
    }
    return badges.get(status, status)


def is_overdue(due_date: str, status: str) -> bool:
    if not due_date or status == "Finalizado":
        return False
    try:
        return datetime.strptime(due_date, "%Y-%m-%d").date() < date.today()
    except ValueError:
        return False


def safe_date_to_string(value):
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value)
