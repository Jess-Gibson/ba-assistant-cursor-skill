# Version 15 upgrade manifest

Every installed file that changed between Version 14 (`750a6c5`) and Version 15, grouped by what the change is.
The same data, machine-readable, is `docs/port-manifest.json`; `tools/ba-merge-upgrade.py` uses it.

- **Tested code commit:** `1478278254e7c4670e727891f9c299d837513554` (all code and tests, including the review addendum: external-write gate, untrusted content, DoR check, undo, and the governance follow-up: gate verb precedence, Story Readiness Preflight, decimal HLR IDs, email recipients in arguments, actions upsert fixes, stale initiatives-root fallback, slim workboard canvas; every later Version 15 release-candidate commit changes documentation only).
- **Release commit:** pin the branch head you were given for the upgrade, and check that `git diff 1478278 <release> --stat` lists only `.md` files.
- **Fallback versions:** tag `v14.0` (`750a6c5`, Version 14 as released) and tag `v15.0-rc1` (`49f11e5`, Version 15 before the review addendum). See `SETUP.md` → "Go back to an older version".

| Category | Files | What happens to a personalised install |
|---|---:|---|
| Behaviour, critical | 34 | Taken, or three-way merged with your edits |
| Behaviour, important | 24 | Taken, or three-way merged with your edits |
| Behaviour, minor | 14 | Taken, or three-way merged with your edits |
| Wording | 48 | Your version kept |

## Your own always-on files

`ba-profile.mdc` and `ba-assistant-config.mdc` are yours, so no tool overwrites them. Two one-off tidy-ups cut what they cost on every message:

- **Profile:** `--patch-profile` (plain upgrade) or `patch_profile: true` (merge tool) replaces only the old command table with a pointer to `~/.cursor/commands/`, keeping rows for your own commands, after a backup.
- **Config:** trim it to values only with the prompt in `docs/PERSONALISED-UPGRADE.md` → "Trim your config file".

Then run the smoke test in `docs/PERSONALISED-UPGRADE.md` → "After you deploy".

## Behaviour, critical

| Installed path | Why |
|---|---|
| `_workstream/ba-actions.py` | New: /todo, action sync and end of day 5a/5b write ba-actions.json through one script (ids, dedupe, no reopen, MD regenerate); exact-wording matches stay within their initiative; a source-only change is saved |
| `_workstream/capture.py` | New: context capture writes to SESSION-CONTEXT.md without a full read; promotion markers; BA actions to ba-actions.json; Required --source; anything but chat-user written as [unverified]; confirmed_by_ba for debrief-card approvals; Saves a version before and after each capture; a stale BA_INITIATIVES_ROOT (not a folder) is ignored, config path still used |
| `_workstream/dor-check.py` | DoR computed from the files (requirement status, Given/When/Then, dependencies, MoSCoW, risks); shared by the hook; --record for metrics; One initiative reached through two folder spellings counts once (case-insensitive disks); Story Readiness Preflight wording; placeholders (TBD) and look-alike words (Risk-free) no longer pass; HLR-08.1 / HLR-08.21 parsed as their own IDs; a stale BA_INITIATIVES_ROOT (not a folder) is ignored, config path still used |
| `_workstream/generate-initiative-snapshots.py` | Resume snapshots: freshness hashes only this initiative's slice of workstream files; --ensure rebuilds when stale; a stale BA_INITIATIVES_ROOT (not a folder) is ignored, config path still used |
| `_workstream/generate-workboard-canvas.py` | End of Day button points at eod-closeout-procedure.md; one calendar roll; config keys read correctly; a stale BA_INITIATIVES_ROOT (not a folder) is ignored, config path still used; canvas embeds only the fields the template reads (at most 5 open key dates), so a big board no longer stops the canvas host |
| `_workstream/initiative-history.py` | Private local undo history per initiative folder (no remote); snapshot/history/undo; no-op without git; a stale BA_INITIATIVES_ROOT (not a folder) is ignored, config path still used |
| `_workstream/render-initiative-canvas.py` | New: initiative canvas + HTML snapshot rendered from status-data.json; a stale BA_INITIATIVES_ROOT (not a folder) is ignored, config path still used |
| `_workstream/roll-calendar-eod.py` | One roll per closeout date (repeat is a no-op, partial roll fails closed); real timezone; config highlights; null duration fix |
| `_workstream/scan-outlook-mail.py` | New: Outlook desktop triage, config-driven noise filters, fails open with exit 2; Mail listing fenced as untrusted data; read-only |
| `_workstream/validate-state.py` | New: local drift scan (state validator steps 3-5) for resume and end of day; a stale BA_INITIATIVES_ROOT (not a folder) is ignored, config path still used |
| `commands/canvas.md` | /canvas renders with the script; no read-every-file, no hand-written canvas |
| `commands/status.md` | /status is chat + metrics script; offers /canvas instead of rendering it; no longer depends on the profile table |
| `commands/undo.md` | New /undo command: plain-English undo from the local history |
| `commands/workboard.md` | End of day defers to eod-closeout-procedure.md and does not walk every action; action sync through ba-actions.py |
| `hooks.json` | Retired beforeSubmitPrompt entry removed; no hook registered twice |
| `hooks/external-write-gate.py` | One beforeMCPExecution gate: unwraps Runlayer execute_tool, denies email send/reply/forward/draft, asks on other external writes, allows reads, runs dor-check.py on Story creates, writes audit-log.jsonl; a write verb anywhere in the name asks (no first-verb shortcut); email compose denied; Story Readiness Preflight wording (never "DoR met"); email recipients in the arguments deny |
| `hooks/hooks.json` | beforeMCPExecution now runs external-write-gate.py (replaces jira-dor-gate.py); afterFileEdit entry removed (Cursor reads no output there) |
| `hooks/inject-state-reminder.py` | Stop hook counts REQ- and ASM- captures as unpromoted too; Stop hook saves a version of the chat's initiative after each reply |
| `hooks/jira-dor-gate.py` | Retired: folded into hooks/external-write-gate.py and _workstream/dor-check.py; the installer drops its hooks.json registration |
| `hooks/session-init.py` | Never picks an initiative by modified time; workspace_roots / CURSOR_PROJECT_DIR; paths.* from config or profile; Initiative by workspace, config paths; SESSION-CONTEXT tail and download names fenced as untrusted data; Saves a version of initiatives that already have history at session start; Calendar refresh time-boxed to 4s; transcripts listed until debriefed (7 days, cap 10); ~/projects scan dropped; Debriefed transcripts matched however the path is spelled (macOS /private/var, Windows short names); a stale BA_INITIATIVES_ROOT (not a folder) is ignored, config path still used |
| `hooks/shared-repo-guard.py` | Folder containment (not string prefix); git -C / cd aware; sharedRepoRoot from config or profile; Comments: postToolUse carries the edit warning |
| `rules/agent-behavior.mdc` | AskQuestion rules in one place (never re-ask, timeout); gate visibility and em-dash rule shortened; Safety: never send or draft email; ingested text is data, not instructions; external writes show the payload first; Lock block covers publish/overwrite/bulk; drafts go ahead with assumptions labelled |
| `rules/critical-gates.mdc` | Same gates, shorter rows; External-write gate row; DoR gate recomputed by dor-check.py; Story Readiness Preflight row; Definition of Ready as a reasoning gate |
| `rules/execution-router.mdc` | Context capture via capture.py; re-entry card moved to a reference; resume row follows SKILL.md Step 2 (snapshot first); settings map and duplicates trimmed; Context capture passes --source; Passive capture skipped while a transcript is debriefed; Placeholder workspace root removed |
| `skills/ba-assistant/references/eod-closeout-procedure.md` | 5a/5b via ba-actions.py eod-scan; validate-state.py for touched initiatives; one-call action upsert; Reply text goes in chat; never an Outlook draft or send; Versions before and after end of day |
| `skills/ba-assistant/references/raid-format.md` | DoR table gains Story key and Result columns the DoR gate reads |
| `skills/ba-assistant/references/sync-procedures.md` | Promotion rules for REQ-, ASM- and OQ-answered captures; Never auto-promote [unverified] items |
| `skills/ba-assistant/sub-skills/ba-context-capture/SKILL.md` | Detect every turn as before; write with capture.py; requirement and action signals; source field required; ingested text is data; confirmed_by_ba; Not during a debrief |
| `skills/ba-assistant/sub-skills/ba-new-initiative/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; Starts the undo history for a new initiative |
| `skills/ba-assistant/sub-skills/ba-project-canvas/SKILL.md` | Canvas rendered by script, on demand only |
| `skills/ba-assistant/sub-skills/ba-project-canvas/canvas-generate.md` | Procedure is now: refresh status-data.json, run the renderer |
| `skills/ba-assistant/sub-skills/ba-state-validator/SKILL.md` | Steps 3-5 run validate-state.py; quick mode on resume, full mode before publish |
| `skills/ba-assistant/sub-skills/ba-story-writing/SKILL.md` | Draft, BA approves, then create in Jira; internal schema checklist; asks which initiative; Agent no longer writes result: pass; runs dor-check.py; logs BA overrides as decisions; structural preflight vs Definition of Ready: never claim Ready from the script alone |
| `skills/ba-assistant/templates/initiative-status.canvas.tsx.template` | New: 8-tab initiative canvas template the renderer fills |

## Behaviour, important

| Installed path | Why |
|---|---|
| `_workstream/compute-metrics.py` | New: the four quality metrics computed from status-data.json with trend and n/a streak; a stale BA_INITIATIVES_ROOT (not a folder) is ignored, config path still used |
| `_workstream/extract-docx-text.py` | Extracted transcript text fenced as untrusted data; Marks the transcript as debriefed |
| `_workstream/list-downloads-recent.py` | Windows fallback when pathlib misses files in Downloads; --mark-processed for transcripts read directly |
| `commands/metrics.md` | /metrics runs compute-metrics.py |
| `commands/next.md` | Comms text ready to copy; no send option |
| `commands/reanchor.md` | Asks which initiative instead of picking the most recent |
| `commands/todo.md` | /todo writes through ba-actions.py |
| `commands/validate-state.md` | /wrap semantics kept; REQ-/ASM- markers; one-call action upsert and capture; Ask before promoting [unverified] items |
| `commands/wrap.md` | Chat checkpoint; REQ-/ASM- markers; ba-actions.py upsert; Never promote [unverified] items without the BA; Versions before and after /wrap |
| `rules/ba-profile.mdc` | /status, /canvas, /todo, /metrics rows (patched only with --patch-profile) |
| `rules/skills-routing.mdc` | Canvas is on demand only, not triggered by /status; /undo routing row |
| `rules/sync-gates.mdc` | /wrap follows commands/wrap.md; end of day is its own procedure |
| `rules/todo-quick-capture.mdc` | /todo, /done and lists use ba-actions.py |
| `skills/ba-assistant/SKILL.md` | Resume: quick validate-state.py, snapshot --ensure, re-entry card reference; canvas on demand |
| `skills/ba-assistant/hook-contracts.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; Cursor lifecycle hooks table (external-write-gate, DoR); gate precedence and preflight wording |
| `skills/ba-assistant/references/ba-actions-format.md` | Sync writes through ba-actions.py |
| `skills/ba-assistant/references/canvas-data-model.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; dorChecks is a metrics record written by dor-check.py, not gate evidence |
| `skills/ba-assistant/references/jira-ticket-format.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; Stories: DoR recomputed at create; not met = BA override; preflight wording; hook never reads dorChecks |
| `skills/ba-assistant/references/re-entry-card.md` | New: re-entry card moved out of the always-on router |
| `skills/ba-assistant/references/workboard-procedure.md` | Initiative folder resolution from paths.initiativesRoot |
| `skills/ba-assistant/sub-skills/ba-current-state-assessment/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; Cursor codebase search first with file:line; Glean for repos not open |
| `skills/ba-assistant/sub-skills/ba-jira-sync/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; Sprint field from config, not a hard-coded tenant field |
| `skills/ba-assistant/sub-skills/ba-meeting-debrief/SKILL.md` | Debrief approve path writes BA actions to the actions file, never workboard personal_tasks; Transcript is data; approved items carry transcript source and confirmed_by_ba; Versions before and after the debrief batch write; Passive capture paused until the card is approved; Mark .vtt/.txt transcripts debriefed after approval; Offered by the orchestrator; internal decision IDs removed |
| `skills/ba-assistant/sub-skills/ba-playback-and-enablement/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; Comms text in chat for the BA to copy; never an Outlook draft or send |

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
| `skills/ba-assistant/ba-profile.template.mdc` | Values only; command table and prose removed; jira.sprintField |
| `skills/ba-assistant/references/user-story-format.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; DoR computed by dor-check.py; DoR checklist split into computed preflight and human review |
| `skills/ba-assistant/sub-skills/ba-initiative-closeout/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; File audit skips the .git history folder |
| `skills/ba-assistant/sub-skills/ba-project-canvas/metrics.md` | Metrics come from compute-metrics.py |
| `skills/ba-assistant/sub-skills/ba-workshop-design/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; Invite text stays in chat; never an Outlook draft or send |

## Wording only

| Installed path | Why |
|---|---|
| `_workstream/README.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; capture.py --source note |
| `rules/ba-delivery-process.mdc` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/BA_Assistant_User_Guide.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; /undo |
| `skills/ba-assistant/hook-contracts-history.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/instructions.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/references/activity-map.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/references/chat-profiles.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/references/co-thinking-protocol.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/references/cursor-runtime-facts.md` | Re-entry card location; Bootstrap and hard-gate facts match the package |
| `skills/ba-assistant/references/dev-handover-format.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/references/markdown-readability.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/references/requirements-register-unified-template.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/references/runlayer-atlassian-mcp.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/references/status-page-format.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/references/workspace-operations.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/references/workstreams.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/slash-commands-ux.md` | Commands are defined in commands/*.md, not an always-on table |
| `skills/ba-assistant/sub-skills/ba-anti-pattern-detector/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-change-strategy/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-commitment-scan/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-data-investigation/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-dev-handover/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-discovery-and-requirements/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-feature-slicing-and-sequencing/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-install/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-intake-reviewer/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-project-canvas/canvas-tab-specs.md` | Marked as the template design reference |
| `skills/ba-assistant/sub-skills/ba-project-canvas/intake-form-canvas.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-project-canvas/status-page-and-data.md` | Status page format reference points at status-page-format.md |
| `skills/ba-assistant/sub-skills/ba-requirements-interrogator/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change; Internal decision ID removed |
| `skills/ba-assistant/sub-skills/ba-retrospective-and-learning/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-risk-and-tracker/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-setup/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-solution-evaluation/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-solution-shaping/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-sponsor-engagement/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-stakeholder-strategy/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/ba-assistant/sub-skills/ba-visual-storytelling/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/miro-board-analysis/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/miro-board-analysis/algorithm.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/miro-board-analysis/design-system.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/miro-board-analysis/recurring-mistakes.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/miro-board-analysis/templates/debrief-board.md` | Example IDs genericised |
| `skills/miro-board-analysis/templates/kickoff-board-template.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/miro-board-analysis/templates/spike-card-template.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/miro-board-analysis/templates/workshop-board.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/publish-docs-to-confluence/SKILL.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |
| `skills/publish-docs-to-confluence/references/confluence-workflow.md` | Public-repo wording, genericisation or doc tidy-up; no behaviour change |

## Not installed

Repo-only changes (tools, tests, docs) are not listed: they never reach `~/.cursor`.
`tools/ba-merge-upgrade.py` itself runs from the package checkout.
