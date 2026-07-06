#!/usr/bin/env bash
# beforeMCPExecution hook — deny Jira STORY creation when no DoR pass is evident.
# Thin wrapper; logic lives in jira-dor-gate.py (shared with the .ps1 twin).
# Contract: stdin = MCP call JSON; stdout = {"permission": allow|deny, ...}.
# Verify payload field names against current Cursor hooks docs — they change.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/jira-dor-gate.py"
