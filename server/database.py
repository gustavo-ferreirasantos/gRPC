import sqlite3
from datetime import datetime, timezone

DB_PATH = "tasks.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL,
            data_limit TEXT,
            status INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


# Converte uma linha da tabela num dicionário python
def row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "created_at": row["created_at"],
        "data_limit": row["data_limit"],
        "status": row["status"],
    }


def get_all_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def get_task_by_id(task_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def create_task(title, description, data_limit=None, status=0):
    conn = get_connection()
    created_at = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        "INSERT INTO tasks (title, description, created_at, data_limit, status) VALUES (?, ?, ?, ?, ?)",
        (title, description, created_at, data_limit, status),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {"id": task_id, "title": title, "description": description, "created_at": created_at, "data_limit": data_limit, "status": status}


def update_task(task_id, title, description, data_limit=None, status=None):
    conn = get_connection()
    conn.execute( # COALESCE retorna o primeiro valor não-NULL de uma lista
        "UPDATE tasks SET title = ?, description = ?, data_limit = COALESCE(?, data_limit), status = COALESCE(?, status) WHERE id = ?",
        (title, description, data_limit, status, task_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def delete_task(task_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    conn.close()
    return row_to_dict(row) if row else None
