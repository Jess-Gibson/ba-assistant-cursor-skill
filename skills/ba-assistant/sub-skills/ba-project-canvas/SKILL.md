# BA Project Canvas

Generate and maintain an interactive Cursor Canvas dashboard for any BA/PM initiative. The canvas provides a visual, tabbed overview of project state — a living status board you can open beside the chat.

**This skill is self-bootstrapping.** It works whether or not the user has previously run the BA Assistant, whether or not project files exist, and regardless of project maturity. It gathers its own context, adapts to what's available, and produces the canvas.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (canvas .tsx, status-snapshot.html, status-data.json, optionally intake-form.canvas.tsx). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant/SKILL.md → Co-thinking and artefact production protocol`. Auto-generation triggers (`/canvas`, `/status`, end-of-Phase-0, every phase gate) are the highest-volume invocation points.

---

## How this skill is organised (Wave 10)

This file is the router: non-negotiables, when to fire, and which capability file to read for the task at hand. **Read the capability file for your task before doing the work — the detail there is mandatory, not optional background.**

| Task | Read (in order) |
|---|---|
| Generate or refresh the canvas + HTML (`/canvas`, `/status`, phase gates, decision refresh) | `canvas-generate.md` → `canvas-tab-specs.md` |
| Offer / build the intake form canvas (Phase 0) | `intake-form-canvas.md` |
| Compute or display quality metrics (`/metrics`, `/status` metrics section, retro feed) | `metrics.md` (+ `references/canvas-data-model.md §Metric computation rules` for formulas) |
| Update status-data.json, publish a status page (`/publish-status`), data validation | `status-page-and-data.md` (+ `references/status-page-format.md`) |
| Schema questions (field names, state values, scope objects) | `references/canvas-data-model.md` |

---

## NON-NEGOTIABLE REQUIREMENTS (read these first)

These rules MUST be followed on every canvas generation or refresh. Failure to follow these rules produces an incomplete, broken output.

### 1. ALWAYS produce exactly 8 tabs (Wave 3 — was 7)

```
type TabId = "overview" | "workstreams" | "features" | "timeline" | "dependencies" | "traceability" | "critical-path" | "tracker";
```

**Never omit a tab. Never substitute a tab** (a "Compliance" tab is NOT a substitute for Traceability — project-specific content goes INSIDE the 8 tabs). If data is insufficient for a tab, render it with an empty-state Callout explaining what's needed. The most common failure mode of this skill is producing fewer than 8 tabs; the full per-tab spec is in `canvas-tab-specs.md`.

### 2. ALWAYS read ALL project files before generating

Before writing any canvas code, read every `.md` file in the project's analysis folder and related directories. Mandatory, not optional. The exhaustive list and search strategy are in `canvas-generate.md → Phase 1`.

### 3. ALWAYS produce both outputs

Every invocation produces TWO files: **`.canvas.tsx`** (interactive, 8 tabs) and **`status-snapshot.html`** (standalone, self-contained, same 8 sections, same data). The HTML spec is in `canvas-tab-specs.md`.

### 4. Canvas MUST include the interactive feature set

Multi-select scope filter (Pills), click-to-highlight in both DAGs (BFS / bidirectional), collapsible RAID cards, open/closed toggle (defaults to outstanding-only CHECKED), hover tooltips, `computeDAGLayout`, `useStatusColours()`. Details per tab in `canvas-tab-specs.md`.

### 5. Context gathering is MANDATORY, not optional

Read files first; the "ask the user" step is a FALLBACK for genuine gaps, never the starting point. Jira is the source of truth for all ticket data when the MCP is reachable — never hardcode ticket status. Full sync sequence in `canvas-generate.md → Phase 2`.

### 6. PM-approval banner is MANDATORY on Phase 0 outputs

Whenever `status-data.json → initiative.pmApproval.status` is `pending` or `requested`, the canvas AND the HTML snapshot MUST display the amber DRAFT banner at the top of every tab:

```
⚠️ DRAFT — pending approval from <pmName>
Problem statement, success metrics, scope, and RAID are draft v1 outputs. Do not treat as authoritative until PM sign-off is captured.
```

Sticky, full width, dismissible only when `status === 'approved'`. If `pmApproval` is absent (legacy projects), treat as `pending / TBC` and show the banner. The Anti-Pattern Detector watches for v1 artefacts without approval state.

### 7. In-progress is ALWAYS blue

🔵 / `#3b82f6` in every visualisation, canvas and HTML. Never amber or brown.

---

## When to invoke

- User runs `/canvas`, or asks for a "project canvas", "project dashboard", "visual status"
- **At Phase 0 intake completion (auto, mandatory)** — sparse, empty-state-heavy canvas is by design; it's the visual roadmap. Tell the user so.
- At Phase 1 kickoff completion (auto) — populated with stakeholders, scope, RAID
- After any phase gate (refresh)
- **After any material tracker change (refresh):** decision logged 📌, risk logged or re-rated 🧨, dependency added/resolved 🚧, sign-off captured ✅, slice confirmed/deferred, solution option selected. Not after every reply — only material changes.
- User runs `/status` — canvas + HTML refresh are mandatory side-effects (triple output: chat + canvas + HTML, never fewer)
- First time a new user runs the skill on an existing project

## Canvas location and naming

Single living canvas per project — overwrite on each refresh.

Path: `~/.cursor/projects/<workspace>/canvases/<project-slug>-status.canvas.tsx` (kebab-case the initiative name, e.g. `merchant-onboarding-status.canvas.tsx`). HTML: `<project-analysis-folder>/status-snapshot.html`. Intake form variant: see `intake-form-canvas.md`.

## Canvas accuracy guardrails (run before writing the final canvas)

| Check | What to verify |
|---|---|
| No premature completion | Is any `status: "done"` item actually still in progress? Compliance sign-offs and analysis items are frequently mislabelled done |
| Timeline bars are honest | In-progress items extend past "today"; only done items end before it |
| Compliance-gated items | Anything needing compliance/legal/privacy sign-off stays `pending`/`in-progress` until the sign-off is recorded |
| Analysis swimlane present | The BA/PM analysis workflow is visible, not just build tickets |
| Week 0 = project start | Timeline starts at D1 kickoff week, not today |
| Jira statuses used | If the MCP is reachable, statuses came from Jira, not markdown |

If any check fails, fix the data before rendering. The full pre-delivery self-check (grown from real demo regressions) is in `canvas-tab-specs.md` — run it every time.

## Integration (summary)

- **Callers:** orchestrator (`/canvas`, `/status`, phase gates), Intake Reviewer (HK-INTK-CANV-init), State Validator (HK-SV-CANV-refresh — refresh status-data from tracker before validation).
- **Calls:** `ba-jira-sync` before any ticket-data use (HK-CANV-JIRA-sync); Risk & Tracker for RAID data (HK-CANV-RT-read); Visual Storytelling standard for embedded diagrams (HK-CANV-VIS-embedded → `references/visual-output-format.md`); internal Data Model section (HK-CANV-DATA-internal → `status-page-and-data.md`).
- Hook contracts live in `hook-contracts.md`; this table is a summary, not the API.

## Data model

`references/canvas-data-model.md` is canonical for the status-data.json schema, workstream state transitions, scope objects, and metric formulas. The operational data tasks (create/update status-data.json, date-aware computation, validation rules, migration, status page publication) are in `status-page-and-data.md`.
