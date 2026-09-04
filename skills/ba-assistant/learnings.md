# BA Assistant Cross-Initiative Learnings

This file is the persistent learning loop across BA initiatives. It is:

- **Written to** by `Retrospective_and_Learning` at Type 2 (mid-initiative when a pattern is confirmed) and Type 3 (closure) retros
- **Read from** by `Intake_Reviewer` at the start of every new initiative
- **Read from** by the orchestrator at key inflection points during work
- **Updated by** `Anti_Pattern_Detector` when a learnings-watchlist item is confirmed across multiple initiatives
- **Audited by** `ba-state-validator` for pattern / trigger consistency

The format is deliberately simple: patterns, watchlist items, and skill refinements. Not a journal.

---

## File format

| Required column | Purpose |
|---|---|
| `Pattern` | One-line description of the pattern |
| `Confirmed-in` | Comma-separated initiative IDs (e.g. P001, P002) |
| `First identified` | Date + retro that first surfaced it |
| `Last confirmed` | Most recent date the pattern was observed or its trigger fired |
| `Status` | `candidate` (1 initiative) / `established` (2+) / `archived` (no activity 6+ months) |
| `Trigger ID` | Anti-Pattern Detector trigger ID (if any). `none - observational` is acceptable |
| `Evidence` | Dated log of times the trigger fired (max 5 entries) |

### Lifecycle rules

- **Candidate** (1 initiative): APD warns but does not block.
- **Established** (2+ initiatives): APD blocks by default (user can proceed at risk, logged).
- **Archived** (6+ months inactive or explicit retire): skipped by Intake and APD.

---

## Patterns (cross-initiative)

| Pattern | Confirmed-in | First identified | Last confirmed | Status | Trigger ID | Evidence |
|---|---|---|---|---|---|---|
| Document proliferation before consolidation - requirements scattered across multiple docs without a clear canonical source | P002 | mid-initiative retro | | candidate | none - observational | |
| Confluence page hierarchy not established upfront - pages created under wrong parents | P002 | mid-initiative retro | | candidate | none - observational | |
| External dependencies tracked but not chased - blockers age without escalation | P002 | mid-initiative retro | | candidate | none - observational | |
| **Regulatory / governmental initiative without external research** - assistant relied on internal wiki interpretation without reading the regulator's own publication | P003 | mid-initiative retro | | candidate | Regulatory initiative without external research | |
| **AI-generated source cites fabricated Confluence/Jira IDs** - prior-session AI page referenced IDs that 404 | P003 | mid-initiative retro | | candidate | AI source not verified / hallucinated references | |
| **v1 Phase 0 outputs presented as authoritative without explicit draft-pending-PM-approval stamp** | P003 | mid-initiative retro | | candidate | v1 outputs presented as authoritative without PM approval state captured | |
| **"Propose" treated as "do it"** - assistant acted on a cleanup recommendation without waiting for explicit go-ahead | P003 | in-session correction | | candidate | none - observational | |
| **Options analysis without engineering consultation** - architectural constraints surface late and force a full reframe | Sample-Compliance | mid-initiative retro | | candidate | Options analysis without engineering consultation | |
| **Compliance initiatives frequently expand in scope** - "simple registration" becomes multi-week architecture work | Sample-Compliance | mid-initiative retro | | candidate | none - observational (intake-reviewer flag) | |
| **Don't create detailed artefacts for unconfirmed paths** - finished drafts invalidated when approach confirmed later | Sample-Compliance | mid-initiative retro | | candidate | none - observational | |
| **BA assistant phase sequencing doesn't hold for fast-track initiatives** - discovery/slicing/shaping interleaved; use `/fast-track` | Sample-Compliance | mid-initiative retro | | candidate | none - observational | |
| **Architecture-first story generation misses downstream path coverage** - stories cover writing data but not every integration outcome | P004 | mid-initiative retro | | candidate | Architecture-first story generation | |
| **Implementation-level stories mask gap visibility** - prefer business-outcome stories so missing paths are obvious | P004 | mid-initiative retro | | candidate | Implementation detail in AC | |
| **Soft Miro pre-flight insufficient after recurrence** - mandatory Pass 2b inventory/placement + HARD gate before `layout_create` | P003 | recurring | | established | Miro board creation without pre-flight compliance | |
| **Promotion cascade must reach personal BA-actions store** - debrief/tracker capture team actions but BA-owned rows do not auto-upsert; user discovers gaps later | P003 | mid-initiative retro | | candidate | Debrief or wrap without ba-actions-sync gate | |
| **Complexity asked before sources reviewed** - user picked complexity blind, before seeing what existed in Confluence/Jira/Glean/Web | P003 | mid-initiative retro | | candidate | Silent source skip - skipped-source check not run | |
| **Incomplete AI brief requires lock block** - thin prompts on source of truth, mutate/freeze, job verb, gold bar, or ship shape led to wrong artefact; assistant must AskQuestion before drafting | P003 | in-session correction | | candidate | Thin brief lock block skipped | |
| **Remediation / bulk ops ticket without downstream outcome ACs** - re-run or reassessment fixes data but republishes downstream notifications or reopens tickets | P004 | mid-initiative retro | | candidate | Remediation without downstream outcome ACs | |

---

## Watchlist items (cross-initiative)

| Pattern | Confirmed-in | First identified | Last confirmed | Status | Trigger ID | Evidence |
|---|---|---|---|---|---|---|

---

## Skill refinements (cross-initiative)

### Anti-Pattern Detector

| Refinement | Reason | Date added |
|---|---|---|
| Trigger: debrief or `/wrap` without `Gate: ba-actions-sync: PASS` | Personal working list went stale after tracker promotion | Version 10 |
| Trigger: thin brief lock block in `agent-behavior.mdc` | Wrong artefact from assumed scope or source of truth | Version 11 |
| Trigger: remediation without downstream outcome ACs | Bulk ops tickets miss integration side effects | Version 11 |
| Reference: `markdown-readability.md` + rule | Stakeholder `.md` readable in dark mode | Version 11 |

### Requirements / register

| Refinement | Reason | Date added |
|---|---|---|
| Unified register + Mode 4 Kickoff HLR review | One canonical register; human closure before `interrogated` | Version 10 |
| Inline `/workboard` + `ba-actions` (not standalone workboard skill / not `personal_tasks[]`) | Cross-initiative view + personal actions store | Version 10 |

---

## Version

Version 11 (2026-09-04). Selective genericized patterns from prior initiative retros. Add new rows via `/retro`; do not paste personal initiative dumps.
