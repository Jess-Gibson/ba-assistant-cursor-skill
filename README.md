# BA Assistant for Cursor

**Version 10** — see [CHANGELOG.md](CHANGELOG.md).

A comprehensive Business Analysis assistant built as a Cursor skill. Designed to support BAs through the full initiative lifecycle — from intake and discovery through delivery, playback, and retrospective.

> Originally designed and built by Jess Gibson, Senior BA (2025–2026).
> Built iteratively across real BA initiatives using agent-assisted development.

---

## What it does

The BA Assistant is an AI-powered BA thinking partner that runs inside [Cursor](https://cursor.com). It provides:

- **Guided intake** — structured Phase 0 intake with multi-source context gathering (Confluence, Jira, Glean, web)
- **Living tracker** — automatic RAID tracking across workstreams
- **Feature slicing before stories** — enforced sequencing before delivery definition
- **Interactive project canvas** — 8-tab dashboard with workstream grid, RAID, metrics, and timeline
- **Cross-initiative workboard** — inline `/workboard` procedure (not a sub-skill): phase, blockers, next actions, **BA actions**, today's meetings. Pairs with `/todo` to `ba-actions.json`
- **Meeting debrief** — transcripts into decisions, actions, risks, and requirement changes
- **Workshop design** — facilitation templates from kickoff through change management
- **Anti-pattern detection** — premature solutioning, scope creep, missing analysis
- **Data investigation** — evidence before confidence scores / priorities / risk ratings
- **Dev handover** — gated publish of confirmed analysis to the delivery repo
- **Retrospectives** — structured learning capture
- **Confluence/Jira integration** — status publishing and ticket sync via MCP

### Sub-skills (orchestrated)

| Phase | Skills |
|-------|--------|
| Intake | Intake Reviewer, Setup (first-run wizard) |
| Kickoff | Workshop Design |
| Discovery | Current State Assessment, Discovery & Requirements, Requirements Interrogator (incl. Mode 4 HLR review) |
| Slicing | Feature Slicing & Sequencing |
| Solution | Solution Shaping |
| Delivery | Story Writing, Jira Sync, Dev Handover |
| Playback | Playback & Enablement |
| Evaluation | Solution Evaluation, Retrospective & Learning |
| Change | Change Strategy |
| Cross-cutting | Risk & Tracker, Stakeholder Strategy, Sponsor Engagement, Anti-Pattern Detector, Context Capture, Meeting Debrief, Project Canvas, State Validator, Data Investigation |

**Workboard** is an **inline Run procedure** (`references/workboard-procedure.md`), not a sub-skill folder.

### Optional companion skill: Miro board analysis

`skills/miro-board-analysis/` — workshop boards, kickoff templates, debrief boards, spike cards, Pass 2b placement rules. Optional Miro MCP.

### Key commands

| Command | What it does |
|---------|-------------|
| `/next` | Top 3 next actions by urgency |
| `/status` | Full current state with canvas and HTML snapshot |
| `/canvas` | Generate/refresh the interactive project dashboard |
| `/report` | Full structured deep-dive report |
| `/validate-state` | Mid-session drift check (read-only) |
| `/wrap` | End-of-session closeout — promote, sync BA actions, refresh workboard |
| `/workboard` | Cross-initiative dashboard |
| `/todo` | Quick-capture into `ba-actions.json` |
| `/fast-track` | Condensed BA flow for time-critical initiatives |
| `/metrics` | BA quality metrics |
| `/retro` | Retrospective |
| `/reanchor` | Re-read state files when the assistant drifts |
| `/handover` | Publish confirmed analysis to the delivery repo |

---

## Quick start (new install)

See [SETUP.md](SETUP.md) for full steps (skills + rules + hooks + commands).

```bash
# macOS / Linux
git clone https://github.com/Jess-Gibson/ba-assistant-cursor-skill.git /tmp/ba-cursor-skill
cp -r /tmp/ba-cursor-skill/skills/ba-assistant ~/.cursor/skills/ba-assistant
cp /tmp/ba-cursor-skill/rules/*.mdc ~/.cursor/rules/

# Windows (PowerShell)
git clone https://github.com/Jess-Gibson/ba-assistant-cursor-skill.git "$env:TEMP\ba-cursor-skill"
Copy-Item "$env:TEMP\ba-cursor-skill\skills\ba-assistant" "$env:USERPROFILE\.cursor\skills\ba-assistant" -Recurse
Copy-Item "$env:TEMP\ba-cursor-skill\rules\*.mdc" "$env:USERPROFILE\.cursor\rules\"
```

First chat runs **ba-setup** (seeds `_workstream/`, optional OS calendar sample).

---

## Upgrade from an older install (Version 10)

Preserves personalised `ba-profile.mdc` and `_workstream` data. Migrates legacy `personal_tasks[]` into `ba-actions.json` when safe.

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

| OS | Sample |
|---|---|
| Windows + Outlook | `skills/ba-assistant/references/sample-scripts/get-calendar.ps1` |
| macOS + Calendar.app | `skills/ba-assistant/references/sample-scripts/get-calendar.mac.sh` |

Both write `_workstream/calendar-feed.json`. `/workboard` works without a calendar.

---

## Repo layout

```
skills/ba-assistant/          # Orchestrator + sub-skills + references
skills/miro-board-analysis/   # Optional Miro companion
rules/                        # Always-on routing, sync gates, todo capture
commands/                     # Slash command stubs
tools/upgrade-ba-assistant.*  # Safe upgrade to Version 10
VERSION                       # 10
CHANGELOG.md
SETUP.md
```

`_workstream/` is created under `~/.cursor/` on first use (not committed).
