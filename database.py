import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "tareas.db"
SEED_DB_PATH = BASE_DIR / "seed_tareas.db"


def database_has_tasks(path: Path) -> bool:
    if not path.exists():
        return False

    try:
        conn = sqlite3.connect(path)
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        conn.close()
        return count > 0
    except sqlite3.Error:
        return False


def ensure_database_file():
    if not SEED_DB_PATH.exists():
        return

    if database_has_tasks(DB_PATH):
        return

    shutil.copyfile(SEED_DB_PATH, DB_PATH)


def get_connection():
    ensure_database_file()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            important INTEGER NOT NULL DEFAULT 0,
            urgent INTEGER NOT NULL DEFAULT 0,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            blocker_type TEXT NOT NULL,
            dependency TEXT,
            start_date TEXT,
            due_date TEXT,
            next_action TEXT,
            progress INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def calculate_priority(important: bool, urgent: bool) -> str:
    if important and urgent:
        return "Crítica"
    if important and not urgent:
        return "Alta"
    if not important and urgent:
        return "Media"
    return "Baja"


def create_task(data: dict):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    priority = calculate_priority(data["important"], data["urgent"])

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (
            title, description, category, important, urgent, priority, status,
            blocker_type, dependency, start_date, due_date, next_action,
            progress, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["title"],
        data.get("description", ""),
        data["category"],
        int(data["important"]),
        int(data["urgent"]),
        priority,
        data["status"],
        data["blocker_type"],
        data.get("dependency", ""),
        data.get("start_date", ""),
        data.get("due_date", ""),
        data.get("next_action", ""),
        int(data.get("progress", 0)),
        now,
        now,
    ))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id


def update_task(task_id: int, data: dict):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    priority = calculate_priority(data["important"], data["urgent"])

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET title = ?, description = ?, category = ?, important = ?, urgent = ?,
            priority = ?, status = ?, blocker_type = ?, dependency = ?,
            start_date = ?, due_date = ?, next_action = ?, progress = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        data["title"],
        data.get("description", ""),
        data["category"],
        int(data["important"]),
        int(data["urgent"]),
        priority,
        data["status"],
        data["blocker_type"],
        data.get("dependency", ""),
        data.get("start_date", ""),
        data.get("due_date", ""),
        data.get("next_action", ""),
        int(data.get("progress", 0)),
        now,
        task_id,
    ))
    conn.commit()
    conn.close()


def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM comments WHERE task_id = ?", (task_id,))
    cursor.execute("DELETE FROM subtasks WHERE task_id = ?", (task_id,))
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def get_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_task(task_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_subtask(task_id: int, title: str, status: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute("""
        INSERT INTO subtasks (task_id, title, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (task_id, title, status, now, now))
    conn.commit()
    conn.close()


def update_subtask(subtask_id: int, title: str, status: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute(
        "UPDATE subtasks SET title = ?, status = ?, updated_at = ? WHERE id = ?",
        (title, status, now, subtask_id),
    )
    conn.commit()
    conn.close()


def delete_subtask(subtask_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    conn.commit()
    conn.close()


def get_subtasks(task_id: int):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM subtasks WHERE task_id = ? ORDER BY created_at ASC", (task_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_comment(task_id: int, comment: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute("""
        INSERT INTO comments (task_id, comment, created_at)
        VALUES (?, ?, ?)
    """, (task_id, comment, now))
    conn.commit()
    conn.close()


def get_comments(task_id: int):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM comments WHERE task_id = ? ORDER BY created_at DESC", (task_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]
