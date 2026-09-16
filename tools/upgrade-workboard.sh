#!/usr/bin/env bash
# Workboard overlay installer wrapper (macOS/Linux)
set -euo pipefail
PACKAGE="$(cd "$(dirname "$0")/.." && pwd)"
APPLY=0
REPLACE_WRAP=0
REPLACE_WB=0
NO_PREVIEW=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --replace-wrap) REPLACE_WRAP=1 ;;
    --replace-workboard-command) REPLACE_WB=1 ;;
    --no-preview-canvas) NO_PREVIEW=1 ;;
    --package) PACKAGE="$2"; shift ;;
  esac
  shift
done
ARGS=(--package "$PACKAGE")
[[ "$APPLY" == 1 ]] && ARGS+=(--apply)
[[ "$REPLACE_WRAP" == 1 ]] && ARGS+=(--replace-wrap)
[[ "$REPLACE_WB" == 1 ]] && ARGS+=(--replace-workboard-command)
[[ "$NO_PREVIEW" == 1 ]] && ARGS+=(--no-preview-canvas)
python3 "$(dirname "$0")/upgrade-workboard.py" "${ARGS[@]}"
