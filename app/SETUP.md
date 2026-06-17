# SETUP.md

# Teacher Management Django App Setup

This guide explains how to run and deploy the Teacher Management Django app.

The project contains both:

- Django API backend using SQLite
- Django HTML/CSS frontend using templates

## 1. Data Model

The app manages four main entities:

```text
Teacher
School
Course
Attendance
```

Relationships:

```text
Teacher 1..n Attendance
School  1..n Attendance
Course  1..n Attendance
```

One attendance entry describes:

- which teacher
- which school
- which course
- which weekday
- start and end time
- room
- optional date range
- notes

## 2. Local Installation

```bash
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

## 3. Frontend Pages

| URL | Description |
|---|---|
| `/` | Dashboard |
| `/teachers/` | Teacher list |
| `/teachers/new/` | Create teacher |
| `/schools/` | School list |
| `/schools/new/` | Create school |
| `/courses/` | Course list |
| `/courses/new/` | Create course |
| `/attendances/` | Attendance plan |
| `/attendances/new/` | Create attendance entry |

## 4. API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/api/teachers/` | List teachers |
| POST | `/api/teachers/create/` | Create teacher |
| GET | `/api/teachers/<id>/` | Teacher detail |
| POST/PUT/PATCH | `/api/teachers/<id>/update/` | Update teacher |
| DELETE/POST | `/api/teachers/<id>/delete/` | Delete teacher |
| GET | `/api/schools/` | List schools |
| GET | `/api/courses/` | List courses |
| GET | `/api/attendances/` | List attendances |
| POST | `/api/attendances/create/` | Create attendance |

## 5. Create GitHub Repository

```bash
git init
git add .
git commit -m "Initial teacher management app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/teacher-management-django.git
git push -u origin main
```

## 6. PythonAnywhere Initial Deployment

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

## 7. PythonAnywhere WSGI Configuration

Use this WSGI file content:

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

## 8. Static Files on PythonAnywhere

Add this static mapping:

| URL | Directory |
|---|---|
| `/static/` | `/home/YOUR_USERNAME/teacher-management-django/staticfiles` |

Then reload the app.

## 9. Update Workflow

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

Then reload the web app.

## 10. Important Notes

Do not commit:

- `db.sqlite3`
- `.venv/`
- `staticfiles/`
- `.env`
- secrets

Always commit migrations when changing models.
