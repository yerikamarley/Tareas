import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
from html import escape

from database import (
    init_db,
    create_task,
    update_task,
    delete_task,
    get_tasks,
    get_task,
    create_subtask,
    update_subtask,
    delete_subtask,
    get_subtasks,
    add_comment,
    get_comments,
)
from utils import (
    CATEGORIES,
    STATUSES,
    BLOCKER_TYPES,
    PRIORITY_ORDER,
    priority_badge,
    status_badge,
    is_overdue,
    safe_date_to_string,
)

st.set_page_config(
    page_title="Gestora de Tareas",
    page_icon="📌",
    layout="wide",
)

init_db()

st.markdown("""
<style>
    .main-title {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .subtitle {
        color: #666;
        font-size: 16px;
        margin-bottom: 24px;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #ececec;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }
    .task-card {
        border: 1px solid #e8e8e8;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
        background: #ffffff;
        box-shadow: 0 1px 8px rgba(0,0,0,0.03);
    }
    .small-muted {
        color: #777;
        font-size: 13px;
    }
    .kanban-subtasks {
        border-top: 1px solid #eeeeee;
        margin-top: 10px;
        padding-top: 8px;
    }
    .kanban-subtasks ul {
        margin: 6px 0 0 18px;
        padding: 0;
    }
    .kanban-subtasks li {
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Tablero de Tareas</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Control de tareas, prioridades, bloqueos, subtareas y seguimiento personal.</div>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Menú",
    [
        "Dashboard",
        "Kanban",
        "Crear tarea",
        "Mis tareas",
        "Subtareas y comentarios",
        "Exportar",
    ],
)

tasks = get_tasks()
df = pd.DataFrame(tasks)


def set_flash_message(kind: str, message: str):
    st.session_state["flash_message"] = {
        "kind": kind,
        "message": message,
    }


def show_flash_message():
    flash = st.session_state.pop("flash_message", None)
    if not flash:
        return

    kind = flash.get("kind", "info")
    message = flash.get("message", "")
    if kind == "success":
        st.success(message)
    elif kind == "error":
        st.error(message)
    elif kind == "warning":
        st.warning(message)
    else:
        st.info(message)


show_flash_message()


TASK_FORM_FIELDS = [
    "title",
    "description",
    "category",
    "important",
    "urgent",
    "progress",
    "status",
    "blocker_type",
    "dependency",
    "next_action",
    "start_date",
    "due_date",
]


def clear_task_form_state(key_prefix: str):
    for field in TASK_FORM_FIELDS:
        st.session_state.pop(f"{key_prefix}_{field}", None)


SUBTASK_DASHBOARD_COLUMNS = [
    "id",
    "task_id",
    "title",
    "status",
    "task_title",
    "task_status",
    "priority",
    "category",
    "blocker_type",
    "due_date",
]

WORKLOAD_DASHBOARD_COLUMNS = [
    "item_type",
    "id",
    "task_id",
    "title",
    "parent_title",
    "status",
    "priority",
    "category",
    "blocker_type",
    "due_date",
]

TASK_WORKLOAD_COLUMNS = [
    "id",
    "title",
    "priority",
    "status",
    "category",
    "blocker_type",
    "due_date",
    "active_task_unit",
    "subtasks_total",
    "subtasks_pending",
    "subtasks_finished",
    "workload_units",
    "subtask_completion",
]


def build_subtask_dataframe(task_rows: list[dict]) -> pd.DataFrame:
    rows = []
    for task in task_rows:
        task_id = int(task["id"])
        for subtask in get_subtasks(task_id):
            rows.append({
                "id": subtask["id"],
                "task_id": task_id,
                "title": subtask["title"],
                "status": subtask["status"],
                "task_title": task["title"],
                "task_status": task["status"],
                "priority": task["priority"],
                "category": task["category"],
                "blocker_type": task["blocker_type"],
                "due_date": task.get("due_date", ""),
            })

    return pd.DataFrame(rows, columns=SUBTASK_DASHBOARD_COLUMNS)


def build_workload_dataframe(task_rows: list[dict], subtasks_dataframe: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for task in task_rows:
        task_id = int(task["id"])
        if task["status"] != "Finalizado":
            rows.append({
                "item_type": "Tarea",
                "id": task_id,
                "task_id": task_id,
                "title": task["title"],
                "parent_title": task["title"],
                "status": task["status"],
                "priority": task["priority"],
                "category": task["category"],
                "blocker_type": task["blocker_type"],
                "due_date": task.get("due_date", ""),
            })

    if not subtasks_dataframe.empty:
        pending_subtasks = subtasks_dataframe[subtasks_dataframe["status"] != "Finalizado"]
        for _, subtask in pending_subtasks.iterrows():
            rows.append({
                "item_type": "Subtarea",
                "id": int(subtask["id"]),
                "task_id": int(subtask["task_id"]),
                "title": subtask["title"],
                "parent_title": subtask["task_title"],
                "status": subtask["status"],
                "priority": subtask["priority"],
                "category": subtask["category"],
                "blocker_type": subtask["blocker_type"],
                "due_date": subtask["due_date"],
            })

    return pd.DataFrame(rows, columns=WORKLOAD_DASHBOARD_COLUMNS)


def build_task_workload_dataframe(task_rows: list[dict], subtasks_dataframe: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for task in task_rows:
        task_id = int(task["id"])
        if subtasks_dataframe.empty:
            task_subtasks = pd.DataFrame(columns=SUBTASK_DASHBOARD_COLUMNS)
        else:
            task_subtasks = subtasks_dataframe[subtasks_dataframe["task_id"] == task_id]

        subtasks_total = len(task_subtasks)
        subtasks_finished = len(task_subtasks[task_subtasks["status"] == "Finalizado"])
        subtasks_pending = subtasks_total - subtasks_finished
        active_task_unit = 0 if task["status"] == "Finalizado" else 1
        workload_units = active_task_unit + subtasks_pending
        subtask_completion = round((subtasks_finished / subtasks_total) * 100) if subtasks_total else int(task.get("progress", 0))

        rows.append({
            "id": task_id,
            "title": task["title"],
            "priority": task["priority"],
            "status": task["status"],
            "category": task["category"],
            "blocker_type": task["blocker_type"],
            "due_date": task.get("due_date", ""),
            "active_task_unit": active_task_unit,
            "subtasks_total": subtasks_total,
            "subtasks_pending": subtasks_pending,
            "subtasks_finished": subtasks_finished,
            "workload_units": workload_units,
            "subtask_completion": subtask_completion,
        })

    return pd.DataFrame(rows, columns=TASK_WORKLOAD_COLUMNS)


def parse_due_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def add_due_date_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    result = dataframe.copy()
    if result.empty:
        result["due_date_value"] = []
        result["days_to_due"] = []
        return result

    today = date.today()
    result["due_date_value"] = result["due_date"].apply(parse_due_date)
    result["days_to_due"] = result["due_date_value"].apply(
        lambda due_date: (due_date - today).days if due_date else None
    )
    return result


def prepare_due_items_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    table = dataframe.copy()
    if table.empty:
        return table

    table["priority_order"] = table["priority"].map(PRIORITY_ORDER).fillna(99)
    table = table.sort_values(["days_to_due", "priority_order", "parent_title", "item_type"])
    table["days_to_due"] = table["days_to_due"].astype(int)
    table = table[[
        "item_type",
        "title",
        "parent_title",
        "priority",
        "status",
        "category",
        "due_date",
        "days_to_due",
        "blocker_type",
    ]]
    return table.rename(columns={
        "item_type": "Tipo",
        "title": "Pendiente",
        "parent_title": "Tarea principal",
        "priority": "Prioridad",
        "status": "Estado",
        "category": "Categoría",
        "due_date": "Fecha límite",
        "days_to_due": "Días",
        "blocker_type": "Bloqueo",
    })


def render_kanban_subtasks(task_id: int) -> str:
    subtasks = get_subtasks(task_id)
    if not subtasks:
        return ""

    items = []
    for subtask in subtasks:
        title = escape(subtask["title"])
        status = status_badge(subtask["status"])
        items.append(f"<li>{title}<br><span class='small-muted'>{status}</span></li>")

    return (
        "<div class='kanban-subtasks'>"
        "<span class='small-muted'><b>Subtareas</b></span>"
        f"<ul>{''.join(items)}</ul>"
        "</div>"
    )


def filter_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe

    with st.expander("Filtros", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status_filter = st.multiselect("Estado", STATUSES, default=[])
        with col2:
            priority_filter = st.multiselect("Prioridad", ["Crítica", "Alta", "Media", "Baja"], default=[])
        with col3:
            category_filter = st.multiselect("Categoría", CATEGORIES, default=[])
        with col4:
            blocker_filter = st.multiselect("Bloqueo", BLOCKER_TYPES, default=[])

        search = st.text_input("Buscar por título, descripción o próxima acción")

    filtered = dataframe.copy()

    if status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]
    if priority_filter:
        filtered = filtered[filtered["priority"].isin(priority_filter)]
    if category_filter:
        filtered = filtered[filtered["category"].isin(category_filter)]
    if blocker_filter:
        filtered = filtered[filtered["blocker_type"].isin(blocker_filter)]
    if search:
        text_cols = ["title", "description", "next_action", "dependency"]
        mask = False
        for col in text_cols:
            mask = mask | filtered[col].fillna("").str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    return filtered


def task_form(default=None, key_prefix="task"):
    default = default or {}

    title = st.text_input("Título de la tarea", value=default.get("title", ""), key=f"{key_prefix}_title")
    description = st.text_area("Descripción", value=default.get("description", ""), key=f"{key_prefix}_description")
    category = st.selectbox(
        "Categoría",
        CATEGORIES,
        index=CATEGORIES.index(default.get("category", "Gestión de Problemas")) if default.get("category", "Gestión de Problemas") in CATEGORIES else 0,
        key=f"{key_prefix}_category",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        important = st.checkbox("Importante", value=bool(default.get("important", False)), key=f"{key_prefix}_important")
    with col2:
        urgent = st.checkbox("Urgente", value=bool(default.get("urgent", False)), key=f"{key_prefix}_urgent")
    with col3:
        progress = st.slider("Avance (%)", 0, 100, int(default.get("progress", 0)), key=f"{key_prefix}_progress")

    col4, col5 = st.columns(2)
    with col4:
        status = st.selectbox(
            "Estado",
            STATUSES,
            index=STATUSES.index(default.get("status", "Sin iniciar")) if default.get("status", "Sin iniciar") in STATUSES else 0,
            key=f"{key_prefix}_status",
        )
    with col5:
        blocker_type = st.selectbox(
            "Tipo de bloqueo",
            BLOCKER_TYPES,
            index=BLOCKER_TYPES.index(default.get("blocker_type", "Sin bloqueo")) if default.get("blocker_type", "Sin bloqueo") in BLOCKER_TYPES else 0,
            key=f"{key_prefix}_blocker_type",
        )

    dependency = st.text_input("Dependencia externa / persona / área", value=default.get("dependency", ""), key=f"{key_prefix}_dependency")
    next_action = st.text_area("Próxima acción", value=default.get("next_action", ""), key=f"{key_prefix}_next_action")

    col6, col7 = st.columns(2)
    with col6:
        current_start = default.get("start_date") or date.today().strftime("%Y-%m-%d")
        start_date = st.date_input("Fecha de inicio", value=datetime.strptime(current_start, "%Y-%m-%d").date() if current_start else date.today(), key=f"{key_prefix}_start_date")
    with col7:
        current_due = default.get("due_date") or date.today().strftime("%Y-%m-%d")
        due_date = st.date_input("Fecha límite", value=datetime.strptime(current_due, "%Y-%m-%d").date() if current_due else date.today(), key=f"{key_prefix}_due_date")

    return {
        "title": title.strip(),
        "description": description.strip(),
        "category": category,
        "important": important,
        "urgent": urgent,
        "status": status,
        "blocker_type": blocker_type,
        "dependency": dependency.strip(),
        "start_date": safe_date_to_string(start_date),
        "due_date": safe_date_to_string(due_date),
        "next_action": next_action.strip(),
        "progress": progress,
    }


subtask_df = build_subtask_dataframe(tasks)
workload_df = build_workload_dataframe(tasks, subtask_df)
task_workload_df = build_task_workload_dataframe(tasks, subtask_df)
workload_due_df = add_due_date_columns(workload_df)


if menu == "Dashboard":
    st.subheader("Dashboard general")

    total = len(tasks)
    critical = len([t for t in tasks if t["priority"] == "Crítica" and t["status"] != "Finalizado"])
    waiting = len([t for t in tasks if t["status"] == "En espera"])
    finished = len([t for t in tasks if t["status"] == "Finalizado"])
    due_workload = (
        workload_due_df[workload_due_df["days_to_due"].notna()].copy()
        if not workload_due_df.empty
        else workload_due_df.copy()
    )
    overdue_items = due_workload[due_workload["days_to_due"] < 0].copy() if not due_workload.empty else due_workload.copy()
    overdue = len(overdue_items)
    total_subtasks = len(subtask_df)
    pending_subtasks = len(subtask_df[subtask_df["status"] != "Finalizado"]) if not subtask_df.empty else 0
    finished_subtasks = len(subtask_df[subtask_df["status"] == "Finalizado"]) if not subtask_df.empty else 0
    real_workload = len(workload_df)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total tareas", total)
    col2.metric("Críticas activas", critical)
    col3.metric("En espera", waiting)
    col4.metric("Vencidas", overdue)
    col5.metric("Finalizadas", finished)

    work_col1, work_col2, work_col3, work_col4 = st.columns(4)
    work_col1.metric("Carga real pendiente", real_workload)
    work_col2.metric("Subtareas totales", total_subtasks)
    work_col3.metric("Subtareas pendientes", pending_subtasks)
    work_col4.metric("Subtareas finalizadas", finished_subtasks)

    if df.empty:
        st.info("Aún no tienes tareas registradas. Crea tu primera tarea en la opción 'Crear tarea'.")
    else:
        st.subheader("Vencidas y próximas a vencer")
        st.caption("Las subtareas usan la fecha límite de su tarea principal.")
        upcoming_days = st.slider("Ventana de próximas a vencer", 1, 30, 7, format="%d días")

        upcoming_limit = date.today() + timedelta(days=upcoming_days)
        upcoming_items = (
            due_workload[
                (due_workload["due_date_value"] >= date.today())
                & (due_workload["due_date_value"] <= upcoming_limit)
            ].copy()
            if not due_workload.empty
            else due_workload.copy()
        )

        due_col1, due_col2 = st.columns(2)
        with due_col1:
            st.markdown(f"#### Vencidas ({len(overdue_items)})")
            if overdue_items.empty:
                st.success("No tienes pendientes vencidos.")
            else:
                st.dataframe(
                    prepare_due_items_table(overdue_items),
                    use_container_width=True,
                    hide_index=True,
                )

        with due_col2:
            st.markdown(f"#### Próximas a vencer ({len(upcoming_items)})")
            if upcoming_items.empty:
                st.info(f"No tienes pendientes que venzan en los próximos {upcoming_days} días.")
            else:
                st.dataframe(
                    prepare_due_items_table(upcoming_items),
                    use_container_width=True,
                    hide_index=True,
                )

        col_a, col_b = st.columns(2)

        with col_a:
            status_count = df.groupby("status").size().reset_index(name="total")
            fig = px.bar(status_count, x="status", y="total", title="Tareas por estado", text="total")
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            priority_count = df.groupby("priority").size().reset_index(name="total")
            priority_count["order"] = priority_count["priority"].map(PRIORITY_ORDER)
            priority_count = priority_count.sort_values("order")
            fig = px.pie(priority_count, names="priority", values="total", title="Tareas por prioridad")
            st.plotly_chart(fig, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            category_count = df.groupby("category").size().reset_index(name="total").sort_values("total", ascending=True)
            fig = px.bar(category_count, x="total", y="category", orientation="h", title="Tareas por categoría", text="total")
            st.plotly_chart(fig, use_container_width=True)

        with col_d:
            blockers = df[df["blocker_type"] != "Sin bloqueo"]
            if blockers.empty:
                st.success("No tienes tareas bloqueadas actualmente.")
            else:
                blocker_count = blockers.groupby("blocker_type").size().reset_index(name="total")
                fig = px.bar(blocker_count, x="blocker_type", y="total", title="Tareas bloqueadas por dependencia", text="total")
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Carga real de trabajo")
        if workload_df.empty:
            st.success("No tienes carga pendiente entre tareas y subtareas.")
        else:
            active_task_workload = task_workload_df[task_workload_df["workload_units"] > 0].copy()
            active_task_workload["display_title"] = active_task_workload["title"].apply(
                lambda value: value if len(value) <= 70 else f"{value[:67]}..."
            )
            active_task_workload = active_task_workload.sort_values("workload_units", ascending=False)

            col_e, col_f = st.columns(2)
            with col_e:
                top_workload = active_task_workload.head(10).sort_values("workload_units", ascending=True)
                fig = px.bar(
                    top_workload,
                    x="workload_units",
                    y="display_title",
                    color="priority",
                    orientation="h",
                    text="workload_units",
                    title="Tareas con más carga pendiente",
                    labels={
                        "workload_units": "Carga pendiente",
                        "display_title": "Tarea",
                        "priority": "Prioridad",
                    },
                    hover_data=["subtasks_pending", "subtasks_total", "subtask_completion", "due_date"],
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_f:
                category_workload = (
                    workload_df.groupby(["category", "item_type"])
                    .size()
                    .reset_index(name="total")
                    .sort_values("total", ascending=True)
                )
                fig = px.bar(
                    category_workload,
                    x="total",
                    y="category",
                    color="item_type",
                    orientation="h",
                    text="total",
                    title="Carga real por categoría",
                    labels={
                        "total": "Pendientes",
                        "category": "Categoría",
                        "item_type": "Tipo",
                    },
                )
                st.plotly_chart(fig, use_container_width=True)

            col_g, col_h = st.columns(2)
            with col_g:
                status_workload = workload_df.groupby(["status", "item_type"]).size().reset_index(name="total")
                fig = px.bar(
                    status_workload,
                    x="status",
                    y="total",
                    color="item_type",
                    text="total",
                    title="Carga real por estado",
                    labels={
                        "status": "Estado",
                        "total": "Pendientes",
                        "item_type": "Tipo",
                    },
                    category_orders={"status": STATUSES},
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_h:
                priority_workload = workload_df.groupby(["priority", "item_type"]).size().reset_index(name="total")
                fig = px.bar(
                    priority_workload,
                    x="priority",
                    y="total",
                    color="item_type",
                    text="total",
                    title="Carga real por prioridad",
                    labels={
                        "priority": "Prioridad",
                        "total": "Pendientes",
                        "item_type": "Tipo",
                    },
                    category_orders={"priority": ["Crítica", "Alta", "Media", "Baja"]},
                )
                st.plotly_chart(fig, use_container_width=True)

            workload_table = active_task_workload[
                [
                    "id",
                    "title",
                    "priority",
                    "status",
                    "workload_units",
                    "subtasks_pending",
                    "subtasks_total",
                    "subtask_completion",
                    "due_date",
                ]
            ].rename(columns={
                "id": "ID",
                "title": "Tarea",
                "priority": "Prioridad",
                "status": "Estado",
                "workload_units": "Carga pendiente",
                "subtasks_pending": "Subtareas pendientes",
                "subtasks_total": "Subtareas totales",
                "subtask_completion": "Avance subtareas (%)",
                "due_date": "Fecha límite",
            })
            st.dataframe(workload_table, use_container_width=True, hide_index=True)

        st.subheader("Para atender primero")
        priority_df = df[df["status"] != "Finalizado"].copy()
        if not priority_df.empty:
            priority_df = priority_df.merge(
                task_workload_df[[
                    "id",
                    "workload_units",
                    "subtasks_pending",
                    "subtasks_total",
                    "subtask_completion",
                ]],
                on="id",
                how="left",
            )
            for column in ["workload_units", "subtasks_pending", "subtasks_total", "subtask_completion"]:
                priority_df[column] = priority_df[column].fillna(0).astype(int)

            priority_df["priority_order"] = priority_df["priority"].map(PRIORITY_ORDER)
            priority_df["vencida"] = priority_df.apply(lambda row: is_overdue(row["due_date"], row["status"]), axis=1)
            priority_df = priority_df.sort_values(
                ["vencida", "priority_order", "workload_units", "due_date"],
                ascending=[False, True, False, True],
            )
            priority_table = priority_df[[
                "id",
                "title",
                "priority",
                "status",
                "workload_units",
                "subtasks_pending",
                "subtasks_total",
                "subtask_completion",
                "blocker_type",
                "due_date",
                "next_action",
            ]].rename(columns={
                "id": "ID",
                "title": "Tarea",
                "priority": "Prioridad",
                "status": "Estado",
                "workload_units": "Carga pendiente",
                "subtasks_pending": "Subtareas pendientes",
                "subtasks_total": "Subtareas totales",
                "subtask_completion": "Avance subtareas (%)",
                "blocker_type": "Bloqueo",
                "due_date": "Fecha límite",
                "next_action": "Próxima acción",
            })
            st.dataframe(priority_table, use_container_width=True, hide_index=True)
        else:
            st.success("No tienes tareas activas pendientes.")

elif menu == "Crear tarea":
    st.subheader("Crear nueva tarea")
    form_version = st.session_state.setdefault("new_task_form_version", 0)
    data = task_form(key_prefix=f"new_task_{form_version}")

    if st.button("Guardar tarea", type="primary"):
        if not data["title"]:
            st.error("El título es obligatorio.")
        else:
            task_id = create_task(data)
            st.session_state["new_task_form_version"] = form_version + 1
            set_flash_message("success", f"Tarea guardada correctamente. ID: {task_id}")
            st.rerun()

elif menu == "Mis tareas":
    st.subheader("Mis tareas")

    if df.empty:
        st.info("Aún no tienes tareas registradas.")
    else:
        filtered = filter_dataframe(df)

        st.write(f"Mostrando {len(filtered)} tarea(s).")

        if filtered.empty:
            st.info("No hay tareas que coincidan con los filtros.")
        else:
            editing_task_id = st.session_state.get("editing_task_id")
            deleting_task_id = st.session_state.get("deleting_task_id")

            for _, row in filtered.iterrows():
                task_id = int(row["id"])
                overdue_text = " ⚠️ VENCIDA" if is_overdue(row["due_date"], row["status"]) else ""
                with st.container():
                    st.markdown(f"""
                    <div class="task-card">
                        <h4>{row['id']} - {row['title']}{overdue_text}</h4>
                        <p><b>Prioridad:</b> {priority_badge(row['priority'])} &nbsp; | &nbsp;
                        <b>Estado:</b> {status_badge(row['status'])} &nbsp; | &nbsp;
                        <b>Bloqueo:</b> {row['blocker_type']}</p>
                        <p><b>Categoría:</b> {row['category']} &nbsp; | &nbsp; <b>Fecha límite:</b> {row['due_date']}</p>
                        <p><b>Próxima acción:</b> {row['next_action'] or 'Sin próxima acción registrada'}</p>
                        <p class="small-muted">{row['description'] or ''}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    edit_col, delete_col, _ = st.columns([1.4, 1.6, 4])
                    if edit_col.button("Editar", key=f"edit_task_{task_id}", use_container_width=True):
                        clear_task_form_state(f"edit_task_{task_id}")
                        st.session_state["editing_task_id"] = task_id
                        st.session_state["deleting_task_id"] = None
                        st.rerun()
                    if delete_col.button("Eliminar", key=f"delete_task_{task_id}", use_container_width=True):
                        clear_task_form_state(f"edit_task_{task_id}")
                        st.session_state["deleting_task_id"] = task_id
                        st.session_state["editing_task_id"] = None
                        st.rerun()

                    if editing_task_id == task_id:
                        selected_task = get_task(task_id)
                        if selected_task:
                            st.markdown(f"#### Editar tarea #{task_id}")
                            with st.form(f"edit_task_form_{task_id}"):
                                updated_data = task_form(selected_task, key_prefix=f"edit_task_{task_id}")
                                save_changes = st.form_submit_button("Guardar cambios", type="primary", use_container_width=True)
                                cancel_edit = st.form_submit_button("Cancelar", use_container_width=True)

                                if save_changes:
                                    if not updated_data["title"]:
                                        st.error("El título es obligatorio.")
                                    else:
                                        update_task(task_id, updated_data)
                                        clear_task_form_state(f"edit_task_{task_id}")
                                        st.session_state["editing_task_id"] = None
                                        set_flash_message("success", "Tarea actualizada correctamente.")
                                        st.rerun()

                                if cancel_edit:
                                    clear_task_form_state(f"edit_task_{task_id}")
                                    st.session_state["editing_task_id"] = None
                                    st.rerun()
                        else:
                            clear_task_form_state(f"edit_task_{task_id}")
                            st.session_state["editing_task_id"] = None

                    if deleting_task_id == task_id:
                        task_to_delete = get_task(task_id)
                        if task_to_delete:
                            st.warning(f"Vas a eliminar '{task_to_delete['title']}'. Esta acción también borra sus subtareas y comentarios.")
                            confirm_col, cancel_col, _ = st.columns([2, 1, 3])
                            if confirm_col.button("Confirmar eliminación", type="primary", key=f"confirm_delete_task_{task_id}", use_container_width=True):
                                delete_task(task_id)
                                clear_task_form_state(f"edit_task_{task_id}")
                                st.session_state["deleting_task_id"] = None
                                st.session_state["editing_task_id"] = None
                                set_flash_message("success", "Tarea eliminada correctamente.")
                                st.rerun()
                            if cancel_col.button("Cancelar", key=f"cancel_delete_task_{task_id}", use_container_width=True):
                                st.session_state["deleting_task_id"] = None
                                st.rerun()
                        else:
                            st.session_state["deleting_task_id"] = None

elif menu == "Kanban":
    st.subheader("Tablero Kanban")

    if df.empty:
        st.info("Aún no tienes tareas registradas.")
    else:
        cols = st.columns(4)
        for idx, status in enumerate(STATUSES):
            with cols[idx]:
                st.markdown(f"### {status_badge(status)}")
                status_tasks = df[df["status"] == status].copy()
                if status_tasks.empty:
                    st.caption("Sin tareas")
                else:
                    status_tasks["priority_order"] = status_tasks["priority"].map(PRIORITY_ORDER)
                    status_tasks = status_tasks.sort_values(["priority_order", "due_date"])
                    for _, row in status_tasks.iterrows():
                        subtasks_html = render_kanban_subtasks(int(row["id"]))
                        card_html = (
                            "<div class='task-card'>"
                            f"<b>{escape(str(row['title']))}</b><br>"
                            f"<span class='small-muted'>{priority_badge(row['priority'])}</span><br>"
                            f"<span class='small-muted'>Bloqueo: {escape(str(row['blocker_type']))}</span><br>"
                            f"<span class='small-muted'>Límite: {escape(str(row['due_date']))}</span><br>"
                            f"<span class='small-muted'>Avance: {int(row['progress'])}%</span>"
                            f"{subtasks_html}"
                            "</div>"
                        )
                        st.markdown(card_html, unsafe_allow_html=True)

elif menu == "Subtareas y comentarios":
    st.subheader("Subtareas y comentarios")

    if df.empty:
        st.info("Primero debes crear una tarea.")
    else:
        task_options = {f"{row['id']} - {row['title']}": row["id"] for _, row in df.iterrows()}
        selected_label = st.selectbox("Selecciona tarea", list(task_options.keys()))
        selected_id = int(task_options[selected_label])
        task = get_task(selected_id)

        st.markdown(f"### {task['title']}")
        st.write(f"**Estado:** {status_badge(task['status'])} | **Prioridad:** {priority_badge(task['priority'])}")
        st.write(f"**Próxima acción:** {task['next_action'] or 'Sin próxima acción'}")

        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Crear subtarea")
            sub_title = st.text_input("Nombre de subtarea")
            sub_status = st.selectbox("Estado de subtarea", STATUSES)
            if st.button("Agregar subtarea"):
                if not sub_title.strip():
                    st.error("La subtarea necesita un nombre.")
                else:
                    create_subtask(selected_id, sub_title.strip(), sub_status)
                    set_flash_message("success", "Subtarea creada correctamente.")
                    st.rerun()

            st.markdown("#### Subtareas")
            subtasks = get_subtasks(selected_id)
            if not subtasks:
                st.caption("Sin subtareas registradas.")
            else:
                for sub in subtasks:
                    with st.form(f"edit_subtask_form_{sub['id']}"):
                        st.markdown(f"**Subtarea #{sub['id']}**")
                        edited_title = st.text_input(
                            "Nombre",
                            value=sub["title"],
                            key=f"sub_title_{sub['id']}",
                        )
                        edited_status = st.selectbox(
                            "Estado",
                            STATUSES,
                            index=STATUSES.index(sub["status"]) if sub["status"] in STATUSES else 0,
                            key=f"sub_status_{sub['id']}",
                        )

                        save_col, delete_col = st.columns([2, 1])
                        with save_col:
                            save_subtask = st.form_submit_button(
                                "Guardar subtarea",
                                type="primary",
                                use_container_width=True,
                            )
                        with delete_col:
                            delete_subtask_clicked = st.form_submit_button(
                                "Eliminar",
                                use_container_width=True,
                            )

                        if save_subtask:
                            if not edited_title.strip():
                                st.error("La subtarea necesita un nombre.")
                            else:
                                update_subtask(sub["id"], edited_title.strip(), edited_status)
                                set_flash_message("success", "Subtarea actualizada correctamente.")
                                st.rerun()

                        if delete_subtask_clicked:
                            delete_subtask(sub["id"])
                            set_flash_message("success", "Subtarea eliminada correctamente.")
                            st.rerun()

        with col2:
            st.markdown("#### Agregar comentario / bitácora")
            comment = st.text_area("Comentario")
            if st.button("Guardar comentario"):
                if not comment.strip():
                    st.error("Escribe un comentario.")
                else:
                    add_comment(selected_id, comment.strip())
                    st.success("Comentario guardado.")
                    st.rerun()

            st.markdown("#### Historial")
            comments = get_comments(selected_id)
            if not comments:
                st.caption("Sin comentarios registrados.")
            else:
                for item in comments:
                    st.markdown(f"""
                    <div class="task-card">
                        <span class="small-muted">{item['created_at']}</span><br>
                        {item['comment']}
                    </div>
                    """, unsafe_allow_html=True)

elif menu == "Exportar":
    st.subheader("Exportar información")

    if df.empty:
        st.info("No hay tareas para exportar.")
    else:
        export_df = df.copy()
        st.dataframe(export_df, use_container_width=True, hide_index=True)

        csv = export_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="Descargar tareas en CSV",
            data=csv,
            file_name="mis_tareas.csv",
            mime="text/csv",
        )
