import sqlite3
from datetime import datetime

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
            created_at TEXT NOT NULL
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
    }


def get_all_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows] # Retorna uma lista de dicionários


def get_task_by_id(task_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return row_to_dict(row) if row else None # Retorna a linha como dicionário


def create_task(title, description):
    conn = get_connection()
    created_at = datetime.now().isoformat()
    cursor = conn.execute(
        "INSERT INTO tasks (title, description, created_at) VALUES (?, ?, ?)",
        (title, description, created_at),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {"id": task_id, "title": title, "description": description, "created_at": created_at}


def update_task(task_id, title, description):
    conn = get_connection()
    conn.execute(
        "UPDATE tasks SET title = ?, description = ? WHERE id = ?",
        (title, description, task_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return row_to_dict(row) if row else None # Retorna a task após a modificação


def delete_task(task_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    conn.close()
    return row_to_dict(row) if row else None # Retorna a a tarefa deletada
