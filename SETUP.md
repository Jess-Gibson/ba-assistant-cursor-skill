# BA Assistant for Cursor — Setup Guide

> Originally designed and built by Jess Gibson, Senior BA at MYOB (2025–2026).
> Architecture: 21 active sub-skills, 7 reference standards, hook-based orchestration.
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
| Snowflake MCP | Quantitative validation and post-launch metrics via pm-data-analyst |

---

## Installation

### Step 1 — Install the BA Assistant skill

Clone this repo into your Cursor skills directory:

```bash
# macOS / Linux
cd ~/.cursor/skills
git clone https://github.com/Jess-Gibson/ba-assistant-cursor-skill.git ba-assistant

# Windows (PowerShell)
cd "$env:USERPROFILE\.cursor\skills"
git clone https://github.com/Jess-Gibson/ba-assistant-cursor-skill.git ba-assistant
```

This creates `~/.cursor/skills/ba-assistant/` with the full skill tree.

### Step 2 — Install the rules

Copy the rules from the `rules/` folder in this repo into your Cursor rules directory:

```bash
# macOS / Linux
cp rules/*.mdc ~/.cursor/rules/

# Windows (PowerShell)
Copy-Item rules\*.mdc "$env:USERPROFILE\.cursor\rules\"
```

**Important:** Review each rule before copying. If you already have rules with the same names, merge rather than overwrite.

### Step 3 — Install the hooks

Copy the hooks configuration and scripts:

```bash
# macOS / Linux
cp hooks/hooks.json ~/.cursor/hooks.json
cp hooks/*.sh ~/.cursor/hooks/
cp hooks/*.ps1 ~/.cursor/hooks/
chmod +x ~/.cursor/hooks/*.sh

# Windows (PowerShell)
Copy-Item hooks\hooks.json "$env:USERPROFILE\.cursor\hooks.json"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\hooks"
Copy-Item hooks\*.ps1 "$env:USERPROFILE\.cursor\hooks\"
```

**Important:** If you already have a `hooks.json`, merge the entries rather than replacing the file.

### Step 4 — Configure your environment

1. **Set your downloads path** (for meeting transcript auto-processing):
   - Set the environment variable `BA_DOWNLOADS_PATH` to your downloads folder
   - macOS/Linux: `export BA_DOWNLOADS_PATH="$HOME/Downloads"`
   - Windows: `$env:BA_DOWNLOADS_PATH = "$env:USERPROFILE\Downloads"`

2. **Set your initiative folder root** (where project folders are created):
   - Set `BA_INITIATIVES_ROOT` to your preferred path
   - Example: `export BA_INITIATIVES_ROOT="$HOME/ba-initiatives"`
   - If not set, the BA Assistant will search for `blueprints/Project*/`, `Initiatives/`, or `projects/` patterns

### Step 5 — Customize your BA profile

Edit `rules/ba-profile.mdc` to personalize:
- Your name and role
- Your preferred communication style
- Any industry-specific or org-specific status page sections

See `CUSTOMIZATION.md` for detailed guidance on what to personalize.

### Step 6 — Install companion skills (optional)

The BA Assistant can invoke these optional companion skills if they are installed:

| Skill | Purpose | Install from |
|-------|---------|-------------|
| `publish-docs-to-confluence` | Publish status pages and documents to Confluence | See `skills/publish-docs-to-confluence/README.md` for setup |
| `miro-board-analysis` | Workshop board creation and analysis | See `skills/miro-board-analysis/README.md` for setup |

---

## Verify Installation

Start a new Cursor chat and type: "run BA assistant"

You should see:
1. The BA Assistant welcome panel with 21 active skills listed
2. A draft depth preference question
3. A prompt asking what you're working on

If the welcome panel does not appear, check:
- The `ba-assistant/SKILL.md` file exists at `~/.cursor/skills/ba-assistant/SKILL.md`
- The `ba-assistant-default.mdc` rule exists in `~/.cursor/rules/`
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
        ... (21 active + 7 redirect stubs)
    publish-docs-to-confluence/  (optional)
    miro-board-analysis/         (optional)
  rules/
    ba-profile.mdc
    ba-assistant-default.mdc
    ba-delivery-process.mdc
    execution-router.mdc
    session-start-protocol.mdc
    skills-routing.mdc
    agent-behavior.mdc
    chat-profiles.mdc
    workspace-operations.mdc
    read-claude-first.mdc
  hooks/
    session-init.ps1  (Windows)
    session-init.sh   (macOS/Linux)
    snapshot-before-compact.ps1 (Windows)
    snapshot-before-compact.sh  (macOS/Linux)
  hooks.json
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
