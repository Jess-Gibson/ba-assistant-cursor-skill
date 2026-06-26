﻿# Skill: Antiâ€‘Pattern Detector

## Description

The Antiâ€‘Pattern Detector skill monitors the analysis and delivery process for common pitfalls and ineffective behaviours.  It alerts the user when they are deviating from best practices or repeating mistakes such as premature solutioning, overscoping, skipping slicing, ignoring compliance, and not engaging the right stakeholders.  It provides rationale for why the observed behaviour is problematic and offers corrective guidance.  This skill acts as a quality guard to ensure that the initiative stays on track.

## Continuous monitoring

This skill runs continuously, not on-demand. After every major output from
any other skill, this skill performs a quick check for anti-patterns. The
check is fast and silent â€” only when an anti-pattern is detected does the
skill produce visible output.

Specific triggers to watch for, by skill:

| Watching | Trigger | Anti-pattern flagged |
|---|---|---|
| Solution Shaping | A design element is justified by a requirement with no Requirements Interrogator output | Solutioning ahead of understanding |
| Solution Shaping | A schema field is proposed without Schema Field Validator output | Unvalidated schema |
| Delivery Definition | A story is being written against an uninterrogated requirement | Story without grounding |
| Delivery Definition | A story touches a schema and Schema Field Validator hasn't run | Story without schema validation |
| Delivery Definition | A story enters Jira without a MoSCoW rating for its scope | Missing MoSCoW (warn-and-flag) |
| Discovery and Requirements | A requirement enters the register without interrogation | Documented â‰  understood |
| Discovery and Requirements | Engineering / compliance / legal / ops not represented | Missing stakeholder |
| Risk and Tracker | Risk identified, no owner | Orphaned risk |
| Critical Path and Priority | Long-lead item not started despite deadline approaching | Critical path slipping |
| Stakeholder Strategy | Same stakeholder appears in multiple RACI matrices as accountable | Accountability conflict |
| Playback and Enablement | Sign-off requested without artefact link | Sign-off without basis |
| Intake Reviewer | Regulatory/governmental keyword detected (RBA, AUSTRAC, APRA, ACCC, OAIC, ATO, PSD2, GDPR, "surcharge ban", "interchange reform", "compliance deadline", etc.) AND `status-data.json â†’ sourcesSearched.web` is `false` OR empty | **Regulatory initiative without external research** (added May 2026) |
| Intake Reviewer | A source flagged as `AI-generated` exists in `confluence-pages.json` AND `verified` field is absent OR `notFound` array is non-empty | **AI source not verified / hallucinated references** (added May 2026) |
| Intake Reviewer | v1 Phase 0 artefacts (problem statement, success metrics, scope) exist AND `status-data.json â†’ initiative.pmApproval.status` is missing or `null` | **v1 outputs presented as authoritative without PM approval state captured** (added May 2026) |
| Intake Reviewer | Any source in the Hook 2 table is marked `SKIPPED` AND there is no corresponding user acknowledgement in `status-data.json â†’ sourcesSearched.acknowledged` | **Silent source skip â€” skipped-source check not run** (added May 2026) |
| All skills | A skill produces an output that references a Confluence/Jira ID NOT present in `confluence-pages.json` or verified via MCP within this session | **Unverified citation in output** (added May 2026) |
| All skills | A single `AskQuestion` user response (e.g. `proceed`, `yes`, `go`, complexity selection, scope selection) produces >3 artefact-class outputs in the same turn (artefact-class = file artefact, structured table, or formal document handed to the user) | **Output-completeness bias â€” single user-yes authorising unbounded artefacts** (added May 2026 RBA retro) |
| All skills | An interrogation point is reached (problem statement, success metrics, scope, requirement, decision, slice, ADR) AND the assistant produces a draft artefact without first surfacing (a) what's known with evidence, (b) explicit knowledge gaps, (c) explicit assumptions, (d) recommendation + reasoning, (e) trade-off | **Missing co-thinking journey at interrogation point** (added May 2026 RBA retro) |
| All skills | An artefact-producing skill (Intake Reviewer, Workshop Design, Discovery & Requirements, Feature Slicing & Sequencing â€” full Phase 3 invocation, Solution Shaping, Delivery Definition, Playback & Enablement, Solution Evaluation, Project Canvas, Sponsor Engagement) is invoked AND begins generating outputs without first emitting a "What I'll produce next" declaration block listing the planned artefacts | **Artefact-producing skill skipped pre-draft declaration** (added May 2026 RBA retro) |
| Any artefact-producing skill | An artefact is produced AND its structure does not match the standard in `references/<format>.md` | Standard drift â€” output diverges from reference standard (added Wave 7) |
| Visual Storytelling | A visual is produced as Mermaid AND destination is Confluence Pattern B (no native render) | Mermaid in non-rendering environment â€” should be interactive HTML (added Wave 7) |
| Visual Storytelling | A visual is produced without colour taxonomy applied | Off-standard visual â€” missing design system (added Wave 7) |
| Visual Storytelling | Flowchart >12 nodes on one page | Diagram too dense â€” split required (added Wave 7) |
| All skills | An artefact-producing skill is invoked AND has no "Standards used" section in its SKILL.md | Skill without declared standards (added Wave 7) |
| Discovery and Requirements | Requirement marked `status: confirmed` without `interrogatorOutput` path | Requirement confirmed without interrogator pass (added Wave 7) |
| Discovery and Requirements | Requirement statement uses vague terms ("performant", "user-friendly", "secure") without measurable definition | Vague requirement (added Wave 7) |
| Discovery and Requirements | Initiative `Must` priority downgraded to `Could` or `Won't` at scope level without decision link | Scope override without decision (added Wave 7) |
| Discovery and Requirements | Compliance requirement (COMP-) priority set to anything other than `Must` | Compliance optionalisation (added Wave 7) |
| Discovery and Requirements | MoSCoW values for one requirement changed >2 times in 30 days | Unstable scope (added Wave 7) |
| Status page publisher | Outcome health section absent or stale >14 days | Outcomes ignored â€” process metrics may mislead (added Wave 7) |
| Status page publisher | Previous status page not marked superseded after new one published | Stale status page live (added Wave 7) |
| Status page publisher | Page published without DRAFT banner when `pmApproval.status` not approved | Approval gate bypassed (added Wave 7) |
| Status page publisher | RAID inline with full narrative content (should link to tracker) | Status page becoming tracker (added Wave 7) |
| Any Jira write | `createJiraIssue` or material `editJiraIssue` invoked without prior `AskQuestion` in session | Clarification gate skipped (added Wave 7) |
| Any Jira write | Write uses `contentFormat: "markdown"` when panels are required | Markdown shortcut (added Wave 7) |
| Any Jira write | Story moved into active sprint while initiative `pmApproval.status: pending` | Approval gate bypassed at sprint level (added Wave 7) |
| Any Jira write | Always-check verification consideration omitted with no explanation | Silence on always-check item (added Wave 7) |

| File sync / repo publish | Agent copies >3 files to a shared/team repository in a single operation AND does not first verify per-file: (a) is the file meant to be shared, (b) is the content current (last-updated date, stage, status match reality), (c) does the file contain private/internal-only content | **Bulk file sync without content review â€” private files may leak or stale content published** (established — always diff + confirm before any multi-file push to a shared repo) |
| BA resume | User message signals resume/continue AND agent produces user-visible reply without Read of `SESSION-CONTEXT.md` and `initiative-tracker.md` in that turn | **BA-resume skipped mandatory state read** (added 3 Jun 2026) |
| Session debrief + Miro | Agent processes a session debrief that references Miro board(s) AND claims "no new information" or "already captured" without listing and cross-referencing every individual board item against the tracker | **Topic-level matching without item-level verification â€” Miro items missed** (added 27 May 2026 a sprint retro) |
| Canvas / HTML / any multi-location-state file | Agent updates a version number, date, stage, or status string in a file AND does not search (Grep) for all other instances of that value pattern in the entire file | **Partial update of multi-location state â€” stale values remain elsewhere in file** (added 27 May 2026 a sprint retro) |
| Canvas / HTML artifacts | Artifact has been incrementally updated >5 times in a session without a full read-through audit comparing all sections to the current tracker/debrief state | **Incremental drift â€” full artifact review needed after sustained updates** (added 27 May 2026 a sprint retro) |
| Miro board creation | Agent calls `layout_create` to add a frame or content to a Miro board AND has not first called `board_list_items` or `layout_read` to check existing frame positions and coordinate ranges | **Spatial blindness â€” creating Miro content without observing existing layout** (added 27 May 2026 a sprint retro) |
| Miro board creation | Agent creates a new Miro frame AND the frame's styling (fill colour, header banner style, section layout, sticky note colour convention, table schema) does not match the established pattern of existing frames on the same board | **Miro styling inconsistency â€” new frame does not match board conventions** (added 27 May 2026 a sprint retro) |
| Solution Shaping / Options Analysis | Agent produces solution options comparison (A/B/C, trade-off table, or architecture options) AND has not consulted engineering or read existing system architecture in this session | **Options analysis without engineering consultation â€” architectural constraints will surface late and force a reframe** (added Jun 2026 — compliance timeline retro) |
| All skills | A fact is written to `status-data.json` without a corresponding entry in `initiative-tracker.md` (for fact types where tracker is canonical per the ownership table) | **Wrong source â€” narrative fact written to derived state file** (added Wave 5) |
| All skills | A material decision (logged with owner + rationale) is captured in `SESSION-CONTEXT.md` AND session end indicators are present (`/status` run, "wrapping up" phrase, etc.) AND the decision has not been promoted to `initiative-tracker.md` | **Session decision not promoted to canonical** (added Wave 5) |
| Project Canvas | Canvas or HTML refresh happens AND `status-data.json` has not been regenerated from `initiative-tracker.md` since the last tracker edit | **Stale derived state â€” downstream rendered from outdated structured view** (added Wave 5) |
| State Validator | The same fact has appeared in the divergence table in 3+ sessions for the same initiative | **Repeatedly drifting fact â€” stronger update gate needed** (added Wave 5; promote to learnings.md watchlist) |
| Orchestrator | >40 user turns since SKILL.md was last loaded AND a mandatory hook is missed | **Long-thread drift â€” suggest `/reanchor`** (added Wave 5) |
| All skills (workspace root = `.cursor`) | Agent writes, opens, or references a file path under `blueprints/` or `skills/` with a leading `.cursor/` segment (e.g. `.cursor/blueprints/...`) when workspace root IS already the `.cursor` folder | **Workspace path prefix poison — Cursor will fail to open file (null URI)** (learnings pattern; use `blueprints/...` or `skills/...` directly, without the `.cursor/` prefix) |
| End-of-session | User signals wrap-up (`wrap up`, `end of session`, `done for tonight`, `checkpoint`) AND agent closes without loading **ba-retrospective-and-learning** (Type 1 minimum) | **End-of-session without retro â€” learnings not captured** (added 3 Jun 2026 cursor-path retro) |

### Mode-aware triggers (Wave 3)

Per-scope mode combinations also flag anti-patterns:

| Mode pattern (per scope) | Anti-pattern flagged |
|---|---|
| M4 (Solution Shaping) or M5 (Delivery) active while M2 (Discovery) is still active or `not started` for the same scope | Solutioning/building on incomplete discovery |
| M5 (Delivery) active for 3+ scopes simultaneously without resource confirmation | Delivery over-commitment |
| M1 (Kickoff) advancing while M0 (Intake) `not complete` | Premature kickoff |
| M6 (Playback) `complete` for a scope without M7 (Solution Evaluation) `active` or scheduled | Launched without evaluation cadence |
| M5 (Delivery) `active` for customer-facing scope, M8 (Change Strategy) `not started` | Customer change with no change plan |
| M2 (Discovery) on a scope reopened after M5 (Delivery) reached `active` | Late discovery (rework signal) |
| Same scope toggling between modes within 7 days (e.g. M5 â†’ M4 â†’ M5) | Mode thrashing |

## Initiative-specific learning

This skill maintains a per-initiative watchlist that grows during the
initiative. When the Retrospective and Learning skill identifies a pattern,
the pattern is added to this skill's watchlist for the duration of the
initiative.

Examples of initiative-specific watchlist items:
- "This initiative has a history of late scope changes â€” flag any scope
  change proposed after Phase 4"
- "This initiative had a pattern of requirements added to schema without
  interrogation â€” flag aggressively on any new field proposal"
- "This initiative has a stakeholder who tends to bypass the BA process â€”
  flag any direct PM-to-engineering communication"

After initiative close, the watchlist patterns that proved valuable across
multiple initiatives become part of the default trigger set.

## Pattern strength tiering (Wave 6)

Triggers in this detector now respect the `Status` field of their associated pattern in `learnings.md`:

| Pattern status | Detector behaviour |
|---|---|
| `candidate` (1 initiative) | Triggers WARN. Surface the issue, suggest the corrective action, but don't block. Note in the warning that this is based on one previous observation. |
| `established` (2+ initiatives) | Triggers BLOCK by default. User can proceed at risk via explicit override, which is logged in the tracker with reason. |
| `archived` | Trigger is dormant. Skipped. |
| `none â€” observational` (pattern without a trigger) | Detector ignores; surfacing happens through Intake Reviewer or active surfacing only. |

### Block override mechanism

When an Established trigger fires and the user wants to proceed at risk:

1. Detector surfaces the block with pattern context: "This is the 3rd initiative where this trigger has fired. On a previous initiative it correlated with significant rework. Proceed at risk?"
2. User responds via AskQuestion: [Address the issue first] [Proceed at risk â€” log reason] [Mark this pattern as no longer relevant]
3. If "Proceed at risk", capture the reason in the tracker. The retro at the end of this initiative will revisit whether the override was right.
4. If "Mark as no longer relevant", reduce the pattern's Confirmed-in count by 1 (or archive if the count drops to 0). This is rare but allows patterns to retire when the underlying conditions change (e.g. tooling improvement removes a failure mode).

### Sensitivity calibration

Once per initiative close (Type 3 retro), review:
- Triggers that fired but were correctly overridden (false positives â€” pattern may need refinement)
- Triggers that should have fired but didn't (false negatives â€” pattern's matching conditions too narrow)
- Triggers that fired and were correctly addressed (true positives â€” pattern is earning its place)

The retro proposes specific tuning patches via the Draft the Diffs mechanism. Sensitivity drift is itself a meta-pattern worth tracking.

## Tasks

1. **Monitor outputs** â€“ Regularly review artefacts, decisions, and plans produced by other skills (requirements, slicing, solution design, backlog, RAID logs) to identify patterns indicative of potential issues.
2. **Detect antiâ€‘patterns** â€“ Recognise common mistakes, including but not limited to:
   - Premature solutioning: jumping to technical solutions before defining the problem and requirements.
   - Overscoping: including too many features or capabilities without slicing or prioritisation.
   - Missing compliance or legal engagement: failing to involve compliance/legal early for data, privacy, or regulatory issues.
   - No slicing: going straight from initiative to epics/stories without feature slices.
   - Ignoring current state: designing solutions without understanding existing processes or systems.
   - Lack of stakeholder engagement: making decisions without consulting key stakeholders.
   - Undocumented assumptions: proceeding with assumptions that are not captured or validated.
   - Gaps in definition of ready: handing over stories without clear acceptance criteria, dependencies, or signâ€‘offs.
3. **Raise alerts** â€“ When an antiâ€‘pattern is detected, generate an alert message explaining the issue, why it is problematic, and what corrective actions to take.
4. **Suggest corrective actions** â€“ Propose specific next steps or questions to address the antiâ€‘pattern.  For example: â€œYou have started writing stories but have not performed feature slicing; please perform slicing and prioritisation before continuing.â€
5. **Update tracker** â€“ Record identified antiâ€‘patterns and corrective actions in the tracker, assign an owner to address them, and note their status.

## Output Guidelines

The Antiâ€‘Pattern Detector skill produces:

- **Antiâ€‘pattern alerts** â€“ Short messages flagged to the orchestrator or user when an issue is detected.  Each alert should describe the antiâ€‘pattern, explain why it is risky, and propose corrective action.
- **Corrective action list** â€“ A table summarising all detected antiâ€‘patterns, their impact, recommended actions, and owners.  Pass this to the Risk & Tracker skill.
- **Quality status** â€“ A periodic summary indicating whether common antiâ€‘patterns are present or absent.  Use this to reassure the user when things are on track or to prompt focus when multiple issues arise.

## Challenge Rules

The Antiâ€‘Pattern Detector must balance vigilance with practicality:

- **Avoid false positives** â€“ Do not flag solution discussions if requirements are sufficiently defined and slicing has occurred.  Context mattersâ€”only raise alerts when the antiâ€‘pattern is genuinely present.
- **Provide rationale** â€“ Always explain why an antiâ€‘pattern is undesirable and what the consequences could be (e.g., rework, misalignment, delays).
- **Suggest actions, not blame** â€“ Keep alerts constructive.  Focus on what can be done to improve, not on criticising the user.
- **Track and close** â€“ When a corrective action has been taken, mark the antiâ€‘pattern as addressed in the tracker.  Avoid repeatedly flagging the same issue once resolved.

