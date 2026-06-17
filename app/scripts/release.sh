#!/usr/bin/env bash
set -euo pipefail

MESSAGE="${1:-}"

if [ -z "$MESSAGE" ]; then
    echo "Usage: scripts/release.sh "commit message""
    exit 1
fi

scripts/validate.sh

git add .
git commit -m "$MESSAGE"
git push origin main
