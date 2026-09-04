# Changelog

## Version 11 - 2026-09-04

### One-shot install for non-developer BAs

- Added `ba-install` skill plus `tools/install-ba-assistant.py` (.ps1 / .sh wrappers).
- Added `/install-ba-assistant` and a paste-this prompt in README, SETUP, and AGENTS.
- Install copies skills, rules, hooks, and commands, seeds `_workstream`, and creates
  `~/.cursor/initiatives` before personalisation.
- Personalisation writes `ba-assistant-config.mdc` and no longer overwrites the
  always-on persona `ba-profile.mdc`.
- Default `BA_INITIATIVES_ROOT` is now `~/.cursor/initiatives` (not `blueprints`).
- Free-text fields (name, URLs, keys) use AskQuestion free-text / Other; never fake chips like "Enter my name".
- Package docs no longer mention other AI tool skill folders; skills load only from `~/.cursor/skills/ba-assistant/`.
- **Context Bootstrap:** setup checks connectors, guides Runlayer servers
  (Glean, Outlook, Jira, Confluence via https://myob.runlayer.com/servers),
  then opt-in smart mail / calendar / hub / Jira harvest with review before
  seeding `ba-actions` and the workboard. See `references/context-bootstrap.md`.
- Setup Step 8 runs Context Bootstrap (or manual initiative/transcript seed), not "empty is fine".
- Orchestrator Step 1.5 runs install preflight, then setup, before the welcome panel.

### First-run and beginner onboarding

- First-run profile detection now invokes the BA Setup wizard before the
  welcome panel.
- Added `/ba-assistant` as the discoverable slash-command entry point.
- Added `/setup` to run or re-run the first-run wizard.
- Setup now offers guided first tasks: debrief a permitted Teams transcript,
  create a workboard, or start an initiative.
- Added slash-command stubs for `/next`, `/report`, `/fast-track`,
  `/publish-status`, `/snapshot`, and `/audit-standards`.
- Added generic MCP setup guidance and updated the installation verification
  checklist.

### Quality and guardrails (from local product improvements)

- Added `markdown-readability.md` reference and matching rule for dark-mode-safe
  stakeholder Markdown.
- Added thin-brief lock block to `agent-behavior.mdc` (source of truth, mutate/
  freeze, job verb, gold bar, ship shape).
- Extended `/todo` quick capture with optional `remind_on` and `reminder` fields
  (schema already supported in `ba-actions-format.md`).
- Added anti-pattern triggers for thin-brief lock block skip and remediation
  without downstream outcome ACs.
- Added anonymised learnings rows for complexity-before-sources and incomplete
  brief handling.

---

## Version 10 — 2026-08-03

Public package release. Going forward, releases are numbered **Version N** only (next: Version 11).

### Highlights

- **Unified requirements register** + Requirements Interrogator **Mode 4 (Kickoff HLR review)** with human closure before `interrogated`
- **Requirements lifecycle:** `proposed` → `interrogated` → `confirmed` (+ `blockedOn`)
- **Inline `/workboard`** (procedure + format refs) — standalone `ba-workboard` sub-skill **removed**
- **BA actions** store (`ba-actions.json` / `ba-actions-format.md`) replaces legacy `workboard.json → personal_tasks[]`
- **Full `/wrap`** closeout with BA-actions sync gate and AskQuestion runthrough
- **Miro Pass 2b** board inventory + placement; HARD pre-flight gate documented
- **AskQuestion** restored for forks, re-entry, runthroughs, and closure ceremonies (Auto-balance; model-tier nudges removed)
- **Cross-platform** workspace ops + calendar samples (Windows Outlook + macOS)
- **Upgrade script:** `tools/upgrade-ba-assistant.py` (preserves `ba-profile.mdc` and `_workstream` data)

### Breaking changes for existing installs

| Before | After |
|---|---|
| `sub-skills/ba-workboard/` | Inline `references/workboard-procedure.md` |
| `personal_tasks[]` in workboard.json | `_workstream/ba-actions.json` |
| Model-tier nudge on activity change | Removed (use Auto-balance) |

Use `tools/upgrade-ba-assistant.py --package <this-repo> --dry-run` then `--apply`.

### Also included (previously Wave 8 / Wave 9 content)

- `ba-data-investigation` data-pairing hooks
- `ba-dev-handover` gated publish to delivery repo

---

## Earlier public docs

User Guide historically covered Waves 1–7. Version 10 is the first numbered public drop that includes the later work above.
