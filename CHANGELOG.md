# Changelog

## Version 16 - 2026-10-01

Lean status and catch-up for every BA who clones or upgrades this package. No extra patch step.

### Lean `/status` and `/canvas`

- **`status-data.json` is updated, not regenerated.** New procedure: `references/status-refresh.md`. One `validate-state.py --json` call, change only what is out of date, query Jira only if the last sync is 60 minutes old or more. Full rebuild only when the file is missing or broken, or you say `/status full`.
- **`validate-state.py`** reports Jira freshness (`jiraSyncedAt`, `jiraSyncAgeMinutes`) so status and canvas can skip Jira when recent.
- **`ba-jira-sync`** uses one `searchJiraIssuesUsingJql` query and stamps `lastJiraSync` on returned tickets.
- **Resume** no longer queries Jira. The re-entry card shows sync age from the state check.
- Commands `/status`, `/canvas`, and `/metrics` all use `status-refresh.md`. `/status` still never renders the canvas.

### Catch-up and end of day

- **`/catchup`** (`ba-comms-debrief`): debriefs Slack, Teams and Outlook since the last catch-up. Review card first; nothing written until you approve. Shared search procedure: `references/comms-retrieval.md`.
- **`catchup-watch.py`**: watch list and due timing (config keys `catchupEveryMinutes`, `catchupHours` in `ba-assistant-config.mdc`).
- Session start lists broader transcript types (`.txt`, `.srt`, and names containing "transcript") and can nudge `CATCH-UP DUE`.
- **`/eod`**: shortcut for the full end-of-day closeout (same as `/workboard end-of-day`), including commitment scan and catch-up step 1c.

### Leftovers cleanup

- Gate renamed **Interrogate before confirming** (requirements may enter the register at `proposed`).
- `register.md` renamed to `requirements-register.md` in skills and visuals.
- Schema Field Validator pointer replaced by the checklist in `ba-story-writing`.
- Retro and workshop prep write follow-ups to BA actions, not `workboard.json`.
- Commitment scan never books; booking stays end of day's job after you confirm.
- Debrief card captures tracker actions as `ACT-XX` (`A-` means assumption in this package).

### Other

- Starter `templates/initiative-tracker.md.template` for new initiatives.
- Config template documents `catchupEveryMinutes` / `catchupHours`.

## Version 15 - 2026-09-27

Version 14 QA fixes (from the fork review) plus the fixes below.

### Governance fixes (independent review follow-up)

- **Write gate: a write verb anywhere in a tool name now asks.** The gate used to decide on the first verb it met, so a name such as `findAndReplaceConfluencePage` or `previewAndPublishPage` ran without a prompt and was logged as a read. Precedence is now: email send / draft / compose (with email, mail or Outlook in the name) denied; any write verb asks; otherwise a read verb is allowed; anything else asks. Missing write verbs (`replace`, `upsert`, `modify`, ...) added. `generateReport` and `composeConfluencePage` are not treated as email and ask.
- **"DoR met" is gone.** `dor-check.py` is now the **Story Readiness Preflight**: five structural checks (linked requirement status, Given/When/Then, dependencies, MoSCoW, risks). A pass reads "Structural preflight passed" and says what it does not confirm (semantic completeness, sign-offs, feasibility, sizing, NFRs). The Definition of Ready stays the BA's judgement, and the story-writing skill no longer lets the assistant call a story Ready on the script result alone.
- **Placeholders no longer pass.** "Dependencies: TBD / TBC / ?" and empty sections don't count as listed; a word such as "Risk-free" is not a Risks section.
- **Detailed requirement IDs parse correctly.** `HLR-08.1` and `HLR-08.21` are read as their own requirements. Before, both were read as `HLR-08`, so a story linked to an unconfirmed `HLR-08.1` could pass on its parent's status. Legacy IDs (`REQ-1`, `FR-001`, `BR-001`, `NFR-001`, ...) still work.

**Compatibility:** the `dor-check.py` file name, arguments, exit codes (0 / 3 / 1), the `Gate: dor-check: PASS | NOT READY (...)` line, the `--json` fields and the `status-data.json → dorChecks` fields are unchanged (JSON gains a `check` field). `dorChecks` rows keep their names; a `pass` there now means the structural preflight passed. Audit rows keep `dor: pass | fail | error`; the `reason` text changed. A story that relied on "Dependencies: TBD" or a stray "risk" word will now show those conditions as not passed, and the BA can still approve it as an override. No initiative data is migrated or rewritten.

### Fixes from the first personalised upgrade

- **A stale `BA_INITIATIVES_ROOT` no longer hides your initiatives.** If that setting points at a folder that doesn't exist (left over from an old install), every script now ignores it and uses `paths.initiativesRoot` from your config or profile. Before, session start, `/validate-state`, snapshots, capture, metrics, undo, the DoR preflight and both canvases found no initiatives at all. Session start also says the setting was ignored.
- **Mail searches filtered by recipient are reads again.** The PR review check that denies a call carrying email recipients also caught reads, so an Outlook mail search with a `to` filter (the end-of-day mail fallback) was blocked. It now applies only to writes and unknown tools.
- **The workboard canvas no longer stops loading on a big board.** The canvas used to embed every initiative and action in full, including long `key_dates` histories, and a large board made Cursor's canvas host stop ("The service was stopped"). It now embeds only the fields the canvas shows, with at most 5 open key dates per initiative. Priorities are still worked out from the full data, and `workboard.json` and the actions file are unchanged.

### PR review follow-up

- **Write gate reads the arguments for email.** A call whose arguments carry email recipients (`to` / `cc` / `bcc` / `*Recipients` holding an address) is denied even when the tool name is generic (`execute`, `run_action`). Calendar, Jira and chat tools by name are unaffected.
- **Actions: exact-wording matches stay inside their initiative.** Two initiatives can each have "Draft AC for refunds"; the second no longer moves the first row across. A row with no initiative can still match.
- **Actions: a source-only change is saved.** Before, it was reported "Already there" and not written.
- `/undo` with unsaved edits was checked and is correct (reverts the last saved change, keeps the edits as their own version); a regression test now pins it.

### Safety and control (independent review, author's addendum)

- **One gate for every Runlayer call** (`hooks/external-write-gate.py`, `beforeMCPExecution`, fail-closed). Reads run without prompts. Every other external write (Jira, Confluence, calendar, Miro, Slack/Teams) asks you first. **Email is never sent, replied to, forwarded or drafted**: the text goes in chat for you to copy. Each decision is logged to `_workstream/audit-log.jsonl`.
- **Definition of Ready is computed, not claimed.** `_workstream/dor-check.py` checks the story against the files (confirmed requirement, Given/When/Then, dependencies, MoSCoW for its scope, risks). The assistant no longer writes its own pass rows. At Jira create the approval dialog reports the result (now worded as a structural preflight, see Governance fixes above), or names what's missing so your approval is a recorded override. `hooks/jira-dor-gate.py` is retired.
- **Ingested text is data, not instructions.** Transcripts, emails, tickets and old notes can't change a status or approval by saying so. `capture.py` needs a `--source`, and anything not said by you in chat lands as `[unverified]` until you confirm it. Session start, the mail scan and extracted transcripts are fenced as untrusted.
- **Undo for initiative folders.** Each initiative keeps a private local history (no remote). It saves around captures, debriefs, `/wrap`, end of day and after each reply. `/undo` shows recent changes in plain English and puts files back; an undo can itself be undone.
- **Passive capture waits for the debrief card.**
- Quick wins: transcripts stay listed until debriefed; session start can't be killed by a slow calendar refresh; the no-op `afterFileEdit` hook is removed; install, upgrade and conformance flag hook scripts that `hooks.json` runs but are missing; optional auto-run guidance in SETUP.md; sprint field from config; code questions use Cursor's codebase search first.

### End of day

- **One calendar roll.** The canvas End of Day button used to run `roll-calendar-eod.py` and then `generate-workboard-canvas.py --eod-roll`, which rolled the calendar twice (Wed to Fri). End of day now has one command: `generate-workboard-canvas.py --eod-roll --closeout-date <date being closed out>`.
- **Safe to re-run.** A second roll for the same closeout date prints `Gate: calendar-roll: SKIPPED` and writes nothing. Roll markers that disagree (a partial roll) print `FAIL` and write nothing. Leaving out `--closeout-date` after a roll fails instead of guessing. The closeout date is the day being closed, so a morning catch-up can close yesterday. A meeting with `duration_min: null` no longer crashes the roll.
- **Canvas End of Day prompt** now points at `eod-closeout-procedure.md` instead of a moved section of `sync-procedures.md`, and follows its action filter (not every open action).
- **Mail check order:** `_workstream/scan-outlook-mail.py` if installed, then the Outlook MCP connector, then "Mail: unable to check". Never blocks end of day.

### New scripts

- **`_workstream/scan-outlook-mail.py`** (Windows, Outlook desktop, read-only): Inbox and Sent triage for end of day. Your noise filters live in config (`mail_noise_subjects`, `mail_ignore_folders`, `mail_noise_repos`), so upgrades never wipe them. Prints one "Mail: unable to check" line and exits 2 when it cannot scan, so end of day moves on to the Outlook connector.
- **`_workstream/generate-initiative-snapshots.py`**: compact, source-linked snapshots for resume. `--check <slug>` says FRESH, STALE, MISSING or MALFORMED; resume only uses a FRESH one. Never used to pick an initiative. End of day step 7a refreshes them.
- **Meeting highlights from config:** `calendar_highlight_substrings` in `ba-assistant-config.mdc`.

### Config found in more places

- Session start, the Jira DoR gate and the shared-repo guard read `paths.*` from `ba-assistant-config.mdc`, then `ba-profile.mdc`. Before, an install with no config file found no initiatives, and the DoR gate denied stories that had a recorded pass.

### Initiative selection

- Session start also reads `CURSOR_PROJECT_DIR` when Cursor sends no `workspace_roots`. Still never picks an initiative by modified time.

### Upgrading

- **Your data is left alone by default.** The upgrader, the installer (when re-run on an existing install) and the workboard overlay no longer run the old data migrations unless you pass `--migrate-legacy`. Before, any of them could move a live actions file with the old pre-Version 10 name into a backup. Now they report what they found and leave it byte-identical.
- **`--patch-profile`** replaces only the old `/wrap` and `/validate-state` rows in your `ba-profile.mdc` (backup first). Without it, the upgrader shows the exact new rows. Rows you have personalised are never rewritten.
- **No hook runs twice.** Old `.sh`/`.ps1` hook wrappers are dropped from `hooks.json` when the package ships the `.py` hook, and moved into the backup once nothing references them.
- **Port manifest:** `docs/port-manifest.json` (readable: `docs/V15-UPGRADE-MANIFEST.md`) marks each changed file as behaviour or wording. The merge tool brings only behaviour changes into a personalised install, three-way merging them with your edits.
- **New: `tools/ba-merge-upgrade.py`** for personalised installs (edited skills, your own rules and skills, your own naming). Backup with restore rehearsal, staging, a three-way comparison, your decisions, a reviewed deploy plan, a drift check, hash-verified deploy with automatic rollback. New files are written in your own naming (for example `alex-actions`, not `ba-actions`). See `docs/PERSONALISED-UPGRADE.md`.

### Upgrading from 14

- Plain install: `python3 tools/upgrade-ba-assistant.py --package <this checkout> --apply --patch-profile`.
- Personalised install: follow `docs/PERSONALISED-UPGRADE.md`.
- Your profile, config, own rules, own skills, actions, workboard, calendar feed and initiatives are not changed by either path.

### Review fixes (before release)

- A failed calendar roll at end of day now stops: no canvas is written and the command exits 1.
- Initiative selection works on case-insensitive disks (macOS), where the same folder is seen as `initiatives/` and `Initiatives/`.
- Snapshots are only FRESH when every input (initiative files, `workboard.json`, `ba-actions.json`, `calendar-feed.json`) is byte-identical to when they were made.
- `dist/ba-workboard-overlay.zip` rebuilt with the Version 15 files and `eod-closeout-procedure.md`; a test keeps it in step with the sources.
- Mail lookback defaults to the previous working day. No region-specific timezone fallback.
- Merge tool: one sign-off for auto-merged files, stale decisions refused, a warning for initiative folders outside `.cursor`, and `changed-since-deploy` for a safe first sync.
- CI runs the tests on Ubuntu, macOS and Windows.

### Scripts do the repeatable work (fewer tokens, same thinking)

The model keeps the judgement (what to capture, how to word it, what to propagate, what to ask). Steps that come out the same every time now run as scripts in `_workstream/`, so they are cheaper and cannot drift between runs.

- **Context capture:** still detects decisions, requirements, actions, answered questions, assumptions, risks, blockers and facts on every BA turn, and still writes them in the same turn with a 📝 line. The write is now one `capture.py` call: no full read and re-edit of `SESSION-CONTEXT.md`, duplicates skipped, and every line tagged (`DEC-`, `REQ-`, `OQ-answered`, `ASM-`, `RISK-`, `ACT-`, `DEP-`) so `/wrap`, `/validate-state`, end of day and the stop hook see it until it is promoted. Requirements and actions are now named signal types; the BA's own actions also go to `ba-actions.json` in the same call.
- **Actions:** `ba-actions.py` does `/todo`, `/done`, lists, batch upserts from debriefs and `/wrap`, and the end-of-day critical scan and walk list (`eod-scan`). It allocates ids, applies the duplicate rules and priority defaults, never reopens a done row without `--reopen`, and regenerates `ba-actions.md`.
- **Canvas:** `/canvas` renders the 8-tab canvas and HTML snapshot from `status-data.json` with `render-initiative-canvas.py` and a packaged template. The old procedure read every file in the initiative and had the model hand-write a large `.canvas.tsx` from about 117k characters of spec; the spec is now a template design reference only. Empty tabs say what data they need. `/status` no longer renders the canvas; it offers it.
- **State validation:** `validate-state.py` does the fact registry, scan and divergence table for local files (tracker vs `status-data.json`, render freshness, names, milestone dates, README status, unpromoted captures). Resume runs this quick mode only (no Jira sync, no Confluence fetch); the full mode with Confluence runs before `/publish-status` or on request. End of day runs it for touched initiatives.
- **Metrics:** `compute-metrics.py` computes the four quality metrics with a 7-day trend and the n/a streak, for `/metrics` and `/status`.
- **Resume snapshots actually get used:** freshness now hashes only this initiative's slice of `workboard.json`, `ba-actions.json` and `calendar-feed.json`, so a calendar refresh or another initiative's `/todo` no longer makes every snapshot stale. `--ensure <slug>` rebuilds a stale one instead of falling back to reading every file.
- **Always-on rules trimmed from about 33k to about 23k characters** (roughly 2,500 fewer tokens on every message, BA or not), with no behaviour removed:
  - The command table left `ba-profile.mdc` and the config template: every command already has its own file in `~/.cursor/commands/`. The profile keeps a one-line pointer so a command typed as plain text still reads its file. `/retro` and `/status` command files gained the AskQuestion lines the table used to carry.
  - The config template is values only (the status page format, Jira notes, customisation and draft-depth prose are gone; they live in references).
  - AskQuestion rules live once, in `agent-behavior.mdc` (the router's copy is gone; its never-re-ask and timeout lines moved there).
  - Wave history notes, the em-dash hook disclaimer and duplicated `/reanchor` steps removed; `critical-gates.mdc` and the router's settings map compressed.
  - The re-entry card templates moved to `references/re-entry-card.md`, read on resume only.
  - Fixed: the router's resume row still said to read SESSION-CONTEXT, the tracker and Project-hub in full, which bypassed the snapshot-first order in `SKILL.md` Step 2.
  - `test_efficiency_scripts.py` caps the always-on size at 24k characters and checks the key rules are still there.
- **Profile patch:** `--patch-profile` (and the merge tool's `patch_profile`) now replaces the old command table in your `ba-profile.mdc` with the one-line pointer, keeping rows for your own commands. Nothing else in the profile changes. Your `ba-assistant-config.mdc` is never touched by the tools: `docs/PERSONALISED-UPGRADE.md` has a prompt to trim it to values only.
- `skills/ba-assistant/VERSION` now says 15 (it still said 14).

### Tests

- `python3 tests/run_all.py` adds end-of-day (roll and canvas prompt), install and upgrade (installs Version 14, personalises it, upgrades, and pins what is kept), and merge-tool (full flow on a personalised install with its own naming) suites, and `test_efficiency_scripts.py` (actions, capture, drift scan, metrics, canvas render, snapshot slices, and doc checks that nothing tells the agent to read every file for a canvas).

## Version 14 - 2026-09-25

### Version 14 tight fix set

- **Which initiative (P1):** session start no longer treats the newest `SESSION-CONTEXT.md` as this chat's initiative. It names one only when the open workspace is that initiative's folder or only one exists; otherwise it lists them and the assistant asks. No drafting or writing against a guessed initiative. The stop reminder and pre-compact snapshot do nothing without a named initiative. With none named, the Jira DoR gate checks every initiative.
- **BA actions only (P2):** debrief's approve path writes `_workstream/ba-actions.json` (never `workboard.json → personal_tasks[]`); the session banner counts open BA actions from `ba-actions.json`.
- **Jira create (P3):** draft → BA reviews → **Create in Jira** → create via Runlayer. No create before approval. No dependency on an unshipped `jira-templates` skill (optional formatting only).
- **Schema check (P4):** internal checklist in `ba-story-writing` replaces the unshipped `Schema_Field_Validator`; warn and confirm, never block on a missing skill.
- **Stop reminder (P5):** comments no longer claim a per-prompt injection; still off unless `stopFollowup: true`.
- **Downloads (P6):** session start scans `paths.downloadsPath` from `/setup` (env var overrides) plus `~/Downloads`.
- **Your settings are used:** `execution-router.mdc` maps every placeholder (`[BA name]`, `PROJ`, Jira/Confluence site, paths, domain) to the `/setup` values. New-initiative and intake pre-fill Jira/Confluence from config; research starts from `domainDocs`. Setup now asks for domain docs. Fixed the workboard canvas and calendar EOD scripts reading the wrong config keys and keeping the trailing comment in `name`.
- **Housekeeping:** user guide skill and command inventory matches the package; dangling names removed (`slash-commands-ux.md`, `agent-memory`, `mcps/`, `/summary`, old status publisher); shared-repo guard compares folders, not string prefixes; resume read order lives only in `SKILL.md` Step 2.
- **Recheck fixes:** one initiative reached through two roots (`initiatives/` and `Initiatives/` on a case-insensitive Mac disk) now counts once, so the single-initiative case no longer asks. Shared-repo guard shell mode checks the folder the git command runs in (cwd, `cd`, `git -C`), not whether the command text mentions the repo path. User guide no longer claims a skill count.
- **Tests:** `python3 tests/run_all.py` runs the DoR gate, hook, and package consistency suites. Repo only: never installed, never run while you use the assistant.

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

### Version 14 fix pass

**If you already installed:** the upgrader never overwrites your `~/.cursor/rules/ba-profile.mdc`, so edit two rows in its commands table by hand (or copy just those rows from the package's `rules/ba-profile.mdc`):
- `/wrap`: "Chat checkpoint only. Capture this chat into session context and the tracker. No workboard refresh."
- `/validate-state`: "Check this whole chat against the initiative files, write anything missing (`SESSION-CONTEXT.md`, tracker, `status-data.json` where they exist, and this chat's BA actions in `ba-actions.json`), then confirm a new chat can pick up." It is no longer a read-only report.

- **Jira DoR gate:** Story creates through Runlayer's `execute_tool` (for example `createJiraIssue`) are now checked, not waved through. The gate reads the final `result` of a DoR check, so a story that failed once and then passed is no longer blocked. It also reads the flat `issueTypeName` field, so a Bug that mentions a story is not blocked. If Python is missing, MCP calls are allowed instead of all being blocked. 7 new test cases (20 in total).
- **DoR writer:** `ba-story-writing` now writes `status-data.json → dorChecks` (`storyTitle`, `storyKey` if known, `result`) at the same time as the tracker register. It no longer relies on a `DoR: PASS` stamp in the Jira description.
- **Initiatives folder:** hooks find `~/.cursor/initiatives` and `paths.initiativesRoot` from `ba-assistant-config.mdc` with no environment variable. Old folder names still work as fallbacks. Debrief reads from the initiatives folder and matches the initiative against what is on disk (the hard-coded keyword table is gone).
- **Shared repo path:** `/handover` stores it as `paths.sharedRepoRoot` in `ba-assistant-config.mdc`, and the leak guard reads it from there. The guard only blocks when a path is set.
- **`/wrap`, end of day, retro:** `/wrap` is a chat-only checkpoint everywhere. "Done for tonight" / "end of day" goes to `/workboard end-of-day`. A retro only runs on `/retro` or when you ask for one.
- **End of day mail:** removed the call to a mail script that never shipped. It does a light Outlook check through MCP if connected, otherwise it says "Mail: unable to check" and carries on.
- **Upgrade:** now updates hook scripts, merges `hooks.json`, installs every command (including `/close`), updates companion skills and workboard helper scripts. Your profile, config, initiatives, and `_workstream` data are still untouched. Reinstalling no longer stacks duplicate prompt hooks, and the unused session-start prompt hook has been removed.
- **Skills:** every sub-skill has `name`, `description`, and `disable-model-invocation: true`, so they no longer jump into a chat on their own. The orchestrator and slash commands still open them. The personal config template is always-on (`alwaysApply: true`).
- **Commands** use `~/.cursor/skills/ba-assistant/...` paths. `/reanchor` and bootstrap no longer read all of `hook-contracts.md`.
- Removed leftover personal product and team names from examples. Two new conformance checks: a mail script that is referenced but missing, and command paths without `~/.cursor/`.

### Version 14 re-review follow-ups

- `/validate-state` now walks the whole chat, writes anything missing, re-reads the files, and ends with "Safe to start a new chat: yes/no".
- Jira DoR gate: when the active initiative is known, only its own DoR passes count (a same-titled pass in another initiative no longer lets a Story through). New test case (21 in total).
- Removed the `beforeSubmitPrompt` hook: Cursor ignores its output. Install and upgrade remove the old entry from existing `hooks.json` files.
- Install prompts now say to run `tools/install-ba-assistant.py` rather than copy files by hand (a hand-copied `hooks.json` has the wrong Python command).
- Sync gates point at `references/canonical-ownership.md`; diagram routing points at `references/visual-output-format.md` instead of the retired visual-storytelling folder.
- Conformance check no longer warns about missing sub-skill counts in `SKILL.md` (0 FAIL, 0 WARN).

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
