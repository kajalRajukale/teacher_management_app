# PROMPT.md

# AI Prompt for Creating the Teacher Management Django Application

This document contains all requirements and context used to create the application.

It can be copied into an AI coding assistant to generate the complete project from scratch.

---

# 1. Application Name

```text
Teacher Management Django App
```

Repository / folder name:

```text
teacher-management-django
```

---

# 2. Main Goal

Create a Django application for managing teachers, their information, schools, courses, and when and where teachers attend schools and courses.

The final Django project must contain both:

1. A Django API backend using SQLite
2. A Django frontend using plain HTML and CSS

The application should be deployable to PythonAnywhere and manageable through a GitHub repository.

The update workflow should be:

```text
Local computer
    ↓ git push
GitHub repository
    ↓ git pull
PythonAnywhere server
    ↓ reload web app
Live Django app
```

---

# 3. Technical Requirements

Use:

- Python
- Django
- SQLite
- Django templates
- HTML
- CSS
- GitHub
- PythonAnywhere

Do not use:

- React
- Vue
- Angular
- Node build tools
- Django REST Framework
- PostgreSQL
- Docker

The app should be simple, beginner-friendly, and PythonAnywhere-ready.

---

# 4. Architecture

The project should be a classic Django monolith:

```text
Browser
    ↓
Django HTML/CSS frontend
    ↓
Django views
    ↓
Django models
    ↓
SQLite database
```

In addition, expose JSON API endpoints:

```text
External client / JavaScript / API consumer
    ↓
Django API views
    ↓
Django models
    ↓
SQLite database
```

---

# 5. Required Django Project Structure

Create this project structure:

```text
teacher-management-django/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── management/
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── templates/
│   └── management/
│       ├── base.html
│       ├── dashboard.html
│       ├── teacher_list.html
│       ├── school_list.html
│       ├── course_list.html
│       ├── attendance_list.html
│       ├── form.html
│       └── confirm_delete.html
│
├── static/
│   └── css/
│       └── app.css
│
├── scripts/
│   ├── clean.sh
│   ├── create_demo_data.py
│   ├── demo_data.sh
│   ├── deploy_pythonanywhere.sh
│   └── reset_db.sh
│
├── manage.py
├── requirements.txt
├── .gitignore
├── justfile
├── deploy.sh
├── README.md
├── SETUP.md
└── PROMPT.md
```

---

# 6. Data Model

Create four main models:

## 6.1 Teacher

Fields:

- `first_name`
- `last_name`
- `email`
- `phone`
- `qualification`
- `notes`
- `active`
- `full_name` property

Ordering:

```python
["last_name", "first_name"]
```

String representation:

```python
"First Last"
```

---

## 6.2 School

Fields:

- `name`
- `city`
- `address`
- `phone`
- `email`

Ordering:

```python
["name"]
```

String representation:

```python
"name"
```

---

## 6.3 Course

Fields:

- `name`
- `subject`
- `level`
- `description`

Ordering:

```python
["name"]
```

String representation:

```python
"name"
```

---

## 6.4 Attendance

An attendance entry describes when and where a teacher attends a school and course.

Fields:

- `teacher`
- `school`
- `course`
- `weekday`
- `start_time`
- `end_time`
- `room`
- `start_date`
- `end_date`
- `notes`

Relationships:

```text
Teacher 1..n Attendance
School  1..n Attendance
Course  1..n Attendance
```

Weekday choices:

```python
[
    ("MON", "Monday"),
    ("TUE", "Tuesday"),
    ("WED", "Wednesday"),
    ("THU", "Thursday"),
    ("FRI", "Friday"),
    ("SAT", "Saturday"),
    ("SUN", "Sunday"),
]
```

Ordering:

```python
["weekday", "start_time", "teacher__last_name"]
```

---

# 7. Frontend Requirements

Create a plain Django template frontend with HTML and CSS.

No frontend framework.

## Pages

| URL | Page |
|---|---|
| `/` | Dashboard |
| `/teachers/` | Teacher list |
| `/teachers/new/` | Create teacher |
| `/teachers/<id>/edit/` | Edit teacher |
| `/teachers/<id>/delete/` | Delete teacher |
| `/schools/` | School list |
| `/schools/new/` | Create school |
| `/schools/<id>/edit/` | Edit school |
| `/schools/<id>/delete/` | Delete school |
| `/courses/` | Course list |
| `/courses/new/` | Create course |
| `/courses/<id>/edit/` | Edit course |
| `/courses/<id>/delete/` | Delete course |
| `/attendances/` | Attendance list |
| `/attendances/new/` | Create attendance |
| `/attendances/<id>/edit/` | Edit attendance |
| `/attendances/<id>/delete/` | Delete attendance |
| `/admin/` | Django admin |

---

## Dashboard

The dashboard should show:

- Number of teachers
- Number of schools
- Number of courses
- Number of attendance entries
- A small table of current attendance entries

---

## Navigation

Create a shared `base.html` template with navigation links:

- Dashboard
- Teachers
- Schools
- Courses
- Attendance
- Admin

---

## CRUD Pages

Create list, create, edit, and delete pages for:

- Teachers
- Schools
- Courses
- Attendance

Use Django `ModelForm` classes.

Use reusable templates where useful:

- `form.html`
- `confirm_delete.html`

---

# 8. API Backend Requirements

Use simple Django JSON views.

Do not use Django REST Framework.

## API Endpoints

| Method | URL | Purpose |
|---|---|---|
| `GET` | `/api/teachers/` | List teachers |
| `POST` | `/api/teachers/create/` | Create teacher |
| `GET` | `/api/teachers/<id>/` | Get teacher detail |
| `POST/PUT/PATCH` | `/api/teachers/<id>/update/` | Update teacher |
| `DELETE/POST` | `/api/teachers/<id>/delete/` | Delete teacher |
| `GET` | `/api/schools/` | List schools |
| `GET` | `/api/courses/` | List courses |
| `GET` | `/api/attendances/` | List attendance entries |
| `POST` | `/api/attendances/create/` | Create attendance entry |

---

## API Format

Teacher JSON:

```json
{
  "id": 1,
  "first_name": "Anna",
  "last_name": "Meyer",
  "full_name": "Anna Meyer",
  "email": "anna.meyer@example.com",
  "phone": "+49 123 456",
  "qualification": "Python Trainer",
  "notes": "Demo teacher",
  "active": true
}
```

School JSON:

```json
{
  "id": 1,
  "name": "Central School",
  "city": "Hamburg",
  "address": "Main Street 1",
  "phone": "+49 40 123456",
  "email": "office@central-school.example"
}
```

Course JSON:

```json
{
  "id": 1,
  "name": "Python Basics",
  "subject": "Computer Science",
  "level": "Beginner",
  "description": "Introductory programming course with Python."
}
```

Attendance JSON:

```json
{
  "id": 1,
  "teacher": {
    "id": 1,
    "full_name": "Anna Meyer"
  },
  "school": {
    "id": 1,
    "name": "Central School"
  },
  "course": {
    "id": 1,
    "name": "Python Basics"
  },
  "weekday": "MON",
  "weekday_display": "Monday",
  "start_time": "09:00",
  "end_time": "11:00",
  "room": "A101",
  "start_date": null,
  "end_date": null,
  "notes": "Demo attendance entry."
}
```

---

# 9. Admin Requirements

Register all models in Django admin:

- Teacher
- School
- Course
- Attendance

Admin should include:

- `list_display`
- `list_filter` where useful
- `search_fields`

---

# 10. Static Files and Design

Use one CSS file:

```text
static/css/app.css
```

Design requirements:

- Clean admin-style layout
- Dark top navigation bar
- Card-based content sections
- Dashboard statistic cards
- Tables for list pages
- Responsive layout
- Simple buttons
- Clear edit/delete links
- Mobile-friendly table overflow

---

# 11. Settings Requirements

The Django settings should support local development and PythonAnywhere production deployment.

Use environment variables:

```python
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-secret-key-change-this-before-production"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")
```

Use SQLite:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

Use static configuration:

```python
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

Timezone:

```python
TIME_ZONE = "Europe/Berlin"
```

---

# 12. GitHub Requirements

The project must be manageable as a GitHub repository.

Create `.gitignore` that excludes:

```text
.venv/
venv/
env/
__pycache__/
*.pyc
db.sqlite3
staticfiles/
media/
.env
*.log
backups/
.DS_Store
.vscode/
.idea/
```

Do commit:

- Source code
- Templates
- Static CSS
- Migrations
- `requirements.txt`
- `README.md`
- `SETUP.md`
- `PROMPT.md`
- `justfile`
- Scripts

Do not commit:

- SQLite database
- Virtual environment
- Collected static files
- Secrets

---

# 13. PythonAnywhere Requirements

The application should be deployable to PythonAnywhere.

## Initial setup on PythonAnywhere

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

## WSGI configuration

Use:

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

## Static file mapping

| URL | Directory |
|---|---|
| `/static/` | `/home/YOUR_USERNAME/teacher-management-django/staticfiles` |

---

# 14. Deployment Script Requirements

Create:

```text
deploy.sh
```

It should call:

```text
scripts/deploy_pythonanywhere.sh
```

Create:

```text
scripts/deploy_pythonanywhere.sh
```

It should:

1. Go to project directory
2. Create `backups/`
3. Back up `db.sqlite3` if it exists
4. Run `git pull origin main`
5. Activate `.venv`
6. Run `pip install -r requirements.txt`
7. Run `python manage.py migrate`
8. Run `python manage.py collectstatic --noinput`
9. Print a reminder to reload the PythonAnywhere web app

---

# 15. Justfile Requirements

Create a `justfile`.

Important instruction:

- Keep simple commands directly in the `justfile`
- Only move complex commands to external scripts
- Simple `python manage.py ...`, `git ...`, and `pip ...` commands should remain in the `justfile`
- External scripts are only for commands that need complex Bash logic or separate Python code

Required `justfile` commands:

```text
default
venv
install
setup
run
run-port
check
makemigrations
migrate
superuser
shell
static
test
validate
freeze
clean
reset-db
demo-data
git-status
commit
push
release
pa-deploy
pa-update
api
pages
```

Expected command style:

```make
migrate:
    .venv/bin/python manage.py migrate

run:
    .venv/bin/python manage.py runserver

push:
    git push origin main
```

Only these actions should use scripts:

```text
clean
reset-db
demo-data
pa-deploy
```

---

# 16. Scripts Requirements

Create only necessary external scripts.

Required scripts:

```text
scripts/clean.sh
scripts/reset_db.sh
scripts/create_demo_data.py
scripts/demo_data.sh
scripts/deploy_pythonanywhere.sh
```

Do not move every command into scripts.

---

# 17. Demo Data Requirements

Create demo data script.

The demo data should create:

## School

```text
Central School
Hamburg
Main Street 1
+49 40 123456
office@central-school.example
```

## Course

```text
Python Basics
Computer Science
Beginner
Introductory programming course with Python.
```

## Teacher

```text
Anna Meyer
anna.meyer@example.com
+49 123 456
Python Trainer
Demo teacher for local testing.
Active: true
```

## Attendance

```text
Teacher: Anna Meyer
School: Central School
Course: Python Basics
Weekday: Monday
Start: 09:00
End: 11:00
Room: A101
Notes: Demo attendance entry.
```

The command should be:

```bash
just demo-data
```

or:

```bash
scripts/demo_data.sh
```

---

# 18. Documentation Requirements

Create:

```text
README.md
SETUP.md
PROMPT.md
```

## README.md

Should include:

- Project overview
- Features
- Local setup
- API examples
- PythonAnywhere deployment
- GitHub update workflow
- Justfile commands
- Scripts explanation

## SETUP.md

Should include:

- Detailed setup steps
- Data model explanation
- Frontend pages
- API endpoints
- GitHub setup
- PythonAnywhere setup
- WSGI config
- Static files config
- Update workflow
- Justfile and scripts strategy

## PROMPT.md

Should include:

- All requirements
- AI generation prompt
- Expected output structure
- Quality checklist

---

# 19. Final AI Generation Prompt

Copy the following prompt into an AI coding assistant to recreate this application.

---

## Prompt

Create a complete Django project named `teacher-management-django`.

The app is a teacher management system for managing teachers, schools, courses, and attendance planning. It must contain both a Django API backend using SQLite and a Django frontend using plain HTML/CSS templates.

Use Python, Django, SQLite, Django templates, HTML, CSS, GitHub-compatible project files, and PythonAnywhere-ready deployment configuration.

Do not use Django REST Framework, React, Vue, Angular, Node tooling, Docker, PostgreSQL, or external frontend frameworks.

Create the following structure:

```text
teacher-management-django/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── management/
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── templates/
│   └── management/
│       ├── base.html
│       ├── dashboard.html
│       ├── teacher_list.html
│       ├── school_list.html
│       ├── course_list.html
│       ├── attendance_list.html
│       ├── form.html
│       └── confirm_delete.html
├── static/
│   └── css/
│       └── app.css
├── scripts/
│   ├── clean.sh
│   ├── create_demo_data.py
│   ├── demo_data.sh
│   ├── deploy_pythonanywhere.sh
│   └── reset_db.sh
├── manage.py
├── requirements.txt
├── .gitignore
├── justfile
├── deploy.sh
├── README.md
├── SETUP.md
└── PROMPT.md
```

Implement these models:

1. `Teacher`
   - first_name
   - last_name
   - email
   - phone
   - qualification
   - notes
   - active
   - full_name property

2. `School`
   - name
   - city
   - address
   - phone
   - email

3. `Course`
   - name
   - subject
   - level
   - description

4. `Attendance`
   - teacher foreign key
   - school foreign key
   - course foreign key
   - weekday choices: MON, TUE, WED, THU, FRI, SAT, SUN
   - start_time
   - end_time
   - room
   - start_date
   - end_date
   - notes

Create admin classes for all models with useful `list_display`, `list_filter`, and `search_fields`.

Create Django `ModelForm` classes for Teacher, School, Course, and Attendance.

Create the frontend pages:

- `/` dashboard
- `/teachers/`
- `/teachers/new/`
- `/teachers/<id>/edit/`
- `/teachers/<id>/delete/`
- `/schools/`
- `/schools/new/`
- `/schools/<id>/edit/`
- `/schools/<id>/delete/`
- `/courses/`
- `/courses/new/`
- `/courses/<id>/edit/`
- `/courses/<id>/delete/`
- `/attendances/`
- `/attendances/new/`
- `/attendances/<id>/edit/`
- `/attendances/<id>/delete/`

Use templates:

- `base.html`
- `dashboard.html`
- `teacher_list.html`
- `school_list.html`
- `course_list.html`
- `attendance_list.html`
- `form.html`
- `confirm_delete.html`

The dashboard should show counts for teachers, schools, courses, and attendance entries. It should also show a small table of attendance entries.

Create JSON API endpoints:

- `GET /api/teachers/`
- `POST /api/teachers/create/`
- `GET /api/teachers/<id>/`
- `POST/PUT/PATCH /api/teachers/<id>/update/`
- `DELETE/POST /api/teachers/<id>/delete/`
- `GET /api/schools/`
- `GET /api/courses/`
- `GET /api/attendances/`
- `POST /api/attendances/create/`

Use Django `JsonResponse`. Do not use Django REST Framework.

Use SQLite as the database.

Configure `settings.py` with environment variables:

```python
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-secret-key-change-this-before-production"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")
```

Configure static files:

```python
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

Set:

```python
TIME_ZONE = "Europe/Berlin"
```

Create `static/css/app.css` with a clean responsive admin-style design:

- Dark top navigation
- Cards
- Statistic cards
- Tables
- Buttons
- Forms
- Mobile responsive behavior

Create `.gitignore` that excludes:

- `.venv/`
- `venv/`
- `env/`
- `__pycache__/`
- `*.pyc`
- `db.sqlite3`
- `staticfiles/`
- `media/`
- `.env`
- `*.log`
- `backups/`
- `.DS_Store`
- `.vscode/`
- `.idea/`

Create `requirements.txt` with Django.

Create `justfile`.

Keep simple commands directly in the `justfile`, for example:

```make
migrate:
    .venv/bin/python manage.py migrate

run:
    .venv/bin/python manage.py runserver

push:
    git push origin main
```

Only use external scripts for complex logic:

- clean
- reset-db
- demo-data
- pa-deploy

Create these scripts:

- `scripts/clean.sh`
- `scripts/reset_db.sh`
- `scripts/create_demo_data.py`
- `scripts/demo_data.sh`
- `scripts/deploy_pythonanywhere.sh`

Create `deploy.sh` that calls:

```bash
scripts/deploy_pythonanywhere.sh
```

The PythonAnywhere deployment script should:

1. Change to `$HOME/teacher-management-django`
2. Create backup folder
3. Backup `db.sqlite3`
4. Run `git pull origin main`
5. Activate `.venv`
6. Install requirements
7. Run migrations
8. Run collectstatic
9. Print reminder to reload the PythonAnywhere web app

Create demo data:

- School: Central School, Hamburg, Main Street 1
- Course: Python Basics, Computer Science, Beginner
- Teacher: Anna Meyer, Python Trainer
- Attendance: Monday 09:00 to 11:00, room A101

Create documentation files:

- `README.md`
- `SETUP.md`
- `PROMPT.md`

The documentation must describe:

- Local setup
- GitHub workflow
- PythonAnywhere deployment
- API endpoints
- Frontend pages
- Justfile commands
- Scripts strategy
- Important rule: do not commit `db.sqlite3`, `.venv`, `staticfiles`, or secrets

The project must run with:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

And with Just:

```bash
just setup
just superuser
just demo-data
just run
```

Return the full project files with complete source code.

---

# 20. Quality Checklist

The generated app is complete only if:

```text
[ ] Django starts without errors
[ ] SQLite database migrates successfully
[ ] Admin login works
[ ] Dashboard works at /
[ ] Teachers CRUD works
[ ] Schools CRUD works
[ ] Courses CRUD works
[ ] Attendance CRUD works
[ ] API returns JSON
[ ] Static CSS loads
[ ] just setup works
[ ] just run works
[ ] just demo-data works
[ ] PythonAnywhere deployment instructions are included
[ ] GitHub workflow is documented
[ ] db.sqlite3 is not committed
[ ] .venv is not committed
[ ] staticfiles is not committed
```
