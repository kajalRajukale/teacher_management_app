#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
Frontend pages:

/                         Dashboard
/teachers/                 Teacher list
/teachers/new/             Create teacher
/schools/                  School list
/schools/new/              Create school
/courses/                  Course list
/courses/new/              Create course
/attendances/              Attendance plan
/attendances/new/          Create attendance
/admin/                    Django admin
EOF
