# Version 15 upgrade manifest

Every installed file that changed between Version 14 (`750a6c5`) and Version 15, grouped by what the change is.
The same data, machine-readable, is `docs/port-manifest.json`; `tools/ba-merge-upgrade.py` uses it.

- **Tested code commit:** `fb2d95b1f65cb8ca20d998a27938b6c1dff6e948` (all code and tests; every later Version 15 release-candidate commit changes documentation only).
- **Release commit:** pin the branch head you were given for the upgrade, and check that `git diff fb2d95b <release> --stat` lists only `.md` files.

| Category | Files | What happens to a personalised install |
|---|---:|---|
| Behaviour, critical | 16 | Taken, or three-way merged with your edits |
| Behaviour, important | 12 | Taken, or three-way merged with your edits |
| Behaviour, minor | 12 | Taken, or three-way merged with your edits |
| Wording | 60 | Your version kept |

## Behaviour, critical

| Installed path | Why |
|---|---|
| `_workstream/generate-initiative-snapshots.py` | New: resume snapshots with --check FRESH/STALE; never used for initiative selection |
| `_workstream/generate-workboard-canvas.py` | End of Day button points at eod-closeout-procedure.md; one calendar roll; config keys read correctly |
| `_workstream/roll-calendar-eod.py` | One roll per closeout date (repeat is a no-op, partial roll fails closed); real timezone; config highlights; null duration fix |
| `_workstream/scan-outlook-mail.py` | New: Outlook desktop triage, config-driven noise filters, fails open with exit 2 |
| `commands/validate-state.md` | /validate-state writes what this chat captured (was read-only) |
| `commands/workboard.md` | End of day defers to eod-closeout-procedure.md and does not walk every action |
| `commands/wrap.md` | /wrap is a chat-only checkpoint; no workboard refresh |
| `hooks.json` | Retired beforeSubmitPrompt entry removed; no hook registered twice |
| `hooks/inject-state-reminder.py` | Stop reminder never guesses an initiative; off unless stopFollowup: true |
| `hooks/jira-dor-gate.py` | DoR gate: Runlayer execute_tool unwrap, reads the final result, issueTypeName, scoped to the named initiative, config or profile root |
| `hooks/session-init.py` | Never picks an initiative by modified time; workspace_roots / CURSOR_PROJECT_DIR; paths.* from config or profile |
| `hooks/shared-repo-guard.py` | Folder containment (not string prefix); git -C / cd aware; sharedRepoRoot from config or profile |
| `skills/ba-assistant/references/eod-closeout-procedure.md` | Single calendar-roll command, mail order script > MCP > unable, snapshots step, 5b action filter |
| `skills/ba-assistant/references/raid-format.md` | DoR table gains Story key and Result columns the DoR gate reads |
| `skills/ba-assistant/sub-skills/ba-meeting-debrief/SKILL.md` | Debrief approve path writes BA actions to the actions file, never workboard personal_tasks |
| `skills/ba-assistant/sub-skills/ba-story-writing/SKILL.md` | Draft, BA approves, then create in Jira; internal schema checklist; asks which initiative |

## Behaviour, important

| Installed path | Why |
|---|---|
| `_workstream/list-downloads-recent.py` | Windows fallback when pathlib misses files in Downloads |
| `commands/reanchor.md` | Asks which initiative instead of picking the most recent |
| `rules/critical-gates.mdc` | Stop reminder documented as off by default; shared repo from config |
| `rules/execution-router.mdc` | Separate routes for chat checkpoint (/wrap), end of day and retro |
| `rules/sync-gates.mdc` | /wrap follows commands/wrap.md; end of day is its own procedure |
| `rules/todo-quick-capture.mdc` | /wrap syncs only this chat's actions; no workboard refresh |
| `skills/ba-assistant/SKILL.md` | Resume order uses snapshot --check; /wrap routing; hook-contracts read on demand |
| `skills/ba-assistant/ba-profile.template.mdc` | Config template: paths.*, sharedRepoRoot, optional workboard and mail keys |
| `skills/ba-assistant/references/ba-actions-format.md` | End of day and /wrap rows; 5b filter instead of walking every action |
| `skills/ba-assistant/references/sync-procedures.md` | /wrap and /validate-state semantics; end of day moved out |
| `skills/ba-assistant/references/workboard-procedure.md` | Initiative folder resolution from paths.initiativesRoot |
| `skills/ba-assistant/sub-skills/ba-state-validator/SKILL.md` | /validate-state writes; read-mostly default only on resume or publish |

## Behaviour, minor

| Installed path | Why |
|---|---|
| `commands/audit-standards.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/canvas.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/close.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/debrief.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/fast-track.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/handover.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/install-ba-assistant.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/publish-status.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/report.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/retro.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/status.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |
| `commands/todo.md` | Command points at the installed ~/.cursor/ path, so it works from any workspace |

## Wording only

Public-repo wording, genericisation or doc tidy-ups. No behaviour change. A personalised install keeps its own version.

- `_workstream/README.md`
- `rules/agent-behavior.mdc`
- `rules/ba-delivery-process.mdc`
- `rules/skills-routing.mdc`
- `skills/ba-assistant/BA_Assistant_User_Guide.md`
- `skills/ba-assistant/hook-contracts-history.md`
- `skills/ba-assistant/hook-contracts.md`
- `skills/ba-assistant/instructions.md`
- `skills/ba-assistant/references/activity-map.md`
- `skills/ba-assistant/references/canvas-data-model.md`
- `skills/ba-assistant/references/chat-profiles.md`
- `skills/ba-assistant/references/co-thinking-protocol.md`
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
- `skills/ba-assistant/sub-skills/ba-context-capture/SKILL.md`
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
- `skills/ba-assistant/sub-skills/ba-project-canvas/SKILL.md`
- `skills/ba-assistant/sub-skills/ba-project-canvas/canvas-generate.md`
- `skills/ba-assistant/sub-skills/ba-project-canvas/canvas-tab-specs.md`
- `skills/ba-assistant/sub-skills/ba-project-canvas/intake-form-canvas.md`
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
