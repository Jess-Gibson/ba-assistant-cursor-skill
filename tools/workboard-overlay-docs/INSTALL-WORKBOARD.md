# BA Workboard overlay install

Upgrades **workboard capability only**. Personal data and the live canvas stay put until you choose otherwise.

| Untouched | Upgraded | Preview only |
|-----------|----------|--------------|
| `workboard.json` | Canvas **template** (not your live canvas) | `ba-workboard-overlay-preview.canvas.tsx` |
| `ba-actions.json` | `generate-workboard-canvas.py` | |
| `calendar-feed.json` | `workboard-procedure.md`, `workboard-format.md` | |
| `ba-profile.mdc`, `ba-assistant-config.mdc` | | |
| Existing `commands/workboard.md` (kept; a `.package` copy is written for comparison) | | |

---

## What to send a friend

1. `dist/ba-workboard-overlay.zip`
2. The prompt in `CURSOR-INSTALL-PROMPT.md` (paste into Cursor after unzip)

They should **not** run a full BA Assistant reinstall.

---

## Before you start

- BA Assistant is already installed (`~/.cursor/skills/ba-assistant/`).
- Python 3 is available (`py`, `python`, or `python3`).

---

## Steps

### 1. Unzip

Extract anywhere (e.g. `Downloads/ba-workboard-overlay/`). The folder must contain `tools/upgrade-workboard.py`.

### 2. Dry-run

**Windows:**

```powershell
cd path\to\extracted-folder
py tools\upgrade-workboard.py --package .
```

**macOS / Linux:**

```bash
cd path/to/extracted-folder
python3 tools/upgrade-workboard.py --package .
```

You should see `PROTECT` on JSON and profile, `KEEP` on your `/workboard` command, and `PREVIEW would write ...overlay-preview...`. Stop if anything says it will replace your data files.

### 3. Apply (still does not touch the live canvas)

```powershell
py tools\upgrade-workboard.py --package . --apply
```

Backup: `~/.cursor/ba-assistant-backups/workboard-overlay-YYYYMMDD-HHMMSS/`.

Open **`ba-workboard-overlay-preview.canvas.tsx`** in Cursor (same canvases folder as your current workboard). Compare. Keep using the old board until you like the preview.

### 4. Promote only when you are happy

In a new chat, ask the agent to regenerate the live canvas from your existing JSON, or run:

```powershell
py $env:USERPROFILE\.cursor\_workstream\generate-workboard-canvas.py --canvas "<your canvases folder>\ba-workboard.canvas.tsx"
```

---

## Optional flags (do not use unless you mean it)

| Flag | Effect |
|------|--------|
| `--replace-workboard-command` | Overwrite `commands/workboard.md` (backed up first) |
| `--replace-wrap` | Overwrite `commands/wrap.md` |
| `--no-preview-canvas` | Skip the preview file |

---

## If something looks wrong

Restore from `~/.cursor/ba-assistant-backups/workboard-overlay-*`. Your actions files were never written by this installer.
