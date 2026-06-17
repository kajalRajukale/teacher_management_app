#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/teacher-management-django}"
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

echo "==> Deployment complete"
echo "Reload the web app in the PythonAnywhere Web tab."
