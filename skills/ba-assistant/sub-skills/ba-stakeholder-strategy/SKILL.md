---
name: ba-stakeholder-strategy
description: Stakeholder identification, influence, comms plan. Use for stakeholder strategy in BA Assistant.
---

# Skill: Stakeholder Strategy

## Description

The Stakeholder Strategy skill assists in identifying, analysing, and engaging stakeholders throughout the initiative.  It considers each stakeholder’s influence, interest, and role, and recommends how and when to involve them.  The goal is to ensure that decisions are informed by the right people, alignment is maintained, and communication is tailored to each audience.

## Tasks

1. **Identify stakeholders** – List all individuals and groups impacted by or involved in the initiative, including internal teams (PM, engineering, design, compliance, legal, operations, service design, finance) and external parties (customers, partners, regulatory bodies).
2. **Stakeholder analysis** – For each stakeholder, assess:
   - Level of influence (High/Medium/Low)
   - Level of interest (High/Medium/Low)
   - Role (Sponsor, Decision‑maker, Contributor, Reviewer, Informed)
   - Preferred communication style (Detailed reports, summaries, workshops)
   - Risk tolerance and concerns
3. **Engagement plan** – Based on the analysis, propose how and when to engage each stakeholder.  Suggest appropriate communication channels and cadences (e.g., weekly syncs, milestone reviews, ad‑hoc consultations).
4. **RACI mapping** – Create a Responsibility/Accountable/Consulted/Informed (RACI) matrix for key decisions and artefacts (e.g., problem statement, requirements, solution options, backlog readiness).  Identify who is responsible, accountable, consulted, and informed.
5. **Influence strategy** – If there are stakeholders who may block or accelerate decisions, propose strategies to gain their buy‑in or mitigate their resistance.  For example, engaging compliance early to avoid surprises or securing an executive sponsor for resource allocation.
6. **Communications planning** – Coordinate with the Playback and Enablement skill to ensure communication plans reflect stakeholder needs.  Provide consistent messaging across different audiences.
7. **Update tracker** – Add stakeholder roles, influence ratings, and engagement plans to the living tracker.  Note any changes in stakeholder influence or interest as the initiative progresses.

## Typical Questions to Ask

- Who are all the stakeholders impacted by or responsible for this initiative?  Have we considered compliance, legal, design, operations, service design, finance, data, customers, and partners?
- For each stakeholder:
  - How much influence do they have over decisions or resources?
  - How interested or invested are they in the outcome?
  - What is their role (Sponsor, Decision‑maker, Contributor, Reviewer, Informed)?
  - What are their primary concerns or motivations?
  - How do they prefer to receive information (detailed, summary, visual, meeting)?
- Are there any stakeholders who might resist the initiative?  If so, why and how can we mitigate this?
- Which stakeholders need to be engaged now vs later?  Who should be consulted for requirements, compliance, or solution decisions?
- Do we have a clear RACI for each major artefact or decision?  Who is accountable for sign‑off and approval?
- Are there stakeholders we are missing or who have gained influence over time?  Should we adjust our engagement plan?

## Output Guidelines

The Stakeholder Strategy skill should produce:

- **Stakeholder list & analysis** – A table or list of stakeholders with columns: Name/Role, Influence (H/M/L), Interest (H/M/L), Role description, Preferred communication, Concerns, Engagement notes.
- **Engagement plan** – A plan detailing when and how each stakeholder will be engaged.  Include meeting cadences, reporting formats, and involvement in key decisions or artefacts.
- **RACI matrix** – A matrix showing key artefacts or decisions along one axis and stakeholders along the other, with indicators (R/A/C/I) of their roles.  Highlight any gaps or conflicts in responsibilities.
- **Influence strategy recommendations** – Notes on how to handle stakeholders with high influence and potentially conflicting interests.  Suggest early engagement or alignment sessions.
- **Tracker updates** – Entries to update the living tracker with stakeholder roles, influence scores, engagement plans, and any changes over time.

## Challenge Rules

The Stakeholder Strategy skill should ensure:

- **Comprehensiveness** – Do not overlook stakeholders who may seem peripheral but could impact the initiative (e.g., customer support, data privacy teams, finance).
- **Objectivity** – Base influence and interest assessments on evidence (role, decision authority, past behaviour), not personal bias.
- **Balanced engagement** – Avoid over‑communicating to low‑interest stakeholders while keeping high‑interest stakeholders adequately informed.  Recommend tailored communication levels.
- **Proactive mitigation** – If a stakeholder might resist, propose a plan to address their concerns early.  Document this in the tracker.
- **Responsibility clarity** – Ensure the RACI matrix clearly assigns accountability.  If two people appear accountable, flag the conflict.

## Scope awareness (Wave 3 convention)

Stakeholders are not always initiative-wide. A compliance reviewer may matter for Feature B only; an integration partner may matter for Cohort 2 only; a UX writer may matter for a single slice. Tag each stakeholder entry with the **scope** they are relevant to, using the same scope object as every other Wave 3 tracker item:

```jsonc
{
  "level": "initiative" | "feature" | "cohort" | "slice",
  "id": "<scope id>",         // e.g. the feature, cohort, or slice id
  "featureId": "<feature id>" // required when level is "cohort" or "slice"
}
```

### Why scope matters here

- **RACI accuracy** — A stakeholder may be Accountable for one feature and only Informed for another. A single flat RACI hides this.
- **Engagement plan filtering** — `/status` and the canvas filter by scope. Stakeholders should appear in the scope they actually engage with, not as initiative-level noise.
- **Anti-pattern detection** — `ba-anti-pattern-detector` watches for "scope without an accountable stakeholder". Without a `scope` field on stakeholder entries, this rule can't fire.

### How to apply

| Stakeholder situation | Recommended scope |
|---|---|
| Executive sponsor, regulator-facing lead, change owner | `initiative` |
| Feature owner, designer, engineering lead for one feature | `feature` |
| Cohort-specific compliance reviewer, segment marketing owner | `cohort` (with parent `featureId`) |
| Single slice integration partner, slice-specific copywriter | `slice` (with parent `featureId`) |
| Cross-cutting capability (e.g. observability, data platform) | `initiative` with a note that they're sustained, not phase-bound |

A stakeholder can appear in **multiple scopes** if their role legitimately differs across them. Record one row per scope rather than collapsing into a single ambiguous entry.

### Tracker integration

When recording a stakeholder to `tracker.stakeholders[]` (per the `ba-project-canvas` data model), include `scope` alongside the existing fields (`name`, `role`, `influence`, `interest`, `engagement`). The Project Canvas Overview and RAID tabs will honour the scope filter automatically.

