# BA Assistant for Cursor — Setup Guide

**Version 10** — see [CHANGELOG.md](CHANGELOG.md) and [README.md](README.md).

> Originally designed and built by Jess Gibson, Senior BA (2025–2026).
> Built iteratively across real BA initiatives using agent-assisted development.

---

## Prerequisites

1. **Cursor IDE** — with Canvas support enabled (for the Project Canvas dashboard)
2. **MCP servers** — at minimum, Jira and Confluence MCPs pointing to your org's Atlassian instance
3. **A workspace** — any Cursor workspace where you do BA work

### Optional MCPs (BA Assistant degrades gracefully without these)

| MCP | Enables |
|-----|---------|
| Miro MCP | Workshop board creation, DRAID table sync, board analysis |
| Glean MCP | Internal doc/code search during intake and current state assessment |
| Warehouse / SQL MCP | Quantitative validation via ba-data-investigation |

---

## Already installed? Upgrade to Version 10

Do **not** blindly overwrite `ba-profile.mdc` or `_workstream/`. Use the upgrade script:

```bash
python tools/upgrade-ba-assistant.py --package /path/to/ba-assistant-cursor-skill          # dry-run
python tools/upgrade-ba-assistant.py --package /path/to/ba-assistant-cursor-skill --apply  # apply
```

Windows: `.\tools\upgrade-ba-assistant.ps1 -PackageRoot "C:\path\to\repo" -Apply`  
macOS/Linux: `./tools/upgrade-ba-assistant.sh /path/to/repo --apply`

This refreshes skills/rules/commands, removes obsolete `ba-workboard`, migrates `personal_tasks[]` → `ba-actions.json` when safe, and leaves personalised profile + workstream data intact.

---

## Installation (new)

### Step 1 — Install the BA Assistant skill

Clone this repo and copy the skill into your Cursor skills directory:

```bash
# macOS / Linux
git clone https://github.com/Jess-Gibson/ba-assistant-cursor-skill.git /tmp/ba-cursor-skill
cp -r /tmp/ba-cursor-skill/skills/ba-assistant ~/.cursor/skills/ba-assistant

# Windows (PowerShell)
git clone https://github.com/Jess-Gibson/ba-assistant-cursor-skill.git "$env:TEMP\ba-cursor-skill"
Copy-Item "$env:TEMP\ba-cursor-skill\skills\ba-assistant" "$env:USERPROFILE\.cursor\skills\ba-assistant" -Recurse
```

This creates `~/.cursor/skills/ba-assistant/` with the full skill tree.

### Step 2 — Install the rules

Copy the rules from the repo into your Cursor rules directory:

```bash
# macOS / Linux — copy from the cloned temp location
cp /tmp/ba-cursor-skill/rules/*.mdc ~/.cursor/rules/

# Windows (PowerShell)
Copy-Item "$env:TEMP\ba-cursor-skill\rules\*.mdc" "$env:USERPROFILE\.cursor\rules\"
```

**Important:** Review each rule before copying. If you already have rules with the same names, merge rather than overwrite. Never overwrite a personalised `ba-profile.mdc` with the template unless you intend to re-run setup.

### Step 3 — Install the hooks

Copy the hooks configuration and scripts:

```bash
# macOS / Linux
cp /tmp/ba-cursor-skill/hooks/hooks.json ~/.cursor/hooks.json
mkdir -p ~/.cursor/hooks
cp /tmp/ba-cursor-skill/hooks/*.{sh,py} ~/.cursor/hooks/
chmod +x ~/.cursor/hooks/*.sh

# Windows (PowerShell)
Copy-Item "$env:TEMP\ba-cursor-skill\hooks\hooks.json" "$env:USERPROFILE\.cursor\hooks.json"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\hooks"
Copy-Item "$env:TEMP\ba-cursor-skill\hooks\*.ps1" "$env:USERPROFILE\.cursor\hooks\"
Copy-Item "$env:TEMP\ba-cursor-skill\hooks\*.py" "$env:USERPROFILE\.cursor\hooks\"
```

**Important:** If you already have a `hooks.json`, merge the entries rather than replacing the file.

**Windows Python:** The hook scripts call `python`. If `python` is not on your PATH, either add it or edit `hooks.json` to use `py` instead (the Windows Python launcher).

### Step 3b — Install slash commands

```bash
# macOS / Linux
mkdir -p ~/.cursor/commands
cp /tmp/ba-cursor-skill/commands/*.md ~/.cursor/commands/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\commands"
Copy-Item "$env:TEMP\ba-cursor-skill\commands\*.md" "$env:USERPROFILE\.cursor\commands\"
```

### Step 4 — Configure your environment

1. **Set your downloads path** (for meeting transcript auto-processing):
   - Set the environment variable `BA_DOWNLOADS_PATH` to your downloads folder
   - macOS/Linux: `export BA_DOWNLOADS_PATH="$HOME/Downloads"`
   - Windows: `$env:BA_DOWNLOADS_PATH = "$env:USERPROFILE\Downloads"`

2. **Set your initiative folder root** (where project folders are created):
   - Set `BA_INITIATIVES_ROOT` to your preferred path
   - Example: `export BA_INITIATIVES_ROOT="$HOME/ba-initiatives"`
   - If not set, the BA Assistant will search for `blueprints/Project*/`, `Initiatives/`, or `projects/` patterns

### Step 5 — Run the first-time setup wizard

The BA Assistant includes an interactive setup wizard that handles personalization for you.

Start a new Cursor chat and type: `run BA assistant`

If `ba-profile.mdc` still contains placeholder values (`[Your Name]`, `[your-instance]`), the assistant will automatically launch the **ba-setup wizard** which will:
- Ask for your name and role
- Configure your Jira instance and project key
- Configure your Confluence space
- Check your MCP connections
- Write a personalized `ba-profile.mdc` to your `~/.cursor/rules/` directory

You can also run the wizard manually by typing: `run the BA setup wizard`

See `CUSTOMIZATION.md` for manual overrides if you prefer to configure by hand.

### Step 6 — Install companion skills (optional)

The BA Assistant can invoke these optional companion skills if they are installed:

| Skill | Purpose | Install from |
|-------|---------|-------------|
| `publish-docs-to-confluence` | Publish status pages and documents to Confluence | See `skills/publish-docs-to-confluence/README.md` for setup |
| `miro-board-analysis` | Workshop board creation and analysis | See `skills/miro-board-analysis/README.md` for setup |

---

## Verify Installation

### Structural check (run first)

From the cloned repo:

```bash
python3 tools/conformance-check.py --root ~/.cursor
# Windows: py tools\conformance-check.py --root $env:USERPROFILE\.cursor
```

Expect **0 FAIL, 0 WARN, 6 PASS**.

### Behavioural check (fresh Cursor chat, model = Auto)

1. **Welcome panel** — type `run BA assistant` → grouped panel (6-2-12-3-1), 24 skills, draft-depth question
2. **AskQuestion judgement** — ask for a requirement verbatim → text only, no trailing AskQuestion; at a real fork → clickable options
3. **Slash menu** — type `/` → status, canvas, handover, wrap, validate-state, retro, metrics, reanchor appear
4. **`/status`** — triple-output flow runs (grid + tracker + canvas refresh)
5. **`/reanchor`** — re-reads SKILL + state files, ends with AskQuestion
6. **`/metrics`** — loads `metrics.md` + `canvas-data-model` only (not the full canvas generation spec)

If the welcome panel does not appear, check:
- `~/.cursor/skills/ba-assistant/SKILL.md` exists
- `~/.cursor/rules/execution-router.mdc` exists (the always-on router — it replaced the old `ba-assistant-default` and `session-start-protocol` rules)
- Restart Cursor if rules were just added

---

## Folder Structure

After installation, your `.cursor` directory should look like:

```
~/.cursor/
  skills/
    ba-assistant/
      SKILL.md
      instructions.md
      hook-contracts.md
      slash-commands-ux.md
      learnings.md              (starts empty — grows with your initiatives)
      BA_Assistant_User_Guide.md
      references/
        canvas-data-model.md
        raid-format.md
        requirement-format.md
        status-page-format.md
        user-story-format.md
        visual-output-format.md
        jira-ticket-format.md
        templates/
          flowchart.html
      sub-skills/
        ba-anti-pattern-detector/
        ba-change-strategy/
        ba-context-capture/
        ba-data-investigation/
        ba-workboard/              (cross-initiative dashboard — /workboard)
        ... (25 active skills total)
    publish-docs-to-confluence/  (optional)
    miro-board-analysis/         (optional)
  commands/
    status.md, canvas.md, handover.md, wrap.md, workboard.md, todo.md, ...
  rules/
    ba-profile.mdc             (generic — customize with your name or use the setup wizard)
    execution-router.mdc       (always-on router — turn classification + skill routing)
    skills-routing.mdc
    sync-gates.mdc
    agent-behavior.mdc
    agent-behavior-extended.mdc
    ba-delivery-process.mdc
    critical-gates.mdc
    todo-quick-capture.mdc     (optional — feeds ba-workboard's personal task list)
  hooks/
    session-init.ps1 / .sh
    snapshot-before-compact.ps1 / .sh
    jira-dor-gate.py, shared-repo-guard.py, inject-state-reminder.py (+ .sh/.ps1 twins)
  hooks.json
  _workstream/                 (created on first /workboard or /todo — cross-initiative data)
    workboard.json
    calendar-feed.json          (optional — your own calendar script populates this)
```

---

## Quick Start

1. Open a Cursor workspace
2. Start a new chat
3. Say: "Start a new initiative called [Your Initiative Name]"
4. The BA Assistant will scaffold a project folder and begin Phase 0 intake
5. Follow the guided intake conversation — the assistant will ask you questions, not the other way around

### Key commands

| Command | What it does |
|---------|-------------|
| `/next` | Top 3 next actions by urgency |
| `/status` | Full current state with canvas and HTML snapshot |
| `/canvas` | Generate/refresh the interactive project dashboard |
| `/report` | Full structured deep-dive report |
| `/validate-state` | Mid-session drift check (read-only) |
| `/wrap` | End-of-session closeout — promotes items, refreshes workboard |
| `/fast-track` | Enable condensed BA flow for time-critical initiatives |
| `/metrics` | Show BA quality metrics for the initiative |
| `/retro` | Trigger a retrospective |
| `/reanchor` | Re-read state files when the assistant drifts in long threads |

---

## Updating

Pull the latest version:

```bash
cd ~/.cursor/skills/ba-assistant
git pull
```

Check `CUSTOMIZATION.md` for any new customization points in the update.
