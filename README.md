# BA Assistant for Cursor

**Version 16** - see [CHANGELOG.md](CHANGELOG.md).

A comprehensive Business Analysis assistant built as a Cursor skill. Designed to support BAs through the full initiative lifecycle — from intake and discovery through delivery, playback, and retrospective.

> Built by Jess Gibson.
> Built iteratively across real BA initiatives using agent-assisted development.

---

## What it does

The BA Assistant is an AI-powered BA thinking partner that runs inside [Cursor](https://cursor.com). It provides:

- **Guided intake** — structured Phase 0 intake with multi-source context gathering (Confluence, Jira, Glean, web)
- **Living tracker** — automatic RAID tracking across workstreams
- **Feature slicing before stories** — enforced sequencing before delivery definition
- **Interactive project canvas** — 8-tab dashboard with workstream grid, RAID, metrics, and timeline
- **Cross-initiative workboard** — portable interactive `/workboard` canvas generated from each BA's own phase, blockers, next actions, **BA actions**, and today's meetings. Pairs with `/todo` to `ba-actions.json`
- **Meeting debrief** — transcripts into decisions, actions, risks, and requirement changes
- **Workshop design** — facilitation templates from kickoff through change management
- **Anti-pattern detection** — premature solutioning, scope creep, missing analysis
- **Data investigation** — evidence before confidence scores / priorities / risk ratings
- **Dev handover** — gated publish of confirmed analysis to the delivery repo
- **Retrospectives** — structured learning capture
- **Confluence/Jira integration** — status publishing and ticket sync via MCP
- **First-run onboarding** — paste the install prompt (or `/install-ba-assistant`), then `/setup` with guided workboard, debrief, initiative, and MCP help
- **Stakeholder Markdown readability** — dark-mode-safe comms and enablement packs
- **Default initiatives root** — `~/.cursor/initiatives`

### Sub-skills (orchestrated)

| Phase | Skills |
|-------|--------|
| Intake | New Initiative (scaffolding + one-time workspace context), Intake Reviewer, Install (one-shot package copy), Setup (personalisation wizard) |
| Kickoff | Workshop Design |
| Discovery | Current State Assessment, Discovery & Requirements, Requirements Interrogator (incl. Mode 4 HLR review) |
| Slicing | Feature Slicing & Sequencing |
| Solution | Solution Shaping |
| Delivery | Story Writing, Jira Sync, Dev Handover |
| Playback | Playback & Enablement |
| Evaluation | Solution Evaluation, Retrospective & Learning |
| Change | Change Strategy |
| Closeout | Initiative Closeout (`/close`, gated one-way archive) |
| Cross-cutting | Risk & Tracker, Stakeholder Strategy, Sponsor Engagement, Anti-Pattern Detector, Context Capture, Meeting Debrief, Project Canvas, State Validator, Data Investigation, Commitment Scan (end-of-day reconciliation) |

**Workboard** is an **inline Run procedure** (`references/workboard-procedure.md`), not a sub-skill folder.

The table above uses friendly phase names as a quick skills index. Day-to-day routing uses `skills/ba-assistant/references/activity-map.md`; the slim `skills/ba-assistant/SKILL.md` is the orchestrator. `skills/ba-assistant/references/workstreams.md` is an optional M0–M8 glossary for legacy terminology and cross-reference.

### Optional companion skills

- `skills/miro-board-analysis/` — workshop boards, kickoff templates, debrief boards, spike cards, Pass 2b placement rules. Optional Miro MCP.
- `skills/publish-docs-to-confluence/` — publish or update Confluence pages from local Markdown, fix broken wiki links, attach assets, link Jira issues. Optional Confluence-capable Atlassian MCP connector.

### Key commands

| Command | What it does |
|---------|-------------|
| `/next` | Top 3 next actions by urgency |
| `/status` | Full current state in chat, with quality metrics (offers `/canvas`) |
| `/canvas` | Render the interactive project dashboard and HTML snapshot from `status-data.json` |
| `/report` | Full structured deep-dive report |
| `/validate-state` | Write this chat's captures into the initiative files and `ba-actions` |
| `/wrap` | Chat-scoped checkpoint — capture, promote, sync BA actions changed in this chat (workboard refresh is `/workboard end-of-day`) |
| `/workboard` | Cross-initiative dashboard |
| `/todo` | Quick-capture into `ba-actions.json` |
| `/fast-track` | Condensed BA flow for time-critical initiatives |
| `/metrics` | BA quality metrics |
| `/retro` | Retrospective |
| `/reanchor` | Re-read state files when the assistant drifts |
| `/handover` | Publish confirmed analysis to the delivery repo |
| `/close` | Archive a finished initiative (closure retro, file audit, move to `archive/`) |
| `/undo` | Put an initiative's files back as they were before a change (local history, nothing leaves the machine) |
| `/ba-assistant` | Start BA Assistant (runs setup wizard on first install) |
| `/install-ba-assistant` | Install or repair package files from the public repo |
| `/setup` | Re-run the first-run configuration wizard |
| `/debrief` | Process a meeting transcript into tracker updates |

---

## Quick start (new install)

**Non-developer BAs:** open Cursor and paste:

```text
Install BA Assistant from https://github.com/Jess-Gibson/ba-assistant-cursor-skill
into my Cursor home. Run tools/install-ba-assistant.py to install skills, rules,
hooks, and commands (do not copy hooks.json by hand), verify the install,
then run the personalisation wizard. Default my initiatives folder to
~/.cursor/initiatives. When setup finishes, help me with MCP / Runlayer
connections and offer to set up my workboard or start my first initiative.
```

See [SETUP.md](SETUP.md) and [AGENTS.md](AGENTS.md). Or from a clone:

```bash
python tools/install-ba-assistant.py --apply
```

Default initiative folders: `~/.cursor/initiatives`. After files are installed, `/setup` personalises the assistant.

---

## Upgrade from an older install

Preserves personalised `ba-profile.mdc` and `_workstream` data. Package files (skills, package rules, commands, hooks) are replaced with the new version. If you applied retro patches or edited those package files, use the merge tool instead and check `_workstream/local-skill-patches.md` for what you changed. Legacy data migrations (old `personal_tasks[]`, an old actions file) only run with `--migrate-legacy`. `--patch-profile` updates only the old `/wrap` and `/validate-state` rows in your profile.

**Edited skills or rules, or renamed things to your own names?** Use `tools/ba-merge-upgrade.py` instead. It backs up, stages, compares your install against the old and new versions, keeps your edits and naming, and deploys only what you approve. Walkthrough: [docs/PERSONALISED-UPGRADE.md](docs/PERSONALISED-UPGRADE.md).

```bash
# Dry-run first
python tools/upgrade-ba-assistant.py --package /path/to/ba-assistant-cursor-skill

# Apply
python tools/upgrade-ba-assistant.py --package /path/to/ba-assistant-cursor-skill --apply
```

Windows: `.\tools\upgrade-ba-assistant.ps1 -PackageRoot "C:\path\to\ba-assistant-cursor-skill" -Apply`  
macOS/Linux: `./tools/upgrade-ba-assistant.sh /path/to/ba-assistant-cursor-skill --apply`

---

## Calendar (optional)

| OS | Script |
|---|---|
| Windows + Outlook | `hooks/get-calendar.ps1` (installer copies it to `~/.cursor/hooks/`; supports `-DaysBehind`) |
| macOS + Calendar.app | `skills/ba-assistant/references/sample-scripts/get-calendar.mac.sh` |

Both write `_workstream/calendar-feed.json`. `/workboard` works without a calendar. The sample-scripts copy of the Windows script is a pointer only.

---

## Workboard overlay (upgrade without wiping personal data)

For BAs who already installed and customised BA Assistant: share `dist/ba-workboard-overlay.zip`.
It upgrades canvas template, generator, and procedure/format. It does **not** overwrite actions JSON, profile, live canvas, or (by default) `/workboard`. Apply writes a preview canvas first.

```powershell
py tools\upgrade-workboard.py --package .          # dry-run (Windows)
py tools\upgrade-workboard.py --package . --apply  # preview canvas, keep live board
```
```bash
python3 tools/upgrade-workboard.py --package .          # dry-run (Mac/Linux)
python3 tools/upgrade-workboard.py --package . --apply
```

See `tools/workboard-overlay-docs/INSTALL-WORKBOARD.md` and `CURSOR-INSTALL-PROMPT.md`.
Rebuild the zip after capability changes: `python3 tools/build-workboard-overlay-zip.py` (Windows: `py`).

---

## Repo layout

```
skills/ba-assistant/          # Orchestrator + sub-skills + references
skills/miro-board-analysis/   # Optional Miro companion
rules/                        # Always-on routing, sync gates, todo capture
commands/                     # Slash command stubs
tools/upgrade-ba-assistant.*  # Safe full upgrade
tools/upgrade-workboard.*     # Workboard capability overlay only
tests/run_all.py              # Package tests (repo only, not installed)
dist/ba-workboard-overlay.zip # Friend handoff package
VERSION                       # 15
CHANGELOG.md
SETUP.md
```

`_workstream/` is created under `~/.cursor/` on first use (not committed).

## Tests (for people changing this repo)

```
python3 tests/run_all.py      # Windows: py tests/run_all.py
```

Runs the Jira story preflight, hook, and package consistency checks. They are not installed and never run while a BA uses the assistant, so they cost no tokens in normal use.
