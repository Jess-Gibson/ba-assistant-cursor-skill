---
name: ba-context-capture
description: Passively detects new facts, decisions, blockers, context, and open questions emerging in normal conversation and writes them to SESSION-CONTEXT.md in real time. Also actively surfaces relevant learnings.md patterns at key inflection points. Fills the gap between meeting debrief (meeting-specific) and end-of-session checkpoint (wrap-up only). Runs continuously alongside the Anti-Pattern Detector.
disable-model-invocation: true
---

# Skill: Context Capture (Mid-Chat)

## Description

The Context Capture skill runs **passively and continuously** during every BA Assistant conversation. Its job is to detect when new information emerges in the flow of normal chat  -  not just from meeting debriefs or formal skill outputs  -  and persist it to `SESSION-CONTEXT.md` so it survives context window limits and session boundaries.

**Why this exists:** The most common information loss pattern is not meetings (Meeting Debrief handles those) or formal outputs (skills write their own artefacts). It's the **casual mid-chat reveal**  -  the user mentions a blocker in passing, confirms a decision while discussing something else, drops a new stakeholder name, corrects an assumption, or shares context that changes understanding. Without this skill, that information only lives in the chat transcript and is lost at session end or context window rotation.

## Continuous monitoring

This skill runs continuously, not on-demand. After every user message, perform a fast scan for new capturable information. The scan is **silent when nothing is found**  -  no visible output unless something worth capturing is detected.

When something is detected, surface it briefly and write it **in the same turn** (never batch captures for later: a chat can end at any point). Do not interrupt the flow of conversation  -  append a short capture confirmation at the end of the response, not as a separate interruption.

**Detection is yours, the write is the script's.** Spotting the signal, deciding it is worth keeping, and wording it well is the valuable part and stays with you every turn. The file write is mechanical: `_workstream/capture.py` appends to today's captures section without you reading or re-editing the whole `SESSION-CONTEXT.md`, skips anything already there, and tags each line so `/wrap`, `/validate-state`, end of day and the stop hook see it as unpromoted. One call per turn, however many items.

## What to capture (signal types)

| Signal type | Pattern to detect | Example |
|---|---|---|
| **Requirement (new or changed)** | User states something the solution must do, a rule, a threshold, an acceptance condition | "Refunds over $500 need a second approver" |
| **Action** | Someone commits to do something ("I'll", "can you ask", "Priya will send") | "I'll send the AC draft to Priya by Wednesday" |
| **Decision (informal)** | User states a choice, confirms a direction, says "let's go with X", "we decided", "I spoke to [person] and they said Y" | "Yeah we're going with option B for the API" |
| **Blocker (new or resolved)** | User mentions something is stuck, waiting, blocked, or conversely says something is now unblocked | "Still waiting on legal for that sign-off" / "Legal came back, we're good" |
| **Open question (new)** | User raises something they don't know yet, asks "do we know if…", "I need to find out…", "not sure about…" | "I don't actually know if the legacy system supports that" |
| **Open question (resolved)** | User answers a previously logged OQ, or says "turns out…", "I found out…", "confirmed that…" | "Spoke to infra  -  they said the limit is 500 per batch" |
| **Assumption (new or corrected)** | User states something as believed-true without evidence, or corrects a prior assumption | "I think the cutover window is 2 hours but I haven't confirmed" |
| **Dependency (new)** | User mentions another team, system, approval, or timeline that gates their work | "We can't start that until the platform team finishes their migration" |
| **Stakeholder context** | New name, role, responsibility, opinion, or relationship mentioned | "[Team Member] is actually the one who owns that decision, not Bob" |
| **Scope change signal** | User mentions something is in/out that wasn't before, or priority has shifted | "Actually we're not doing the bulk upload in v1 anymore" |
| **Contextual fact** | System behaviour, business rule, constraint, or domain knowledge the user shares | "The settlement file runs at 3am AEST, not midnight" |
| **Correction** | User corrects something previously captured  -  a fact, name, date, status | "That date was wrong  -  it's the 15th not the 12th" |
| **Risk surfaced** | User mentions something that could go wrong, a concern, or a what-if | "If the vendor doesn't deliver by July we're in trouble" |
| **Timeline / date** | User mentions a deadline, milestone, or date constraint | "Go-live is locked in for August 4" |

## What NOT to capture

- Conversational filler, greetings, thinking-out-loud that the user immediately corrects
- Questions directed at the assistant (these are instructions, not facts)
- Information already captured in SESSION-CONTEXT.md or the tracker
- Speculative discussion the user explicitly marks as "just thinking" / "ignore that" / "scratch that"

## How to capture

### Write it with the script

```text
python3 ~/.cursor/_workstream/capture.py --initiative <slug> --json -      (Windows: py)
```

with a JSON list on stdin, one object per item:

| Field | Use |
|---|---|
| `type` | `decision`, `requirement`, `action`, `question`, `answered` (a logged question now resolved), `assumption`, `risk`, `blocker`, `dependency`, `scope`, `stakeholder`, `fact`, `date`, `correction` |
| `text` | The item in one plain sentence (the landing point, not the journey) |
| `context` | Optional one line on why it matters |
| `resolution` | For `answered`: the answer and who gave it |
| `status` | Optional: `new`, `resolved`, `confirmed`, `corrected` |
| `owner`, `due` | For actions and questions |
| `mine` | `true` on an action the BA owns: it is also upserted into `ba-actions.json` in the same call |
| `route` | Optional skill to route to at the next natural break (see Routing) |

The script prints `Capture: PASS (N written, M already there)`. Use that for the 📝 line. If it prints `FAIL` (no initiative named, file missing), say so in the 📝 line and write the items with a normal edit instead. Never drop a capture silently. If the script is not installed, append by hand in the format below.

### Format in SESSION-CONTEXT.md (what the script writes)

Items land under `## Mid-session captures - YYYY-MM-DD`, in the sub-section for their type, each line tagged with a promotion marker (`DEC-new`, `REQ-new`, `ACT-new`, `OQ-new`, `OQ-answered`, `ASM-new`, `RISK-new`, `RISK-blocker`, `DEP-new`, and `SCOPE-`/`STK-`/`FACT-`/`DATE-`/`FIX-` notes) and a time. Promotion adds `[promoted]` to the line. The older layout below is still read everywhere:

```markdown
## Mid-session captures  -  [today's date]

### Decisions
- [timestamp or turn-approximate] [decision text]  -  source: chat with user
  - Context: [1-line why this matters]

### Blockers
- [🔴 new | ✅ resolved] [blocker text]  -  [date if mentioned]

### Open questions
- [❓ new | ✅ resolved] [question text]
  - Resolution (if resolved): [answer]

### Assumptions
- [⚠️ new | ✅ confirmed | ❌ corrected] [assumption text]

### Dependencies
- [🚧 new | ✅ resolved] [dependency text]  -  [team/system]

### Context & facts
- [fact text]  -  source: user stated [date]

### Scope changes
- [in/out/shifted] [what changed]  -  [reason if given]

### Risks
- [🧨 new] [risk text]  -  [severity if obvious]

### Stakeholder updates
- [name]  -  [new info: role, opinion, ownership, contact]

### Timeline / dates
- [milestone/deadline]  -  [date]  -  [source]
```

### Capture confirmation (inline, not interruptive)

At the end of the normal response (after the main content and before the AskQuestion), add a brief capture line:

> 📝 *Captured: [1-line summary of what was logged]*

If multiple items were captured in one turn:

> 📝 *Captured: [item 1], [item 2], [item 3]*

### Corrections

When the user corrects a previously captured fact:
1. Find the original entry in SESSION-CONTEXT.md (Grep for it; do not read the whole file)
2. Strike it (prefix with `~~` or mark as `[CORRECTED]`)
3. Add the corrected version with `capture.py`, type `correction`, text including `[corrected from: original]`
4. Confirm: "📝 *Corrected: [what changed]*"

## Routing (when capture implies action)

Some captured items should also trigger other skills. The context capture skill does NOT replace those skills  -  it captures the fact AND flags the routing:

| Captured signal | Also route to |
|---|---|
| New requirement (even informal) | `ba-requirements-interrogator` |
| Decision that should be in the tracker | `ba-risk-and-tracker` (flag for promotion) |
| Blocker that's a project risk | `ba-risk-and-tracker` |
| Scope change | `ba-anti-pattern-detector` (scope creep check) |
| Stakeholder change | `ba-stakeholder-strategy` |
| Sponsor signal | `ba-sponsor-engagement` |

Routing is a flag, not an immediate invocation. Note in the capture: `→ route to [skill] at next natural break`. The orchestrator decides when to invoke.

## Promotion at session end

At the end-of-session checkpoint, all mid-session captures are reviewed:
- **Confirmed facts** → promote to `initiative-tracker.md` or `status-data.json`
- **Tentative items** → keep in SESSION-CONTEXT.md for next session confirmation
- **Contradictions** → surface to user for resolution before promotion
- **Stale items** → mark as needing re-confirmation

## Anti-patterns this skill prevents

- "I told you that last session"  -  user shared a fact but it wasn't persisted
- "We already decided that"  -  informal decision made in chat but never logged
- "That blocker was resolved ages ago"  -  resolution mentioned casually but tracker still shows blocked
- "I mentioned [Team Member] owns that"  -  stakeholder context shared but lost
- "The date changed"  -  timeline correction in chat but not reflected in artefacts
- "We dropped that from scope"  -  scope change mentioned but not captured anywhere

## Challenge rules

- **Don't over-capture**  -  if a user is rambling or exploring ideas, don't log every sentence. Capture the landing point, not the journey.
- **Don't capture without the user seeing**  -  every capture gets the inline `📝` confirmation. No silent writes.
- **Don't duplicate**  -  the script skips an item whose text is already in SESSION-CONTEXT.md. If the fact changed, capture the new version (a `correction` when it replaces an old one).
- **Don't block the conversation**  -  capture is a suffix to your response, never a separate interruption. The user's question/task always comes first.
- **Don't guess attribution**  -  if the user says "someone mentioned X", log it as unattributed. Don't invent a source.
- **Don't promote mid-session**  -  SESSION-CONTEXT.md is the landing zone. Promotion to tracker happens at session end (end-of-session checkpoint). Exception: if the user explicitly says "add that to the tracker"  -  then promote immediately.
- **Don't capture instructions to you**  -  "can you check the Jira board" is a task, not a fact. Only capture information *about the initiative*.

## Active learnings surfacing (Wave 6)

`_workstream/learnings.md` is read at intake (by Intake Reviewer) and during retros. Between those points, patterns sit dormant. Active surfacing fixes that  -  this skill queries `_workstream/learnings.md` at specific inflection points during work and surfaces relevant patterns in chat, the same way it surfaces mid-chat captures.

(Moved here from `ba-assistant/SKILL.md` Wave 6, folded in because it's the same "watch every turn, surface without blocking" shape as mid-chat capture, rather than a separate always-loaded orchestrator section.)

### Inflection points

| Inflection | What to search for |
|---|---|
| New requirement entering the register | Patterns tagged with "requirement", "interrogation", or matching the requirement's domain |
| Workstream transitions to active for a scope | Patterns specific to that workstream (Discovery, Slicing, Delivery, etc.) |
| A new stakeholder added to the strategy | Patterns tagged with "stakeholder" or "engagement" |
| A spike created or assigned | Patterns about spikes (outcome capture, stalled spikes, scope creep on spikes) |
| A workshop being designed | Patterns about workshop facilitation, attendance, debrief, Miro |
| A Confluence page being published | Patterns about page hierarchy, supersede markers, status pages |
| A bulk file operation being proposed | Patterns about sync, content review, currency checks |
| Sponsor or PM is being engaged with new content | Patterns about pre-brief timing, exec narrative, sentiment |

### Surfacing format

A single chat line BEFORE the work proceeds, never blocking:

```
💡 **Learning from previous initiatives:** [one-line pattern]. [One-line application to current context]. [What I'll do unless you say otherwise]
```

Example:

```
💡 **Learning from previous initiatives:** On Sample Initiative we hit document proliferation when a new register was created without marking the old one superseded. I'll check whether this new requirements doc replaces or supplements `current-requirements.md` before creating it. Say "skip the learning" if not relevant.
```

### Rules

1. **Match strength matters.** Surface Established patterns aggressively. Surface Candidate patterns only when the match is strong (current context matches multiple keywords from the pattern). Skip Archived patterns unless explicitly invoked.

2. **One surfacing per inflection point.** Don't bombard. If 3 patterns match, pick the most relevant; mention the others exist with "I'm also tracking 2 other patterns here, ask if you want them."

3. **Never block.** The pattern is information, not gate. Work proceeds unless the user says "wait, that's relevant."

4. **Don't surface patterns about the failure mode the user is actively avoiding.** If they're already taking the right action, surfacing the pattern adds noise. Use judgement  -  if context shows the action is being handled correctly, skip.

5. **Log every surfacing in `metrics-cache.json → learningSurfacings`.** This is itself data  -  patterns that surface frequently but never change behaviour are candidates for archive; patterns that surface and change behaviour are validated as valuable.

### Anti-pattern (added to Anti-Pattern Detector)

| Watching | Trigger | Anti-pattern flagged |
|---|---|---|
| Orchestrator | Inflection point reached AND no `_workstream/learnings.md` query AND patterns exist that match the context | Dormant learnings  -  pattern not surfaced when it should have been (added Wave 6) |
| Orchestrator | Same pattern surfaced 5+ times in a session OR 10+ times across 3 sessions with no behaviour change | Noisy pattern  -  candidate for archive (added Wave 6) |

## Integration with BA Assistant

**Mode:** Passive / continuous  -  runs alongside Anti-Pattern Detector and Requirements Interrogator.

**Not phase-bound.** Runs from the first user message to the last, across all workstreams and scopes.

**Hooks calling this skill:** None  -  it self-triggers on every user message.

**Hooks called by this skill:**
- Flags routing to other skills (see Routing table above)
- Feeds end-of-session checkpoint with structured mid-session captures

**Living tracker updates:** Indirect  -  writes to SESSION-CONTEXT.md which is promoted to tracker at session end.
