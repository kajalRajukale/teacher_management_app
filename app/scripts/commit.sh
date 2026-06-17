#!/usr/bin/env bash
set -euo pipefail

MESSAGE="${1:-}"

if [ -z "$MESSAGE" ]; then
    echo "Usage: scripts/commit.sh "commit message""
    exit 1
fi

git add .
git commit -m "$MESSAGE"
