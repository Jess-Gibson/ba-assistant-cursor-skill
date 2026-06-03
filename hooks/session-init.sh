#!/usr/bin/env bash
# sessionStart hook — inject latest SESSION-CONTEXT snippet into agent context
set -euo pipefail

echo "session-init.sh running — $(date '+%H:%M:%S')" >&2

search_roots=()

if [[ -n "${BA_INITIATIVES_ROOT:-}" ]]; then
  search_roots+=("$BA_INITIATIVES_ROOT")
fi

home="${HOME:-${USERPROFILE:-}}"
search_roots+=(
  "$home/.cursor/Initiatives"
  "$home/.cursor/blueprints"
  "$home/ba-initiatives"
  "$home/Initiatives"
  "$home/projects"
)

latest=""
latest_mtime=0

for root in "${search_roots[@]}"; do
  [[ -d "$root" ]] || continue
  while IFS= read -r -d '' file; do
    if [[ "$OSTYPE" == "darwin"* ]]; then
      mtime=$(stat -f '%m' "$file" 2>/dev/null || echo 0)
    else
      mtime=$(stat -c '%Y' "$file" 2>/dev/null || echo 0)
    fi
    if (( mtime > latest_mtime )); then
      latest_mtime=$mtime
      latest=$file
    fi
  done < <(find "$root" -name 'SESSION-CONTEXT.md' -type f -print0 2>/dev/null)
done

roots_label=$(IFS='; '; echo "${search_roots[*]}")
context_block="No SESSION-CONTEXT.md found under configured initiative roots: ${roots_label}. Set BA_INITIATIVES_ROOT to your project folder root."
ctx_path=""

if [[ -n "$latest" ]]; then
  ctx_path=$latest
  if [[ "$OSTYPE" == "darwin"* ]]; then
    modified=$(stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$latest" 2>/dev/null || date '+%Y-%m-%d %H:%M')
  else
    modified=$(stat -c '%y' "$latest" 2>/dev/null | cut -d'.' -f1 || date '+%Y-%m-%d %H:%M')
  fi
  snippet=$(tail -n 45 "$latest" 2>/dev/null || true)
  context_block=$(cat <<EOF
ACTIVE INITIATIVE CONTEXT (auto-injected from ${latest}, modified ${modified}):
On BA-resume threads, READ the full file before acting. Do not rely on this snippet alone.

--- SESSION-CONTEXT tail ---
${snippet}
--- end ---
EOF
)
fi

export CONTEXT_BLOCK="$context_block"
export CTX_PATH="$ctx_path"

if command -v python3 >/dev/null 2>&1; then
  python3 <<'PY'
import json, os
print(json.dumps({
    "additional_context": os.environ.get("CONTEXT_BLOCK", ""),
    "env": {"CURSOR_SESSION_CONTEXT_PATH": os.environ.get("CTX_PATH", "")}
}, ensure_ascii=False))
PY
elif command -v jq >/dev/null 2>&1; then
  jq -n \
    --arg ctx "$context_block" \
    --arg path "$ctx_path" \
    '{additional_context: $ctx, env: {CURSOR_SESSION_CONTEXT_PATH: $path}}'
else
  echo '{"additional_context":"","env":{"CURSOR_SESSION_CONTEXT_PATH":""}}'
fi

exit 0
