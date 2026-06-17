#!/usr/bin/env bash
set -euo pipefail

.venv/bin/pip freeze > requirements.txt
echo "requirements.txt updated."
