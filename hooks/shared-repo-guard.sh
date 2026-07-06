#!/usr/bin/env bash
# afterFileEdit + beforeShellExecution hook — blocks working-file leakage into the
# shared delivery repo. Thin wrapper; logic in shared-repo-guard.py.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/shared-repo-guard.py"
