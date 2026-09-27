#!/usr/bin/env bash
# Personalised-install upgrade helper (Mac/Linux). Passes every argument through.
# See docs/V15-WORK-LAPTOP.md for the full walkthrough.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$ROOT/ba-merge-upgrade.py" "$@"
