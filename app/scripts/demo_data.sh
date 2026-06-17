#!/usr/bin/env bash
set -euo pipefail

.venv/bin/python manage.py shell < scripts/create_demo_data.py
