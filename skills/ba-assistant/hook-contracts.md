# BA Assistant — Hook Contracts Registry

This file documents **every inter-skill hook** in the BA Assistant as a stable contract. Hooks are how specialist skills delegate work to each other; without explicit contracts they drift, duplicate, or silently fail.

**Treat this file as the API.** When changing a hub skill (one called by many others), check this registry first to see what callers depend on. When adding a new hook, add an entry here.

---

## Conventions

| Concept | Meaning |
|---|---|
| **Caller** | The skill that invokes the hook |
| **Callee** | The skill (or section, post-Wave 3 merges) that the hook lands in |
| **Trigger** | The specific condition or event that causes the caller to fire the hook |
| **Inputs** | What the caller passes to the callee |
| **Outputs** | What the callee returns; what the caller does with it |
| **Failure mode** | What should happen if the callee fails, times out, or returns nothing actionable |
| **Hook version** | Semver — bump major for breaking changes; minor for additive |

### Hook ID format

`HK-<caller-prefix>-<callee-prefix>-<short-name>` — e.g. `HK-DISC-INT-pre-register`

### Status legend

- 🟢 **Stable** — well-tested, no plans to change
- 🟡 **Wave 3** — added or modified in Wave 3 (May 2026); monitor for first 2 initiatives
- 🟣 **Wave 4** — added or modified in Wave 4 (May 2026)
- 🟣 **Wave 5** — added or modified in Wave 5 (May–Jun 2026)
- 🔴 **Deprecated** — kept for compatibility but a replacement exists

### Visible status header rule (Wave 4 — MANDATORY)

**Every hook in this registry MUST be preceded by a visible status header in the chat.** This is non-negotiable. See `ba-assistant/SKILL.md → "Visible skill handoffs (MANDATORY — Wave 4 enforcement)"` for the format and rules.

If a hook fires without a header, the user loses visibility into what the assistant is doing. Treat missing headers as a bug, not a stylistic choice.

Format:

```
> Running: <Skill Name> [(mode)] → <one-line intent>
```

Completion line (after the hook returns):

```
✓ <Skill Name> complete — <one-line outcome>
```

---

## Hub skills (called by many)

These skills receive the most hooks. Changes to them are highest-risk.

| Hub skill | Hook count (in) | Why it's a hub |
|---|---|---|
| `Requirements_Interrogator` | 6+ | Interrogation gate before requirements/stories/design are accepted |
| `Risk_and_Tracker` | 12+ | All RAID, actions, decisions, sign-offs route here |
| `Visual_Storytelling` | 9+ | Every output that has a visual element calls here |
| `Communication_Drafter` *(now inside Playback)* | 12+ | Every stakeholder-facing message routes here |
| `Sponsor_Engagement` | 7+ | Sustained sponsor relationship — many phases call back |
| `Anti_Pattern_Detector` | passive (no inbound) | Watches all outputs; flags inline |
| `Meeting_Debrief` | event-driven | Called after every meeting; routes outputs to many skills |

---

## All hooks (caller → callee)

### Intake Reviewer (M0 Intake) — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-INTK-SPON-init | Sponsor_Engagement | Phase 0, after sponsor named | sponsor name, role, decision rights | Sponsor profile draft | If no sponsor identified, log as 🧨 risk and proceed | 🟡 W3 |
| HK-INTK-CSA-baseline | Current_State_Assessment | If initiative deemed `standard` or `full` complexity (Wave 3 — Step 7) | Initiative context, known systems | Current state report draft | Lean intake skips; logs as assumption | 🟡 W3 |
| HK-INTK-RT-init | Risk_and_Tracker | Always at end of Phase 0 | Initial knowns/unknowns from intake | Tracker initialised | Block — no Phase 1 without tracker | 🟢 |
| HK-INTK-CANV-init | Project_Canvas | Always at end of Phase 0 | Tracker, initial scope | Canvas + HTML snapshot at Phase 0 state | Warn; not blocking | 🟢 |

### Workshop Design (M1 Kickoff and workshop triggers) — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-WD-COMD-invites | Communication_Drafter (section in Playback) | Workshop scheduled | Workshop type, attendees, date | Invite, pre-read, post-meeting summary | Block — workshops without invites don't happen | 🟢 |
| HK-WD-STAK-attendees | Stakeholder_Strategy | Workshop being designed | Workshop purpose | Attendee list with rationale | Warn — workshop can proceed but quality drops | 🟢 |
| HK-WD-RT-raid | Risk_and_Tracker | After every workshop | Decisions/RAID/actions from workshop | Tracker updated | Block — undocumented workshops create drift | 🟢 |
| HK-WD-MD-debrief | Meeting_Debrief | After every workshop | Transcript or notes | Structured debrief routed to multiple skills | Warn — block on high-stakes workshops | 🟡 W2 |
| HK-WD-VIS-visuals | Visual_Storytelling | Workshop needs current state diagram, journey map, etc | Workshop output | Diagram | Warn — fall back to text-only | 🟢 |
| HK-WD-SPON-prebrief | Sponsor_Engagement | High-stakes workshop with sponsor invited | Sponsor profile, workshop ask | Pre-brief talking points | Block — never bring sponsor in cold | 🟡 W1 |
| HK-WD-CHG-kickoff | Change_Strategy | At initiative kickoff (Template 1) | Audience register, change burden | Initial change plan | Warn — defer to Phase 4 if change burden low | 🟡 W1 |

### Current State Assessment (M2a) — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-CSA-VIS-diagrams | Visual_Storytelling | Always — current state needs diagrams | Process/system maps | Mermaid/PlantUML diagrams | Block — undocumented current state | 🟢 |
| HK-CSA-PMDA-data | pm-data-analyst (external skill) | If quantitative current state needed | Data sources, metrics needed | Data analysis | Warn — proceed with qualitative if data unavailable | 🟢 |
| HK-CSA-GLEAN-code | Glean code-exploration (external) | If initiative is technical | Repos in scope | Code findings | Warn — fall back to interviews | 🟢 |
| HK-CSA-WD-tribal | Workshop_Design | When tribal knowledge is the gap | Audience, gap description | Tribal-knowledge workshop plan | Warn | 🟡 W1 |

### Discovery and Requirements (M2 Discovery) — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-DISC-CSA-pre | Current_State_Assessment | Before any requirements extraction (unless current state is fresh) | Initiative context | Current state report | Block by default; user can override and log as 🧨 risk | 🟢 |
| HK-DISC-INT-pre-register | Requirements_Interrogator | Before any requirement enters the register | Stated requirement, source | Provisional requirement statement | Block — uninterrogated requirements never enter the register | 🟢 |
| HK-DISC-RT-state-changes | Risk_and_Tracker | Every requirement lifecycle state change | Requirement ID, from state, to state, reason, owner | Change log entry | Block — silent state changes break traceability | 🟡 W2 |
| HK-DISC-INT-jtbd | Requirements_Interrogator (JTBD lens) | When the requirement is user-experience-related | Stated requirement | JTBD breakdown (functional / emotional / social) | Optional — skip for non-UX requirements | 🟡 W2 |
| HK-DISC-COMD-moscow | Communication_Drafter (section in Playback) | When MoSCoW is missing for a story's scope | Story, scope, PM name | MoSCoW gap message | Warn — proceed if PM overrides | 🟡 W3 |
| HK-DISC-VIS-process | Visual_Storytelling | When process/data flow needs a diagram | Process description | Diagram | Warn — fall back to text-only | 🟢 |
| HK-DISC-PMDA-validate | pm-data-analyst | When an assumption needs data validation (Wave 3 — was Experiment_and_Validation hook) | Assumption, metrics, data source | Validation result | Warn — proceed with assumption flagged | 🟡 W3 |

### Solution Shaping (M4) — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-SOL-INT-justify | Requirements_Interrogator | If a design element is justified by an uninterrogated requirement | Design element, requirement | Provisional statement | Block — design ahead of interrogation is the #1 anti-pattern | 🟢 |
| HK-SOL-INT-jtbd-check | Requirements_Interrogator (JTBD lens) | If requirement has JTBD breakdown — evaluate each option against the 3 dimensions | Solution options, JTBD breakdown | Coverage scoring | Optional | 🟡 W2 |
| HK-SOL-VIS-arch | Visual_Storytelling | Architecture/sequence diagrams needed | Solution structure | Diagram | Warn — fall back to text-only | 🟢 |
| HK-SOL-SPON-prebrief | Sponsor_Engagement | Before locking solution direction | Options, recommendation, trade-offs | Sponsor pre-brief | Block on high-stakes initiatives | 🟡 W1 |
| HK-SOL-CHG-burden | Change_Strategy | When evaluating change burden of each option | Solution options | Per-option change burden assessment | Warn | 🟡 W1 |

### Delivery Definition (M5 + DoR) — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-DEL-INT-uninter | Requirements_Interrogator | If a story is being written against an uninterrogated requirement | Story, requirement | Provisional statement | Block | 🟢 |
| HK-DEL-SFV-schema | Schema_Field_Validator (external) | If story touches a data model/API schema | Story, schema | Validation report | Block | 🟢 |
| HK-DEL-DOR-internal | DoR section (formerly Definition_of_Ready) | Final check before any story moves to In Progress | Story, requirement, scope | Ready / Partial / Not Ready | Warn-and-flag for MoSCoW; block for other failures | 🟡 W3 |
| HK-DEL-RT-moscow-override | Risk_and_Tracker | When PM overrides a MoSCoW warning | Story, scope, rationale | Decision logged | Block — overrides must be auditable | 🟡 W3 |
| HK-DEL-SPON-scope-commit | Sponsor_Engagement | Before scope commitment | Scope summary | Sponsor sign-off | Block on Must scope | 🟡 W1 |
| HK-DEL-COMD-tickets | Communication_Drafter | When ticket batch needs a stakeholder announcement | Ticket batch, audience | Draft message | Warn | 🟢 |

### Feature Slicing and Sequencing (M3 + Critical Path) — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-SLI-VIS-gantt | Visual_Storytelling | Always — sequencing needs Gantt-style timeline | Sequence plan | Gantt diagram | Warn — fall back to table | 🟢 |
| HK-SLI-RT-cp | Risk_and_Tracker | Critical path tracker entries (Wave 3 — was Critical_Path_and_Priority's outbound) | Critical path items | Tracker entries | Block — undocumented critical path is highest-risk | 🟡 W3 |
| HK-SLI-IMP-mapping | (internal — Impact Mapping section) | When user requests impact mapping | Goal, actors | Impact map artefact | Optional — alternative to traditional slicing | 🟡 W2 |

### Stakeholder Strategy — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-STAK-VIS-grid | Visual_Storytelling | Always — influence × interest grid | Stakeholder data | Grid diagram | Warn — fall back to table | 🟢 |
| HK-STAK-COMD-eng | Communication_Drafter | Per-stakeholder engagement messages | Stakeholder profile | Draft messages | Warn | 🟢 |
| HK-STAK-SPON-xref | Sponsor_Engagement | Cross-reference sponsor and stakeholder profiles | Stakeholder list | Updated sponsor profile (if sponsor was in stakeholder list) | Warn | 🟡 W1 |

### Sponsor Engagement — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-SPON-COMD-email | Communication_Drafter | Sponsor email/pre-read needed | Purpose, sponsor profile | Draft message | Block | 🟡 W1 |
| HK-SPON-VIS-onepager | Visual_Storytelling | Exec one-pager needed | Initiative summary | One-pager | Warn — fall back to text | 🟡 W1 |
| HK-SPON-RT-risks | Risk_and_Tracker | Sponsor-impacting risks need flagging | Risk description | Risk logged with sponsor-impacting flag | Block | 🟡 W1 |
| HK-SPON-STAK-xref | Stakeholder_Strategy | Cross-reference | Sponsor profile | Stakeholder grid updated | Warn | 🟡 W1 |
| HK-SPON-EVAL-postlaunch | Solution_Evaluation | Post-launch sponsor brief | Sponsor profile, evaluation results | Sponsor brief with outcome narrative | Warn | 🟡 W1 |

### Change Strategy — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-CHG-STAK-audience | Stakeholder_Strategy | Audience identification | Stakeholder list | Per-audience change segmentation | Block | 🟡 W1 |
| HK-CHG-COMD-msg | Communication_Drafter | Per-audience messaging | Audience, change content | Draft messages | Block | 🟡 W1 |
| HK-CHG-VIS-roadmap | Visual_Storytelling | Change roadmap + adoption dashboard | Change plan | Diagram + dashboard | Warn | 🟡 W1 |
| HK-CHG-SPON-backing | Sponsor_Engagement | Public sponsor backing for change (Desire phase of ADKAR) | Change ask | Sponsor backing artefact | Block — change without sponsor backing fails | 🟡 W1 |
| HK-CHG-EVAL-adoption | Solution_Evaluation | Post-launch adoption metrics | Change plan, metrics | Adoption report | Warn | 🟡 W1 |
| HK-CHG-RT-resistance | Risk_and_Tracker | Resistance/change saturation risks | Resistance signals | Risks logged | Block | 🟡 W1 |
| HK-CHG-RETRO-milestones | Retrospective_and_Learning | At change milestones | Change progress | Milestone retro | Warn | 🟡 W1 |

### Solution Evaluation (M7) — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-EVAL-PMDA-actual | pm-data-analyst | Pull actual outcome metrics | Metrics defined at intake | Actual metrics | Block — no evaluation without actuals | 🟡 W1 |
| HK-EVAL-VIS-charts | Visual_Storytelling | Outcome charts | Actual vs expected | Charts | Warn | 🟡 W1 |
| HK-EVAL-INT-rethink | Requirements_Interrogator (Rethink mode) | When actual ≠ expected | Requirement, gap | Rethink analysis | Warn | 🟡 W1 |
| HK-EVAL-RT-postlaunch | Risk_and_Tracker | Post-launch issues | Issue | Risk logged | Block | 🟡 W1 |
| HK-EVAL-RETRO-learnings | Retrospective_and_Learning | After evaluation | Evaluation findings | Cross-initiative learnings entry | Warn | 🟡 W1 |
| HK-EVAL-AP-watchlist | Anti_Pattern_Detector | Update watchlist with new patterns | New pattern | Watchlist updated | Warn | 🟡 W1 |

### Playback and Enablement (M6 + Communication Drafter section) — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-PLA-VIS-deck | Visual_Storytelling | Playback one-pager and deck | Playback content | One-pager, deck | Block — playback without visuals fails | 🟢 |
| HK-PLA-SPON-launch | Sponsor_Engagement | Before launch decision | Playback content | Sponsor launch sign-off | Block | 🟡 W1 |
| HK-PLA-CHG-coordinate | Change_Strategy | Coordinate playback with sustained change plan | Playback timing, change plan | Aligned timeline | Warn | 🟡 W1 |
| HK-PLA-WD-format | Workshop_Design (Template 7) | For the playback workshop format | Playback objective, audience | Workshop plan | Warn | 🟡 W3 |

### Meeting Debrief — outbound (this is a routing hub)

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-MD-INT-discovery | Requirements_Interrogator (Discovery) | New requirement extracted from meeting | New requirement | Provisional statement | Block | 🟡 W2 |
| HK-MD-INT-rethink | Requirements_Interrogator (Rethink/In-flight) | Requirement change extracted from meeting | Requirement change | Rethink result | Block | 🟡 W2 |
| HK-MD-RT-raid | Risk_and_Tracker | Decisions / RAID / OQs / actions extracted | Each item | Tracker updated | Block — debrief output that doesn't route to tracker is wasted | 🟡 W2 |
| HK-MD-SPON-signal | Sponsor_Engagement | Sponsor signal observed in meeting | Signal | Sponsor profile updated | Warn | 🟡 W2 |
| HK-MD-CHG-adoption | Change_Strategy | Adoption signal observed | Signal | Change plan updated | Warn | 🟡 W2 |
| HK-MD-STAK-dynamics | Stakeholder_Strategy | Stakeholder dynamics observed | Signal | Stakeholder profile updated | Warn | 🟡 W2 |
| HK-MD-AP-patterns | Anti_Pattern_Detector | Patterns observed | Pattern | Watchlist updated | Warn | 🟡 W2 |
| HK-MD-EVAL-postlaunch | Solution_Evaluation | Post-launch meeting evidence | Evidence | Evaluation updated | Warn | 🟡 W2 |
| HK-MD-COMD-summary | Communication_Drafter (section in Playback) | Post-meeting summary draft | Meeting outputs | Draft summary + action DMs | Warn | 🟡 W2 |

### Retrospective and Learning — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-RETRO-AP-watch | Anti_Pattern_Detector | At workstream-completion / phase boundary | Patterns identified | Watchlist updated | Block — retro without watchlist update is wasted | 🟢 |
| HK-RETRO-DEL-dor | Delivery_Definition (DoR section, formerly Definition_of_Ready) | Refine DoR criteria from learnings | DoR refinements | Updated DoR checklist | Warn | 🟡 W3 |
| HK-RETRO-COMD-summary | Communication_Drafter | Retro summary | Retro outputs | Draft summary | Warn | 🟢 |

### Project Canvas (includes Data Model section) — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-CANV-RT-read | Risk_and_Tracker | Reads tracker data | n/a | Tracker data | Block — canvas without tracker is empty | 🟢 |
| HK-CANV-JIRA-sync | Jira_Sync | Refresh ticket data | Project, epics | Updated tickets | Warn — proceed with stale data flagged | 🟢 |
| HK-CANV-VIS-embedded | Visual_Storytelling | Embedded diagrams in tabs | Diagram definitions | Inline SVG/Mermaid | Warn | 🟢 |
| HK-CANV-DATA-internal | Data Model section (formerly Status_Data_Model) | Read/write status-data.json | n/a | JSON | Block | 🟡 W3 |

### State Validator (Wave 5) — outbound

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-SV-JS-presync | Jira_Sync | Always before validation | Ticket list from status-data.json | Refreshed ticket statuses | Warn — proceed with stale; flag in report | 🟣 W5 |
| HK-SV-CANV-refresh | Project_Canvas (Data Model section) | Always before validation | Tracker content | Refreshed status-data.json | Block — can't validate against stale derived state | 🟣 W5 |
| HK-SV-APD-patterns | Anti_Pattern_Detector | After validation | Divergence list | Updated watchlist entries (only if patterns) | Warn | 🟣 W5 |
| HK-SV-COMD-supersede | Communication_Drafter | When pages need superseding | Page list | Supersede banner content | Warn — manual fallback | 🟣 W5 |

---

## Hook audit checklist (run before any major skill change)

Before modifying a hub skill, run through:

1. **Find inbound hooks** — search this registry for `Callee = <skill>`. List them.
2. **For each inbound hook, check:** would this change break the caller? If yes, version bump (major) and notify all callers.
3. **Find outbound hooks** — search this registry for `Caller = <skill>`. List them.
4. **For each outbound hook, check:** does the change require the callee to behave differently? If yes, update the contract here AND the callee skill.
5. **Update this file** — add new hooks, deprecate old ones with 🔴 status. Don't delete deprecated hooks for at least one initiative cycle.

## Deprecation policy

- A hook marked 🔴 Deprecated remains functional for at least one full initiative cycle after deprecation.
- After one cycle, if no caller still uses it, remove the entry and the underlying logic.
- If a caller still uses it after one cycle, raise a 🧨 risk and force the migration.

## Wave 3 hook changes summary

- **New hooks (W3):** MoSCoW gate hooks (DEL-DOR-internal, DISC-COMD-moscow, DEL-RT-moscow-override); workstream-aware hooks in Anti-Pattern Detector; scope on every tracker hook; action register hooks; data-model hooks moved internal to Canvas.
- **Internalised hooks (W3 — were external, now in-skill):** Kickoff Prep → Workshop Design; DoR → Delivery Definition; Critical Path → Slicing; Experiment → Discovery; Status Data Model → Canvas; Communication Drafter → Playback.
- **Hook name preservation:** All caller skills still use the same hook names (`Definition_of_Ready`, `Communication_Drafter`, `Critical_Path_and_Priority`, etc). The orchestrator routes those names to the new locations. Callers don't need to change.
