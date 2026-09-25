---
name: ba-initiative-closeout
description: >
  One-way tidy-up for an initiative that is genuinely finished: run the closure
  retro, audit every file in its analysis folder for keep/publish/delete,
  confirm Confluence is complete, finalise its README, move the whole folder
  into the archive tree, and flip workboard.json to archived so it drops out
  of daily refresh churn. Invoke on "/close", "close out X", "archive X",
  "this one's done". Never runs automatically — always explicit, user-initiated,
  and confirmed batch by batch. Mirrors ba-new-initiative in reverse.
---

# Skill: Initiative Closeout

Tidy-up, not ceremony. No welcome panel, no complexity dial. Confirm the
initiative is actually done, run the retro so its learnings inform the file
calls, walk the folder once, move it, and stop tracking it daily.

## Standards used

- `references/workboard-format.md`  -  status enum (§1), `workboard.json` fields
  (§4), canvas display rules (§5). **Note:** at time of writing this standard's
  status enum does not yet include `archived` (see step 7) — add it there in the
  same change that wires this skill in.
- `references/workspace-operations.md`  -  initiative folder convention,
  `BA_INITIATIVES_ROOT`

## When to invoke

- Trigger phrases: `/close`, "close out X", "archive X", "wrap up X for good",
  "this one's done".
- Never triggered by a phase gate, a retro, or any other skill on its own.
  This is a deliberate, one-way action the user asks for by name.

If the initiative isn't actually finished (ops obligations still active, a
dev ticket still open against core scope), say so and suggest `closed` in
`workboard.json` instead — see `references/workboard-format.md` §1. `closed`
and `archived` are different states; this skill only ever produces the latter.

## What this does not do

- Does not run automatically at any workstream gate, retro, or session end.
- Does not delete or move a single file without per-batch confirmation.
- Does not touch `workboard.json` status until the folder has actually moved
  (see `references/workboard-format.md` anti-patterns — never set `archived`
  by hand or ahead of the real move).
- Does not skip the closure retro. Retro runs first; its "what to keep"
  output is what makes the file-audit calls informed rather than guessed.
- Does not invent an archive location. One convention, see below, always.

## Flow

### 0. Confirm scope

Confirm which initiative (slug) and that it's genuinely finished, not just
quiet. Read `workboard.json`'s current status and `next_action` for this
slug first — if it already says something like "archive candidate", that's
a strong signal this is the right call, surface it. If status is still
`on-track` or `at-risk`, flag the mismatch and ask before proceeding.

### 1. Closure retro (mandatory, first)

> Running: Retrospective and Learning (Type 3 — closure) → what to carry forward

Invoke `sub-skills/ba-retrospective-and-learning/SKILL.md`, Type 3 (closure).
Do not skip this by asking "want a retro?" — for this skill it's not optional,
it's the input the file audit in step 2 depends on. Capture:
- The one-paragraph outcome summary (goal / delivered / met-or-not) — this
  becomes the README.md closing paragraph in step 4.
- Which artefacts the retro called out as "worked well" or "worth keeping as
  reference" — carry this bias into step 2's default recommendations.

### 2. File-by-file audit

Walk every file under the initiative's folder (`$BA_INITIATIVES_ROOT/{slug}/`
or `$BA_INITIATIVES_ROOT/short-term/{slug}/`). Batch by subfolder, not one wall of
decisions — present each batch with a recommended action per file and reasons,
then one `AskQuestion` per batch:

```
[Approve all in this batch] [Review each file] [Skip this batch for now]
```

Five possible outcomes per file:

| Outcome | When |
|---|---|
| **Keep as-is** | Canonical state file, or reference material the retro flagged as worth keeping |
| **Archive as-is** | Fine to move but not worth any further action — most files land here |
| **Publish to Confluence, keep a stub** | Content should be visible to others but the working file stays as local record |
| **Publish to Confluence, delete local** | Content's only value was getting to Confluence; the local draft is redundant once it's there |
| **Delete** | Clutter — meeting prep for a meeting long past, misfiled content, an abandoned draft |

Defaults worth calling out explicitly rather than leaving to judgement:

- **Canonical state files are never offered for deletion** — `README.md`,
  `SESSION-CONTEXT.md`, `initiative-tracker.md`, `status-data.json`,
  `Project-hub.md`, `confluence-pages.json`, `superseded-pages.json` always
  move with the folder.
- **`ANALYSIS-HANDOFF.md` / `BLUEPRINTS-HANDOFF.md` default to keep.** These
  are the permanent record of the git-sync mapping to a shared repo, not
  working clutter, even for a fully closed initiative.
- **Meeting-prep docs for a meeting that has already happened** default to
  delete, unless the retro flagged the prep itself as reusable (e.g. a
  reusable briefing template).
- **A folder or file whose subject doesn't match the initiative it's sitting
  in** (wrong client, wrong ticket type, evidence for a different piece of
  work entirely) gets flagged individually, never silently deleted or
  silently archived in place — ask where it actually belongs.
- **`jira-drafts/*`** — check whether the linked ticket exists in Jira. If it
  does, the draft is redundant, default delete. If it doesn't, ask whether to
  keep, convert now, or abandon.

### 3. Confluence completeness check

Read `confluence-pages.json`. Confirm a hub or status page exists and
reflects the closed state. Flag:
- Any live page still carrying a `DRAFT — pending approval` banner.
- Any decision, outcome, or number that only ever lived in
  `initiative-tracker.md` and never reached a page anyone else can read.

Surface gaps, don't silently publish — ask before creating or updating any
Confluence page.

### 4. Finalise README.md

Write the outcome summary from step 1 into the initiative's `README.md`
(see `ba-new-initiative/SKILL.md` step 4b for its shape). Flip the status
line to `Closed — see outcome summary below`. This is the only skill allowed
to write that status line (see `references/canonical-ownership.md`).

### 5. Update the master registry

Read `$BA_INITIATIVES_ROOT/README.md` (the cross-initiative registry, not the
per-initiative one just finalised), if this workspace keeps one. Move this
initiative's row out of the active **Initiative map** table into a new
**Archived** section, noting the archive path from step 6. Don't just leave
the row looking live.

### 6. Physical archive move

Relocate the whole folder:

```
$BA_INITIATIVES_ROOT/{slug}/               → <archive-root>/{slug} (archived)/
$BA_INITIATIVES_ROOT/short-term/{slug}/    → <archive-root>/short-term/{slug} (archived)/
```

See "Archive location convention" below for `<archive-root>`. Only after
steps 2 to 5 are settled — never move a folder mid-audit. This is a real
file-system move (not a copy), confirm with the user before executing since
it's the one step in this flow that isn't trivially reversible from chat
alone.

### 7. Update the workboard

Set in `workboard.json`:
- `status: "archived"`
- `archived_path`: the new location from step 6
- Leave `phase`, `top_blocker`, etc. as a frozen snapshot of the closing state
  rather than clearing them — they're the historical record now.

**Status enum dependency:** `references/workboard-format.md` §1 defines the
allowed `workboard.json → initiatives[].status` values. If `archived` isn't
in that table yet, add it there (alongside `closed`, with a "do not use when"
row pointing back to this skill) in the same change that wires this skill in.

Regenerate the canvas (`generate-workboard-canvas.py`) so the Initiatives tab
collapses this one into the "Archived (N)" line per
`references/workboard-format.md` §5.

**First run only:** this depends on `templates/ba-workboard.canvas.tsx.template`
knowing about the `archived` status (StatusDot colour/label, the "Active
initiatives" filter excluding it, an "Archived initiatives" collapsible
section mirroring "Closed initiatives"). If the template predates this skill,
regenerating without that fix will render the archived initiative as if it
were still active. Apply the fix to the template once; every run after that
is just a normal regen.

### 8. State Validator pass

> Running: State Validator → confirm nothing still points at the old path

Invoke `sub-skills/ba-state-validator/SKILL.md`. After a folder move, anything
that referenced the old `$BA_INITIATIVES_ROOT/{slug}/` path (canvas discovery,
`confluence-pages.json` entries, cross-initiative mentions in other trackers)
needs to still resolve. Treat this as the closing gate, not optional.

## Archive location convention

One convention, always: a sibling `archive/` directory next to
`BA_INITIATIVES_ROOT` (not inside it, so archived work stops showing up in
any glob scoped to the live initiatives root):

```
<parent of BA_INITIATIVES_ROOT>/archive/{slug} (archived)/
<parent of BA_INITIATIVES_ROOT>/archive/short-term/{slug} (archived)/
```

With the default root (`~/.cursor/initiatives`), that resolves to
`~/.cursor/archive/{slug} (archived)/`. If `BA_INITIATIVES_ROOT` has been
customised for this workspace, the archive root moves with it — same sibling
relationship, same naming style (the literal `(archived)` suffix on the
folder name). Never invent a different layout — if this convention turns out
to be wrong, fix it here, don't improvise per-initiative.

## Failure modes

| Failure | What to do |
|---|---|
| Retro (step 1) surfaces the initiative isn't actually done | Stop. Don't proceed to the file audit. Report back and let the user decide. |
| User wants to skip the retro | Explain why it's not optional here (it's the input to the file audit), offer a fast Type-1-shaped closure retro instead of skipping entirely, but do not skip |
| A file's right home is genuinely ambiguous | Ask, don't guess — batch decisions speed things up, but an ambiguous file gets its own question |
| Confluence MCP unavailable at step 3 | Skip the live-page check, note it in the closeout summary, don't block the rest of the flow on it |
| Folder move (step 6) partially fails (some files locked/in use) | Stop, report exactly which files didn't move, don't leave the initiative split across two locations without saying so |
| Something outside this initiative still references the old path after step 8 | Report it, don't silently break the reference — let the user decide whether to fix the referencing file or leave a redirect note |

## Integration with other skills

| Hook | Callee | Trigger | Inputs | Outputs | Failure mode |
|---|---|---|---|---|---|
| HK-CLOSE-RETRO-closure | Retrospective_and_Learning | Step 1, always, first | Initiative slug | Type 3 closure retro output | Block — cannot proceed to file audit without it |
| HK-CLOSE-SV-postmove | State_Validator | Step 8, after archive move | Old path, new path | Divergence report | Block — closing gate |
| HK-CLOSE-COMD-supersede | Communication_Drafter | Step 3, if pages need a supersede banner | Page list | Supersede banner content | Warn — manual fallback |

Add these three rows to `hook-contracts.md` under a new
"Initiative Closeout — outbound" section when this skill is wired in.
