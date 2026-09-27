# Version 15 upgrade manifest

Every installed file that changed between Version 14 (`750a6c5`) and Version 15, grouped by what the change is.
The same data, machine-readable, is `docs/port-manifest.json`; `tools/ba-merge-upgrade.py` uses it.

- **Tested code commit:** `4b06a976bdd466b4c62edbff1ea47d0890b03eea` (all code and tests; every later Version 15 release-candidate commit changes documentation only).
- **Release commit:** pin the branch head you were given for the upgrade, and check that `git diff 4b06a97 <release> --stat` lists only `.md` files.

| Category | Files | What happens to a personalised install |
|---|---:|---|
| Behaviour, critical | 27 | Taken, or three-way merged with your edits |
| Behaviour, important | 14 | Taken, or three-way merged with your edits |
| Behaviour, minor | 14 | Taken, or three-way merged with your edits |
| Wording | 57 | Your version kept |

## Your own always-on files

`ba-profile.mdc` and `ba-assistant-config.mdc` are yours, so no tool overwrites them. Two one-off tidy-ups cut what they cost on every message:

- **Profile:** `--patch-profile` (plain upgrade) or `patch_profile: true` (merge tool) replaces only the old command table with a pointer to `~/.cursor/commands/`, keeping rows for your own commands, after a backup.
- **Config:** trim it to values only with the prompt in `docs/PERSONALISED-UPGRADE.md` → "Trim your config file".

Then run the smoke test in `docs/PERSONALISED-UPGRADE.md` → "After you deploy".

## Behaviour, critical

| Installed path | Why |
|---|---|
| `_workstream/ba-actions.py` | New: /todo, action sync and end of day 5a/5b write ba-actions.json through one script (ids, dedupe, no reopen, MD regenerate) |
| `_workstream/capture.py` | New: context capture writes to SESSION-CONTEXT.md without a full read; promotion markers; BA actions to ba-actions.json |
| `_workstream/generate-initiative-snapshots.py` | Resume snapshots: freshness hashes only this initiative's slice of workstream files; --ensure rebuilds when stale |
| `_workstream/generate-workboard-canvas.py` | End of Day button points at eod-closeout-procedure.md; one calendar roll; config keys read correctly |
| `_workstream/render-initiative-canvas.py` | New: initiative canvas + HTML snapshot rendered from status-data.json |
| `_workstream/roll-calendar-eod.py` | One roll per closeout date (repeat is a no-op, partial roll fails closed); real timezone; config highlights; null duration fix |
| `_workstream/scan-outlook-mail.py` | New: Outlook desktop triage, config-driven noise filters, fails open with exit 2 |
| `_workstream/validate-state.py` | New: local drift scan (state validator steps 3-5) for resume and end of day |
| `commands/canvas.md` | /canvas renders with the script; no read-every-file, no hand-written canvas |
| `commands/status.md` | /status is chat + metrics script; offers /canvas instead of rendering it; no longer depends on the profile table |
| `commands/validate-state.md` | /wrap semantics kept; REQ-/ASM- markers; one-call action upsert and capture |
| `commands/workboard.md` | End of day defers to eod-closeout-procedure.md and does not walk every action; action sync through ba-actions.py |
| `commands/wrap.md` | Chat checkpoint; REQ-/ASM- markers; ba-actions.py upsert |
| `hooks.json` | Retired beforeSubmitPrompt entry removed; no hook registered twice |
| `hooks/inject-state-reminder.py` | Stop hook counts REQ- and ASM- captures as unpromoted too |
| `hooks/jira-dor-gate.py` | DoR gate: Runlayer execute_tool unwrap, reads the final result, issueTypeName, scoped to the named initiative, config or profile root |
| `hooks/session-init.py` | Never picks an initiative by modified time; workspace_roots / CURSOR_PROJECT_DIR; paths.* from config or profile |
| `hooks/shared-repo-guard.py` | Folder containment (not string prefix); git -C / cd aware; sharedRepoRoot from config or profile |
| `skills/ba-assistant/references/eod-closeout-procedure.md` | 5a/5b via ba-actions.py eod-scan; validate-state.py for touched initiatives; one-call action upsert |
| `skills/ba-assistant/references/raid-format.md` | DoR table gains Story key and Result columns the DoR gate reads |
| `skills/ba-assistant/sub-skills/ba-context-capture/SKILL.md` | Detect every turn as before; write with capture.py; requirement and action signals |
| `skills/ba-assistant/sub-skills/ba-meeting-debrief/SKILL.md` | Debrief approve path writes BA actions to the actions file, never workboard personal_tasks |
| `skills/ba-assistant/sub-skills/ba-project-canvas/SKILL.md` | Canvas rendered by script, on demand only |
| `skills/ba-assistant/sub-skills/ba-project-canvas/canvas-generate.md` | Procedure is now: refresh status-data.json, run the renderer |
| `skills/ba-assistant/sub-skills/ba-state-validator/SKILL.md` | Steps 3-5 run validate-state.py; quick mode on resume, full mode before publish |
| `skills/ba-assistant/sub-skills/ba-story-writing/SKILL.md` | Draft, BA approves, then create in Jira; internal schema checklist; asks which initiative |
| `skills/ba-assistant/templates/initiative-status.canvas.tsx.template` | New: 8-tab initiative canvas template the renderer fills |

## Behaviour, important

| Installed path | Why |
|---|---|
| `_workstream/compute-metrics.py` | New: the four quality metrics computed from status-data.json with trend and n/a streak |
| `_workstream/list-downloads-recent.py` | Windows fallback when pathlib misses files in Downloads |
| `commands/metrics.md` | /metrics runs compute-metrics.py |
| `commands/reanchor.md` | Asks which initiative instead of picking the most recent |
| `commands/todo.md` | /todo writes through ba-actions.py |
| `rules/ba-profile.mdc` | /status, /canvas, /todo, /metrics rows (patched only with --patch-profile) |
| `rules/execution-router.mdc` | Context capture via capture.py; re-entry card moved to a reference; resume row follows SKILL.md Step 2 (snapshot first); settings map and duplicates trimmed |
| `rules/sync-gates.mdc` | /wrap follows commands/wrap.md; end of day is its own procedure |
| `rules/todo-quick-capture.mdc` | /todo, /done and lists use ba-actions.py |
| `skills/ba-assistant/SKILL.md` | Resume: quick validate-state.py, snapshot --ensure, re-entry card reference; canvas on demand |
| `skills/ba-assistant/references/ba-actions-format.md` | Sync writes through ba-actions.py |
| `skills/ba-assistant/references/re-entry-card.md` | New: re-entry card moved out of the always-on router |
| `skills/ba-assistant/references/sync-procedures.md` | Promotion rules for REQ-, ASM- and OQ-answered captures |
| `skills/ba-assistant/references/workboard-procedure.md` | Initiative folder resolution from paths.initiativesRoot |

## Behaviour, minor

| Installed path | Why |
|---|---|
| `commands/audit-standards.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/close.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/debrief.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/fast-track.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/handover.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/install-ba-assistant.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/publish-status.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/report.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/retro.md` | Ends with an AskQuestion on which actions to implement (was only in the profile table) |
| `rules/agent-behavior.mdc` | AskQuestion rules in one place (never re-ask, timeout); gate visibility and em-dash rule shortened |
| `rules/critical-gates.mdc` | Same gates, shorter rows |
| `rules/skills-routing.mdc` | Canvas is on demand only, not triggered by /status |
| `skills/ba-assistant/ba-profile.template.mdc` | Values only; command table and prose removed |
| `skills/ba-assistant/sub-skills/ba-project-canvas/metrics.md` | Metrics come from compute-metrics.py |

## Wording only

Public-repo wording, genericisation or doc tidy-ups. No behaviour change. A personalised install keeps its own version.

- `_workstream/README.md`
- `rules/ba-delivery-process.mdc`
- `skills/ba-assistant/BA_Assistant_User_Guide.md`
- `skills/ba-assistant/hook-contracts-history.md`
- `skills/ba-assistant/hook-contracts.md`
- `skills/ba-assistant/instructions.md`
- `skills/ba-assistant/references/activity-map.md`
- `skills/ba-assistant/references/canvas-data-model.md`
- `skills/ba-assistant/references/chat-profiles.md`
- `skills/ba-assistant/references/co-thinking-protocol.md`
- `skills/ba-assistant/references/cursor-runtime-facts.md`
- `skills/ba-assistant/references/dev-handover-format.md`
- `skills/ba-assistant/references/jira-ticket-format.md`
- `skills/ba-assistant/references/markdown-readability.md`
- `skills/ba-assistant/references/requirements-register-unified-template.md`
- `skills/ba-assistant/references/runlayer-atlassian-mcp.md`
- `skills/ba-assistant/references/status-page-format.md`
- `skills/ba-assistant/references/user-story-format.md`
- `skills/ba-assistant/references/workspace-operations.md`
- `skills/ba-assistant/references/workstreams.md`
- `skills/ba-assistant/slash-commands-ux.md`
- `skills/ba-assistant/sub-skills/ba-anti-pattern-detector/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-change-strategy/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-commitment-scan/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-current-state-assessment/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-data-investigation/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-dev-handover/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-discovery-and-requirements/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-feature-slicing-and-sequencing/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-initiative-closeout/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-install/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-intake-reviewer/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-jira-sync/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-new-initiative/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-playback-and-enablement/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-project-canvas/canvas-tab-specs.md`
- `skills/ba-assistant/sub-skills/ba-project-canvas/intake-form-canvas.md`
- `skills/ba-assistant/sub-skills/ba-project-canvas/status-page-and-data.md`
- `skills/ba-assistant/sub-skills/ba-requirements-interrogator/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-retrospective-and-learning/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-risk-and-tracker/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-setup/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-solution-evaluation/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-solution-shaping/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-sponsor-engagement/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-stakeholder-strategy/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-visual-storytelling/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-workshop-design/SKILL.md`
- `skills/miro-board-analysis/SKILL.md`
- `skills/miro-board-analysis/algorithm.md`
- `skills/miro-board-analysis/design-system.md`
- `skills/miro-board-analysis/recurring-mistakes.md`
- `skills/miro-board-analysis/templates/kickoff-board-template.md`
- `skills/miro-board-analysis/templates/spike-card-template.md`
- `skills/miro-board-analysis/templates/workshop-board.md`
- `skills/publish-docs-to-confluence/SKILL.md`
- `skills/publish-docs-to-confluence/references/confluence-workflow.md`

## Not installed

Repo-only changes (tools, tests, docs) are not listed: they never reach `~/.cursor`.
`tools/ba-merge-upgrade.py` itself runs from the package checkout.
