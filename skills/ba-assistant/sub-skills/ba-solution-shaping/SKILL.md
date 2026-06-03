# Skill: Solution Shaping

## Description

The Solution Shaping skill helps transition from understanding the problem and requirements to exploring possible solution paths.  It encourages blue‑sky thinking before committing to a technical implementation and aligns the future state with the earlier feature slices.  The skill enumerates solution options, compares their trade‑offs, identifies required spikes and ADRs, and ensures compliance, legal, design, and operations considerations are factored in.  The aim is to select or narrow down to a preferred solution direction, not to produce detailed architecture or code.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (options docs, ADRs, spike tickets, recommendation document). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant\SKILL.md → Co-thinking and artefact production protocol` — surface planned artefacts upfront and ask the user to select. Pair with the co-thinking journey when shaping each option (recommendation + reasoning + trade-off before drafting).

## Mandatory hooks

Before generating solution options or proposing any design element, this skill
MUST invoke:

1. **Requirements Interrogator** — for every requirement that a proposed
   design element is intended to satisfy. If a design element is being
   justified by a requirement that has no interrogation output, invoke
   Requirements Interrogator first. Do not proceed to design until the
   requirement is genuinely understood (not just documented).

2. **Schema Field Validator** — for every proposed field on a data model,
   table, or API response. The validator runs the five-question check
   (requirement → produced by process → authoritative source → consumer
   question → storage justification) before the field is committed to the
   schema.

These are not optional. The most common failure mode in solution shaping is
designing against an uninterrogated requirement or adding a field that
duplicates data owned elsewhere. These hooks close that loop.

## Tasks

1. **Define the desired future state** – Describe what success looks like from a business and user perspective.  Consider the target experience, performance expectations, regulatory compliance, and operational impact.
2. **Generate solution options** – List multiple approaches to achieve the desired future state.  Options can include different architectures, process changes, technology choices, service design interventions, or external integrations.  Encourage diversity of thought to avoid locking into a single path prematurely.

   To ensure genuine diversity (not minor variants of the same design), vary options along at least two of these dimensions:
   - **Storage location** — where the data lives (existing service vs new module vs new service)
   - **Integration point** — synchronous vs asynchronous, push vs pull, event vs request
   - **Build vs buy** — internal capability vs third-party
   - **Phasing** — big bang vs phased delivery
   - **Ownership** — which team owns the new capability
   - **Coupling** — tight vs loose integration with existing systems

   For each option, also state explicitly:
   - What this option does NOT solve
   - What this option assumes
   - Confidence in viability (high/medium/low)
   - Effort estimate (dev / AI-paired / risk)

   Invoke Visual_Storytelling to produce a Mermaid architecture diagram for each option.
3. **Assess trade‑offs** – For each solution option, evaluate pros/cons, costs, benefits, risks, technical feasibility, timeline impact, and stakeholder alignment.  Note how each option satisfies the requirements and interacts with feature slices.

3.5. **JTBD lens check (when a requirement has a JTBD breakdown)** – For every requirement that was interrogated with the JTBD lens (functional / emotional / social), score each solution option against all three dimensions:

   | Option | Functional | Emotional | Social | Overall JTBD fit |
   |---|---|---|---|---|
   | A | ✅ Full | ⚠️ Partial | ❌ None | Functional only |
   | B | ✅ Full | ✅ Full | ⚠️ Partial | Functional + Emotional |
   | C | ✅ Full | ✅ Full | ✅ Full | All three |

   This prevents the common pattern of choosing the lowest-cost option that satisfies the functional job but leaves the customer feeling no better — or worse, feeling worse perceived by their peers. A functionally-correct solution that misses the emotional or social job often gets reported as "we shipped it but adoption is low" at Solution Evaluation. The JTBD check catches it before commitment.

   If only one option addresses all three dimensions, that doesn't automatically make it the recommendation — cost and feasibility still matter — but make the trade-off explicit: "Option A is cheapest and meets the functional job. It does not solve the emotional or social job. We are accepting this trade-off because [reason]."
4. **Identify spikes and ADRs** – Determine which aspects of the solution require technical validation (spikes) or formal decisions (Architectural Decision Records).  Suggest specific spike questions (e.g., “Can system X handle Y throughput?”) and ADR topics (e.g., “Monolith vs microservice separation?”).
5. **Consider compliance, legal, and design** – Check whether each option meets compliance and legal requirements.  Assess the need for UI/UX design, copy updates, and service design.  If relevant, plan to involve external teams (e.g., security review).
6. **Refine requirements** – Identify new or changed requirements arising from the preferred solution.  Update the requirements documentation accordingly and trace the changes.
7. **Recommend next steps** – Suggest a preferred solution direction (or top two options) based on the assessment and rationale.  Define what validation or sign‑offs are needed to proceed (e.g., compliance approval, design mock‑ups, technical spikes completed).

## Typical Questions to Ask

- What does a successful future state look like from the perspective of users, operations, business outcomes, compliance, and legal?  How should the system behave, and what performance or reliability levels are needed?
- What are at least three different solution approaches we could take?  (Encourage options that vary technology, process, or service design.)
- For each option:
  - How does it meet the high‑level requirements and feature slices?
  - What are the pros (value, cost, speed, alignment) and cons (complexity, risk, dependencies)?
  - What new risks, assumptions, or dependencies arise?
  - What compliance or legal considerations apply?  Do we need specific approvals?
  - What design or service changes are required?  Who needs to provide input?
  - What technical questions remain unanswered?  What spikes are needed?
  - Does this option require an Architectural Decision Record?  If so, what should the ADR focus on?
- Which stakeholders need to weigh in on the options?  What concerns might they have?
- Are there compelling reasons to defer or discard any options?

## Output Guidelines

The Solution Shaping skill should produce:

- **Future state description** – A brief narrative or bullet list describing the desired future state from multiple perspectives (user, business, operations, compliance, legal).  Include performance/availability expectations and success criteria.
- **Solution options table** – A comparison table with columns: Option name, Description, Pros, Cons, Key risks/assumptions, Technical feasibility (High/Medium/Low), Compliance & legal considerations, Design/service requirements, Required spikes/ADRs, Impact on slices.
- **Spike & ADR plan** – A list of recommended spikes and ADR topics, each with a brief description of what needs to be validated or decided, and suggested owners.
- **Requirement updates** – A list of any new or changed requirements resulting from solution design.  Indicate which slice or option drove the change and whether a requirement is now mandatory or optional.
- **Recommended direction** – A short section summarising which option is preferred (or if further evaluation is needed), with rationale.  Note next steps and required sign‑offs (e.g., compliance review, design approval, technical spike outcomes).

## Challenge Rules

The Solution Shaping skill should guard against:

- **Designing against an uninterrogated requirement** — if a design element is justified by a requirement that has no Requirements Interrogator output, halt and invoke the interrogator before proceeding. This is the single most common failure mode.
- **Adding fields without validation** — every proposed schema field must pass the Schema Field Validator before being included. No exceptions, even for "obvious" fields.
- **Locking into a single solution too early** – Always ask the user to consider multiple options.  If only one option is proposed, challenge them to brainstorm alternatives.
- **Ignoring trade‑offs** – Require pros/cons and risks for each option.  If the user cannot articulate trade‑offs, mark it as an assumption and prompt to revisit.
- **Compliance and legal oversight** – Always ask whether there are any compliance or legal constraints on data retention, privacy, accessibility, or other policies.  Suggest consulting the appropriate teams.
- **Skipping spikes/ADRs** – If there are unknown technical questions or design choices, propose spikes or ADRs rather than assuming feasibility.
- **Premature detail** – Keep the solution at an appropriately high level.  Do not dive into code or detailed design; focus on evaluating options and next steps.
