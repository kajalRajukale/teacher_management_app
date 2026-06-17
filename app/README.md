# Teacher Management Django App

A complete starter Django project for managing:

- Teachers
- Schools
- Courses
- Teacher attendance at schools and courses

The project contains both:

- A Django API backend using SQLite
- A Django HTML/CSS frontend using templates

## Features

### HTML frontend

- Dashboard with counts
- Teacher list, create, edit, delete
- School list, create, edit, delete
- Course list, create, edit, delete
- Attendance list, create, edit, delete

### API backend

Available JSON endpoints:

| Method | URL | Description |
|---|---|---|
| GET | `/api/teachers/` | List teachers |
| POST | `/api/teachers/create/` | Create teacher |
| GET | `/api/teachers/<id>/` | Get teacher |
| POST/PUT/PATCH | `/api/teachers/<id>/update/` | Update teacher |
| DELETE/POST | `/api/teachers/<id>/delete/` | Delete teacher |
| GET | `/api/schools/` | List schools |
| GET | `/api/courses/` | List courses |
| GET | `/api/attendances/` | List attendance entries |
| POST | `/api/attendances/create/` | Create attendance entry |

## Local setup

```bash
git clone https://github.com/YOUR_USERNAME/teacher-management-django.git
cd teacher-management-django

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000
```

Admin:

```text
http://127.0.0.1:8000/admin/
```

## API examples

List teachers:

```bash
curl http://127.0.0.1:8000/api/teachers/
```

Create teacher:

```bash
curl -X POST http://127.0.0.1:8000/api/teachers/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Anna",
    "last_name": "Meyer",
    "email": "anna@example.com",
    "phone": "+49 123 456",
    "qualification": "Mathematics teacher",
    "active": true
  }'
```

## PythonAnywhere deployment

On PythonAnywhere:

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/teacher-management-django.git
cd teacher-management-django

python3.10 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

Configure the WSGI file:

```python
import os
import sys

path = "/home/YOUR_USERNAME/teacher-management-django"

if path not in sys.path:
    sys.path.append(path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_ALLOWED_HOSTS"] = "YOUR_USERNAME.pythonanywhere.com"
os.environ["DJANGO_SECRET_KEY"] = "replace-this-with-a-long-random-secret-key"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

Static files mapping on PythonAnywhere:

| URL | Directory |
|---|---|
| `/static/` | `/home/YOUR_USERNAME/teacher-management-django/staticfiles` |

## Update deployment

Local:

```bash
git add .
git commit -m "Update app"
git push origin main
```

PythonAnywhere:

```bash
cd ~/teacher-management-django
./deploy.sh
```

Then reload the web app in the PythonAnywhere Web tab.

## Assistant answer summary

This ZIP contains a ready-to-use Django project for a teacher management application. It implements a SQLite backend, CRUD pages with Django templates and CSS, basic JSON API endpoints, admin integration, deployment script, `.gitignore`, and setup instructions for local development and PythonAnywhere deployment through GitHub and `git pull`.
