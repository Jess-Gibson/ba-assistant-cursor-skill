# BA Assistant for Cursor — Agent Guide

This repository is a **Cursor skill package** for Business Analysts. When a user
opens this workspace, or pastes the install prompt, your job is to **install the
files**, then run the personalisation wizard. Do not only chat about setup.

## Paste-this prompt (share with new BAs)

```text
Install BA Assistant from https://github.com/Jess-Gibson/ba-assistant-cursor-skill
into my Cursor home. Copy skills, rules, hooks, and commands, verify the install,
then run the personalisation wizard. Default my initiatives folder to
~/.cursor/initiatives. When setup finishes, help me with MCP / Runlayer
connections and offer to set up my workboard or start my first initiative.
```

## On first conversation

1. Read `skills/ba-assistant/sub-skills/ba-install/SKILL.md` and follow it.
2. Run `tools/install-ba-assistant.py --dry-run`, then `--apply` after confirmation.
3. Verify `~/.cursor/skills/ba-assistant/SKILL.md` exists.
4. Immediately run `skills/ba-assistant/sub-skills/ba-setup/SKILL.md`
   (from the **installed** tree after copy).
5. Offer guided next tasks: workboard, debrief, first initiative, MCP help.

If the user is only browsing, AskQuestion once:
- "I'm brand new — install and set me up"
- "I've already installed — help me customise"
- "I'm just browsing the repo"

## Non-negotiables

- **Install is file copy**, not profile chat. Missing skills/rules/commands = not installed.
- **Default initiatives root** is `~/.cursor/initiatives` (not `blueprints`).
- **Name / URLs / keys:** use AskQuestion free-text fields (type below). Never invent chips like "Enter my name (Recommended)" that capture nothing.
- **Do not overwrite** a personalised install without confirmation.
- Read skills **only** from `~/.cursor/skills/ba-assistant/`. Do not search other skill folders on the machine.

## MCP / Runlayer

After personalisation, help the BA open **Cursor Settings → Tools & MCP** and
enable organisation-approved Jira, Confluence, and optional Runlayer connectors.
Never ask them to paste API tokens into chat.

## After install

Ask them to open a normal BA workspace (not this package repo) and use:

- `/ba-assistant` — start
- `/setup` — reconfigure
- `/workboard` — cross-initiative priorities
- `/debrief` — meeting transcript
- "Start a new initiative called [name]"

## Key files

| File | Purpose |
|------|---------|
| `SETUP.md` | Human install guide |
| `tools/install-ba-assistant.py` | One-command file installer |
| `skills/ba-assistant/sub-skills/ba-install/SKILL.md` | Agent install flow |
| `skills/ba-assistant/sub-skills/ba-setup/SKILL.md` | Personalisation wizard |
| `rules/ba-profile.mdc` | Always-on persona (do not overwrite with wizard YAML) |
| `skills/ba-assistant/ba-profile.template.mdc` | Written to `ba-assistant-config.mdc` |

## What this repo is NOT

- Not a place to run live initiatives
- After installation, use a real BA workspace and `~/.cursor/initiatives/`
