# Canonical ownership (Wave 5)

**Owner:** State Validator (`sub-skills/ba-state-validator/SKILL.md`)
**Loaded:** on demand when writing state, validating drift, or resolving conflicts. Not at orchestrator bootstrap.

The BA Assistant uses multiple state files. Each owns specific facts. The State Validator enforces consistency between them and downstream artefacts.

**Exception:** `status-data.json` is a **derived cache**, regenerated from the tracker + Jira before any canvas/status/metrics read, except for Jira-synced ticket statuses, workstream states, and confidence scores, which remain status-data-canonical.

## Ownership table

| Fact type | Canonical source | Derived to |
|---|---|---|
| Narrative RAID (decisions, reasoning, evidence) | `initiative-tracker.md` | status-data.json structured fields, canvas RAID tab, status page Living Tracker |
| Decisions (text + rationale) | `initiative-tracker.md` | status-data.json decisions[], canvas Tracker tab |
| Decisions (structured: ID, owner, date) | `status-data.json decisions[]` (synced FROM tracker) | canvas, status page |
| Open questions | `initiative-tracker.md` | status-data.json, canvas |
| Assumptions | `initiative-tracker.md` | status-data.json, canvas |
| Risks | `initiative-tracker.md` | status-data.json, canvas |
| Dependencies | `initiative-tracker.md` | status-data.json, canvas |
| Ticket statuses | `status-data.json` (synced from Jira) | canvas, status page |
| Workstream states (per scope) | `status-data.json` | canvas Workstreams tab, status page |
| Confidence scores | `status-data.json` | canvas, status page |
| Sponsor / PM / Tech Lead names | `status-data.json → initiative` | every artefact, README.md |
| pmApproval state | `initiative-tracker.md` (PM approval register) | `status-data.json → initiative.pmApproval` (derived mirror), DRAFT banner everywhere |
| DoR checks | `initiative-tracker.md` (DoR checks register) | `status-data.json → dorChecks` (derived mirror), canvas metrics |
| MoSCoW ratings + overrides | `initiative-tracker.md` (MoSCoW register) | `status-data.json → requirements[].moscowMatrix` (derived mirror), canvas MoSCoW tab |
| Sign-offs | `initiative-tracker.md` (Sign-offs register) | `status-data.json → signOffs` (derived mirror), canvas Sign-offs tab |
| Workspace context (Jira project, Confluence space, parent page) | `confluence-pages.json` + `status-data.json` | every artefact, README.md |
| Initiative status line in README.md (Active / Closed) | `workboard.json → initiatives[].status` | README.md only (written by `ba-initiative-closeout` at close; never a second SoT for status) |
| Outcome summary (closing paragraph in README.md) | Closure retro output (`ba-retrospective-and-learning`, Type 3) | README.md only, written once at closeout |
| This-session decisions, blockers, OQs (before confirmed) | `SESSION-CONTEXT.md` | promoted to tracker / status-data.json at session end |
| Cross-initiative patterns | `learnings.md` | Anti-Pattern Detector watchlist |
| Confluence page registry | `confluence-pages.json` | every artefact that publishes |
| Superseded Confluence pages | `superseded-pages.json` | skipped in context gathering |

## Conflict resolution rules

When the same fact appears in multiple files with different values:

1. **Tracker wins over status-data.json** for narrative facts (decisions, RAID, OQs, assumptions, dependencies). status-data.json is a structured view; the human-edited tracker is the source.
2. **status-data.json wins over tracker** for machine-derived facts (Jira ticket statuses, workstream computation, dates from Jira changelog).
3. **Most recently human-modified wins** for facts that could be either (e.g. a manually-set milestone date). The State Validator reports last-modified timestamps and asks the user to confirm.
4. **SESSION-CONTEXT.md is never canonical for facts that should outlive the session.** At session end, promote session decisions/blockers to tracker or status-data.json. Until promotion, treat SESSION-CONTEXT.md as draft.

## Update discipline (per fact type)

When a skill records new facts:

- Decisions, RAID, OQs, assumptions, dependencies → write to **`initiative-tracker.md` first**. Project Canvas regenerates the structured view into status-data.json on next refresh.
- Ticket status changes → **`status-data.json`** (via Jira Sync).
- Workstream state changes → **`status-data.json`**.
- Session-scoped notes (meeting outcomes, today's tentative decisions) → **`SESSION-CONTEXT.md`**.

The Anti-Pattern Detector triggers when:

- A new fact is written to status-data.json without a corresponding tracker entry (likely wrong source)
- A decision is logged in SESSION-CONTEXT.md but not promoted to the tracker by session end
- The canvas or HTML is regenerated without first regenerating status-data.json from the tracker
