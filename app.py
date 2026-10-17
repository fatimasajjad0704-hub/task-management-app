"""
app.py - the Flask web application (routes + validation).

Flow of a request:
  Browser -> Flask route (this file) -> database.py -> SQLite
  Browser <- Jinja2 template (HTML) <- Flask route
"""
import os
import sqlite3
from datetime import date, datetime

from flask import Flask, flash, redirect, render_template, request, url_for

import database

app = Flask(__name__)
# flash() messages are stored in a signed cookie, which needs a secret key.
# For a real deployment set the SECRET_KEY environment variable.
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Pending", "In Progress", "Completed"]

# Create tasks.db and the table automatically the first time the app starts.
database.init_db()


def read_task_form(form):
    """Read and validate the submitted form.
    Returns (clean_data, errors). If errors is not empty, don't save."""
    title = form.get("title", "").strip()
    description = form.get("description", "").strip()
    priority = form.get("priority", "Medium")
    status = form.get("status", "Pending")
    due_date = form.get("due_date", "").strip()

    errors = []
    if not title:
        errors.append("Title is required.")
    elif len(title) > 100:
        errors.append("Title must be 100 characters or fewer.")
    if priority not in PRIORITIES:
        errors.append("Priority must be Low, Medium or High.")
    if status not in STATUSES:
        errors.append("Status must be Pending, In Progress or Completed.")
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Due date is not a valid date.")

    data = {
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "due_date": due_date or None,  # store NULL when empty
    }
    return data, errors


def task_not_found():
    flash("That task does not exist (it may already have been deleted).", "error")
    return redirect(url_for("tasks"))


@app.context_processor
def inject_globals():
    """Variables available in EVERY template."""
    return {"today": date.today().isoformat(), "PRIORITIES": PRIORITIES, "STATUSES": STATUSES}


# ---------- Dashboard ----------
@app.route("/")
def dashboard():
    try:
        stats = database.get_stats()
        recent = database.get_recent_tasks()
    except sqlite3.Error:
        flash("Could not load dashboard data from the database.", "error")
        stats = {"total": 0, "pending": 0, "in_progress": 0, "completed": 0, "percent": 0}
        recent = []
    return render_template("dashboard.html", stats=stats, recent=recent, active="dashboard")


# ---------- Read (list + search + filter + sort) ----------
@app.route("/tasks")
def tasks():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    sort = request.args.get("sort", "created_desc")
    try:
        task_list = database.get_tasks(search, status, priority, sort)
    except sqlite3.Error:
        flash("Could not load tasks from the database.", "error")
        task_list = []
    return render_template(
        "tasks.html",
        tasks=task_list,
        search=search,
        status=status,
        priority=priority,
        sort=sort,
        active=status or "all",
    )


# ---------- Create ----------
@app.route("/tasks/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        data, errors = read_task_form(request.form)
        if errors:
            for message in errors:
                flash(message, "error")
            # Re-show the form with what the user already typed.
            return render_template("add_task.html", task=data, active="add")
        try:
            database.create_task(**data)
        except sqlite3.Error:
            flash("Database error: the task could not be saved.", "error")
            return render_template("add_task.html", task=data, active="add")
        flash("Task created successfully!", "success")
        return redirect(url_for("tasks"))

    blank = {"title": "", "description": "", "priority": "Medium", "status": "Pending", "due_date": ""}
    return render_template("add_task.html", task=blank, active="add")


# ---------- Update ----------
@app.route("/tasks/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    task = database.get_task(task_id)
    if task is None:
        return task_not_found()

    if request.method == "POST":
        data, errors = read_task_form(request.form)
        if errors:
            for message in errors:
                flash(message, "error")
            data["id"] = task_id
            return render_template("edit_task.html", task=data, active="tasks")
        try:
            database.update_task(task_id, **data)
        except sqlite3.Error:
            flash("Database error: changes could not be saved.", "error")
            data["id"] = task_id
            return render_template("edit_task.html", task=data, active="tasks")
        flash("Task updated successfully!", "success")
        return redirect(url_for("tasks"))

    return render_template("edit_task.html", task=task, active="tasks")


# ---------- Delete (POST only) ----------
@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    try:
        deleted = database.delete_task(task_id)
    except sqlite3.Error:
        flash("Database error: the task could not be deleted.", "error")
        return redirect(request.referrer or url_for("tasks"))
    if not deleted:
        return task_not_found()
    flash("Task deleted.", "success")
    return redirect(request.referrer or url_for("tasks"))


# ---------- Mark completed (POST only) ----------
@app.route("/tasks/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    try:
        changed = database.mark_completed(task_id)
    except sqlite3.Error:
        flash("Database error: the task could not be updated.", "error")
        return redirect(request.referrer or url_for("tasks"))
    if not changed:
        return task_not_found()
    flash("Nice work! Task marked as completed.", "success")
    return redirect(request.referrer or url_for("tasks"))


if __name__ == "__main__":
    app.run(debug=True)
