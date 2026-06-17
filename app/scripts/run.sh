#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8000}"
python manage.py runserver "0.0.0.0:${PORT}"
