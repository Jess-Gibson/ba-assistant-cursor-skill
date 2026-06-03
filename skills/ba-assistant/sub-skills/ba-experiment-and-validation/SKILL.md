---
name: ba-experiment-and-validation
description: SUPERSEDED — merged into ba-discovery-and-requirements. Experiments, POCs, and validation work now live as a section within Discovery and Requirements.
---

# SUPERSEDED — see `ba-discovery-and-requirements`

This skill has been **merged into `ba-discovery-and-requirements`** as of Wave 3 (May 2026).

## Why merged

Every assumption surfaced during discovery is a candidate for an experiment. Every experiment outcome feeds back into requirements (validates, invalidates, or refines them). In practice the BA always invoked both skills as a pair — discover something, design an experiment to validate it, capture the result, update the requirement. Keeping them as separate skills required a deliberate context switch between two activities that are operationally inseparable.

By merging:
- Assumptions flow directly from discovery into validation plans
- Experiment outcomes auto-trigger Requirements_Interrogator (Rethink mode) when they invalidate an assumption underlying a requirement
- One less hook to maintain — `ba-discovery-and-requirements → ba-experiment-and-validation` is now internal
- The cognitive load of "is this discovery or validation?" disappears — it's one loop

## Where the content moved

| Old section in `ba-experiment-and-validation` | New location in `ba-discovery-and-requirements` |
|---|---|
| Description | `## Experiment and Validation (Wave 3) → Experiment description` |
| Tasks 1–6 | `### Experiment tasks` |
| Typical Questions to Ask | `### Experiment typical questions` |
| Output Guidelines | `### Experiment outputs` |
| Challenge Rules | `### Experiment challenge rules` |

## What stayed the same

- The Experiment/Pilot plan template (Objective / Method / Metrics / Success criteria / Duration / Data collection / Ownership) is unchanged.
- Assumption tracking still happens in `ba-risk-and-tracker → tracker.assumptions[]` with a `validation` field linking to the experiment plan.
- `pm-data-analyst` is still invoked for warehouse queries.
- All other skills (`ba-solution-shaping`, `ba-solution-evaluation`, etc.) still consume the same experiment outputs.

## What to do

If you were planning to invoke this skill, invoke `ba-discovery-and-requirements` instead and read the "Experiment and Validation" section. Validation is no longer a separate phase — it's part of the discovery loop.
