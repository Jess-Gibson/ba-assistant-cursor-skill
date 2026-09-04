---
name: ba-install
description: >
  Install BA Assistant from the public package repo into the user's Cursor home.
  Use when the user asks to install BA Assistant, clone and install from a GitHub URL,
  "set up BA Assistant for me", or opens this package repo as a first-time BA.
  Copies skills, rules, hooks, and commands, then hands off to ba-setup.
disable-model-invocation: false
---

# BA Install — One-shot package install for non-developer BAs

This skill **installs files**. Personalisation is owned by `ba-setup`. Never treat
profile chat as a substitute for copying skills/rules/commands/hooks.

## When this skill runs

- User pastes the public repo URL and asks Cursor to install BA Assistant
- User opens this package repo and says they are brand new / want full setup
- User says "install BA Assistant", "set up the BA skill package", or similar
- Pre-flight in `/ba-assistant` or `/setup` finds `skills/ba-assistant/SKILL.md` missing

## Hard rules

1. **Install files first.** Do not start Phase 0 intake until install + setup complete.
2. **Never invent a skill tree from chat.** If the package is not on disk, clone or open it.
3. **Confirm overwrite** if `~/.cursor/skills/ba-assistant/SKILL.md` already exists and looks personalised (demo sheets, private initiative names). Offer backup / skip / replace.
4. **Default Cursor home** is `~/.cursor` (Windows: `%USERPROFILE%\.cursor`). Only use another home if the user explicitly set one for testing.
5. After install, **immediately run `ba-setup`** (read `sub-skills/ba-setup/SKILL.md`).

## Target public URL

Default package:

```text
https://github.com/Jess-Gibson/ba-assistant-cursor-skill
```

If the user supplies a different HTTPS git URL, use theirs.

---

## Flow

### Step 0 — Explain in plain language

Tell the BA (non-dev friendly):

> I will download the BA Assistant package, copy the skills into your Cursor
> folder, then walk you through a short personalisation wizard. You do not need
> to run terminal commands yourself unless something fails.

### Step 1 — Resolve package source

Pick the first that works:

1. **This workspace is already the package** — `SETUP.md` and `skills/ba-assistant/SKILL.md` exist at the workspace root. Use that path as `--package`.
2. **User gave a git URL** — clone to a temp folder.
   - Repo root: `https://github.com/Jess-Gibson/ba-assistant-cursor-skill.git`
   - Branch page: `https://github.com/Jess-Gibson/ba-assistant-cursor-skill/tree/<branch>`
     → clone with `git clone --branch <branch> --single-branch https://github.com/Jess-Gibson/ba-assistant-cursor-skill.git <temp>`
   - Windows example:
     `git clone --branch v11-first-run-install --single-branch https://github.com/Jess-Gibson/ba-assistant-cursor-skill.git "$env:TEMP\ba-cursor-skill"`
   - macOS/Linux example:
     `git clone --branch v11-first-run-install --single-branch https://github.com/Jess-Gibson/ba-assistant-cursor-skill.git /tmp/ba-cursor-skill`
3. **Neither** — AskQuestion: open the GitHub repo in browser / paste URL / point me at a local clone.

### Step 2 — Pre-flight existing install

Check:

- `~/.cursor/skills/ba-assistant/SKILL.md`
- `~/.cursor/rules/execution-router.mdc`
- `~/.cursor/commands/ba-assistant.md`

If skill exists: AskQuestion backup-and-replace / keep-and-upgrade / cancel.

### Step 3 — Run the installer

From the package root:

```text
# Dry-run first (show the user what will happen)
python tools/install-ba-assistant.py --package <package-root> --cursor-home <cursor-home> --dry-run

# Then apply after confirmation
python tools/install-ba-assistant.py --package <package-root> --cursor-home <cursor-home> --apply
```

Windows may use `py tools\install-ba-assistant.py ...` or `.\tools\install-ba-assistant.ps1 -Apply`.

Show the user a short summary: skills copied, N rules, N commands, hooks, `_workstream` seeded, `initiatives/` created.

### Step 4 — Verify

Confirm these exist after apply:

| Path | Required |
|------|----------|
| `~/.cursor/skills/ba-assistant/SKILL.md` | Yes |
| `~/.cursor/rules/execution-router.mdc` | Yes |
| `~/.cursor/commands/ba-assistant.md` | Yes |
| `~/.cursor/commands/setup.md` | Yes |
| `~/.cursor/hooks.json` | Yes |
| `~/.cursor/_workstream/ba-actions.json` | Yes |
| `~/.cursor/initiatives/` | Yes |
| `~/.cursor/.ba-assistant-installed.json` | Yes |

If any required path is missing: stop and fix. Do not pretend setup succeeded.

Optional: run `python tools/conformance-check.py --root <cursor-home>`.

### Step 5 — Hand off to personalisation

1. Tell the BA: "Files are installed. Next is a short personalisation wizard."
2. Read and follow `sub-skills/ba-setup/SKILL.md` **only** from the installed tree:
   `~/.cursor/skills/ba-assistant/sub-skills/ba-setup/SKILL.md`.
   Do not load setup skills from any other folder on the machine.
3. After ba-setup finishes, the guided first tasks include workboard, debrief,
   initiative, and MCP help.

### Step 6 — Restart note

If slash commands do not appear yet:

> Restart Cursor once (or open a brand-new chat). Then type `/ba-assistant`
> or `/setup`. You should see those commands in the `/` menu.

---

## Paste-this prompt (for README / Jess to share)

Agents may show this to the BA if they arrived without context:

```text
Install BA Assistant from https://github.com/Jess-Gibson/ba-assistant-cursor-skill
into my Cursor home. Copy skills, rules, hooks, and commands, verify the install,
then run the personalisation wizard. Default my initiatives folder to
~/.cursor/initiatives. When setup finishes, help me with MCP connections and
offer to set up my workboard or start my first initiative.
```

---

## Error handling

| Problem | Action |
|---------|--------|
| `git` missing | Ask them to install Git, or download ZIP of the repo and point you at the unzipped folder |
| `python` / `py` missing | Run the copy steps manually with file tools (Read/Write/Shell copy) matching `install-ba-assistant.py` behaviour |
| Permission denied on `.cursor` | Explain Cursor must be allowed to write to the user profile; retry |
| Existing personal install | Never overwrite without AskQuestion confirmation |

---

## What this skill does NOT do

- Does not create Jira/Confluence credentials
- Does not replace `ba-setup` personalisation
- Does not create initiative analysis folders beyond seeding `~/.cursor/initiatives/`
- Does not push or modify the public git remote
