# TaskFlow – Task Management App (Flask + SQLite)

A beginner-friendly CRUD web app built with **Python, Flask, SQLite, Jinja2, HTML, CSS and vanilla JavaScript**.

## Features
- Dashboard: total / pending / in-progress / completed counts, completion %, recent tasks
- Create, view, edit, delete tasks (delete asks for confirmation)
- Mark as completed (completed tasks look different)
- Search by title; filter by status and priority; sort by creation or due date
- Priority and status badges, overdue highlighting, empty states, flash notifications
- Responsive layout with sidebar, plus dark mode (remembered in your browser)

## Project structure
```
task-management-app/
├── app.py            # Flask routes + form validation
├── database.py       # all SQLite code (parameterized queries)
├── tasks.db          # created automatically on first run
├── requirements.txt
├── templates/        # Jinja2 HTML (base, dashboard, tasks, add, edit)
└── static/           # css/style.css and js/script.js
```

## Setup

**1. Open a terminal in the project folder**
```bash
cd task-management-app
```

**2. Create and activate a virtual environment**
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat
```
(If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.)

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the server**
```bash
python app.py
```

**5. Open** http://127.0.0.1:5000

Stop the server with `Ctrl + C`.

## Routes
| Route | Methods | Purpose |
|---|---|---|
| `/` | GET | Dashboard |
| `/tasks` | GET | List, search, filter, sort (`?search=&status=&priority=&sort=`) |
| `/tasks/add` | GET, POST | Show form / create task |
| `/tasks/edit/<id>` | GET, POST | Show form / update task |
| `/tasks/delete/<id>` | POST | Delete task |
| `/tasks/complete/<id>` | POST | Mark task completed |

## How it works
1. The browser sends a request (a link click or a form submit).
2. A Flask route in `app.py` receives it and validates the input.
3. The route calls a function in `database.py`, which runs SQL against `tasks.db`.
4. The route renders a Jinja2 template with the data and returns HTML (or redirects).

**CRUD map:** Create = `INSERT` · Read = `SELECT` · Update = `UPDATE` · Delete = `DELETE`

## Manual test checklist
1. Open the dashboard: all counts are 0 and an empty state shows.
2. Add a task with an empty title: you get an error message.
3. Add 3 tasks with different priorities, statuses and due dates.
4. Dashboard numbers and the percentage update.
5. Search, filter and sort on the Tasks page.
6. Click **Complete** on a task: it turns green/struck-through.
7. Edit a task, save, and check the change.
8. Delete a task: a confirm dialog appears; cancel keeps it, OK removes it.
9. Stop and restart the server: your tasks are still there.
10. Visit `/tasks/edit/9999`: you are redirected with a friendly error.

## Troubleshooting
| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Activate the venv, then `pip install -r requirements.txt` |
| `'python' is not recognized` (Windows) | Try `py app.py`, or reinstall Python with "Add to PATH" ticked |
| `Address already in use` | Another app uses port 5000. Change to `app.run(debug=True, port=5001)` |
| `jinja2.exceptions.UndefinedError` | A variable name in a template doesn't match what the route passes to `render_template` |
| `sqlite3.OperationalError: no such table` | Delete `tasks.db` and restart; it is recreated |
| `database is locked` | Close other programs (e.g. DB Browser) that have `tasks.db` open |
| CSS/JS changes not showing | Hard refresh: `Ctrl+Shift+R` |
| `405 Method Not Allowed` | A form is missing `method="post"`, or a route is missing a method in `methods=[...]` |
| Flash messages not showing | Check that `app.secret_key` is set and the template has `get_flashed_messages()` |

Debug mode (`debug=True`) shows a detailed error page and auto-reloads on code changes. Turn it off before deploying anywhere public.

## Put it on GitHub
```bash
git init
git add .
git commit -m "Initial commit: Flask task manager"
git branch -M main
git remote add origin https://github.com/<your-username>/task-management-app.git
git push -u origin main
```
`.gitignore` keeps `venv/` and `tasks.db` out of the repository.

## Ideas to extend
User login, categories/tags, pagination, unit tests with `pytest`, deploying to Render or PythonAnywhere.
