#!/usr/bin/env bash
# Atomic state file writer for BMAD project state
# Usage: bmad-state-write.sh <project_root> <new_content_file>
# Writes .a0proj/instructions/02-bmad-state.md atomically via temp+rename
set -euo pipefail

PROJECT_ROOT="${1:-/a0/usr/projects/a0_bmad_method}"
CONTENT_FILE="${2:-}"
STATE_FILE="$PROJECT_ROOT/.a0proj/instructions/02-bmad-state.md"
TMP_FILE=$(mktemp "${STATE_FILE}.XXXXXX")

if [ -z "$CONTENT_FILE" ]; then
  echo "Usage: $0 <project_root> <content_file>" >&2
  exit 1
fi

if [ ! -f "$CONTENT_FILE" ]; then
  echo "Content file not found: $CONTENT_FILE" >&2
  exit 1
fi

# Write to temp first, then atomic rename
cp "$CONTENT_FILE" "$TMP_FILE"
mv "$TMP_FILE" "$STATE_FILE"
echo "State written atomically to $STATE_FILE"
