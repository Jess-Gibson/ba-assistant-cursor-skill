# Changelog

## Version 14 - 2026-09-25

### Orchestrator slim (cost, same working relationship)

- Replaced the 800-line `SKILL.md` ceremony (welcome panel, draft-depth quiz, inline Phase 0 checklist, duplicated learnings/standards/workstreams essays, auto-canvas) with a ~90-line router plus a 5-bullet working-relationship contract.
- `instructions.md` is persona and craft only (~54 lines). Routing, resume/`/reanchor`, and the partnership contract live in `SKILL.md` and are not restated.
- Default BAU is resume / `/reanchor`. New-initiative scaffolding is the exception (`ba-new-initiative` then Intake Reviewer).
- Canvas is on demand only (`/canvas`, `/status`). Ownership table moved to `references/canonical-ownership.md`. Co-thinking, AskQuestion, and skill-handoff headers moved to `references/co-thinking-protocol.md`.
- `/reanchor` re-reads `hook-contracts.md` and runs the bounded readiness pass. Does not invent an initiative.
- `workstreams.md` remains as an optional M0–M8 glossary; it is not loaded at bootstrap. Activity map is the day-to-day routing model.

### Version 14 QA correction pass

- Aligned resume/new-initiative routing, explicit-only canvas triggers, hook IDs, skill discovery, and manual Miro pre-flight guidance with the slim orchestrator.
- Removed public Miro identifiers and personal BA-action aliases while preserving a one-time, data-safe workboard migration path.
- Corrected Windows Downloads fallback, local calendar timezone handling, platform-specific calendar dispatch, and installer coverage for companion skills and the sample calendar feed.
- Corrected current-facing Version 14 documentation, generic BA identity guidance, status-colour examples, hook history, and README-only author attribution.

## Version 13 - 2026-09-25

### Initiative lifecycle bookends + commitment scan (Wave 10)

- Added `ba-new-initiative`: scaffolds a brand-new initiative, captures one-time workspace context (Jira project key, Confluence space, repos) so later skills never re-ask, then runs the multi-source research pass (Confluence, Jira, Glean, web) with the mandatory regulator gate and AI-source verification, before handing off to `ba-intake-reviewer`.
- Added `ba-initiative-closeout`: gated, one-way `/close` teardown for a finished initiative — mandatory closure retro first, then a file-by-file keep/publish/delete pass, Confluence completeness check, move to `archive/`, and a State Validator pass.
- Added `ba-commitment-scan`: read-only end-of-day reconciliation across mail and chat platforms against local BA action-tracker state (commitments, follow-ups, decisions, completions, watchpoints, open questions).
- Reconciled `ba-intake-reviewer` for the split: dropped the workspace-context-capture and multi-source-research steps it used to own (now `ba-new-initiative`'s job), leaner 5-task sequence, and ported a previously-missing "PM approval state" section.
- Registered all three new skills across `SKILL.md` (welcome panel, sub-skill count), `references/activity-map.md` (routing table), `instructions.md` (skill-to-skill hooks), and `hook-contracts.md` (new Wave 10 section, relocated `HK-NEWI-BDI-baseline`).
- Added `workboard-format.md` status value `archived`, set once by `ba-initiative-closeout` when it moves a folder — distinct from `closed` (BA delivery track ended but folder stays active).

### Calendar roll-forward at end-of-day

- Added `tools/roll-calendar-eod.py`: advances `calendar-feed.json` + `workboard.json` meetings to the next working day at EOD (step 7b of the closeout sequence), also runnable via `generate-workboard-canvas.py --eod-roll`.
- Wired it into `tools/install-ba-assistant.py` (fresh-install seed), `tools/upgrade-workboard.py` and `tools/build-workboard-overlay-zip.py` (existing-install upgrade paths) — it was previously undocumented-but-required by `eod-closeout-procedure.md` with no install path.
- Genericized: highlighting a meeting is now read from `calendar-feed.json`'s own `highlight` field (matching `generate-workboard-canvas.py`'s existing convention) instead of a hardcoded keyword list of real meeting/initiative names; solo-focus-block detection now reads the configured BA name instead of a hardcoded person's name.
- Fixed `_workstream/calendar-feed.sample.json`, which documented a stale nested `days[].meetings[]` shape that didn't match what `get-calendar.ps1`/`get-calendar.mac.sh` and both scripts actually read (flat `meetings[]` with `start`/`subject`/`required`/`highlight`, etc.).
- Fixed a stale "Version 10" target in `tools/upgrade-ba-assistant.py`'s docstring/argparse description.

### Content currency pass

- Synced real content drift across `rules/` (`skills-routing`, `execution-router`, `agent-behavior`, `critical-gates`, `sync-gates`, `todo-quick-capture`) and `commands/` (new `/close`; content updates to `ba-assistant`, `debrief`, `fast-track`, `next`, `reanchor`, `validate-state`, `workboard`, `wrap`).
- `publish-docs-to-confluence` was previously just a placeholder README — the actual skill (`SKILL.md` + two reference files) had never been published. Fully ported and genericized.
- `miro-board-analysis` caught up on a real missed feature (the "Accent Card" narrative-panel pattern) across 7 files.
- Restored genuine content drift across several `ba-assistant` sub-skills and references that had fallen behind source (`ba-data-investigation`, `ba-playback-and-enablement`, `ba-requirements-interrogator`, `ba-workshop-design`, `ba-context-capture`, `ba-meeting-debrief`, `ba-state-validator`, plus `references/cursor-runtime-facts.md`, `proactive-assistance-protocol.md`, `standards-index.md`, `hook-contracts-history.md`, `eod-closeout-procedure.md`).
- Fixed two pre-existing genericization bugs found during the audit: a duplicated-word artifact in `ba-project-canvas/canvas-generate.md`, and a leaked real surname in a path in `ba-project-canvas/canvas-tab-specs.md`.

### Fixes from round-3 QA (full end-to-end re-audit)

- Two more instances of the `null`-vs-missing `dict.get(key, default)` crash class (same root cause as the `next_milestone` fix), found by a requested-but-initially-skipped broader sweep, then genuinely swept this time: `calendar.get("days", [])` and `today_meetings()`'s per-day meetings lookup in `generate-workboard-canvas.py`; the top-level `meetings` lookup in `roll-calendar-eod.py`. While sweeping properly, found and fixed three more real (if less likely) instances: `downloads_since_refresh`'s nested lookups, `workboard.get("initiatives", [])`, `actions_data.get("actions", [])` in `generate-workboard-canvas.py`, `actions`/`watching` in `regenerate-ba-actions-md.py`, and `personal_tasks` in `upgrade-ba-assistant.py` (×2). All eight reproduced end-to-end with synthetic `null` JSON fields before fixing, and re-verified clean after.
- Fixed a leftover literal internal project-key example ("e.g. FCM or TEAM") in `ba-setup/SKILL.md`'s setup wizard prompt, missed by the earlier genericization pass.

### Meeting debrief: real, cross-platform docx/downloads scripts (previously phantom)

- `ba-meeting-debrief` referenced three scripts that never existed anywhere in the repo, on either platform: `list-downloads-recent.ps1`, `extract-docx-text.ps1`, `extract-docx.ps1`. Debriefing a `.docx` transcript, or scanning Downloads for one, would have failed for every user, Windows or Mac.
- Added `_workstream/list-downloads-recent.py` and `_workstream/extract-docx-text.py` (stdlib-only: `pathlib` + `zipfile`/XML parsing, no PowerShell, no external packages) — the latter also replaces the separate "unzip XML only" script via a `--raw-xml` flag, one file instead of two. Verified against a hand-built `.docx` fixture (correct paragraph/tab extraction, correct raw-XML dump, clean errors on missing/invalid files) and a synthetic Downloads folder with mixed file ages (correct cutoff filtering and newest-first ordering).
- Found and fixed a related gap while wiring these in: `_workstream/regenerate-ba-actions-md.py` — referenced everywhere (`/todo`, `/wrap`, `/workboard`, `sync-ba-actions`) and already present in the upgrade/overlay install paths — was never actually seeded by a **fresh** install. All three scripts now copied by `install-ba-assistant.py`'s `seed_workstream()`; verified with a clean dry-run.
- `ba-meeting-debrief/SKILL.md` rewritten to call the real scripts with platform-neutral commands instead of the old PowerShell-only invocation ceremony (nested-shell warnings, `Test-Path`, `Expand-Archive` cautions) that no longer applies.

### Hook runtime: cross-platform port + stop-hook opt-in (B4a + B4c)

- `sessionStart`/`preCompact` were registered as raw PowerShell — silently never fired on Mac. Ported `session-init` and `snapshot-before-compact` to single cross-platform `.py` files (net -4 files: the four `.ps1`/`.sh` twins deleted). Reconciled real behavioral drift between the old twins rather than picking one arbitrarily (timestamp tracking, workboard/calendar blocks, and `.vtt` support existed only in one of the two; kept the union). Found and fixed a real Windows console encoding crash in the process (cp1252 default choking on em-dashes/emoji).
- `tools/install-ba-assistant.py` now rewrites the Python interpreter token in every package-owned hook command to the OS-correct one (`py` on Windows, `python3` on Mac/Linux) at install time, instead of shipping a static `hooks.json` with a bare `python` that isn't guaranteed to resolve on either platform.
- Found and fixed a related bug in the same hook-merge logic (added earlier tonight): a hook entry using a quoted absolute path wasn't recognized as package-owned by the basename matcher (trailing quote broke the extension check), which would have caused a real merge to duplicate the entry instead of replacing it. Verified against the exact real-world quoted-path entry.
- Stop hook's auto-injected follow-up message (an unprompted "ghost" user turn) is now **off by default** — opt in with `stopFollowup: true` in `ba-assistant-config.mdc`. Verified all four states: no config, explicit false, explicit true, and already-nudged-once.

### Jira DoR gate — closed all three known security holes, plus one found during review

- `hooks/jira-dor-gate.py`: fixed the empty-title wildcard match (Hole A), removed the whole-tracker-file regex that let any story ride on an unrelated approval (Hole B), and removed the ability for a create payload to self-stamp its own "DoR: PASS" approval (Hole C) — plus rewrote the deny message so it no longer hands out the exact bypass string. `failClosed: true` now set, scoped to this one gate only. Verified with a 13-case fixture suite (`hooks/tests/test_jira_dor_gate.py`) run against both the fixed code and the original committed version, confirming all three named holes were genuinely exploitable before and are closed after.
- Found during review (not one of the three original holes): the title-matching fallback used open substring containment, so a short generic new-story title could match against an unrelated, much longer, already-passed story's title purely by coincidence. Tightened to a length-ratio-gated prefix match (handles genuine truncation, rejects short-phrase collisions) and added a fixture case proving the old logic would have allowed it.

### Fixes from independent QA pass (round 2)

- `tools/upgrade-ba-assistant.py`: removed a hardcoded `"jess-voice"` literal from `VOICE_HINTS` (redundant — `"voice"` alone already matches it) found by a fresh QA sweep after round 1. While fixing it, found and fixed a real functional bug in the same file: `VERSION` was hardcoded to `"11"` and silently written into a fresh install's `VERSION` file on every upgrade, regardless of the package's actual version. Now read dynamically from the package's own `VERSION` file at run time.
- `tools/install-ba-assistant.py`: same class of bug in the sibling script — `VERSION` was hardcoded to `"12"` and written into `.ba-assistant-installed.json` on every fresh install. Now reads the package's own `VERSION` file the same way.

### Fixes from independent QA pass (round 1)

- `tools/generate-workboard-canvas.py`: removed a hardcoded real name that `normalize_stakeholder_raise()` used as a fallback display value for an undocumented personal workboard key, plus the key itself. Rebuilt `dist/ba-workboard-overlay.zip` from the fixed source so the packaged copy doesn't carry the same leak.
- `.gitignore`: added `dist/ba-workboard-overlay/` (the unzipped build output of `build-workboard-overlay-zip.py` was untracked and unignored, duplicating whatever source leak existed at build time).
- `ba-install/SKILL.md`: fixed a leftover "for README / Jess to share" heading.
- `SKILL.md`: welcome-panel invocation-group arithmetic didn't sum to the stated total (`ba-install` was in the total count but missing from every group); added it as a second "once-ever" skill alongside Setup.

### Cleanup

- `ba-install`: added a temp-clone cleanup step (asks before deleting the temporary git-clone folder once install verification passes), and replaced a hardcoded example branch name with a default-branch clone (branch/tag pinning now points at `CHANGELOG.md`/`VERSION` instead of a name that goes stale every release).
- Removed `dist/ba-workboard-package/` — marked obsolete since Version 10, carried its own `DEPRECATED.md`.
- Scrubbed a real organisation name and hardcoded Runlayer server URL that had leaked into `context-bootstrap.md`, `ba-setup/SKILL.md`, `SETUP.md`, and `AGENTS.md`; genericized to a per-organisation placeholder pattern.
- `.gitignore`: added `__pycache__/` / `*.pyc`.

## Version 12 - 2026-09-04

### Workboard Control Centre

- Rebuilt portable workboard canvas contract: **Today / Initiatives / Open actions** tabs; **End of Day** starts `/wrap`, not a duplicate tab.
- Added a reusable canvas template plus `generate-workboard-canvas.py`, which embeds each BA's own canonical workboard, action, and optional calendar data.
- Initiative cards with status colour escalation (orange at-risk, red critical/overdue).
- Open actions tab supports **draft edits** in canvas sidecar; **Apply action updates** routes to agent for canonical `ba-actions.json` writes.
- Added `_workstream/regenerate-ba-actions-md.py` (was documented but missing).
- Expanded `workboard.json` optional fields: `meetings_today`, `meetings_tomorrow`, `ba_actions_summary`, `review_queue`.
- `workboard-procedure.md`: initiative path resolution (`initiatives/` → `-- analysis --/` → `blueprints/`), optional email scan, canvas draft apply procedure.
- `workboard-format.md`: tab contract, draft overlay rules, optional top-level JSON fields.
- `calendar-feed.sample.json` added for optional meeting feed setup.

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
- Setup wizard: AskQuestion only; path defaults; domain (for personalisation);
  dedicated Jira site/project + Confluence space/hub (no Cloud/Server quiz);
  Runlayer connectors; pull-in starting work. No calendar-hook script, no
  output-depth quiz, no Claude upsell.
- **Context Bootstrap:** setup checks connectors, guides Runlayer servers
  (Glean, Outlook, Jira, Confluence via your organisation's Runlayer servers page),
  then opt-in smart mail / calendar / hub / Jira harvest with review before
  seeding `ba-actions` and the workboard. See `references/context-bootstrap.md`.
- Setup ends with pull-in starting work (or manual initiative/transcript seed), not "empty is fine".
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
