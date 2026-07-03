# BA Assistant Cross-Initiative Learnings

This file is the persistent learning loop across BA initiatives. It is:

- **Written to** by `Retrospective_and_Learning` at Type 2 (mid-initiative when a pattern is confirmed) and Type 3 (closure) retros
- **Read from** by `Intake_Reviewer` at the start of every new initiative
- **Read from** by the orchestrator at key inflection points during work (see Active Surfacing section in `ba-assistant/SKILL.md`)
- **Updated by** `Anti_Pattern_Detector` when a learnings-watchlist item is confirmed across multiple initiatives
- **Audited by** `ba-state-validator` for pattern ↔ trigger consistency

The format is deliberately simple — patterns, watchlist items, and skill refinements. Not a journal, not a narrative, just the things that should change how the next initiative runs.

---

## File format (Wave 6)

Each pattern row carries lifecycle metadata so the file stays scannable as it grows.

| Required column | Purpose |
|---|---|
| `Pattern` | One-line description of the pattern |
| `Confirmed-in` | Comma-separated initiative IDs (e.g. P001, P002) |
| `First identified` | Date + retro that first surfaced it |
| `Last confirmed` | Most recent date the pattern was observed or its trigger fired |
| `Status` | `candidate` (1 initiative) / `established` (2+) / `archived` (no activity 6+ months) |
| `Trigger ID` | Anti-Pattern Detector trigger ID (if any). `none — observational` is acceptable |
| `Evidence` | Dated log of times the trigger fired and what happened (max 5 entries; older ones rotate) |

### Lifecycle rules

- **Candidate** (observed in 1 initiative): the APD trigger WARNS but does not block. Intake Reviewer surfaces the pattern in intake conversation with a note that it's based on one initiative.
- **Established** (observed in 2+ initiatives): the APD trigger BLOCKS by default (user can still proceed at risk, logged in tracker). Intake Reviewer surfaces aggressively.
- **Archived** (no activity in 6+ months OR explicit retire): skipped by Intake Reviewer and APD. Kept for audit. Can be promoted back if the trigger fires again.

### When to write to learnings.md

- **At Type 3 (closure retro):** Always update — new patterns, watchlist items, skill refinements, log entry.
- **At Type 2 (mid-initiative retro):** Update only when a pattern is confirmed across 2+ instances OR the user agrees it carries forward.
- **At Type 1 (workstream-completion retro):** Do not write. Workstream-level learnings stay within the initiative.
- **At Type 0 (pre-mortem):** Do not write. Pre-mortem outputs go to the tracker, not learnings.md. (Exception: if the pre-mortem identifies a risk that learnings.md should already have flagged but didn't, that's a meta-pattern — log it.)

### Promotion and decay

Once per session, the Retrospective skill reviews learnings.md for status transitions:

- Candidate → Established: pattern now observed in 2+ initiatives. Update Trigger ID's block/warn status.
- Established → Archived: pattern has had no Last-confirmed activity in 6+ months. Move to archive section.
- Archived → Established: archived pattern's trigger fires again. Restore.

The State Validator flags inconsistencies: pattern marked Established but Trigger ID is missing, pattern Confirmed-in count doesn't match initiatives listed, etc.

---

## Patterns (cross-initiative)

Patterns that have appeared across initiatives. These become default triggers in the Anti-Pattern Detector.

| Pattern | Confirmed-in | First identified | Last confirmed | Status | Trigger ID | Evidence |
|---|---|---|---|---|---|---|

<!-- Learnings are added automatically by the /retro command. You can also add entries manually following the format above. -->

---

## Watchlist items (cross-initiative)

Specific things to watch for proactively at the start of every initiative.

| Pattern | Confirmed-in | First identified | Last confirmed | Status | Trigger ID | Evidence |
|---|---|---|---|---|---|---|

---

## Skill refinements (cross-initiative)

Changes to specific skills that have been validated and should persist.

### Anti-Pattern Detector

| Refinement | Reason | Date added |
|---|---|---|

### Definition of Ready

| Refinement | Reason | Date added |
|---|---|---|

### Requirements Interrogator

| Refinement | Reason | Date added |
|---|---|---|

### Discovery and Requirements

| Refinement | Reason | Date added |
|---|---|---|

### Risk and Tracker

| Refinement | Reason | Date added |
|---|---|---|

### Intake Reviewer

| Refinement | Reason | Date added |
|---|---|---|

### Meeting Debrief

| Refinement | Reason | Date added |
|---|---|---|

### Other skills

| Skill | Refinement | Reason | Date added |
|---|---|---|---|

---

## Initiative log

A lightweight log of every initiative that has gone through the BA assistant, with one-line summary.

| Initiative | Closed | Verdict (met / partial / not met) | Top learning |
|---|---|---|---|

---

## Archive

Patterns that have had no activity in 6+ months. Kept for audit and possible promotion.

| Pattern | Confirmed-in | Last confirmed | Archived on | Reason archived |
|---|---|---|---|---|

---

*This file persists across initiatives. Do not reset it. The Retrospective_and_Learning skill is responsible for keeping it accurate and actionable.*
