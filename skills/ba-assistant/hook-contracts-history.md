# Hook contracts history

Changelog for `hook-contracts.md`. Read this only when auditing why a hook exists in
its current form, or writing up a new wave's changes, not as part of normal
operation. Split out because it was dead weight on every bootstrap read.

---

## Wave 3 hook changes summary

- **New hooks (W3):** MoSCoW gate hooks (DEL-DOR-internal, DISC-COMD-moscow, DEL-RT-moscow-override); workstream-aware hooks in Anti-Pattern Detector; scope on every tracker hook; action register hooks; data-model hooks moved internal to Canvas.
- **Internalised hooks (W3, were external, now in-skill):** Kickoff Prep → Workshop Design; DoR → Delivery Definition; Critical Path → Slicing; Experiment → Discovery; Status Data Model → Canvas; Communication Drafter → Playback.
- **Hook name preservation:** All caller skills still use the same hook names (`Definition_of_Ready`, `Communication_Drafter`, `Critical_Path_and_Priority`, etc). The orchestrator routes those names to the new locations. Callers don't need to change.

## Wave 8 hook changes summary (`ba-data-investigation`)

- **New skill:** `ba-data-investigation`, the canonical BA Assistant data-pairing skill, encoding the BA's own cross-validation / dedup-forensics / annotated-SQL / blocking-questions methodology (see `sub-skills/ba-data-investigation/SKILL.md`). Not a replacement for a generic PM-analytics skill, which remains available for standalone analytics outside BA Assistant decision points.
- **New hooks (W8):** HK-SOL-BDI-viability (Solution Shaping), HK-SLI-BDI-sizing (Feature Slicing & Sequencing), HK-RT-BDI-evidence (Risk & Tracker), HK-INTK-BDI-baseline (Intake Reviewer, extends hook 2; later renamed to HK-NEWI-BDI-baseline in Wave 10, when multi-source research moved to New Initiative).
- **Rerouted hooks (W8, were → generic pm-data-analyst, now → ba-data-investigation):** the Current State Assessment, Discovery and Requirements, and Solution Evaluation data hooks all reroute to `ba-data-investigation` (the Solution Evaluation one stays a block-on-failure hook).
- **Schema change:** `confidenceScores.*` (and the flat `confidence[]` alternative) in `status-data.json` gained an `evidence: { type: "data" | "qualitative" | "not-yet-assessed", source: string | null }` field, see `references/canvas-data-model.md`.
- **Anti-Pattern Detector additions:** "Ungrounded rating", "Options compared on gut feel only", "Stale blocking question" triggers; extended the "Missing co-thinking journey" trigger to include data-pairing hook awareness.
- **Why a new skill instead of extending a generic analytics skill:** a generic PM-analytics skill wasn't built around this assistant's specific investigation discipline (source ranking with status tags, row-level dedup/null/sentinel-date forensics before trusting an aggregate, annotated SQL, mandatory cross-validation against a second source, a persistent Blocking Questions Log and Data Quality Caveats register). Keeping it as a dedicated BA Assistant skill means every data-pairing hook across the assistant behaves consistently.

## Wave 9 hook changes summary (`ba-dev-handover`)

- **New skill:** `ba-dev-handover`, publishes confirmed analysis to the shared delivery repo, gated. Derived-publish pattern, parallel to Confluence publish. Confirmation and publication are two separate events.
- **New hooks (W9):** HK-DH-INT-confirm (handoff-and-halt, not a synchronous sub-call), HK-DH-BDI-ground, HK-DH-RT-raid (embed, never link), HK-DH-JIRA-ticket, HK-DH-SV-register.
- **State Validator extension:** dev-handover exports added to the watched artefact set; new conformance row (handover freshness vs confirmed register; no working-file links).
- **No format changes to existing artefacts.** EARS is render-at-export only; the register is untouched.

## Wave 10 hook changes summary

- **ba-visual-storytelling merged into `references/visual-output-format.md`** (§4 expanded types, §13 storytelling framework, §14 production workflow); all `HK-*-VIS-*` hooks unchanged by name, fulfilled inline against the standard. The sub-skill folder keeps a SUPERSEDED stub for redirect compatibility.
- **ba-project-canvas split into a router + 5 capability files** (`canvas-generate.md`, `canvas-tab-specs.md`, `intake-form-canvas.md`, `metrics.md`, `status-page-and-data.md`); no hook changes, HK-CANV-DATA-internal and HK-SV-CANV-refresh now point at `status-page-and-data.md`. Metric formulas deduplicated: canonical in `references/canvas-data-model.md` only.

## Proposed non-skill hook change: Miro pre-flight hard gate (never shipped)

Not a `ba-*` inter-skill hook (it's a lifecycle hook, `beforeMCPExecution`), but
logged here because a critical-gates rule set requires a matching hook-contracts update
on any gate table change. This section records a design proposal only. The
proposed hook and its script twins were never shipped or registered, so none of
the mechanics below ever became live package behaviour.

- **What was proposed:** Enforce the Miro 6-pass algorithm / Plan Review Gate with a HARD pre-flight hook and matching platform twins registered under `beforeMCPExecution`.
- **Why:** Confirmed 3rd+ recurrence of the identical failure (skip Passes 1-4, skip Plan Review Gate, build directly to `layout_create`) across separate initiatives. Per `retrospective-and-learning`'s own pattern-vs-incident rule, 2+ occurrences is a pattern; a reasoning gate that fails on the identical trigger 3 times needs harder enforcement, not a fourth reminder. See the corresponding `established` row in `learnings.md`.
- **Proposed mechanism:** Deny `layout_create` unless a fresh coordinate manifest contains both `## Board inventory (context_explore)` and `## Board placement`, with an explicit manual override after approval.
- **Proposed hardening:** Require the inventory section after a frame-on-frame overlap incident.
- **Proposed failure behavior:** Fail open on script errors so unrelated work is not blocked.
- **What actually shipped:** No gate script, platform twin, registration, or override. Miro pre-flight remains a soft/manual check documented in `rules/critical-gates.mdc` and `miro-board-analysis/algorithm.md`.
