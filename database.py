"""
database.py - everything that talks to SQLite lives in this file.

app.py never writes SQL. It calls the small functions below instead.
That keeps the project organized: app.py = web logic, database.py = data logic.

SECURITY NOTE: every query uses "?" placeholders (parameterized queries).
The values are passed separately, so user input can never be run as SQL.
This is what prevents SQL injection.
"""
import os
import sqlite3
from datetime import datetime

# tasks.db is created next to this file, no matter where you run Python from.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.db")

# Whitelist of allowed sort orders. The user picks a KEY; we use our own SQL.
# (Column names can't be "?" placeholders, so we never put user text in ORDER BY.)
SORT_OPTIONS = {
    "created_desc": "created_at DESC, id DESC",
    "created_asc": "created_at ASC, id ASC",
    # "due_date IS NULL" pushes tasks without a due date to the bottom.
    "due_asc": "due_date IS NULL, due_date ASC",
    "due_desc": "due_date IS NULL, due_date DESC",
}


def get_connection():
    """Open a connection. row_factory lets us read columns by name: task['title']."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the tasks table if it does not exist yet (runs on every start-up)."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT,
                priority    TEXT NOT NULL DEFAULT 'Medium',
                status      TEXT NOT NULL DEFAULT 'Pending',
                due_date    TEXT,
                created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def get_tasks(search="", status="", priority="", sort="created_desc"):
    """Return a list of tasks, optionally searched, filtered and sorted."""
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)

    query += " ORDER BY " + SORT_OPTIONS.get(sort, SORT_OPTIONS["created_desc"])

    conn = get_connection()
    try:
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()


def get_task(task_id):
    """Return one task, or None if the id does not exist."""
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    finally:
        conn.close()


def create_task(title, description, priority, status, due_date):
    """INSERT a new task. Returns the new task's id."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:  # "with" commits automatically on success
        cursor = conn.execute(
            """INSERT INTO tasks (title, description, priority, status, due_date, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (title, description, priority, status, due_date, created_at),
        )
        return cursor.lastrowid


def update_task(task_id, title, description, priority, status, due_date):
    """UPDATE a task. Returns True if a row was changed."""
    with get_connection() as conn:
        cursor = conn.execute(
            """UPDATE tasks
               SET title = ?, description = ?, priority = ?, status = ?, due_date = ?
               WHERE id = ?""",
            (title, description, priority, status, due_date, task_id),
        )
        return cursor.rowcount > 0


def delete_task(task_id):
    """DELETE a task. Returns True if a row was removed."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


def mark_completed(task_id):
    """Set a task's status to Completed. Returns True if a row was changed."""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status = 'Completed' WHERE id = ?", (task_id,)
        )
        return cursor.rowcount > 0


def get_stats():
    """Counts for the dashboard. Calculated fresh from the DB on every request,
    which is why the numbers are always up to date."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM tasks GROUP BY status"
        ).fetchall()
    finally:
        conn.close()

    counts = {row["status"]: row["n"] for row in rows}
    total = sum(counts.values())
    completed = counts.get("Completed", 0)
    return {
        "total": total,
        "pending": counts.get("Pending", 0),
        "in_progress": counts.get("In Progress", 0),
        "completed": completed,
        "percent": round(completed / total * 100) if total else 0,
    }


def get_recent_tasks(limit=5):
    """The newest tasks, for the dashboard."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC, id DESC LIMIT ?", (limit,)
        ).fetchall()
    finally:
        conn.close()
