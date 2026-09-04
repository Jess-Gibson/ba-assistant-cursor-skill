#!/usr/bin/env bash
# Install BA Assistant into your Cursor home
# Usage:
#   ./tools/install-ba-assistant.sh
#   ./tools/install-ba-assistant.sh --apply
#   ./tools/install-ba-assistant.sh --apply --cursor-home "$HOME/.cursor"

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CURSOR_HOME="${HOME}/.cursor"
APPLY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY="--apply"; shift ;;
    --dry-run) APPLY="--dry-run"; shift ;;
    --cursor-home) CURSOR_HOME="$2"; shift 2 ;;
    --package) PACKAGE_ROOT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

if [[ -z "$APPLY" ]]; then
  APPLY="--dry-run"
fi

python3 "$SCRIPT_DIR/install-ba-assistant.py" \
  --package "$PACKAGE_ROOT" \
  --cursor-home "$CURSOR_HOME" \
  $APPLY
