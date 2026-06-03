#!/usr/bin/env bash
# preCompact hook — snapshot SESSION-CONTEXT before context compaction
set -euo pipefail

if [[ "$OSTYPE" == "darwin"* ]]; then
  scratch="${TMPDIR:-/tmp}/cursor-agent-scratch"
else
  scratch="${XDG_RUNTIME_DIR:-/tmp}/cursor-agent-scratch"
fi
mkdir -p "$scratch"

ctx_path="${CURSOR_SESSION_CONTEXT_PATH:-}"
if [[ -z "$ctx_path" || ! -f "$ctx_path" ]]; then
  echo '{}'
  exit 0
fi

stamp=$(date '+%Y%m%d-%H%M%S')
dest="$scratch/SESSION-CONTEXT-precompact-$stamp.md"
cp "$ctx_path" "$dest"

echo '{}'
exit 0
