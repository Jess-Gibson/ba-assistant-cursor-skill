#!/usr/bin/env bash
# Upgrade BA Assistant to Version 10
# Dry-run:  ./tools/upgrade-ba-assistant.sh /path/to/ba-assistant-cursor-skill
# Apply:    ./tools/upgrade-ba-assistant.sh /path/to/ba-assistant-cursor-skill --apply
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PKG="${1:?Package root required}"
shift || true
exec python3 "$ROOT/upgrade-ba-assistant.py" --package "$PKG" "$@"
