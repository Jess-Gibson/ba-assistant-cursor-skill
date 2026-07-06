# Dev Handover Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/dev-handover-format.md`
**Owner:** ba-dev-handover (workflow), this standard (format)
**Last reviewed:** 2026-07-05

Canonical source for the four dev handover artefact shapes, the handover note wrapper, the shared-repo folder convention, and the confirmed-vs-working boundary. The Dev Handover skill produces artefacts in conformance with this file. State Validator checks published handovers against it and against the confirmed register they derive from.

---

## 1. The confirmed-vs-working boundary

Two kinds of thing, kept physically apart.

| | Working (BA workspace, git-ignored, never shared) | Confirmed (shared delivery repo) |
|---|---|---|
| Examples | SESSION-CONTEXT.md, meeting debriefs, initiative-tracker.md, status-data.json, canvas, draft requirements | Confirmed requirements (EARS render), agreed current-state, ADRs, DoR-passed stories, handover notes |
| Changes | Constantly | Only on a deliberate confirmation / publish event |
| Who reads | You | You, the devs, the delivery agents |

The BA workspace already git-ignores its state files (`.gitignore`: SESSION-CONTEXT.md, initiative-tracker.md, status-data.json, etc.). The shared repo is a **separate** repo (the devs' repo). Nothing from the working set is ever written to it, and nothing in it may ever **link** to a working file — a link to a git-ignored file points at nothing the devs can see. Where a handover needs working-side content (RAID entries, tracker decisions), that content is **embedded** as a summary, with its tracker ID preserved for BA-side traceability.

**Confirmation and publication are two separate events.** Confirmation = the requirement reaches `status: confirmed` in `register.md` (Interrogator pass + stakeholder agreement, in the workspace). Publication = the confirmed content is rendered and written to the shared repo. Confirmation always happens first, as its own event; publishing never confirms anything as a side effect.

---

## 2. Shared-repo folder convention

Root is `BA_SHARED_REPO_ROOT` (env var) or the path recorded in `confluence-pages.json → sharedRepo`. Ask once, cache it. Per initiative:

```
<shared-repo>/
  analysis/
    <initiative-slug>/
      README.md                    # slim published index — status map, one row per artefact
      confirmed/
        requirements.md            # EARS render of confirmed register entries, by scope
        current-state.md           # confirmed current-state summary (derived)
        gap-analysis.md
        design/
          ADR-001-<slug>.md        # dev-authored, lands here when agreed
        stories/
          story-pack-01.md         # DoR-passed stories, with traceability
      exchanges/
        SPK-001-request.md         # BA-authored spike request
        SPK-001-result.md          # dev-authored result (feeds back)
        ADR-001-request.md         # BA-authored ADR request
        handover-notes/
          2026-07-04-story-pack-01.md
```

Scope folders are optional under `confirmed/` for multi-scope initiatives (e.g. `confirmed/high-risk-merchants/requirements.md`). Use real business names, not codes.

### README.md index (the map)

One table, kept current on every publish. Shows mixed maturity, which is the point.

```markdown
# <Initiative name> — analysis index

| Artefact | Status | Last published | Link |
|---|---|---|---|
| Requirements (High-risk merchants) | CONFIRMED | 2026-07-04 | confirmed/high-risk-merchants/requirements.md |
| SPK-001 vendor accuracy | OPEN | 2026-07-02 | exchanges/SPK-001-request.md |
| ADR-001 verification service split | REQUESTED | 2026-07-04 | exchanges/ADR-001-request.md |
| Story pack 01 | BLOCKED on ADR-001 | — | — |
```

---

## 3. The handover note (the wrapper)

Every published artefact gets a note. It is thin: it links to shared-repo artefacts and embeds anything workspace-sourced. It is the one place provisional context is allowed, clearly flagged.

```markdown
# Handover: <artefact name>
**Type:** Requirements pack | Spike request | ADR request | Story pack
**Initiative:** <name> (<slug>)  ·  **From:** <BA>  ·  **Date:** <date>
**Scope:** <real business name>

## What this is
[One or two sentences. What's being handed over and why now.]

## Confirmed (safe to build on)
- [Link to confirmed/requirements.md] — requirements as of <date>
- [Link to confirmed/current-state.md]
[Links only, and only to files inside this shared repo's confirmed store.]

## Relevant RAID (embedded from the BA tracker)
| ID | Type | Item | Status |
|---|---|---|---|
| DEP-04 | Dependency | Vendor sandbox access (owner: <name>) | Pending |
[Embedded summary, not a link — the tracker is a working file the devs can't see.
Omit this section if the handover references no RAID.]

## Provisional (NOT confirmed — do not build on this yet)
- [Anything still in flight that the dev needs to be aware of, flagged explicitly.
  Omit this section entirely if nothing is provisional.]

## What I need back
[The specific thing. "A recommendation on X with rough effort" / "the ADR recorded" /
"stories picked up in sprint N". Not "thoughts".]

## Where this initiative is
[Link to README.md index]
```

Rule: if the "Confirmed" section is empty, the handover isn't ready. If a link would point at a working file, stop — embed a summary instead or remove the reference.

---

## 4. Required inputs per type (the readiness checklist)

The Dev Handover skill checks these before rendering. Gaps trigger the mandatory hooks or block.

| Type | Required inputs |
|---|---|
| **Requirements pack** | ≥1 requirement at `status: confirmed`; each with `interrogatorOutput`; grounded facts where they touch real systems; relevant RAID pulled for embedding; scope named |
| **Spike request** | One decision-linked question; the decision it unblocks; done-looks-like (acceptance for closure); time-box; links to confirmed shared-repo context only |
| **ADR request** | Confirmed requirements attached; current-state + gap present; the decision to be made stated explicitly |
| **Story pack** | Stories passing DoR (user-story-format §6); requirement→AC→story traceability; slice linked; Negative case per story; grounded facts where relevant |

---

## 5. Artefact shapes

### Requirements pack
Header (initiative, scope, date, source = register.md), then confirmed requirements rendered EARS-style per `ears-translation.md`, grouped by type (COMP first, then BR, FR, NFR, CON). Each carries its trace ID and evidence tag. **Relevant RAID embedded as a summary table at the end** (tracker IDs preserved; the tracker itself is git-ignored and never linked). This is a derived view; it says so in the header and points back to the register by name (not link) as the workspace source of truth.

### Spike request
Reuses the spike structure from `user-story-format.md §3` (Question being answered, Why this is a spike, Time-box, Method, Acceptance for closure, Outcome capture, Scope), plus two handover additions:
- **Unblocks:** the requirement or decision this spike is needed for
- **Context:** links to confirmed shared-repo artefacts only; workspace-sourced context embedded; any working assumption flagged as provisional

The markdown is the source; `HK-DH-JIRA-ticket` renders it into the Jira spike per `jira-ticket-format.md`.

### ADR request
```markdown
# ADR Request: <decision title>
**Initiative:** <name>  ·  **Scope:** <name>  ·  **Date:** <date>

## Decision needed
[The architecture decision to be made, stated as a question. Not "look at the architecture."]

## Why it's needed now
[What this unblocks. Which requirements / slices are waiting on it.]

## Confirmed inputs
- Requirements: [link to confirmed/requirements.md]
- Current state: [link]
- Gap: [link]

## Known options / constraints (if any)
[From Solution Shaping, if options were already surfaced. Otherwise "open."
Constraints sourced from the tracker are embedded here with their IDs.]

## What I need back
An ADR recorded at confirmed/design/ADR-NNN, with the decision, rationale, and any
new constraints it introduces so I can slice against it.
```

### Story pack
DoR-passed stories per `user-story-format.md`, grouped by slice, with the traceability matrix (requirement → AC → story) at the top. Nothing new invented here; this is the existing story format, published to the repo and fed to Jira.

---

## 6. Publish rules

- Confirmed artefacts overwrite their file on republish (last confirmed wins); the README index date updates.
- Exchanges are append-only; a new spike is a new file, never an edit to a closed one.
- Every confirmed artefact carries a `Last confirmed: <date>` header so a dev can see its age at a glance.
- On republish of a confirmed artefact, State Validator checks whether any open exchange or downstream artefact depended on the old version (`HK-DH-SV-register`).

---

## 7. Conformance (checked by State Validator)

| Check | Rule |
|---|---|
| No working leakage | No handover links to a git-ignored working file; workspace-sourced content appears only as embedded summaries |
| Confirmed only | Every requirement in a pack is `status: confirmed` |
| Freshness | Published confirmed artefact matches current register (no drift) |
| Traceability | Story pack traces requirement → AC → story; embedded RAID rows carry tracker IDs |
| Note present | Every published artefact has a handover note |

---

## 8. Versioning

v1.0 (2026-07-05). Added with the Dev Handover skill (Wave 9). New artefact type or new required field requires a version bump.
