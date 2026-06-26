---
name: ba-context-capture
description: Passively detects new facts, decisions, blockers, context, and open questions emerging in normal conversation and writes them to SESSION-CONTEXT.md in real time. Fills the gap between meeting debrief (meeting-specific) and end-of-session checkpoint (wrap-up only). Runs continuously alongside the Anti-Pattern Detector.
---

# Skill: Context Capture (Mid-Chat)

## Description

The Context Capture skill runs **passively and continuously** during every BA Assistant conversation. Its job is to detect when new information emerges in the flow of normal chat â€” not just from meeting debriefs or formal skill outputs â€” and persist it to `SESSION-CONTEXT.md` so it survives context window limits and session boundaries.

**Why this exists:** The most common information loss pattern is not meetings (Meeting Debrief handles those) or formal outputs (skills write their own artefacts). It's the **casual mid-chat reveal** â€” the user mentions a blocker in passing, confirms a decision while discussing something else, drops a new stakeholder name, corrects an assumption, or shares context that changes understanding. Without this skill, that information only lives in the chat transcript and is lost at session end or context window rotation.

## Continuous monitoring

This skill runs continuously, not on-demand. After every user message, perform a fast scan for new capturable information. The scan is **silent when nothing is found** â€” no visible output unless something worth capturing is detected.

When something is detected, surface it briefly and write it. Do not interrupt the flow of conversation â€” append a short capture confirmation at the end of the response, not as a separate interruption.

## What to capture (signal types)

| Signal type | Pattern to detect | Example |
|---|---|---|
| **Decision (informal)** | User states a choice, confirms a direction, says "let's go with X", "we decided", "I spoke to [person] and they said Y" | "Yeah we're going with option B for the API" |
| **Blocker (new or resolved)** | User mentions something is stuck, waiting, blocked, or conversely says something is now unblocked | "Still waiting on legal for that sign-off" / "Legal came back, we're good" |
| **Open question (new)** | User raises something they don't know yet, asks "do we know ifâ€¦", "I need to find outâ€¦", "not sure aboutâ€¦" | "I don't actually know if the legacy system supports that" |
| **Open question (resolved)** | User answers a previously logged OQ, or says "turns outâ€¦", "I found outâ€¦", "confirmed thatâ€¦" | "Spoke to infra â€” they said the limit is 500 per batch" |
| **Assumption (new or corrected)** | User states something as believed-true without evidence, or corrects a prior assumption | "I think the cutover window is 2 hours but I haven't confirmed" |
| **Dependency (new)** | User mentions another team, system, approval, or timeline that gates their work | "We can't start that until the platform team finishes their migration" |
| **Stakeholder context** | New name, role, responsibility, opinion, or relationship mentioned | "[Stakeholder A] is actually the one who owns that decision, not [Stakeholder B]" |
| **Scope change signal** | User mentions something is in/out that wasn't before, or priority has shifted | "Actually we're not doing the bulk upload in v1 anymore" |
| **Contextual fact** | System behaviour, business rule, constraint, or domain knowledge the user shares | "The settlement file runs at 3am AEST, not midnight" |
| **Correction** | User corrects something previously captured â€” a fact, name, date, status | "That date was wrong â€” it's the 15th not the 12th" |
| **Risk surfaced** | User mentions something that could go wrong, a concern, or a what-if | "If the vendor doesn't deliver by July we're in trouble" |
| **Timeline / date** | User mentions a deadline, milestone, or date constraint | "Go-live is locked in for August 4" |

## What NOT to capture

- Conversational filler, greetings, thinking-out-loud that the user immediately corrects
- Questions directed at the assistant (these are instructions, not facts)
- Information already captured in SESSION-CONTEXT.md or the tracker
- Speculative discussion the user explicitly marks as "just thinking" / "ignore that" / "scratch that"

## How to capture

### Format in SESSION-CONTEXT.md

Append to the relevant section. If no matching section exists, create one.

```markdown
## Mid-session captures â€” [today's date]

### Decisions
- [timestamp or turn-approximate] [decision text] â€” source: chat with user
  - Context: [1-line why this matters]

### Blockers
- [ðŸ”´ new | âœ… resolved] [blocker text] â€” [date if mentioned]

### Open questions
- [â“ new | âœ… resolved] [question text]
  - Resolution (if resolved): [answer]

### Assumptions
- [âš ï¸ new | âœ… confirmed | âŒ corrected] [assumption text]

### Dependencies
- [ðŸš§ new | âœ… resolved] [dependency text] â€” [team/system]

### Context & facts
- [fact text] â€” source: user stated [date]

### Scope changes
- [in/out/shifted] [what changed] â€” [reason if given]

### Risks
- [ðŸ§¨ new] [risk text] â€” [severity if obvious]

### Stakeholder updates
- [name] â€” [new info: role, opinion, ownership, contact]

### Timeline / dates
- [milestone/deadline] â€” [date] â€” [source]
```

### Capture confirmation (inline, not interruptive)

At the end of the normal response (after the main content and before the AskQuestion), add a brief capture line:

> ðŸ“ *Captured: [1-line summary of what was logged]*

If multiple items were captured in one turn:

> ðŸ“ *Captured: [item 1], [item 2], [item 3]*

### Corrections

When the user corrects a previously captured fact:
1. Find the original entry in SESSION-CONTEXT.md
2. Strike it (prefix with `~~` or mark as `[CORRECTED]`)
3. Add the corrected version with `[corrected from: original]`
4. Confirm: "ðŸ“ *Corrected: [what changed]*"

## Routing (when capture implies action)

Some captured items should also trigger other skills. The context capture skill does NOT replace those skills â€” it captures the fact AND flags the routing:

| Captured signal | Also route to |
|---|---|
| New requirement (even informal) | `ba-requirements-interrogator` |
| Decision that should be in the tracker | `ba-risk-and-tracker` (flag for promotion) |
| Blocker that's a project risk | `ba-risk-and-tracker` |
| Scope change | `ba-anti-pattern-detector` (scope creep check) |
| Stakeholder change | `ba-stakeholder-strategy` |
| Sponsor signal | `ba-sponsor-engagement` |

Routing is a flag, not an immediate invocation. Note in the capture: `â†’ route to [skill] at next natural break`. The orchestrator decides when to invoke.

## Promotion at session end

At the end-of-session checkpoint, all mid-session captures are reviewed:
- **Confirmed facts** â†’ promote to `initiative-tracker.md` or `status-data.json`
- **Tentative items** â†’ keep in SESSION-CONTEXT.md for next session confirmation
- **Contradictions** â†’ surface to user for resolution before promotion
- **Stale items** â†’ mark as needing re-confirmation

## Anti-patterns this skill prevents

- "I told you that last session" â€” user shared a fact but it wasn't persisted
- "We already decided that" â€” informal decision made in chat but never logged
- "That blocker was resolved ages ago" â€” resolution mentioned casually but tracker still shows blocked
- "I mentioned [stakeholder] owns that" â€” stakeholder context shared but lost
- "The date changed" â€” timeline correction in chat but not reflected in artefacts
- "We dropped that from scope" â€” scope change mentioned but not captured anywhere

## Challenge rules

- **Don't over-capture** â€” if a user is rambling or exploring ideas, don't log every sentence. Capture the landing point, not the journey.
- **Don't capture without the user seeing** â€” every capture gets the inline `ðŸ“` confirmation. No silent writes.
- **Don't duplicate** â€” before writing, scan SESSION-CONTEXT.md for whether this fact already exists. If it does and hasn't changed, skip.
- **Don't block the conversation** â€” capture is a suffix to your response, never a separate interruption. The user's question/task always comes first.
- **Don't guess attribution** â€” if the user says "someone mentioned X", log it as unattributed. Don't invent a source.
- **Don't promote mid-session** â€” SESSION-CONTEXT.md is the landing zone. Promotion to tracker happens at session end (end-of-session checkpoint). Exception: if the user explicitly says "add that to the tracker" â€” then promote immediately.
- **Don't capture instructions to you** â€” "can you check the Jira board" is a task, not a fact. Only capture information *about the initiative*.

## Integration with BA Assistant

**Mode:** Passive / continuous â€” runs alongside Anti-Pattern Detector and Requirements Interrogator.

**Not phase-bound.** Runs from the first user message to the last, across all workstreams and scopes.

**Hooks calling this skill:** None â€” it self-triggers on every user message.

**Hooks called by this skill:**
- Flags routing to other skills (see Routing table above)
- Feeds end-of-session checkpoint with structured mid-session captures

**Living tracker updates:** Indirect â€” writes to SESSION-CONTEXT.md which is promoted to tracker at session end.

