# Activity Map Standard

**Location:** `~/.cursor/skills/ba-assistant/references/activity-map.md`
**Owner:** execution-router (routing), this standard (the map)
**Last reviewed:** 2026-08-03 (Version 10: model-tier column removed; Auto-balance assumed)

The single source of truth for how the BA Assistant's sub-skills group into **activities** and how each skill gets invoked. The user drives by activity ("I'm framing a problem", "I'm shaping a solution"), not by remembering 25 skill names. Leave the Cursor model picker on Auto-balance; do not print model-tier nudges.

This map replaces the old "Specialist Skills" table in `ba-profile.mdc`. Workstreams (M0–M8) describe **where the initiative is**; activities describe **what kind of thinking the current task needs**. A Discovery-workstream task can still be a Frame activity (e.g. reframing the problem mid-discovery).

---

## 1. The five activities + cross-cutting monitors

| Activity | The thinking | Typical moments |
|---|---|---|
| **Frame** | Divergent, strategic  -  what problem, who cares, what would success mean | Intake, workshop design, sponsor/stakeholder strategy, problem interrogation |
| **Discover** | Evidence-gathering  -  how it works today, what's actually required | Current state, requirements extraction, data investigation, debriefs |
| **Shape** | Option thinking  -  futures, trade-offs, slices, sequence | Solution options, ADR/spike identification, feature slicing |
| **Deliver** | Convergent, precise  -  stories, tickets, handover to engineering | Story writing, Jira sync, dev handover, change strategy |
| **Run** | Mechanical, stateful  -  status, canvas, publish, retro, wrap, workboard | /status, /canvas, /publish-status, /workboard, /wrap, retro, evaluation |

**Cross-cutting monitors** run continuously inside whatever activity is active. They are never invoked by name.

## 2. Invocation types

| Type | Meaning |
|---|---|
| **Router-picked** | A tier-1 activity the execution router engages from the user's intent |
| **Specialist (auto-load)** | Pulled in automatically by the active activity; the user never names it |
| **Monitor** | Continuous background; fires on triggers, not invocation |
| **Explicit** | User-initiated (command or clear request)  -  has side effects, is a gate, or is a distinct deliverable |

## 3. The map

| Skill | Activity | Invocation |
|---|---|---|
| ba-setup | Onboarding | Explicit (first run) |
| ba-intake-reviewer | Frame | Specialist |
| ba-workshop-design | Frame | Specialist |
| ba-sponsor-engagement | Frame | Specialist |
| ba-stakeholder-strategy | Frame | Specialist |
| ba-requirements-interrogator | Frame + Discover | Specialist |
| ba-current-state-assessment | Discover | Specialist |
| ba-discovery-and-requirements | Discover | Specialist |
| ba-data-investigation | Discover + Shape | Specialist (hooks) + Explicit |
| ba-meeting-debrief | Discover-adjacent | Explicit (auto-detected via downloads check) |
| ba-solution-shaping | Shape | Specialist |
| ba-feature-slicing-and-sequencing | Shape | Specialist |
| ba-story-writing | Deliver | Specialist |
| ba-jira-sync | Deliver | Specialist + Explicit |
| ba-dev-handover | Deliver | Explicit (gate) |
| ba-change-strategy | Deliver | Specialist |
| ba-project-canvas | Run | Explicit (`/canvas` `/status`) + auto at gates |
| ba-playback-and-enablement | Run | Specialist / Explicit |
| ba-solution-evaluation | Run | Explicit (post-launch) |
| ba-retrospective-and-learning | Run | Explicit (`/retro`) + auto-suggest |
| ba-risk-and-tracker | Cross-cutting | Monitor + specialist writes |
| ba-anti-pattern-detector | Cross-cutting | Monitor |
| ba-context-capture | Cross-cutting | Monitor |
| ba-state-validator | Cross-cutting | Monitor + `/validate-state` |
| `/workboard` (inline procedure) | Run | Explicit (`/workboard`)  -  see `references/workboard-procedure.md` |

**Companions (workspace-level, not sub-skills):** publish-docs-to-confluence (Run, explicit `/publish-status`); miro-board-analysis (Frame/workshops, explicit, optional).

Notes:
- ba-requirements-interrogator and ba-data-investigation legitimately span two activities. That's connective tissue, not duplication  -  interrogation guards the Frame→Discover seam; data grounding guards the Discover→Shape seam.
- Absorbed capabilities (do not list as skills anywhere): Kickoff Preparation → ba-workshop-design (Template 1); Experiment & Validation → ba-discovery-and-requirements; Definition of Ready → ba-story-writing (closing section); Critical Path & Priority → ba-feature-slicing-and-sequencing; Communication Drafter → ba-playback-and-enablement (utility section); Status Data Model → ba-project-canvas (data layer); Visual Storytelling → references/visual-output-format.md §4/§13/§14; cross-initiative workboard → inline `/workboard` procedure (not a sub-skill).

## 4. How the router uses this map

1. Classify the turn's **activity** (alongside the existing BA-resume/BA-new/Non-BA classification) from intent signals.
2. Load the tier-1 skill(s) for that activity lazily, per `execution-router.mdc` and `skills-routing.mdc`.
3. Specialists auto-load when the active skill's hooks call them (`hook-contracts.md`).
4. Do **not** print model-tier nudges on activity transitions (Auto-balance handles model selection).
5. Monitors are always notionally on; their triggers live in `execution-router.mdc`.

## 5. Versioning

v1.1 (2026-08-03, Version 10). Model-tier column and nudge removed. Workboard listed as inline Run procedure. Adding or absorbing a skill requires updating this map in the same change.
