---
name: ba-project-canvas
description: Generates and maintains an interactive tabbed Cursor canvas and HTML snapshot of an initiative's status.
disable-model-invocation: true
---

# BA Project Canvas

> **Hook ids:** this skill names `HK-...` ids. Open that row in `~/.cursor/skills/ba-assistant/hook-contracts.md` if you need the contract. Do not read the whole file.

Generate and maintain an interactive Cursor Canvas dashboard for any BA/PM initiative. The canvas provides a visual, tabbed overview of project state  -  a living status board you can open beside the chat.

**This skill is self-bootstrapping.** It works whether or not the user has previously run the BA Assistant, whether or not project files exist, and regardless of project maturity. It gathers its own context, adapts to what's available, and produces the canvas.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (canvas .tsx, status-snapshot.html, status-data.json, optionally intake-form.canvas.tsx). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `references/co-thinking-protocol.md`. Canvas is on demand only (`/canvas`); never auto at `/status`, Phase 0 or phase gates.

---

## How this skill is organised

The canvas and HTML snapshot are **rendered by a script** (`_workstream/render-initiative-canvas.py`) from `status-data.json`. You keep the data right; the script draws the 8 tabs the same way every time. Read only the capability file for your task.

| Task | Read |
|---|---|
| Generate or refresh the canvas + HTML (`/canvas`, or a direct request for a project canvas / dashboard / visual status) | `canvas-generate.md` (the whole procedure) |
| Build an intake form canvas after a direct user request | `intake-form-canvas.md` |
| Compute or display quality metrics (`/metrics`, `/status` metrics section, retro feed) | run `_workstream/compute-metrics.py`; `metrics.md` explains what they mean |
| Update status-data.json, publish a status page (`/publish-status`), data validation | `status-page-and-data.md` (+ `references/status-page-format.md`) |
| Schema questions (field names, state values, scope objects) | `references/canvas-data-model.md` |
| Change how the canvas looks (template maintenance only) | `canvas-tab-specs.md` (design reference; never needed to make a canvas) |

---

## Non-negotiables

1. **On demand only.** Render only on `/canvas` or a direct request. Never automatically: not on `/status`, resume, Phase 0, gates or decisions. `/status` may offer it in one line.
2. **The script renders, you do not.** Never read every project file for a canvas, and never hand-write or hand-edit `.canvas.tsx` code. Fix `status-data.json` and re-run.
3. **Always 8 tabs, always both outputs.** The template guarantees `overview | workstreams | features | timeline | dependencies | traceability | critical-path | tracker` and the script writes the `.canvas.tsx` and `status-snapshot.html` together. Empty tabs show what data they need.
4. **Honest data.** Jira is the source of truth for tickets when reachable; nothing is `done` until confirmed; compliance-gated items stay pending until the sign-off is recorded; scope labels are real business names. Details in `canvas-generate.md`.
5. **DRAFT banner** shows on every tab while `initiative.pmApproval.status` is anything but `approved` (absent counts as pending). The template does this; keep `pmApproval` accurate.
6. **In-progress is blue** everywhere (the template's theme tokens handle it).

## When to invoke

- User runs `/canvas`, or asks for a "project canvas", "project dashboard", "visual status"
- User independently and directly requests an intake-form canvas

## Canvas location and naming

Single living canvas per initiative, overwritten on each render: `~/.cursor/projects/<workspace>/canvases/<slug>-status.canvas.tsx` (the script finds an existing one, or pass `--canvas`). HTML: `<initiative folder>/status-snapshot.html`. Intake form variant: see `intake-form-canvas.md`.

## Integration (summary)

- **Callers:** orchestrator (`/canvas`, or direct user request; `/status` only uses the metrics script). State Validator may refresh `status-data.json` from the tracker before validation, but does not generate a canvas.
- **Calls:** `ba-jira-sync` before any ticket-data use (HK-CANV-JIRA-sync); Risk & Tracker for RAID data (HK-CANV-RT-read); Visual Storytelling standard for embedded diagrams (HK-CANV-VIS-embedded → `references/visual-output-format.md`); internal Data Model section (HK-CANV-DATA-internal → `status-page-and-data.md`).
- Hook contracts live in `hook-contracts.md`; this table is a summary, not the API.

## Data model

`references/canvas-data-model.md` is canonical for the status-data.json schema, workstream state transitions, scope objects, and metric formulas. The operational data tasks (create/update status-data.json, date-aware computation, validation rules, migration, status page publication) are in `status-page-and-data.md`.
