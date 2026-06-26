# Skill: Delivery Definition

## Standards used

- `references/user-story-format.md` — story / spike / bug / enabler structure, INVEST, DoR checklist
- `references/raid-format.md` — any RAID entries created during delivery definition (typically new risks or assumptions)

If standards conflict with skill-specific guidance below, the standard wins.

## Description

The Delivery Definition skill converts the shaped solution and feature slices into a delivery backlog.  It creates epics, user stories, spikes, and acceptance criteria, ensures that each item meets the definition of ready, and proposes a delivery sequence.  It interacts closely with the Feature Slicing and Sequencing skill for sequencing logic and with the Requirements skill for traceability.  This skill is responsible for producing a backlog that engineers can start working on with minimal uncertainty.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (epics, stories with acceptance criteria, DoR evaluations, story-level dependencies, MoSCoW evaluations). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant\SKILL.md → Co-thinking and artefact production protocol` — surface planned artefacts upfront and ask the user to select. The Jira drafting flow is especially prone to over-production once a template is in place.

## Workspace setup — confirm before drafting

Before drafting any tickets or epics, this skill MUST confirm:

1. **Which Jira project** will the tickets be created in? (e.g., PROJ, TEAM)
   - **Wave 4** — first read from `status-data.json → initiative.jiraProjectKey` (captured at intake). If present, use it without re-asking; only ask if missing.
2. **Which Jira issue type templates** are expected? Some projects use custom templates with specific fields, custom fields, or labels.
   - **Wave 4 — Jira template story** — first read from `status-data.json → initiative.jiraTemplate` (captured at intake). If a template was provided:
     - Use the captured structure (description sections, custom fields, labels) for every new story drafted.
     - Tell the user: "Using template from PROJ-XXXX (captured at intake). New stories will follow: [list sections]."
     - If user wants a different template, confirm via `AskQuestion`.
   - If no template was captured at intake (user skipped), prompt now: "What template story should I base new tickets on? Paste key, use most recent, or skip and use generic format."
3. **Which Confluence space** holds the requirements and design documents?
   - First read from `status-data.json → initiative.confluenceSpace`.
4. **What is the parent epic key**, if epics already exist?
5. **What is the link convention** — should stories link to a specific requirements page, a parent epic, or both?

If MCP connections to Jira and Confluence are available, query for the project's existing ticket structure and use the same patterns. If templates exist, ask the user to confirm which template to use before drafting.

Never assume — always ask or confirm.

## Mandatory hooks

Before any story is marked as ready, this skill MUST invoke:

1. **Schema Field Validator** — for every story that touches a data model,
   table, or API schema. Stories that propose a field, change a field, or
   query a field must pass the validator before reaching ready state.

2. **Requirements Interrogator** — for every requirement that a story is
   satisfying. If a story is being written against a requirement that has
   no interrogation output, halt and invoke the Interrogator first.

3. **Definition of Ready** — runs as the final check on every story.

## Tasks

1. **Map slices to epics** – For each feature slice defined in the slicing phase, create one or more epics that capture the key objectives and requirements.  Ensure each epic aligns with the problem statement, requirements, and solution direction.
2. **Write user stories** – Break each epic into user stories that follow a clear template (e.g., As a <user>, I want <capability> so that <benefit>).  Each story should be an independently valuable, testable chunk of work tied to specific requirements and slices.
3. **Define spikes and technical investigations** – Identify technical questions or uncertainties that require investigation before coding.  Write spikes with clear objectives and expected outcomes.
4. **Document acceptance criteria** – For each story and spike, define acceptance criteria that are specific, measurable, and testable.  Base these on requirements, compliance/legal considerations, data expectations, and design outcomes.
5. **Identify dependencies** – Note any dependencies between stories (e.g., one story must be completed before another).  Mark dependencies on external teams, systems, design, compliance, or data availability.
6. **Check definition of ready** – Ensure each story is ready for development: requirements are clear, dependencies identified, acceptance criteria defined, and risks logged.  Use the Definition of Ready skill to validate readiness.
7. **Propose delivery sequencing** – Based on the sequencing plan from the slicing skill, assign an order to epics and stories.  Identify parallel opportunities.  Suggest staging (e.g., proof of concept, alpha release) if appropriate.
8. **Prepare backlog summary** – Provide a structured backlog overview that product managers, engineers, and stakeholders can review and approve.

## Typical Questions to Ask

- For each feature slice, what epics should capture its core outcomes?  Do these epics map clearly back to the problem, requirements, and solution direction?
- For each epic, what are the independent user stories that deliver value?  Are these stories small enough to complete in a sprint?  Can they be tested independently?
- What spikes are needed to validate unknowns (e.g., performance testing, integration feasibility, library assessment)?
- What acceptance criteria make it clear when a story is done?  Are these criteria testable and objective?  Do they include non‑functional requirements (performance, security, accessibility)?
- Are there dependencies between stories?  Which stories need completion or inputs before others start?
- Does each story meet the definition of ready (requirements understood, dependencies known, acceptance criteria defined, risks logged, sign‑offs obtained)?
- How should we sequence the backlog to balance value, risk, and dependencies?  Are there opportunities to parallelise development and analysis?  Are there slices that can be delivered as proof of concept or pilot before full rollout?

## Output format
Tickets produced by this skill conform to `references/user-story-format.md`.
Read that file before generating any ticket. The format is the authoritative source.

## Output Guidelines

The Delivery Definition skill should produce:

- **Epics list** – A list of epics with descriptions, linked feature slice, objective, success metrics, and high‑level acceptance criteria.
- **User stories list** – A table or list of user stories with columns: Story ID, Epic, Description (in user story format), Acceptance criteria, Dependencies, Priority, Status, Confidence (high/medium/low — how sure are we this story is complete and won't rework), Dev effort estimate, AI-paired effort estimate, and Notes.  Include an indication of which requirement(s) each story satisfies and link to the requirements page in Confluence.
- **Spike list** – A list of spike stories with objectives, expected outcomes, and timeboxes.  Identify which unknowns the spike addresses.
- **Delivery sequence** – A proposed order for epics and stories, indicating what can be run in parallel, what must be sequential, and where to insert proofs of concept or pilots.  Note critical path considerations.
- **Definition of ready checklist results** – For each story, summarise the definition of ready (DoR) status (e.g., Requirements ready? Dependencies identified? Acceptance criteria defined? Risks logged? Sign‑offs obtained?).  Highlight any stories that are not ready and what is missing.
- **Backlog summary** – A brief narrative summarising the backlog contents, sequence rationale, and next steps for engineering and product management.  This summary should be ready to paste into a planning tool or document.
- **Ready-to-push ticket drafts** – For each story, produce the full ticket text (title, description, acceptance criteria, labels) in the format expected by the confirmed Jira template. Invoke Communication_Drafter if a stakeholder message is needed to accompany the new tickets.
- **Traceability map** – A table linking every story → slice → requirement → design decision. Each story must trace back to a specific interrogated requirement.

## Challenge Rules

The Delivery Definition skill must enforce good backlog practices:

- **Avoid oversized stories** – If a story is too large or lacks clear acceptance criteria, prompt the user to break it down further.
- **Ensure independence** – Challenge stories that cannot be tested or delivered independently.  Suggest splitting or re‑sequencing.
- **Trace requirements** – Require each story and epic to map back to requirements and feature slices.  If a story doesn’t tie to a requirement, question its inclusion.
- **Definition of ready** – Use the Definition of Ready section (below — formerly a standalone skill) to confirm each story is ready.  If not, highlight missing inputs or sign‑offs.
- **Capture rationale** – Ask the user to explain why they ordered stories as proposed.  If the reasoning is weak, note it as an assumption or risk.
- **Avoid over‑parallelisation** – While parallel work can speed delivery, caution that too many parallel tracks may strain resources or cause integration issues.  Recommend manageable concurrency.

---

## Definition of Ready (Wave 3 — merged from ba-definition-of-ready)

This section absorbs the former `ba-definition-of-ready` skill. DoR is the gate that lives at the end of Delivery Definition — every story produced here must pass DoR before being moved into `In Progress`. Keeping DoR as a peer-level skill meant two skills had to coordinate around the same artefact (the story); merging them eliminates that hop.

### DoR description

The Definition of Ready ensures that each epic or story in the backlog meets a clear set of criteria before development begins. It verifies that requirements are understood, dependencies are known, acceptance criteria are defined, risks are logged, MoSCoW rating is captured (warn-and-flag), and necessary sign-offs are obtained. DoR acts as a gatekeeper to reduce churn during development and to give engineering teams confidence that work is actionable.

### DoR tasks

1. **Define DoR criteria** — Establish a checklist that a story or epic must satisfy before it can enter development. Typical criteria include: requirements clearly stated, scope defined, acceptance criteria agreed, dependencies identified, constraints (compliance/legal/design) considered, risks logged, sign-offs obtained, and **MoSCoW rating set for the story's scope (Wave 3 — warn-and-flag, see Task 6)**.

2. **Evaluate backlog items** — For each story or epic, assess whether it meets the DoR. If criteria are missing, flag the gaps and suggest actions to fill them (e.g., get design approval, clarify requirements, identify dependencies).

3. **Track readiness status** — Maintain a readiness status (Ready / Not Ready / Partial) for each story and summarise the reasons for items that are not ready. Communicate this to the orchestrator and delivery planning skills.

4. **Enforce stop-the-line** — If a critical DoR criterion is missing (e.g., legal sign-off), warn that proceeding may cause rework or delay. Let the user decide to proceed at risk, and log that decision in the tracker.

5. **Update the definition** — Over time, refine and adjust the DoR criteria based on feedback from engineering and product teams. Capture lessons learned about what information is truly required for smooth development.

6. **MoSCoW warn-and-flag gate (Wave 3)** — Before a story moves into `In Progress`, check that the linked requirement(s) have a MoSCoW rating for the story's **scope** (initiative / feature / cohort / slice). MoSCoW is captured in `ba-discovery-and-requirements` Task 13 as a matrix per requirement.

    **Gate behaviour — warn-and-flag, NOT hard block:**

    | MoSCoW state for story's scope | DoR status | Action |
    |---|---|---|
    | Must / Should / Could rating exists | **Ready** (other DoR criteria permitting) | Proceed normally |
    | No MoSCoW rating for this scope | **Partial — MoSCoW warning** | Surface in `/status`, Canvas tracker, and `/next`. Story can still proceed if PM explicitly overrides (decision logged). |
    | MoSCoW = Won't for this scope | **Not Ready — anti-pattern** | Flag as "building something explicitly out of scope". Block by default; PM override possible if rationale logged. |
    | MoSCoW = Could AND blocks a Must on critical path | **Partial — priority conflict** | Flag as "low-priority work blocking high-priority". Surface in `/next` for re-sequencing. |

    **Why warn-and-flag, not hard block:**
    - Initiatives with rolling cohorts often have emerging scopes where MoSCoW may not be fully captured when delivery starts (e.g. Cohort 2 is mid-discovery while Cohort 1 is delivering shared infrastructure).
    - Hard blocking would force MoSCoW capture too early and create friction.
    - Warn-and-flag gives the PM visibility and an explicit override path, with a decision log that becomes the audit trail at playback.

    **Override mechanism:**
    - PM (or PO) explicitly states "proceed without MoSCoW for [scope]".
    - DoR writes a decision into the tracker: `Decision DEC-XXX: Proceed with PROJ-XXXX (Cohort 2) without MoSCoW rating for [scope]. Rationale: [reason]. Owner: [PM]. Date: [today]. Status: Active until MoSCoW captured.`
    - The warning becomes a "tracked override" — still visible in `/status` but coloured differently (amber instead of red).
    - When MoSCoW is later captured, the override auto-closes.

    **Surface in outputs (Wave 3):**
    - **`/status`** — Workstream grid includes a `MoSCoW coverage` row per scope; red cells for unrated scopes.
    - **Canvas Tracker tab** — `MoSCoW warnings` section lists every unrated story with the linked requirement, scope, and a "Draft message to PM" action (via Communication_Drafter).
    - **Canvas Overview tab** — `MoSCoW coverage` stat (e.g. `82% (45/55)`); tone warning if <80%.
    - **`/next`** — Surfaces unrated stories under "PM hasn't rated MoSCoW for these stories" with high priority.

    **What this is NOT** — this is not requirement prioritisation by the BA. The BA captures and structures MoSCoW; the PM/PO sets it.

### DoR typical questions

- Does each story have a clear description and link to a requirement and feature slice? Are edge cases and failure modes considered?
- Are acceptance criteria specific, measurable, and testable? Do they cover non-functional aspects (performance, security, accessibility)?
- Have dependencies been identified and documented? Is work blocked by another story or external team?
- Have relevant stakeholders (PM, design, compliance, legal, operations) signed off on the story? Are approvals recorded?
- Are there any outstanding risks or unknowns that could significantly impact development? Have these been logged?
- Is the scope small enough to complete in a sprint? If not, should the story be broken down further?
- Does the story meet performance, security, and regulatory requirements? Are these captured in acceptance criteria?
- **(Wave 3)** Is there a MoSCoW rating for this story's scope? If not, who needs to set it and when?

### DoR outputs

- **DoR checklist** — A standard list of criteria that must be satisfied before development begins. The list should be customisable per initiative but start with defaults such as: requirements clarity, scope definition, acceptance criteria defined, dependencies known, risks logged, sign-off obtained, performance/security/regulatory requirements addressed, stories small and independent, MoSCoW rating captured for the story's scope.
- **Readiness status report** — For each story and epic, a status (Ready / Not Ready / Partial) along with notes on which criteria are met or missing. Provide actionable guidance on how to achieve readiness.
- **Missing inputs list** — A list of missing or incomplete items preventing readiness (e.g., missing compliance approval, unclear acceptance criteria, unknown dependencies, missing MoSCoW). Suggest who should provide each missing input.
- **DoR improvements** — Suggestions to refine the DoR criteria based on feedback or lessons learned. For example, adding a requirement to have a performance budget when working on user-facing features.

### DoR challenge rules

- **Avoid over-engineering** — Do not add unnecessary criteria that slow delivery without adding value. Tailor the checklist to the initiative's needs.
- **Clear guidance** — When marking a story as not ready, clearly state what is missing and how to address it. Avoid vague statements like "Needs clarification."
- **Respect risk appetite** — If the user chooses to proceed at risk, record that choice and the reason. Do not repeatedly block the same item once the risk is accepted.
- **Continuous improvement** — Treat the DoR as a living set of criteria; refine it based on retrospective feedback from engineering and product teams.

### Migration note (Wave 3)

This content was previously the `ba-definition-of-ready` skill. The standalone skill is now a SUPERSEDED marker; DoR runs as the closing step of Delivery Definition.


