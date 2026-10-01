# Status refresh: keep `status-data.json` current without rebuilding it

**Owner:** this file. **Used by:** `/status`, `/canvas`, `/publish-status`, `/metrics` (and anything else that reads `status-data.json`).
**Tooling:** `~/.cursor/_workstream/validate-state.py` (read-only) and `compute-metrics.py`. Windows: `py`, Mac/Linux: `python3`.

`status-data.json` is **updated, not regenerated**. A script says what is out of date, and only that is changed. A full rebuild happens only when the file is missing or broken, or the BA asks for one.

## 1. Check (one script call, read-only)

```text
python3 ~/.cursor/_workstream/validate-state.py --initiative <slug> --json
```

From the result:

| Field | Means |
|---|---|
| `divergences` | Exactly which facts are out of date: tracker items missing from `status-data.json`, status mismatches, stale snapshot or canvas, people or milestone dates that disagree |
| `summary.jiraSyncAgeMinutes` | Minutes since tickets were last synced (`null` = never, or no tickets) |
| `summary.unpromoted` | Captures in `SESSION-CONTEXT.md` not yet in the tracker |

## 2. Decide what to do

| Situation | Action |
|---|---|
| No divergences about `status-data.json`, Jira synced under 60 minutes ago (or the initiative has no tickets) | **Nothing.** Read `status-data.json` as it is |
| Divergences about `status-data.json` | **Targeted update:** change only the items the table names (add the missing IDs from the tracker, correct the mismatched statuses). Read only those tracker rows (Grep by ID), never the whole tracker |
| Only "status-data.json freshness" (the tracker was edited after it, but every ID and status matches) | Re-read only the tracker sections the script cannot compare: milestones and the four tracker-owned registers (DoR checks, MoSCoW, PM approval, sign-offs; `raid-format.md`). Update what differs |
| Jira synced 60 minutes ago or more, or never | **One Jira query** (`ba-jira-sync`), then merge only tickets that changed |
| `status-data.json` missing or unreadable, or the BA says "refresh", "full refresh" or `/status full` | **Full rebuild** from the tracker and Jira (`ba-project-canvas` → `status-page-and-data.md`, data task 1) |
| Jira not reachable | Say "Jira: unable to check, statuses as at <time>" and carry on with the data you have |

Unpromoted captures are reported, not promoted here: promotion belongs to `/wrap` and end of day.

## 3. Write (only when step 2 changed something)

- Edit only the fields that changed. Set `initiative.lastUpdated` to today.
- Recompute metrics with `compute-metrics.py --initiative <slug>` (it writes `metrics-cache.json`). Never compute the formulas by hand.
- Never render the canvas or HTML here. That is `/canvas`.

## 4. Report in one line

`Data: up to date` / `Data: updated 3 items (D-04, R-02, OQ-07)` / `Data: rebuilt (full refresh)`, then `Jira: synced 25m ago` / `Jira: 2 tickets changed` / `Jira: unable to check`.
