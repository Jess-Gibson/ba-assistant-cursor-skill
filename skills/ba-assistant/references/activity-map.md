# Activity Map Standard

**Location:** `~/.cursor/skills/ba-assistant/references/activity-map.md`
**Owner:** execution-router (routing), this standard (the map)
**Last reviewed:** 2026-07-05

The single source of truth for how the BA Assistant's sub-skills group into **activities**, how each skill gets invoked, and which **model tier** each activity warrants. The user drives by activity ("I'm framing a problem", "I'm shaping a solution"), not by remembering 25 skill names. The model tier falls out of the activity.

This map replaces the old "Specialist Skills" table in `ba-profile.mdc`. Workstreams (M0–M8) describe **where the initiative is**; activities describe **what kind of thinking the current task needs**. A Discovery-workstream task can still be a Frame activity (e.g. reframing the problem mid-discovery).

---

## 1. The five activities + cross-cutting monitors

| Activity | The thinking | Typical moments |
|---|---|---|
| **Frame** | Divergent, strategic — what problem, who cares, what would success mean | Intake, workshop design, sponsor/stakeholder strategy, problem interrogation |
| **Discover** | Evidence-gathering — how it works today, what's actually required | Current state, requirements extraction, data investigation, debriefs |
| **Shape** | Option thinking — futures, trade-offs, slices, sequence | Solution options, ADR/spike identification, feature slicing |
| **Deliver** | Convergent, precise — stories, tickets, handover to engineering | Story writing, Jira sync, dev handover, change strategy |
| **Run** | Mechanical, stateful — status, canvas, publish, retro, wrap | /status, /canvas, /publish-status, /handover admin, retro, evaluation |

**Cross-cutting monitors** run continuously inside whatever activity is active. They are never invoked by name and inherit the active activity's model (they're cheap).

## 2. Invocation types

| Type | Meaning |
|---|---|
| **Router-picked** | A tier-1 activity the execution router engages from the user's intent |
| **Specialist (auto-load)** | Pulled in automatically by the active activity; the user never names it |
| **Monitor** | Continuous background; fires on triggers, not invocation |
| **Explicit** | User-initiated (command or clear request) — has side effects, is a gate, or is a distinct deliverable |

## 3. The map

| Skill | Activity | Invocation | Model tier |
|---|---|---|---|
| ba-setup | Onboarding | Explicit (first run) | Auto |
| ba-intake-reviewer | Frame | Specialist | Opus |
| ba-workshop-design | Frame | Specialist | Opus |
| ba-sponsor-engagement | Frame | Specialist | Opus |
| ba-stakeholder-strategy | Frame | Specialist | Opus |
| ba-requirements-interrogator | Frame + Discover | Specialist | Opus/Sonnet |
| ba-current-state-assessment | Discover | Specialist | Sonnet |
| ba-discovery-and-requirements | Discover | Specialist | Sonnet |
| ba-data-investigation | Discover + Shape | Specialist (hooks) + Explicit | Sonnet/Opus |
| ba-meeting-debrief | Discover-adjacent | Explicit (auto-detected via downloads check) | Sonnet |
| ba-solution-shaping | Shape | Specialist | Opus + thinking |
| ba-feature-slicing-and-sequencing | Shape | Specialist | Opus/Sonnet |
| ba-story-writing | Deliver | Specialist | Sonnet |
| ba-jira-sync | Deliver | Specialist + Explicit | Auto |
| ba-dev-handover | Deliver | Explicit (gate) | Sonnet/Auto |
| ba-change-strategy | Deliver | Specialist | Sonnet |
| ba-project-canvas | Run | Explicit (`/canvas` `/status`) + auto at gates | Auto |
| ba-playback-and-enablement | Run | Specialist / Explicit | Sonnet |
| ba-solution-evaluation | Run | Explicit (post-launch) | Sonnet |
| ba-retrospective-and-learning | Run | Explicit (`/retro`) + auto-suggest | Sonnet |
| ba-risk-and-tracker | Cross-cutting | Monitor + specialist writes | inherits |
| ba-anti-pattern-detector | Cross-cutting | Monitor | inherits |
| ba-context-capture | Cross-cutting | Monitor | inherits |
| ba-state-validator | Cross-cutting | Monitor + `/validate-state` | inherits |

**Companions (workspace-level, not sub-skills):** publish-docs-to-confluence (Run, explicit `/publish-status`); miro-board-analysis (Frame/workshops, explicit, optional).

Notes:
- ba-requirements-interrogator and ba-data-investigation legitimately span two activities. That's connective tissue, not duplication — interrogation guards the Frame→Discover seam; data grounding guards the Discover→Shape seam.
- Absorbed capabilities (do not list as skills anywhere): Kickoff Preparation → ba-workshop-design (Template 1); Experiment & Validation → ba-discovery-and-requirements; Definition of Ready → ba-story-writing (closing section); Critical Path & Priority → ba-feature-slicing-and-sequencing; Communication Drafter → ba-playback-and-enablement (utility section); Status Data Model → ba-project-canvas (data layer); Visual Storytelling → references/visual-output-format.md §4/§13/§14 (absorbed W10 — HK-*-VIS-* hooks fulfilled inline against the standard).

## 4. Model tiers per activity

| Activity | Recommended tier | Why |
|---|---|---|
| Frame | Opus (+ thinking for gnarly framing) | Divergent reasoning quality compounds downstream |
| Discover | Sonnet (Opus only if genuinely gnarly) | Mostly extraction and structuring |
| Shape | Opus + thinking | Trade-off reasoning is the highest-leverage thinking in the lifecycle |
| Deliver | Sonnet | Convergent, format-driven |
| Run | Auto | Mechanical and stateful; Auto is unmetered on paid plans |
| Monitors | inherit | Never worth a model switch on their own |

**Facts this rests on (verify as Cursor changes):** no skill or rule can change the active model — it's a thread-level picker setting; custom subagents CAN pin a model in frontmatter; Auto mode is unmetered against the credit pool on paid plans while manually-selected Opus draws from the pool at full rate. Hence: default the picker to Auto, bump to Opus+thinking when entering Frame/Shape, drop back after. The model tier nudge (`ba-profile.mdc`) prints a one-line advisory on activity transitions.

## 5. How the router uses this map

1. Classify the turn's **activity** (alongside the existing BA-resume/BA-new/Non-BA classification) from intent signals.
2. Load the tier-1 skill(s) for that activity lazily, per `execution-router.mdc` and `skills-routing.mdc`.
3. Specialists auto-load when the active skill's hooks call them (`hook-contracts.md`).
4. On an **activity transition**, print the model tier nudge (once, on the transition — never as an AskQuestion).
5. Monitors are always notionally on; their triggers live in `execution-router.mdc §4`.

## 6. Versioning

v1.0 (2026-07-05). Adding, absorbing, or re-tiering a skill requires updating this map in the same change — the map being stale is worse than no map.
