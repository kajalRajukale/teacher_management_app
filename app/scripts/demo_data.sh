#!/usr/bin/env bash
set -euo pipefail

python manage.py shell < scripts/create_demo_data.py
