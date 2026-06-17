# SETUP.md

# Django Todo App Setup and Deployment Guide

This document describes how to create, manage, and deploy a simple Django Todo application.

The app uses:

- Django
- SQLite
- HTML templates
- CSS
- Simple JSON API endpoints
- GitHub for source control
- PythonAnywhere for hosting

The intended workflow is:

```text
Local development machine
    ↓ git push
GitHub repository
    ↓ git pull
PythonAnywhere server
    ↓ reload web app
Live Django application
```

---

# 1. Project Goal

The goal is to build a small Django Todo app with:

- A web frontend using plain HTML and CSS
- A Django backend
- SQLite as the database
- API endpoints for future frontend or JavaScript integration
- Deployment on PythonAnywhere
- Updates through GitHub using `git pull`

The final application should be accessible at:

```text
https://YOUR_USERNAME.pythonanywhere.com
```

---

# 2. Required Tools

## Local computer

You need:

- Python 3.10 or newer
- Git
- GitHub account
- Code editor, for example VS Code
- Terminal or command line

Check Python:

```bash
python3 --version
```

Check Git:

```bash
git --version
```

---

# 3. Create Local Project Folder

Create a new folder:

```bash
mkdir django-todo-app
cd django-todo-app
```

---

# 4. Create Python Virtual Environment

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Upgrade pip:

```bash
pip install --upgrade pip
```

---

# 5. Install Django

Install Django:

```bash
pip install django
```

Check Django version:

```bash
python -m django --version
```

---

# 6. Create Django Project

Create the Django project in the current directory:

```bash
django-admin startproject config .
```

Create the Todo app:

```bash
python manage.py startapp todos
```

The project now looks like this:

```text
django-todo-app/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── todos/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── manage.py
```

---

# 7. Register the Todo App

Open:

```text
config/settings.py
```

Find `INSTALLED_APPS` and add `todos`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "todos",
]
```

---

# 8. Configure Templates and Static Files

In `config/settings.py`, make sure these imports exist at the top:

```python
import os
from pathlib import Path
```

Make sure `BASE_DIR` exists:

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```

Update the `TEMPLATES` setting:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

Add or update the static configuration near the bottom of `settings.py`:

```python
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

Create the required folders:

```bash
mkdir -p templates/todos
mkdir -p static/css
```

---

# 9. Configure Environment-Based Settings

For local development and PythonAnywhere production deployment, update these settings in `config/settings.py`.

Replace the existing `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` settings with:

```python
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-secret-key-change-this"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")
```

Explanation:

- Locally, `DEBUG` is `True`
- On PythonAnywhere, `DEBUG` should be `False`
- Locally, allowed hosts are `localhost` and `127.0.0.1`
- On PythonAnywhere, the allowed host is `YOUR_USERNAME.pythonanywhere.com`

---

# 10. SQLite Database Configuration

Django already uses SQLite by default.

In `config/settings.py`, the database setting should look like this:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

This creates a database file:

```text
db.sqlite3
```

Do not commit this file to Git.

---

# 11. Create Todo Model

Open:

```text
todos/models.py
```

Add:

```python
from django.db import models


class Todo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
```

Create and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# 12. Register Todo Model in Admin

Open:

```text
todos/admin.py
```

Add:

```python
from django.contrib import admin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ("title", "completed", "created_at")
    list_filter = ("completed", "created_at")
    search_fields = ("title", "description")
```

Create an admin user:

```bash
python manage.py createsuperuser
```

---

# 13. Create Views and API Endpoints

Open:

```text
todos/views.py
```

Replace the content with:

```python
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Todo


def todo_page(request):
    todos = Todo.objects.all()
    return render(request, "todos/index.html", {"todos": todos})


def create_todo(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()

        if title:
            Todo.objects.create(
                title=title,
                description=description,
            )

    return redirect("todo_page")


def toggle_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    todo.completed = not todo.completed
    todo.save()
    return redirect("todo_page")


def delete_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    todo.delete()
    return redirect("todo_page")


def api_list_todos(request):
    todos = Todo.objects.all()

    data = [
        {
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "completed": todo.completed,
            "created_at": todo.created_at.isoformat(),
        }
        for todo in todos
    ]

    return JsonResponse(data, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def api_create_todo(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    title = payload.get("title", "").strip()
    description = payload.get("description", "").strip()

    if not title:
        return JsonResponse({"error": "Title is required"}, status=400)

    todo = Todo.objects.create(
        title=title,
        description=description,
    )

    return JsonResponse(
        {
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "completed": todo.completed,
            "created_at": todo.created_at.isoformat(),
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["PATCH"])
def api_toggle_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    todo.completed = not todo.completed
    todo.save()

    return JsonResponse(
        {
            "id": todo.id,
            "title": todo.title,
            "completed": todo.completed,
        }
    )


@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    todo.delete()

    return JsonResponse({"deleted": True})
```

---

# 14. Create Todo URL Configuration

Create:

```text
todos/urls.py
```

Add:

```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.todo_page, name="todo_page"),
    path("create/", views.create_todo, name="create_todo"),
    path("toggle/<int:todo_id>/", views.toggle_todo, name="toggle_todo"),
    path("delete/<int:todo_id>/", views.delete_todo, name="delete_todo"),

    path("api/todos/", views.api_list_todos, name="api_list_todos"),
    path("api/todos/create/", views.api_create_todo, name="api_create_todo"),
    path("api/todos/<int:todo_id>/toggle/", views.api_toggle_todo, name="api_toggle_todo"),
    path("api/todos/<int:todo_id>/delete/", views.api_delete_todo, name="api_delete_todo"),
]
```

Open:

```text
config/urls.py
```

Replace it with:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("todos.urls")),
]
```

---

# 15. Create HTML Frontend

Create:

```text
templates/todos/index.html
```

Add:

```html
{% load static %}

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Django Todo App</title>
    <link rel="stylesheet" href="{% static 'css/app.css' %}">
</head>
<body>

<div class="app">
    <header class="hero">
        <h1>Todo App</h1>
        <p>Simple Django + SQLite + HTML/CSS application</p>
    </header>

    <section class="card">
        <h2>Add Todo</h2>

        <form method="post" action="{% url 'create_todo' %}" class="todo-form">
            {% csrf_token %}

            <input
                type="text"
                name="title"
                placeholder="Todo title"
                required
            >

            <textarea
                name="description"
                placeholder="Description"
            ></textarea>

            <button type="submit">Add Todo</button>
        </form>
    </section>

    <section class="card">
        <h2>Todos</h2>

        {% if todos %}
            <ul class="todo-list">
                {% for todo in todos %}
                    <li class="todo-item {% if todo.completed %}done{% endif %}">
                        <div>
                            <h3>{{ todo.title }}</h3>

                            {% if todo.description %}
                                <p>{{ todo.description }}</p>
                            {% endif %}

                            <small>{{ todo.created_at }}</small>
                        </div>

                        <div class="actions">
                            <a href="{% url 'toggle_todo' todo.id %}">
                                {% if todo.completed %}
                                    Undo
                                {% else %}
                                    Done
                                {% endif %}
                            </a>

                            <a href="{% url 'delete_todo' todo.id %}" class="danger">
                                Delete
                            </a>
                        </div>
                    </li>
                {% endfor %}
            </ul>
        {% else %}
            <p>No todos yet.</p>
        {% endif %}
    </section>
</div>

</body>
</html>
```

---

# 16. Create CSS File

Create:

```text
static/css/app.css
```

Add:

```css
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    color: #1f2937;
}

.app {
    width: min(900px, 92%);
    margin: 40px auto;
}

.hero {
    text-align: center;
    margin-bottom: 32px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 8px;
}

.hero p {
    color: #6b7280;
}

.card {
    background: #ffffff;
    padding: 24px;
    margin-bottom: 24px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

.todo-form {
    display: grid;
    gap: 14px;
}

input,
textarea {
    width: 100%;
    padding: 12px 14px;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    font-size: 16px;
}

textarea {
    min-height: 90px;
    resize: vertical;
}

button {
    padding: 12px 16px;
    border: 0;
    border-radius: 10px;
    background: #2563eb;
    color: #ffffff;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #1d4ed8;
}

.todo-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.todo-item {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    padding: 18px 0;
    border-bottom: 1px solid #e5e7eb;
}

.todo-item:last-child {
    border-bottom: 0;
}

.todo-item h3 {
    margin: 0 0 6px;
}

.todo-item p {
    margin: 0 0 8px;
    color: #4b5563;
}

.todo-item small {
    color: #9ca3af;
}

.todo-item.done h3 {
    text-decoration: line-through;
    color: #6b7280;
}

.actions {
    display: flex;
    gap: 10px;
    align-items: center;
}

.actions a {
    text-decoration: none;
    color: #2563eb;
    font-weight: bold;
}

.actions a.danger {
    color: #dc2626;
}
```

---

# 17. Test Locally

Run the development server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000
```

Open the admin:

```text
http://127.0.0.1:8000/admin/
```

Test the API:

```bash
curl http://127.0.0.1:8000/api/todos/
```

Create a todo with the API:

```bash
curl -X POST http://127.0.0.1:8000/api/todos/create/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Django", "description": "Build and deploy todo app"}'
```

---

# 18. Create `requirements.txt`

Create the requirements file:

```bash
pip freeze > requirements.txt
```

Check it:

```bash
cat requirements.txt
```

Example:

```text
asgiref==3.8.1
Django==5.2.4
sqlparse==0.5.3
```

---

# 19. Create `.gitignore`

Create:

```bash
touch .gitignore
```

Add:

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd

# Virtual environments
.venv/
venv/
env/

# Django
db.sqlite3
staticfiles/
media/

# Local settings and secrets
.env
*.log

# SQLite backups
backups/

# macOS
.DS_Store

# IDE
.vscode/
.idea/
```

Important:

```text
Do not commit db.sqlite3.
Do not commit .venv/.
Do not commit staticfiles/.
```

---

# 20. Create `deploy.sh`

Create:

```bash
touch deploy.sh
chmod +x deploy.sh
```

Add:

```bash
#!/usr/bin/env bash
set -e

APP_DIR="$HOME/django-todo-app"
BACKUP_DIR="$APP_DIR/backups"
DB_FILE="$APP_DIR/db.sqlite3"

echo "==> Go to project directory"
cd "$APP_DIR"

echo "==> Create backup directory"
mkdir -p "$BACKUP_DIR"

if [ -f "$DB_FILE" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    echo "==> Backup SQLite database"
    cp "$DB_FILE" "$BACKUP_DIR/db_$TIMESTAMP.sqlite3"
fi

echo "==> Pull latest code"
git pull origin main

echo "==> Activate virtual environment"
source .venv/bin/activate

echo "==> Install/update dependencies"
pip install -r requirements.txt

echo "==> Run database migrations"
python manage.py migrate

echo "==> Collect static files"
python manage.py collectstatic --noinput

echo "==> Deployment steps complete"
echo "Reload the web app in the PythonAnywhere Web tab."
```

Commit this file to Git.

---

# 21. Initialize Git Repository

Inside the project folder:

```bash
git init
git add .
git commit -m "Initial Django todo app"
git branch -M main
```

---

# 22. Create GitHub Repository

On GitHub:

1. Create a new repository
2. Name it:

```text
django-todo-app
```

3. Do not initialize it with README if you already have local files
4. Copy the repository URL

Example repository URL:

```text
https://github.com/YOUR_GITHUB_USERNAME/django-todo-app.git
```

Connect the local project to GitHub:

```bash
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/django-todo-app.git
git push -u origin main
```

---

# 23. Local Development Workflow

After the first setup, your normal local workflow is:

```bash
source .venv/bin/activate
python manage.py runserver
```

Edit code.

Test locally.

Then commit and push:

```bash
git status
git add .
git commit -m "Describe your change"
git push origin main
```

---

# 24. PythonAnywhere Initial Setup

## 24.1 Create PythonAnywhere Account

Create a PythonAnywhere account.

Your free web app URL will be:

```text
https://YOUR_USERNAME.pythonanywhere.com
```

## 24.2 Open Bash Console

In PythonAnywhere:

```text
Dashboard → Consoles → Bash
```

## 24.3 Clone the Repository

Run:

```bash
cd ~
git clone https://github.com/YOUR_GITHUB_USERNAME/django-todo-app.git
cd django-todo-app
```

If your repository is private, use SSH or a GitHub personal access token.

---

# 25. Private GitHub Repository Access

## Option A: Use SSH Key

On PythonAnywhere Bash:

```bash
ssh-keygen -t ed25519 -C "pythonanywhere"
cat ~/.ssh/id_ed25519.pub
```

Copy the printed public key.

In GitHub:

```text
GitHub → Settings → SSH and GPG keys → New SSH key
```

Then clone with SSH:

```bash
git clone git@github.com:YOUR_GITHUB_USERNAME/django-todo-app.git
```

## Option B: Use GitHub Token

Create a GitHub Personal Access Token.

Clone with:

```bash
git clone https://YOUR_GITHUB_USERNAME:YOUR_TOKEN@github.com/YOUR_GITHUB_USERNAME/django-todo-app.git
```

For long-term use, SSH is usually cleaner.

---

# 26. Create Virtual Environment on PythonAnywhere

Inside PythonAnywhere Bash:

```bash
cd ~/django-todo-app
python3.10 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Use the same Python version as your PythonAnywhere Web app.

---

# 27. Run Initial Django Setup on PythonAnywhere

Run:

```bash
cd ~/django-todo-app
source .venv/bin/activate

python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

This creates:

```text
/home/YOUR_USERNAME/django-todo-app/db.sqlite3
/home/YOUR_USERNAME/django-todo-app/staticfiles/
```

Both should stay on PythonAnywhere and should not be committed to Git.

---

# 28. Configure PythonAnywhere Web App

In PythonAnywhere:

```text
Dashboard → Web → Add a new web app
```

Choose:

```text
Manual configuration
```

Choose the Python version, for example:

```text
Python 3.10
```

Do not select the automatic Django setup when you already have an existing project.

---

# 29. Configure PythonAnywhere Paths

In the PythonAnywhere Web tab:

## Source code

Set:

```text
/home/YOUR_USERNAME/django-todo-app
```

## Working directory

Set:

```text
/home/YOUR_USERNAME/django-todo-app
```

## Virtualenv

Set:

```text
/home/YOUR_USERNAME/django-todo-app/.venv
```

---

# 30. Configure WSGI File

In PythonAnywhere Web tab, click the WSGI configuration file.

Replace its content with:

```python
import os
import sys

path = "/home/YOUR_USERNAME/django-todo-app"

if path not in sys.path:
    sys.path.append(path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_ALLOWED_HOSTS"] = "YOUR_USERNAME.pythonanywhere.com"
os.environ["DJANGO_SECRET_KEY"] = "replace-this-with-a-long-random-secret-key"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

Replace every occurrence of `YOUR_USERNAME`.

Example:

```python
path = "/home/ralph/django-todo-app"
os.environ["DJANGO_ALLOWED_HOSTS"] = "ralph.pythonanywhere.com"
```

Important:

```text
Never publish the production SECRET_KEY in GitHub.
```

That is why it is placed in the PythonAnywhere WSGI file.

---

# 31. Configure Static Files on PythonAnywhere

In PythonAnywhere:

```text
Web → Static files
```

Add this mapping:

| URL | Directory |
|---|---|
| `/static/` | `/home/YOUR_USERNAME/django-todo-app/staticfiles` |

Then reload the web app.

---

# 32. First Test on PythonAnywhere

Open:

```text
https://YOUR_USERNAME.pythonanywhere.com
```

Open admin:

```text
https://YOUR_USERNAME.pythonanywhere.com/admin/
```

Open API:

```text
https://YOUR_USERNAME.pythonanywhere.com/api/todos/
```

---

# 33. Update Workflow With Git Pull

After the initial deployment, updates are simple.

## Local computer

Make changes:

```bash
git status
git add .
git commit -m "Update todo app"
git push origin main
```

## PythonAnywhere

Open Bash console and run:

```bash
cd ~/django-todo-app
./deploy.sh
```

Then go to:

```text
PythonAnywhere → Web → Reload
```

The deployment script does this:

1. Creates a SQLite backup
2. Pulls the latest GitHub code
3. Activates the virtual environment
4. Installs changed requirements
5. Runs migrations
6. Collects static files

---

# 34. Optional Bash Alias

On PythonAnywhere, open:

```bash
nano ~/.bashrc
```

Add:

```bash
alias deploy-todo='cd ~/django-todo-app && ./deploy.sh'
```

Reload shell settings:

```bash
source ~/.bashrc
```

Now deployment becomes:

```bash
deploy-todo
```

Then reload the web app.

---

# 35. Important Git Rules

## Always commit migrations

When you change models locally:

```bash
python manage.py makemigrations
python manage.py migrate
```

Then commit migration files:

```bash
git add todos/migrations/
git commit -m "Add todo model changes"
git push origin main
```

On PythonAnywhere:

```bash
cd ~/django-todo-app
./deploy.sh
```

## Never commit SQLite database

Never run:

```bash
git add db.sqlite3
```

The production database belongs only on PythonAnywhere.

## Never commit secrets

Never commit:

```text
SECRET_KEY
API keys
passwords
.env files
```

---

# 36. Useful Commands

## Start local server

```bash
python manage.py runserver
```

## Create migrations

```bash
python manage.py makemigrations
```

## Apply migrations

```bash
python manage.py migrate
```

## Create admin user

```bash
python manage.py createsuperuser
```

## Collect static files

```bash
python manage.py collectstatic --noinput
```

## Check Django project

```bash
python manage.py check
```

## Open Django shell

```bash
python manage.py shell
```

---

# 37. Troubleshooting

## CSS is not loading on PythonAnywhere

Run:

```bash
cd ~/django-todo-app
source .venv/bin/activate
python manage.py collectstatic --noinput
```

Check the static file mapping:

```text
/static/ → /home/YOUR_USERNAME/django-todo-app/staticfiles
```

Then reload the web app.

## DisallowedHost error

Check `DJANGO_ALLOWED_HOSTS` in the WSGI file:

```python
os.environ["DJANGO_ALLOWED_HOSTS"] = "YOUR_USERNAME.pythonanywhere.com"
```

Then reload the web app.

## New model fields are missing

Run locally:

```bash
python manage.py makemigrations
python manage.py migrate
git add .
git commit -m "Add database migration"
git push origin main
```

Then on PythonAnywhere:

```bash
cd ~/django-todo-app
./deploy.sh
```

## Git pull fails because files changed on PythonAnywhere

Check status:

```bash
git status
```

If only generated files are changed, add them to `.gitignore`.

If you edited source files directly on PythonAnywhere, either commit them or discard them:

```bash
git checkout -- path/to/file.py
```

Then:

```bash
git pull origin main
```

## Database was accidentally committed

Remove it from Git tracking:

```bash
git rm --cached db.sqlite3
echo "db.sqlite3" >> .gitignore
git add .gitignore
git commit -m "Stop tracking SQLite database"
git push origin main
```

## Server shows old version after git pull

Run:

```bash
cd ~/django-todo-app
source .venv/bin/activate
python manage.py collectstatic --noinput
```

Then reload the app in the PythonAnywhere Web tab.

---

# 38. Final Checklist

Before local commit:

```text
[ ] App runs locally
[ ] No errors in terminal
[ ] Migrations are created
[ ] Migrations are committed
[ ] requirements.txt is updated if packages changed
[ ] db.sqlite3 is not committed
[ ] .venv is not committed
```

Before PythonAnywhere reload:

```text
[ ] git pull completed
[ ] pip install -r requirements.txt completed
[ ] python manage.py migrate completed
[ ] python manage.py collectstatic --noinput completed
[ ] Web app reloaded
```

---

# 39. Final Production Workflow

Use this workflow every time:

## Local

```bash
source .venv/bin/activate
python manage.py runserver
```

After changes:

```bash
git add .
git commit -m "Describe the update"
git push origin main
```

## PythonAnywhere

```bash
deploy-todo
```

or:

```bash
cd ~/django-todo-app
./deploy.sh
```

Then:

```text
PythonAnywhere → Web → Reload
```

---

# 40. Summary of Main Files

```text
django-todo-app/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── todos/
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── templates/
│   └── todos/
│       └── index.html
├── static/
│   └── css/
│       └── app.css
├── manage.py
├── requirements.txt
├── .gitignore
├── deploy.sh
└── SETUP.md
```
