#!/usr/bin/env bash
# beforeSubmitPrompt hook — computed per-turn state reminder (C3).
# Thin wrapper; logic in inject-state-reminder.py.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/inject-state-reminder.py"
