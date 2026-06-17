#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

echo "==> Create virtual environment"
"$PYTHON_BIN" -m venv "$VENV_DIR"

echo "==> Upgrade pip"
"$VENV_DIR/bin/pip" install --upgrade pip

echo "==> Install dependencies"
"$VENV_DIR/bin/pip" install -r requirements.txt

echo "==> Run migrations"
"$VENV_DIR/bin/python" manage.py migrate

echo "Setup complete."
echo "Next:"
echo "  source .venv/bin/activate"
echo "  python manage.py createsuperuser"
echo "  python manage.py runserver"
