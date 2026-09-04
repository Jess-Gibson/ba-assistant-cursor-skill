#!/usr/bin/env bash
# sessionStart hook v2 — inject latest SESSION-CONTEXT snippet + DETERMINISTIC downloads check (D5).
# Changes from v1:
#   - Actually sets CURSOR_NEW_TRANSCRIPTS (meeting-debrief and Step 2.75 have been reading
#     this env var since Wave 7, but v1 never set it — that was a bug).
#   - Lists .docx files in BA_DOWNLOADS_PATH newer than the SESSION-CONTEXT file (the
#     "unprocessed transcript" heuristic from workspace-operations.mdc, now hard-wired).
#   - Injects workspace agent-file guidance (AGENTS.md / README.md, D6).
set -euo pipefail

echo "session-init v2 running — $(date '+%H:%M:%S')" >&2

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

# --- Deterministic downloads check (D5) ---
downloads="${BA_DOWNLOADS_PATH:-$home/Downloads}"
new_transcripts=""
transcript_count=0
if [[ -d "$downloads" ]]; then
  while IFS= read -r f; do
    [[ -n "$f" ]] || continue
    if [[ "$OSTYPE" == "darwin"* ]]; then
      fmtime=$(stat -f '%m' "$f" 2>/dev/null || echo 0)
    else
      fmtime=$(stat -c '%Y' "$f" 2>/dev/null || echo 0)
    fi
    # Newer than last session activity (or last 48h when no SESSION-CONTEXT exists)
    threshold=$latest_mtime
    (( threshold == 0 )) && threshold=$(( $(date +%s) - 172800 ))
    if (( fmtime > threshold )); then
      new_transcripts+="$f"$'\n'
      transcript_count=$((transcript_count+1))
    fi
  done < <(find "$downloads" -maxdepth 1 -name '*.docx' -type f 2>/dev/null | head -20)
fi

transcript_block="New transcripts: none"
if (( transcript_count > 0 )); then
  transcript_block="New transcripts: ${transcript_count} unprocessed .docx in ${downloads} (newer than last session):
${new_transcripts}Process these as meeting debriefs (ba-meeting-debrief) before or alongside the user's first ask."
fi

roots_label=$(IFS='; '; echo "${search_roots[*]}")
context_block="No SESSION-CONTEXT.md found under configured initiative roots: ${roots_label}. Set BA_INITIATIVES_ROOT to your project folder root.
${transcript_block}"
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
If the open workspace has AGENTS.md at its root, read it as primary project context (else README.md). Load BA skills only from ~/.cursor/skills/ba-assistant/.

${transcript_block}

--- SESSION-CONTEXT tail ---
${snippet}
--- end ---
EOF
)
fi

export CONTEXT_BLOCK="$context_block"
export CTX_PATH="$ctx_path"
export NEW_TRANSCRIPTS="$new_transcripts"
export TRANSCRIPT_COUNT="$transcript_count"

if command -v python3 >/dev/null 2>&1; then
  python3 <<'PY'
import json, os
print(json.dumps({
    "additional_context": os.environ.get("CONTEXT_BLOCK", ""),
    "env": {
        "CURSOR_SESSION_CONTEXT_PATH": os.environ.get("CTX_PATH", ""),
        "CURSOR_NEW_TRANSCRIPTS": os.environ.get("NEW_TRANSCRIPTS", "").strip(),
        "CURSOR_NEW_TRANSCRIPT_COUNT": os.environ.get("TRANSCRIPT_COUNT", "0"),
    }
}, ensure_ascii=False))
PY
elif command -v jq >/dev/null 2>&1; then
  jq -n \
    --arg ctx "$context_block" \
    --arg path "$ctx_path" \
    --arg tr "$new_transcripts" \
    --arg trc "$transcript_count" \
    '{additional_context: $ctx, env: {CURSOR_SESSION_CONTEXT_PATH: $path, CURSOR_NEW_TRANSCRIPTS: $tr, CURSOR_NEW_TRANSCRIPT_COUNT: $trc}}'
else
  echo '{"additional_context":"","env":{"CURSOR_SESSION_CONTEXT_PATH":"","CURSOR_NEW_TRANSCRIPTS":"","CURSOR_NEW_TRANSCRIPT_COUNT":"0"}}'
fi

exit 0
