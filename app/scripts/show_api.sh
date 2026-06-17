#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
API endpoints:

GET              /api/teachers/
POST             /api/teachers/create/
GET              /api/teachers/<id>/
POST/PUT/PATCH   /api/teachers/<id>/update/
DELETE/POST      /api/teachers/<id>/delete/

GET              /api/schools/
GET              /api/courses/

GET              /api/attendances/
POST             /api/attendances/create/
EOF
