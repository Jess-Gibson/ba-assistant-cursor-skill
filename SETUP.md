# BA Assistant for Cursor — Setup Guide

**Version 11** - see [CHANGELOG.md](CHANGELOG.md) and [README.md](README.md).

> Originally designed and built by Jess Gibson, Senior BA (2025–2026).
> Built iteratively across real BA initiatives using agent-assisted development.

---

## Fastest path for BAs (recommended)

You do **not** need to be a developer. Open Cursor, start a new chat, and paste:

```text
Install BA Assistant from https://github.com/Jess-Gibson/ba-assistant-cursor-skill
into my Cursor home. Copy skills, rules, hooks, and commands, verify the install,
then run the personalisation wizard. Default my initiatives folder to
~/.cursor/initiatives. When setup finishes, help me with MCP / Runlayer
connections and offer to set up my workboard or start my first initiative.
```

Cursor should:

1. Clone or open the package
2. Copy skills, rules, hooks, and commands into your Cursor home (`~/.cursor`)
3. Create `~/.cursor/initiatives` and seed `_workstream`
4. Run the personalisation wizard (name, role, Jira/Confluence, output depth)
5. Offer first tasks: workboard, meeting debrief, first initiative, or MCP help

If Cursor asks to run terminal commands or the install script, approve them.
If slash commands are missing afterwards, restart Cursor once.

### Alternative: open this repo first

1. Clone or download this repository
2. Open the folder in Cursor
3. Paste: `I'm brand new — install BA Assistant and walk me through setup`
4. Follow the assistant (it reads `AGENTS.md` + `ba-install` + `ba-setup`)

---

## What "installed" means

After a successful install you must have:

| Path | Purpose |
|------|---------|
| `~/.cursor/skills/ba-assistant/SKILL.md` | Main skill |
| `~/.cursor/rules/execution-router.mdc` | Routing |
| `~/.cursor/commands/ba-assistant.md` | Slash entry |
| `~/.cursor/hooks.json` | Hooks |
| `~/.cursor/_workstream/` | Workboard + BA actions |
| `~/.cursor/initiatives/` | Default initiative folders |
| `~/.cursor/rules/ba-assistant-config.mdc` | Your personalisation (after wizard) |

A lone `ba-profile.mdc` from a chat wizard is **not** a full install.

---

## Manual install (if you prefer scripts)

### Prerequisites

1. **Cursor IDE**
2. Optional later: Jira / Confluence MCP (or Runlayer connectors)
3. A workspace where you do BA work (not required for install itself)

### One-command installer

From this repo:

```bash
# Dry-run
python tools/install-ba-assistant.py --dry-run

# Apply
python tools/install-ba-assistant.py --apply
```

Windows:

```powershell
.\tools\install-ba-assistant.ps1
.\tools\install-ba-assistant.ps1 -Apply
```

macOS / Linux:

```bash
./tools/install-ba-assistant.sh --apply
```

Then in a new Cursor chat: `/setup` (or `/ba-assistant`).

### Already installed? Upgrade

```bash
python tools/upgrade-ba-assistant.py --package /path/to/ba-assistant-cursor-skill
python tools/upgrade-ba-assistant.py --package /path/to/ba-assistant-cursor-skill --apply
```

---

## Configuring MCP / Runlayer integrations

BA Assistant works without connectors, but mail actions, calendar, Jira,
Confluence, and company search need them. Prefer **Runlayer-governed** servers.

### MYOB (recommended)

1. Open **[Runlayer servers](https://myob.runlayer.com/servers)** and sign in with SSO
2. Search for what you need, for example:
   - `Glean` (company search; often mail/meetings too)
   - `Microsoft Outlook` / `Microsoft Outlook Calendar`
   - `Atlassian - Jira` / `Atlassian - Confluence`
3. Open the server → **Add to client** → Cursor
4. In Cursor: **Settings → Tools & MCP** → Authenticate / enable
5. **Start a new chat**, then run `/setup` and choose Context Bootstrap

Prefer **Glean via Runlayer**. Do not install a standalone unmanaged Glean MCP
(older Security notes about “Glean MCP not approved” refer to that unmanaged path).

Do not paste API tokens into chat. Do not store secrets in initiative files.

Full cold-start procedure: `skills/ba-assistant/references/context-bootstrap.md`.

---

## Verify Installation

### Structural check

```bash
python3 tools/conformance-check.py --root ~/.cursor
# Windows: py tools\conformance-check.py --root $env:USERPROFILE\.cursor
```

Also confirm `~/.cursor/skills/ba-assistant/SKILL.md` exists.

### Behavioural check (new chat)

1. `/ba-assistant` → install preflight if needed → setup if needed → guided first tasks
2. Slash menu includes `ba-assistant`, `setup`, `install-ba-assistant`, `debrief`, `workboard`
3. `/workboard` runs without error (after Context Bootstrap it should show real actions/initiatives when the BA opted in)
4. Name/role use AskQuestion (free-text name; role chips). Paths default without CLI tokens.
5. Setup offers Runlayer connector help, then “pull in starting work” for the workboard.
6. No calendar-hook script question; no Claude extension upsell.

---

## Defaults

| Setting | Default |
|---------|---------|
| Initiatives root | `~/.cursor/initiatives` (`BA_INITIATIVES_ROOT`) |
| Downloads | `~/Downloads` (`BA_DOWNLOADS_PATH`) |
| Personalisation file | `~/.cursor/rules/ba-assistant-config.mdc` |
| Persona rule | `~/.cursor/rules/ba-profile.mdc` (package; not overwritten by wizard) |

Legacy `blueprints/` folders still work if you point `BA_INITIATIVES_ROOT` there.

---

## Quick Start after setup

1. Open a BA workspace
2. `/workboard` or "Start a new initiative called [Name]"
3. Or attach a permitted Teams transcript and run `/debrief`

### Key commands

| Command | What it does |
|---------|-------------|
| `/install-ba-assistant` | Install or repair package files |
| `/ba-assistant` | Start BA Assistant |
| `/setup` | Personalisation wizard |
| `/workboard` | Cross-initiative priorities |
| `/debrief` | Meeting transcript → tracker updates |
| `/next` | Top 3 next actions |
| `/status` | Full current state |
| `/wrap` | End-of-session closeout |

---

## Folder Structure (after install)

```
~/.cursor/
  skills/ba-assistant/
  skills/miro-board-analysis/   (optional)
  commands/
  rules/
    ba-profile.mdc              (persona)
    ba-assistant-config.mdc     (your wizard output)
    execution-router.mdc
    ...
  hooks/ + hooks.json
  _workstream/
  initiatives/                  (default initiative root)
  .ba-assistant-installed.json
```

---

## Updating

Prefer `tools/upgrade-ba-assistant.py --apply`, or ask Cursor:

```text
Upgrade my BA Assistant install from https://github.com/Jess-Gibson/ba-assistant-cursor-skill
without overwriting my ba-assistant-config.mdc
```
