---
name: ba-status-data-model
description: SUPERSEDED — merged into ba-project-canvas. Status data model schema and tasks now live in the Data Model section of ba-project-canvas/SKILL.md.
---

# SUPERSEDED — see `ba-project-canvas`

This skill has been **merged into `ba-project-canvas`** as of Wave 3 (May 2026).

## Why merged

The status data model existed primarily to feed the canvas, HTML snapshot, and Confluence status page. In practice, every change to the schema also required a change to the canvas, and every canvas generation required reading the data model. Keeping them as separate skills created hook noise and split the documentation of a tightly-coupled pair.

By merging:
- The canonical schema lives with its primary consumer
- Schema changes and rendering changes happen in one file, in one diff
- One less hook to maintain (`ba-project-canvas → ba-status-data-model` is now internal)
- The cognitive load of "where does this data live?" reduces — it's all in canvas

## Where the content moved

| Old section in `ba-status-data-model` | New location in `ba-project-canvas` |
|---|---|
| Description / Why this exists | `## Data model — status-data.json` (top of section) |
| File location | `### File location` |
| Schema — scope identifier | `### Schema — scope identifier convention` |
| Schema — main structure | `### Schema — main structure` |
| Schema — modeStates | `### Schema — modeStates object` |
| Tasks 1–5 (create/update, downstream, date-aware, validation, migration) | `### Data tasks (formerly ba-status-data-model)` |
| Anti-patterns to prevent | `### Data anti-patterns to prevent` |
| Wave 3 changes summary | `### Wave 3 schema changes summary` |

## What stayed the same

- The `status-data.json` file format and location are unchanged.
- All other skills (`ba-risk-and-tracker`, `ba-jira-sync`, etc.) still read/write the same JSON.
- The `/status` and `/publish-status` commands still produce the same outputs.

## What to do

If you were planning to invoke this skill, invoke `ba-project-canvas` instead and read the "Data model" section. The data model is no longer a peer-level skill — it's the data layer underneath the canvas.
