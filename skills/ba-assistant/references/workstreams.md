# Workstreams Standard

**Location:** `~/.cursor/skills/ba-assistant/references/workstreams.md`
**Owner:** orchestrator (`SKILL.md`, `instructions.md`) for usage; this standard (the model itself)
**Last reviewed:** 2026-09-25

This file is the canonical source for the **workstream model**: the M0–M8 list, what each workstream fundamentally is, how scope levels apply to it, what its states mean, and how its gates work. Any file that needs to reference a workstream should link here rather than re-describing the model inline.

---

## 1. Workstreams vs activities  -  two different axes

The BA Assistant has two independent classification systems that are easy to conflate:

| | Workstreams (this file) | Activities (`references/activity-map.md`) |
|---|---|---|
| **Answers** | Where is the initiative? | What kind of thinking does the current task need? |
| **Values** | M0–M8 (Intake → Change) | Frame / Discover / Shape / Deliver / Run |
| **Granularity** | Per scope (initiative / feature / cohort / slice) | Per turn / per task |
| **Changes when** | An exit gate passes for a scope | The user's intent shifts, even within the same workstream |

A Discovery-workstream (M2) task can still be a Frame activity  -  e.g. reframing the problem mid-discovery. The two are orthogonal: workstream is the initiative's position on the map; activity is the compass heading for the current step. Don't use one term where the other is meant.

---

## 2. The 9 workstreams

User-facing UI uses the friendly name only (Intake, Kickoff, etc). The `M0`–`M8` codes are internal cross-references used in data models (`status-data.json`), hooks (`hook-contracts.md`), and skill-to-skill calls  -  never shown in stakeholder-facing output.

| Workstream (friendly name) | Code | Old phase name | Scope level | Primary skills | Purpose |
|---|---|---|---|---|---|
| **Intake** | M0 | Phase 0 | Initiative only (one-time, at start) | Intake Reviewer, New Initiative, Sponsor Engagement | PM brief, complexity signal, workspace setup, multi-source research, initial RAID |
| **Kickoff** | M1 | Phase 1 | Per-scope  -  typically one initiative kickoff, then feature kickoffs as needed. Not used at cohort/slice granularity | Workshop Design (Template 1) | Workshop facilitation, D1 kickoff agenda, stakeholder/sponsor alignment |
| **Discovery** | M2 | Phase 2 | Per-feature / per-cohort / per-slice | Current State Assessment, Discovery and Requirements, Requirements Interrogator | Evidence-based current state, requirements extraction with MoSCoW per scope, experiments and validation |
| ↳ **Current State Assessment** (sub-workstream) | M2a | Phase 2 (early) | Per-feature / per-cohort | Current State Assessment | Deep evidence-based "as-is" pass inside Discovery  -  diagrams, code dives, source vetting, tribal-knowledge capture. Runs before requirements extraction, not a separate top-level workstream |
| **Slicing & Sequencing** | M3 | Phase 3 | Per-feature (see note below) | Feature Slicing and Sequencing | Break the initiative into independently valuable slices; critical path; priority reconciliation; impact mapping |
| **Solution** | M4 | Phase 4 | Per-feature / per-cohort / per-slice | Solution Shaping | Future state, solution options, trade-offs, ADRs/spikes, JTBD-segmented evaluation |
| **Delivery** | M5 | Phase 5 | Per-feature / per-cohort / per-slice | Delivery Definition (includes Definition of Ready) | Epics, stories, spikes, acceptance criteria, MoSCoW warn-and-flag gate |
| **Playback** | M6 | Phase 6 | Per-feature (initiative-level playback also occurs for whole-initiative launches) | Playback and Enablement | Sign-offs, training, stakeholder communications, launch readiness |
| **Eval & Retro** | M7 + retro | New (Wave 1)  -  no direct old-phase equivalent | Per-feature / per-cohort / per-slice (post-delivery) | Solution Evaluation, Retrospective and Learning | Post-launch: measure actual vs expected outcomes; workstream-completion / mid-initiative / closure retros |
| **Change** | M8 | New (Wave 1)  -  previously implicit inside Playback | Initiative (sustained  -  spans pre- and post-launch) | Change Strategy | Sustained ADKAR-based organisational change management across impacted audiences |

**Note on Slicing & Sequencing (M3) scope:** `instructions.md` and `SKILL.md` describe M3 as per-feature. `BA_Assistant_User_Guide.md` previously described it as initiative-level (the initial decomposition of the initiative into features happens once, at initiative scope, before per-feature re-slicing occurs later). Both are true at different points in an initiative's life; this file states per-feature as the steady-state scope. Flagged for confirmation  -  see the consolidation report that introduced this file.

**Note on scope-level lists for M2/M4:** source files disagreed on whether Discovery (M2) ever runs at initiative scope, and whether Solution (M4) applies at cohort scope. This file takes the union of all scope levels mentioned across sources. Treat the "Scope level" column as the superset until confirmed; see the same consolidation report for detail.

Cross-cutting capabilities run continuously across all workstreams and scopes, and are not workstreams themselves: Risk & Tracker, Stakeholder Strategy, Sponsor Engagement, Anti-Pattern Detector (passive), Meeting Debrief (event-driven), Visual Storytelling, Communication Drafter (called by other skills).

---

## 3. Scopes  -  what a workstream applies to

Three scope levels, broadest to narrowest:

1. **Initiative scope**  -  the whole initiative. Used by Intake (M0), Change (M8), and cross-cutting capabilities.
2. **Feature scope**  -  one feature within the initiative. Most workstreams (M1–M7) can run per-feature.
3. **Cohort or Slice scope**  -  a finer subdivision of a feature. Some initiatives use cohorts (e.g. customer-segment style groupings); others slice by region, customer tier, or technical layer.

A single requirement, RAID item, or decision is tagged with the scope it applies to. The same requirement may carry a different MoSCoW rating for different cohorts.

**Scope labels in user-facing output must use real business names, never abstract codes** (`F-A`, `C-B`, etc). Internal IDs may be used for routing in code/data (canvas scope ids, `status-data.json` keys, Jira labels) but must never appear in text the user reads. See `SKILL.md → "Scope label naming"` for the full rule and source-of-truth order.

---

## 4. Workstream states (per scope)

Each scope tracks its own state, independently, per workstream.

| State | Meaning | Emoji |
|---|---|---|
| `not started` | Workstream hasn't begun for this scope | ○ |
| `active` | Currently running for this scope | 🔵 |
| `paused` | Started but blocked / waiting (e.g. on a stakeholder sign-off) | ⏸ |
| `complete` | Exit gate passed for this scope | 🟢 |
| `na` | Workstream does not apply to this scope level (e.g. M0 Intake at feature scope) | · |

In-progress / active cells in every visualisation MUST render in **blue**  -  never amber or brown.

`delivering` is a Delivery-workstream-only sub-state (implies stories are in flight); see `references/canvas-data-model.md` for the full state-machine including this and other schema-level detail.

---

## 5. Gates (per scope, not per initiative)

Gates are per-scope: Discovery for Feature A can complete and move to Slicing while Discovery for Feature B is still running. Each gate uses the same exit-checklist mechanics regardless of scope, just applied narrower.

| Gate | Cardinality |
|---|---|
| Intake (M0) exit gate | Per initiative (one-time, before Kickoff) |
| Kickoff (M1) exit gate | Per scope (initiative kickoff before any feature work; feature kickoff before that feature's Discovery) |
| Discovery → Slicing → Solution → Delivery (M2–M5) exit gates | Per scope (per feature, or per cohort/slice) |
| Playback (M6) exit gate | Per feature (sign-off before launch) |
| Eval & Retro (M7) | No exit gate  -  runs on cadence (default 2/6/12 weeks post-launch), not gated |

---

## 6. Worked example  -  one initiative, multiple scopes active at once

This is the reason the model exists: a single-phase model forces you to pick one "current phase" and lie about the rest. A multi-scope initiative genuinely has different workstreams active for different scopes at the same time.

| Scope | Active workstreams today |
|---|---|
| Initiative | Change (M8) active; Sponsor Engagement sustained; Risk & Tracker active |
| Feature A | Delivery (M5) active, Playback (M6) starting |
| Feature B | Discovery (M2) active; Solution (M4) active for spike S-04 |
| Feature C (mature) | Slicing (M3) complete, Solution (M4) complete, Delivery (M5) active |
| Feature D (long-running) | Discovery (M2) active, Slicing (M3) not started |

---

## 7. Backwards compatibility  -  Phases → Modes → Workstreams

The concept has had three names across iterations: **"Phases"** (original sequential model) → **"Modes"** (an intermediate parallel model) → **"Workstreams"** (current). All three names refer to the same underlying M0–M8 model; only the framing changed, from strictly sequential, to parallel-but-still-called-modes, to parallel-and-explicitly-scoped.

| Old name | Current workstream | Scope |
|---|---|---|
| Phase 0 / M0 | Intake | Initiative |
| Phase 1 / M1 | Kickoff | Per-scope |
| Phase 2 / M2 | Discovery | Per-scope |
| Phase 3 / M3 | Slicing & Sequencing | Per-feature |
| Phase 4 / M4 | Solution | Per-scope |
| Phase 5 / M5 | Delivery | Per-scope |
| Phase 6 / M6 | Playback | Per-feature |
| (new, Wave 1) / M7 + retro | Eval & Retro | Per-scope, post-delivery |
| (new, Wave 1) / M8 | Change | Initiative (sustained) |

If an initiative has a single scope (one feature, no cohorts/slices), only one workstream is active at a time and the assistant behaves exactly like the old sequential-phase model  -  "Phase 2" still resolves to "Discovery workstream (M2), initiative scope." No vocabulary change is forced on the user, and old user guides, status pages, and historic transcripts that use phase or mode language remain valid.

The workstream grid only needs to surface in `/status` and `/next` once multiple scopes actually exist.

---

## 8. Versioning

v1.0 (2026-09-25). First canonical extraction  -  consolidated from `instructions.md` ("Workstreams and Scopes"), `SKILL.md` ("Active workstreams" + "Phases / Modes"), `BA_Assistant_User_Guide.md`, and `README.md`, which previously each carried their own partial or divergent copy of this model. See those files' edit history for what they now point here instead of restating. Two scope-level discrepancies across sources (M2's initiative-scope applicability, M3's initiative- vs feature-scope framing) were reconciled by union/majority rather than by discarding either source  -  flagged above for a confidence check by whoever owns this file next.
