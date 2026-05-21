#!/usr/bin/env bash
# Daily commit ritual for AeroRAG.
#
# Usage:
#   ./scripts/daily.sh "Day 03: PDF parsing pipeline with pdfplumber"
#
# What it does:
#   1. Creates docs/daily_logs/YYYY-MM-DD.md from the template if missing.
#   2. Opens it in $EDITOR for you to fill in.
#   3. Stages everything new + modified.
#   4. Shows you `git status` and asks for confirmation.
#   5. Commits with the message you passed.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 \"Day NN: short message\"" >&2
  exit 2
fi

MSG="$1"
DATE="$(date +%Y-%m-%d)"
LOG_DIR="docs/daily_logs"
LOG_FILE="${LOG_DIR}/${DATE}.md"
TEMPLATE="${LOG_DIR}/TEMPLATE.md"

mkdir -p "$LOG_DIR"

if [[ ! -f "$LOG_FILE" ]]; then
  if [[ -f "$TEMPLATE" ]]; then
    cp "$TEMPLATE" "$LOG_FILE"
  else
    cat > "$LOG_FILE" <<EOF
# ${DATE} — ${MSG}

## What I did

## What worked

## What broke

## Tomorrow
EOF
  fi
  echo "Created $LOG_FILE"
fi

EDITOR_BIN="${EDITOR:-cursor}"
echo "Opening $LOG_FILE in $EDITOR_BIN..."
"$EDITOR_BIN" "$LOG_FILE" || true

git add -A
git status --short

read -r -p "Commit with message: \"$MSG\"? [y/N] " confirm
case "$confirm" in
  [yY]|[yY][eE][sS])
    git commit -m "$MSG"
    echo "Committed. Push when ready: git push"
    ;;
  *)
    echo "Aborted. Changes are staged."
    exit 1
    ;;
esac
