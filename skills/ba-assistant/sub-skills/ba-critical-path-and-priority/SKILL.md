---
name: ba-critical-path-and-priority
description: SUPERSEDED — merged into ba-feature-slicing-and-sequencing. Critical path analysis and priority reconciliation now live as a section within the slicing skill.
---

# SUPERSEDED — see `ba-feature-slicing-and-sequencing`

This skill has been **merged into `ba-feature-slicing-and-sequencing`** as of Wave 3 (May 2026).

## Why merged

Critical path analysis and feature slicing are the same job from two angles. Slicing decides how work breaks down and is ordered; critical-path analysis zooms out to ensure that long-lead items, fixed deadlines, and priority reconciliation flow into that order. Both produced overlapping artefacts (slicing produced a sequencing plan; critical path produced a tracker that depended on it). In practice the BA could never finish one without doing the other.

By merging:
- The sequencing plan and critical-path tracker are produced together
- Priority types (business / analysis / delivery / critical-path) are reconciled in one place
- One less hook to maintain — slicing's outputs already drive the tracker
- The cognitive load of "which skill owns sequencing?" disappears — it's slicing

## Where the content moved

| Old section in `ba-critical-path-and-priority` | New location in `ba-feature-slicing-and-sequencing` |
|---|---|
| Description | Implicit (merged into slicing's description) |
| Tasks 1–6 (identify, analyse, reconcile, propose, maintain, scenario) | `## Critical Path and Priority Analysis (Wave 3) → Critical-path tasks` |
| Typical Questions to Ask | `### Critical-path-specific questions` |
| Output Guidelines | `### Critical-path-specific outputs` |
| Challenge Rules | `### Critical-path-specific challenge rules` |
| Priority types (4 types) explanation | `### Priority types — always distinguish` |

## What stayed the same

- Critical path tracker still writes to `status-data.json → criticalPath[]`.
- Canvas → Critical Path tab still renders the same data.
- All other skills (`ba-risk-and-tracker`, `ba-project-canvas`, etc.) still consume the same data.
- The 4 priority types (business, analysis, delivery, critical-path) are preserved.

## What to do

If you were planning to invoke this skill, invoke `ba-feature-slicing-and-sequencing` instead and read the "Critical Path and Priority Analysis" section. Sequencing without critical-path awareness is incomplete; the merge makes that integration mandatory.
