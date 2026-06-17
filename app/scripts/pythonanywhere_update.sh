#!/usr/bin/env bash
set -euo pipefail

git pull origin main

source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

echo "PythonAnywhere update complete."
echo "Now reload the web app in the PythonAnywhere Web tab."
