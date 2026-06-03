# BA Assistant for Cursor — Agent Guide

This repository is a **Cursor skill package** for Business Analysts. When a user opens this workspace, your job is to help them install, configure, and use the BA Assistant.

## On first conversation

If the user has just cloned this repo or opened it for the first time:

1. **Read `SETUP.md`** — this is the step-by-step installation guide
2. **Ask the user what stage they're at** using AskQuestion:
   - "I'm brand new — walk me through the full setup"
   - "I've already installed — help me customize"
   - "I'm just browsing the repo to understand what this is"
3. **Guide them through setup interactively** — don't just point them at the docs. Actually help them:
   - Check if they have the skill installed at `~/.cursor/skills/ba-assistant/`
   - Check if the rules are copied to `~/.cursor/rules/`
   - Check if hooks are installed
   - Help them configure environment variables
   - Help them customize `ba-profile.mdc` with their name and preferences
   - Help them set up Jira/Confluence MCP connections

## Installation walkthrough

When guiding a new user through setup:

### Step 1: Skill installation
The user needs to copy or symlink the `skills/ba-assistant/` folder to `~/.cursor/skills/ba-assistant/`. On Windows this is `%USERPROFILE%\.cursor\skills\ba-assistant\`.

Check if it exists:
- Windows: `Test-Path "$env:USERPROFILE\.cursor\skills\ba-assistant\SKILL.md"`
- macOS/Linux: `test -f ~/.cursor/skills/ba-assistant/SKILL.md`

### Step 2: Rules installation
Copy all `.mdc` files from `rules/` to `~/.cursor/rules/`. Warn the user if they already have files with the same names — merge rather than overwrite.

### Step 3: Hooks installation
- Copy `hooks/hooks.json` to `~/.cursor/hooks.json` (merge if exists)
- Copy hook scripts to `~/.cursor/hooks/`
- Windows users need the `.ps1` files; macOS/Linux users need the `.sh` files

### Step 4: Environment variables
Help them set:
- `BA_DOWNLOADS_PATH` — their downloads folder (for meeting transcript auto-processing)
- `BA_INITIATIVES_ROOT` — where project folders will be created (or they can use the `blueprints/` folder in their workspace)

### Step 5: Customize ba-profile.mdc
Read `CUSTOMIZATION.md` for the full list of what to personalize. The most important changes:
- Replace the generic title with their name and role
- Adjust the status page format for their org
- Configure the Delivery Model section (optional, for cohort-based work)

### Step 6: MCP servers
The user needs at minimum:
- A Jira MCP server pointing to their Atlassian instance
- A Confluence MCP server pointing to their Atlassian instance

Optional: Miro MCP, Glean MCP, Snowflake MCP.

### Step 7: Verify
Have the user open a different workspace (not this repo) and type "run BA assistant" in a new chat. They should see the welcome panel.

## If the BA Assistant is already installed

If the user says they've installed and want to start using it:
- Direct them to open their BA workspace (not this repo)
- They can start with "Start a new initiative called [name]"
- Or resume an existing one with "continue" or "resume [initiative name]"

## Key files in this repo

| File | Purpose |
|------|---------|
| `SETUP.md` | Step-by-step installation guide |
| `CUSTOMIZATION.md` | What to personalize after installation |
| `skills/ba-assistant/SKILL.md` | The main skill orchestrator |
| `skills/ba-assistant/BA_Assistant_User_Guide.md` | End-user documentation |
| `rules/ba-profile.mdc` | The BA profile rule to customize |
| `blueprints/` | Starter project folder convention |

## What this repo is NOT

- This is NOT a workspace for doing BA work — it's a package to install into your actual workspace
- Do not create initiatives or projects in this repo
- After installation, open your real BA workspace and use the BA Assistant there
