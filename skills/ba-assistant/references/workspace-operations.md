# Workspace Operations Reference

**Location:** `~/.cursor/skills/ba-assistant/references/workspace-operations.md`  
**Last reviewed:** 2026-08-03 (Version 10 — cross-platform)

Configurable paths (set in **ba-setup** Step 2.5):

| Variable | Purpose | Typical default |
|---|---|---|
| `BA_DOWNLOADS_PATH` | Transcripts / downloads inbox | `~/Downloads` |
| `BA_INITIATIVES_ROOT` | Initiative folders root | `~/.cursor/initiatives` |
| `BA_SHARED_REPO_ROOT` | Shared delivery repo for `/handover` | (optional) |

---

## Downloads / transcripts check

On resume, `/reanchor`, `/workboard`, and `/wrap`: list recent files in `BA_DOWNLOADS_PATH` (all types, not only `.docx`). Flag anything unprocessed vs SESSION-CONTEXT / tracker.

### Platform commands

| OS | How to list |
|---|---|
| **Windows** | Prefer `cmd /c dir "%BA_DOWNLOADS_PATH%" /a-d /o-d`. On some Windows profiles, PowerShell `Get-ChildItem` and .NET directory APIs silently return empty for Downloads. If that happens, use `cmd /c dir` only. |
| **macOS / Linux** | `ls -lt "$BA_DOWNLOADS_PATH"` or the agent **Glob** tool. Do not use Windows `cmd`. |
| **Any OS** | Prefer **Glob** / **Read** over Shell when the tool can see the folder. |

### Scoped windows

| Flow | Window |
|---|---|
| `/debrief` with `@` attachment | Skip Downloads scan |
| `/debrief` finding newest transcript | ~3 days |
| Resume / `/workboard` / `/wrap` | ~7 days |

---

## Shell safety (all platforms)

1. Prefer **Read / Glob / MCP** over Shell for file inspection.
2. Avoid nested shells that expand variables before the inner command runs (especially nested `powershell -Command` with `$vars` on Windows).
3. Throwaway scripts: use the OS temp directory (e.g. `%TEMP%\cursor-agent-scratch` or `$TMPDIR`), never initiative blueprint folders.
4. Validate JSON with a small Python one-liner or a package script when needed.

---

## Multi-root workspaces

Multi-root Cursor workspaces are fine. Classify by **user intent**, not which folder is focused. Initiative state lives under `BA_INITIATIVES_ROOT` / `initiatives/{slug}/` (legacy `blueprints/{slug}/` still works if configured). Cross-initiative data lives in `~/.cursor/_workstream/`.

---

## Calendar feed (optional)

Populate `_workstream/calendar-feed.json` via:

- Windows: `references/sample-scripts/get-calendar.ps1` (Outlook COM)
- macOS: `references/sample-scripts/get-calendar.mac.sh` (Calendar.app)

Not required for `/workboard`.
