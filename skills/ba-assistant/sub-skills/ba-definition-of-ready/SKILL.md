---
name: ba-definition-of-ready
description: SUPERSEDED — merged into ba-delivery-definition. DoR criteria, evaluation, and the MoSCoW warn-and-flag gate now live as a section within the delivery definition skill.
---

# SUPERSEDED — see `ba-delivery-definition`

This skill has been **merged into `ba-delivery-definition`** as of Wave 3 (May 2026).

## Why merged

DoR ran exclusively as the closing step of Delivery Definition — every story produced by Delivery Definition was immediately checked against DoR. Keeping them as separate skills meant Delivery Definition always had to invoke DoR as a hook, and DoR always operated on Delivery Definition's outputs. The skills were effectively pipeline stages of the same activity.

By merging:
- DoR runs in-line at the end of Delivery Definition (no skill hop)
- The MoSCoW warn-and-flag gate (Wave 3) lives next to the story creation logic that triggers it
- One less hook to maintain — `ba-delivery-definition → ba-definition-of-ready` is now internal
- The cognitive load of "is this the BA writing stories or checking stories?" disappears — it's one continuous flow

## Where the content moved

| Old section in `ba-definition-of-ready` | New location in `ba-delivery-definition` |
|---|---|
| Description | `## Definition of Ready (Wave 3) → DoR description` |
| Tasks 1–5 + Task 6 (MoSCoW gate) | `### DoR tasks` |
| Typical Questions to Ask | `### DoR typical questions` |
| Output Guidelines | `### DoR outputs` |
| Challenge Rules | `### DoR challenge rules` |

## What stayed the same

- DoR criteria and the readiness status (Ready / Not Ready / Partial) are unchanged.
- The MoSCoW warn-and-flag gate (Wave 3) still works the same way — surfaces in `/status`, Canvas, and `/next`.
- The decision-log override mechanism for proceeding without MoSCoW is unchanged.
- All other skills (`ba-risk-and-tracker`, `ba-project-canvas`, etc.) still consume the same data.

## What to do

If you were planning to invoke this skill, invoke `ba-delivery-definition` instead and read the "Definition of Ready" section. DoR is no longer a separate step — it's the natural closing of delivery definition.
