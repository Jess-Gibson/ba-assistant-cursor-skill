---
name: ba-dev-handover
description: >
  ALWAYS activate when ANY of these are true:
  (1) User types /handover, or says "hand this to devs", "package for delivery", "create a spike request",
      "raise an ADR request", "publish confirmed requirements to the repo", "give the devs the requirements".
  (2) Confirmed analysis needs to cross the boundary from the BA workspace to the shared delivery repo.
  (3) A spike or ADR identified in Solution Shaping needs to be turned into a request the devs can action.
  (4) A sliced, DoR-passed story set is ready to hand to delivery.
  This skill is a PUBLISHER and a GATE, not an analysis engine. It derives dev-facing handover artefacts
  from the confirmed register (parallel to how /publish-status derives a Confluence page), gates them for
  quality before they leave, writes them to the shared repo, and feeds the matching Jira ticket.
  It never publishes unconfirmed work.
---

# Skill: Dev Handover

## Description

The Dev Handover skill moves **confirmed** analysis across the boundary from the BA workspace into the shared delivery repo the devs and delivery agents read. It is the delivery-facing sibling of `/publish-status`: where that derives a Confluence page for stakeholders, this derives handover artefacts for engineering, from the same source of truth (`register.md`, the tracker, status-data.json).

It exists because a bad handover fails downstream. A spike request with no decision link bounces back with "what do you actually want." A story pack with untestable ACs gets rejected at pickup. Every bounce is rework, and rework is where BA value looks muted. This skill's job is to stop bad handovers leaving: it assembles what is confirmed, gates it, and refuses to publish what isn't ready.

**Core principle: derive, don't re-author.** The source of truth stays in the BA workspace (`register.md` for requirements, `initiative-tracker.md` for RAID, Solution Shaping outputs for options/ADRs). This skill reads confirmed entries, renders them into the dev-facing shape, and publishes. It does not become a second place requirements live. If a requirement isn't `status: confirmed` in the register, it does not go in a handover.

**Two distinct events, never conflated:**

1. **Confirmation**  -  a requirement is promoted to `status: confirmed` in `register.md`. Happens in the BA workspace, via the Interrogator conversation and stakeholder agreement. This skill never performs confirmation.
2. **Publication**  -  already-confirmed content is rendered and written to the shared repo. This is the only event this skill owns.

If a handover needs something that isn't confirmed yet, the handover stops and event 1 happens first, separately (see the Interrogator hook below). Publishing does not confirm, and confirming does not publish.

## Standards used

- `references/dev-handover-format.md`  -  the four handover artefact shapes, the handover note wrapper, the shared-repo folder convention, the confirmed-vs-working boundary
- `references/ears-translation.md`  -  how a confirmed register requirement is rendered into EARS form for the export (source register stays as-is)
- `references/user-story-format.md`  -  spike structure (§3) and DoR checklist (§6); the spike request and story pack reuse these, they don't reinvent them
- `references/requirement-format.md`  -  the confirmed requirement fields that get pulled
- `references/raid-format.md`  -  the RAID entry shape used when embedding RAID summaries into a handover

## Cross-cutting rules

- This skill produces multiple artefact-class outputs. Before generating, apply the **"What I'll produce next" declaration** rule from `ba-assistant/SKILL.md → Co-thinking and artefact production protocol`. Surface the planned handover artefact and its gate result, then let the user confirm before publishing.
- Apply the **co-thinking journey** (what I know / what I don't / recommendation / trade-off / ask) before publishing anything the user hasn't explicitly requested by type.
- Follow the **real business names** rule: handover artefacts use real scope names (e.g. "High-risk merchants"), never internal codes (`C-A`), in any human-readable field.
- Print the **visible skill handoff header** on every hook (`> Running: <Skill> → <intent>`).

## When to invoke

- `/handover` on demand
- User asks to hand something specific to the devs (spike, ADR, requirements, stories)
- Solution Shaping has identified a spike or ADR and the user wants to raise it
- A story set has passed DoR and is ready for delivery
- Do NOT invoke to publish work in progress. If the user asks to "send the devs my current thinking," offer to confirm the relevant requirements first (via the readiness check below) rather than publishing drafts.

## The four handover types

Each maps to the SDD canonical set (requirements → design → tasks) plus the loop-specific spike request. Each is a derived publish, gated before it leaves.

| Type | What it is | Derived from | Feeds |
|---|---|---|---|
| **Requirements pack** | Confirmed requirements for a scope, rendered EARS-style, with embedded RAID summary and grounded facts | `register.md` (status: confirmed) + tracker RAID + Data Investigation evidence | repo `confirmed/requirements.md` |
| **Spike request** | A decision-linked investigation question for the devs | Solution Shaping spike list + confirmed context | repo `exchanges/` + Jira spike ticket |
| **ADR request** | A request for the devs to make and record an architecture decision | Solution Shaping ADR list + confirmed requirements + current state + gap | repo `exchanges/` + (optionally) Jira |
| **Story pack** | DoR-passed stories with traceability, for delivery | `ba-story-writing` output + slices + confirmed requirements | repo `confirmed/stories/` + Jira stories |

Every published artefact is wrapped in a **handover note** (see `dev-handover-format.md`): what this is, what's confirmed (links to the confirmed store in the shared repo), what's still provisional (flagged inline), the initiative index link, and what's needed back.

**RAID is embedded, never linked.** The tracker is a working, git-ignored file  -  a link to it from the shared repo would point at nothing the devs can see. Any dependency, decision, or constraint a handover relies on is copied in as a short summary table (per `raid-format.md` shape), with its tracker ID preserved for traceability on the BA side. Links inside a handover may only ever point at other files inside the shared repo's confirmed store.

## Mandatory hooks

Fire these as part of the readiness check, before publishing. Print the status header for each.

1. **Requirements Interrogator** (`HK-DH-INT-confirm`)  -  **handoff-and-halt, not a sub-call.** The Interrogator runs as a conversation (one good question at a time, per its own skill); it cannot be invoked synchronously inside a publish flow and "return" a confirmed requirement. If a handover needs a requirement that is `draft` rather than `confirmed`: **halt the handover**, tell the user which requirements aren't ready, and offer to hand off to the Interrogator conversation now. Confirmation then happens in the register as its own event (with stakeholder agreement, per requirement-format status transitions). The user re-runs `/handover` afterwards. Block for the requirements pack and story pack; for spike/ADR requests a draft may instead be flagged provisional in the note (warn).

2. **Data Investigation** (`HK-DH-BDI-ground`)  -  if a requirement being handed over touches a real system (endpoint, field, state, schema) and its grounding evidence is qualitative or absent (the register's `evidence` field where present, else the absence of a linked Data Investigation output), fire the standard data-pairing prompt before publishing: pull data now / user shares data / proceed and tag `evidence: qualitative` (explicit) / not needed. Warn, not block. Ungrounded system facts are the anti-hallucination gap the devs' agents fall into.

3. **Risk & Tracker** (`HK-DH-RT-raid`)  -  pull the confirmed RAID items a handover references (dependencies, decisions, compliance constraints) from the tracker and **embed them as a summary table in the published artefact** (the tracker itself never leaves the workspace). Block if a handover asserts a dependency or constraint with no tracker entry (untraceable).

4. **Jira** (`HK-DH-JIRA-ticket`)  -  for spike requests, ADR requests, and story packs, after the markdown is published and the gate passes, offer to create/update the matching Jira ticket using the project-specific Jira skill (`jira-templates` in this workspace's convention  -  in the public repo this is a create-your-own skill per CUSTOMIZATION.md) and `references/jira-ticket-format.md`. The markdown is the source; the Jira ticket is the actioned view. Warn if the Jira MCP is unavailable; the markdown still publishes.

5. **State Validator** (`HK-DH-SV-register`)  -  after publishing, register the handover's dependencies so the validator can flag it if a confirmed artefact it derived from later changes (making the published handover stale). Warn on failure.

## Tasks

### 1. Determine handover type

If the user hasn't said, ask via AskQuestion: Requirements pack / Spike request / ADR request / Story pack. Surface a recommendation if context makes it obvious (e.g. Solution Shaping just produced a spike list → "looks like a spike request").

### 2. Confirm the shared-repo target

Read `BA_SHARED_REPO_ROOT` (env var) or `confluence-pages.json → sharedRepo` if recorded. If neither exists, ask once for the shared repo path and the initiative slug, then cache it. The confirmed export lands at `<shared-repo>/analysis/<slug>/confirmed/`; exchanges at `<shared-repo>/analysis/<slug>/exchanges/`. See `dev-handover-format.md` for the full structure.

### 3. Readiness check (the gate's first half)

Load the required-inputs checklist for the type (from `dev-handover-format.md`). For each required input, check it exists and is at the required state. On a gap, do NOT publish. Instead:

- **Requirement is not `confirmed`** → halt and hand off to the Interrogator conversation (`HK-DH-INT-confirm`); the user re-runs `/handover` once the register shows `confirmed`. Spike/ADR only: may flag it provisional in the note instead.
- **Requirement touches a real system but grounding is qualitative/absent** → fire `HK-DH-BDI-ground`.
- **Spike/ADR question is vague or not decision-linked** → prompt for a sharper question. Block until it names the decision it unblocks and what "done" looks like. (This is the single most common bad handover.)
- **Referenced RAID missing from tracker** → record it in the tracker first (via Risk & Tracker), then embed via `HK-DH-RT-raid`.
- **Story missing DoR** → run the DoR section of `ba-story-writing`; block the story pack until it passes.

### 4. Run the gate (the gate's second half)

Apply the per-type gate (below). Posture is **warn hard**: a soft fail prints a loud warning and requires an explicit "publish anyway, this will likely bounce" acknowledgement via AskQuestion. A hard fail blocks with no override. The **story pack DoR is a hard block**.

### 5. Render

Produce the artefact per `dev-handover-format.md`. For the requirements pack, render each confirmed requirement in EARS form per `ears-translation.md` (the register entry stays untouched; EARS is generated at export). Wrap in the handover note. Links point only at confirmed artefacts inside the shared repo; RAID and any workspace-sourced context are embedded, not linked; provisional items are flagged inline.

### 6. Publish

Write the artefact and handover note to the shared-repo paths. Do not write anything from the BA working set (SESSION-CONTEXT, debriefs, the tracker file itself) to the shared repo  -  embedded RAID summaries derived from the tracker are the only tracker content that crosses, and only via `HK-DH-RT-raid`.

### 7. Feed Jira

For spike/ADR/story types, fire `HK-DH-JIRA-ticket` to offer ticket creation from the published markdown.

### 8. Register and log

Fire `HK-DH-SV-register`. Append a one-line entry to the initiative index (`<shared-repo>/analysis/<slug>/README.md`) recording the handover, its type, and date. Log the handover in `metrics-cache.json → handovers` for the bounce-rate metric (see Metrics).

### 9. Self-critique

Per `instructions.md → Self-Critique`, before presenting: what am I assuming this handover is complete on, what would a senior dev push back on at pickup, what's missing. Surface it in chat with the publish confirmation.

## Gates

### Requirements pack
- **Hard:** every included requirement is `status: confirmed` and has an `interrogatorOutput` path.
- **Hard:** requirements touching real systems carry grounded facts (`evidence: data` where the field exists, else a linked Data Investigation output), OR are explicitly published as qualitative after an acknowledged warning.
- **Warn hard:** acceptance-for-met present and testable; relevant RAID embedded; EARS render clean (no requirement that can't be expressed as a testable "shall").

### Spike request
- **Hard:** exactly one decision-linked question (names the decision it unblocks).
- **Hard:** "acceptance for closure" / done-looks-like defined; time-box set (reuses user-story-format §3).
- **Hard:** links point only to confirmed artefacts in the shared repo; workspace context is embedded, not linked.
- **Warn hard:** provisional assumptions flagged inline; method suggested.

### ADR request
- **Hard:** confirmed requirements attached, plus current-state and gap.
- **Hard:** the decision to be made is stated explicitly (not "figure out the architecture").
- **Warn hard:** known options and constraints noted; compliance flagged if relevant.

### Story pack (hard block on any Hard item)
- **Hard:** every story passes the DoR checklist (`user-story-format.md §6`).
- **Hard:** traceability present  -  requirement → AC → story, and each story links a slice.
- **Hard:** Negative case present on every story.
- **Hard:** grounded system facts included where the story touches real systems.
- **Warn hard:** NFR/compliance noted; MoSCoW set per scope.

## Metrics

- `handoverBounceRate`  -  of handovers published, how many came back for rework (the user marks a handover "bounced" when it does). The whole point of the gate is to drive this down. Derivable, honest n/a until there's data.
- Log every publish and every acknowledged soft-fail override to `metrics-cache.json → handovers` so a retro can see whether the gate is too loose (bounces despite passing) or too tight (overrides that never bounce).

## Outputs

| Output | Format | Where it goes |
|---|---|---|
| Handover artefact | Markdown | `<shared-repo>/analysis/<slug>/confirmed/` or `/exchanges/` |
| Handover note | Markdown | `<shared-repo>/analysis/<slug>/exchanges/handover-notes/` |
| Jira ticket (spike/ADR/story) | Jira issue | Jira, via the project-specific Jira skill |
| Index entry | Markdown row | `<shared-repo>/analysis/<slug>/README.md` |
| Handover log | JSON | `metrics-cache.json → handovers` |

## Failure modes

| Failure | What to do |
|---|---|
| Shared repo path unknown | Ask once, cache in confluence-pages.json → sharedRepo |
| Jira MCP unavailable | Publish the markdown; skip ticket; note in the handover note that the ticket is pending |
| A required requirement isn't confirmed | Halt and hand off to the Interrogator conversation (requirements/story pack) or flag provisional (spike/ADR); never silently publish a draft |
| User insists on publishing a soft-fail | Allow after explicit acknowledgement; log the override to metrics-cache |
| User asks to publish working docs | Refuse; offer to confirm the relevant entries first |
| EARS render fails for a requirement | The requirement can't be expressed as a testable "shall"  -  flag it back for interrogation, don't force a mangled render |
| No `evidence` field in the local register format | Fall back to checking for a linked Data Investigation output; suggest adding the optional `evidence` field per the Wave 9 requirement-format patch |

## Anti-patterns (add to Anti-Pattern Detector)

| Watching | Trigger | Anti-pattern |
|---|---|---|
| Dev Handover | Any handover published containing a requirement not `status: confirmed` | Unconfirmed handover |
| Dev Handover | Spike request with no decision link or no done-looks-like | Vague spike request |
| Dev Handover | Handover links to a working file (SESSION-CONTEXT, debrief, tracker) instead of embedding | Working doc leaked to devs |
| Dev Handover | Story pack published with a DoR fail overridden | DoR bypass on delivery handover |
| Dev Handover | A confirmed artefact changed after a handover derived from it, and the handover wasn't re-checked | Stale handover (caught by State Validator) |
| Dev Handover | Interrogation attempted inline as a sub-call during publish instead of handoff-and-halt | Synchronous interrogation |

## Integration with other skills

| Caller / partner | Why |
|---|---|
| Solution Shaping | Produces the spike and ADR lists this skill turns into requests |
| Story Writing | Produces the DoR-passed stories this skill packs |
| Requirements Interrogator | Matures drafts to confirmable  -  via handoff-and-halt, before a handover can pull them |
| Data Investigation | Grounds system facts before they're handed over |
| Risk & Tracker | Source of the confirmed RAID a handover embeds |
| State Validator | Registers handover dependencies; flags stale handovers on confirmed-artefact change |
| Project-specific Jira skill (`jira-templates` convention) | Renders the published markdown into the Jira ticket |

## Hook contract

Add to `hook-contracts.md`:

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-DH-INT-confirm | Requirements_Interrogator | Handover needs a requirement not yet confirmed | Requirement, source | Handoff-and-halt: Interrogator conversation runs; requirement confirmed in register as a separate event; user re-runs /handover | Block (reqs/story pack); warn+flag provisional (spike/ADR) | 🟠 W9 |
| HK-DH-BDI-ground | ba-data-investigation | Requirement touches a real system with qualitative/absent grounding | Requirement, candidate sources | Grounded facts or qualitative tag | Warn  -  publish as qualitative after acknowledgement | 🟠 W9 |
| HK-DH-RT-raid | Risk_and_Tracker | Handover references a dependency/decision/constraint | RAID reference | RAID summary table embedded in the artefact (tracker IDs preserved) | Block  -  untraceable handover | 🟠 W9 |
| HK-DH-JIRA-ticket | Project Jira skill (jira-templates convention) | Spike/ADR/story published, gate passed | Published markdown | Jira ticket created/updated | Warn  -  markdown stands; ticket pending | 🟠 W9 |
| HK-DH-SV-register | ba-state-validator | After publish | Handover + source artefact IDs | Dependency registered for drift watch | Warn  -  manual re-check fallback | 🟠 W9 |
