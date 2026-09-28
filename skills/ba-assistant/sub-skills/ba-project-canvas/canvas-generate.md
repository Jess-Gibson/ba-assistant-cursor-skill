# Canvas generation: keep the data right, let the script draw
<!-- Version 15: the canvas and HTML snapshot are rendered by render-initiative-canvas.py from
     status-data.json. This file is the whole procedure. canvas-tab-specs.md is the design
     reference for the template and is not needed to make a canvas. -->

Your job on `/canvas` is the judgement part: make sure `status-data.json` is current and honest. The layout, the 8 tabs, the scope filter, the DAGs, the Gantt, the HTML snapshot and the pre-delivery self-check are all in the template and the script, so they come out the same every time.

**Do not** read every file in the initiative folder, and do not hand-write or hand-edit `.canvas.tsx` code.

## 1. Which initiative

The one the user named, or the session banner's `INITIATIVE CONTEXT`, else ask (AskQuestion listing the initiatives under `paths.initiativesRoot`). Never search the whole machine for project folders.

## 2. Bring `status-data.json` up to date (read only what you need)

Per `status-page-and-data.md` (regenerate-before-read):

1. **Jira** (`ba-jira-sync`, when the MCP is reachable; Jira wins over markdown for tickets). JQL for the initiative's epics and their stories (`project = <key> AND parent = <epic>`). Per story write `key`, `title`, `status`, `scope`, `moscow`, `storyPoints`, `linkedRequirements`, `linkedSlice`, and `dependsOn` (inward "blocks" links). For stories that will show on the timeline, take `startedAt` (To Do → In Progress) and `doneAt` (→ Done) from the changelog; never use sprint dates as a start date. Skip Won't Do / Duplicate. No Jira: say "Jira: unable to check" and use the tracker.
2. **Tracker** (`initiative-tracker.md`): re-derive decisions, RAID, open questions, milestones, sign-offs, DoR checks, MoSCoW and PM approval. Use Grep or the sections you need, not a top-to-bottom read of a large tracker.
3. **Recent context:** the tail of `SESSION-CONTEXT.md` (the session banner already has it) for the `narrative` (2 to 4 sentences, plain English) and anything captured today but not yet promoted.
4. **Optional blocks** the script uses when present (see the script header): `initiative.deadline`, `initiative.drivers`, `timeline` {`lanes`, `bars`} for extra swimlanes such as an Analysis lane, `dependencyGraph` {`nodes`, `edges`} when the dependency picture is richer than `raid.dependencies[].blocks`, `workstreamChanges`.
5. **Ask the user only for genuine gaps** (deadline, parent epic, a sponsor name) and only once.

Data rules that keep the canvas honest (the script cannot judge these):

| Rule | Why |
|---|---|
| Nothing is `done` unless it is confirmed done (compliance and sign-off items stay pending until the sign-off is recorded) | Premature green is the most common canvas lie |
| In-progress work has no end date in the past | The script extends open bars past today; do not add an early `doneAt` |
| Scope labels are real business names (`label`, and `shortLabel` of 18 characters or fewer), never "Feature A" / "Cohort B" | Stakeholders read this, not BAs |
| Ticket statuses come from Jira when reachable | Markdown statuses go stale |
| `pmApproval.status` stays `pending` until the PM has signed off | Drives the DRAFT banner |

## 3. Render

```text
python3 ~/.cursor/_workstream/render-initiative-canvas.py --initiative <slug>        (Windows: py)
```

It writes `~/.cursor/projects/<workspace>/canvases/<slug>-status.canvas.tsx` (or `--canvas <path>`) and `<initiative>/status-snapshot.html`, and prints `Tabs with data: N / 8` with a line per empty tab saying what data it needs, then `Gate: canvas-render: PASS`. Empty tabs still render, with a prompt, so there are always 8.

If the script is missing (an older install), say so and suggest re-running the installer. Do not fall back to hand-writing a canvas.

## 4. Tell the user

> Canvas and HTML snapshot generated. Canvas: `<path>`. HTML: `<path>/status-snapshot.html` (open it in any browser, email it, or attach it to Confluence).

Then list the empty tabs from the script output and offer to fill the ones that matter, in one AskQuestion. Do not generate anything else.

## Changing how the canvas looks

Edit `skills/ba-assistant/templates/initiative-status.canvas.tsx.template` (canvas) or `render_html` in `tools/render-initiative-canvas.py` (HTML), using `canvas-tab-specs.md` as the design reference, and re-render. The generated `.canvas.tsx` is overwritten on every run.
