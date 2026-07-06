#!/usr/bin/env bash
# stop hook — sync-gate breakpoint check at end of an agent response (D3).
# Replaces the soft "at 20 turns / at breakpoints, check for unpromoted items" rule
# with a deterministic check. Reuses inject-state-reminder.py: same computation,
# different event. Emits additional context only when there is real drift.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/inject-state-reminder.py" --stop
