# Quality metrics — invocation, caching, surfacing
<!-- Wave 10: moved from SKILL.md. Formulas are NOT here: canonical formulas live in
     references/canvas-data-model.md → Metric computation rules. -->

## Metrics computation (Wave 6 — new)

The Project Canvas computes four derivable BA quality metrics from existing state. These are surfaced in `/status`, `/snapshot`, and feed every retro automatically (per `ba-retrospective-and-learning` Metrics integration section).

## The four metrics — formulas

Canonical formulas, sources, and thresholds live in `references/canvas-data-model.md → Metric computation rules`. Read that section before computing. (Deduplicated Wave 10 — the formulas previously lived in both files and drifted risk was real. Note: the E-promote wave shipped, so sources for dorChecks / MoSCoW / sign-offs are the tracker registers, mirrored into status-data.json on refresh — canvas-data-model documents this.)

### Computation invocation

Compute these:
- Before every `/status` output (after Jira sync, before the chat status text is generated)
- Before every retro (Type 2 / Type 3 — the retro skill reads them)
- Before every `/snapshot`
- On demand via `/metrics` (new command)

### Storage

Computed metrics are NOT stored in `status-data.json` as canonical (they're derived). They're cached in a sibling file `metrics-cache.json` that includes a `computedAt` timestamp. Anything older than 1 hour is recomputed on next request.

### Surfacing in /status

Add a new section to the `/status` output template:

```
## Quality metrics (rolling 30 days)

| Metric | Value | Trend | Warn? |
|---|---|---|---|
| MoSCoW coverage (initiative) | 87% | ↗ | ✓ |
| MoSCoW coverage (Cohort A) | 92% | → | ✓ |
| MoSCoW coverage (Cohort B) | 64% | ↘ | 🔴 below threshold |
| DoR hit rate (Cohort A) | 78% | → | ✓ |
| DoR hit rate (Cohort B) | 55% | ↘ | 🔴 below threshold |
| Requirement interrogation rate | 91% | → | 🟡 below 95% target |
| Sign-off cycle time (median) | 6.5 days | ↗ | 🔴 above 5d target |
```

### Failure handling

If any metric can't be computed (insufficient data — e.g. no DoR checks logged yet on a new initiative), display `n/a` in the metrics table, NOT 0% or a fabricated value. Showing `n/a` is honest; showing 0% looks like everything is broken.

After 3 status outputs with the same metric `n/a`, surface a one-line nudge: "DoR hit rate has been n/a for 3 status runs — likely missing instrumentation in Delivery Definition. Want me to look?"

### New `/metrics` command

Add to the orchestrator's command set:

| `/metrics` | Pull and display all four metrics with per-scope breakdown and trend. Equivalent to the metrics section of `/status` but without the rest of the status output. Useful for quick check-ins. Always follow with an `AskQuestion` on whether to dig into a specific metric. |

---

