---
name: ba-communication-drafter
description: SUPERSEDED — merged into ba-playback-and-enablement as a cross-cutting utility section. All comms drafting (emails, Slack, invites, escalations, MoSCoW gap messages, change comms) now lives there but is still invokable by any skill via the Communication_Drafter hook name.
---

# SUPERSEDED — see `ba-playback-and-enablement`

This skill has been **merged into `ba-playback-and-enablement`** as of Wave 3 (May 2026).

## Why merged

Communication Drafter and Playback both produce human-facing messages. Playback is the highest-volume consumer of polished comms (executive readouts, ops change notices, customer messaging), and the two skills always operated as a pair when stakeholder messaging was the goal.

By merging:
- Playback's existing communication-planning task gains the full drafting toolkit
- One less skill to load
- Comms drafting still has a clear home

## Honest architectural caveat

**Communication Drafter is genuinely cross-cutting** — 12+ skills invoke it (Discovery, Workshop Design, Risk & Tracker, Stakeholder Strategy, Requirements Interrogator in-flight, Retro, Meeting Debrief, Solution Evaluation, Sponsor Engagement, Change Strategy, DoR/Delivery Definition for MoSCoW messages, and Playback). Merging it into Playback created an awkwardness: a utility lives under a practice skill that doesn't always own the calling context.

The merge proceeded because:
- The user explicitly chose Option B which included this merge
- The hook contract is preserved — any skill can still call `Communication_Drafter` and the orchestrator routes to the section inside Playback
- The alternative (splitting into a peer "tools" layer) would require restructuring the skill hierarchy, which is a Wave 4+ effort

**If this feels wrong after a few initiatives, split Communication Drafter back out.** The split is mechanically simple — copy the section back to a standalone SKILL.md and update the SUPERSEDED marker here.

## Where the content moved

| Old section in `ba-communication-drafter` | New location in `ba-playback-and-enablement` |
|---|---|
| Description | `## Communication Drafter (Wave 3)` opening paragraph |
| Core principle | `### Core principle` |
| Inputs needed | `### Inputs needed before drafting` |
| Tone calibration by audience | `### Tone calibration by audience` |
| Message types (8 templates) + new MoSCoW gap message | `### Message types and structures` |
| Tasks | `### Drafting tasks` |
| Self-critique checklist | `### Self-critique checklist (run before output)` |
| Two modes | `### Two modes` |
| Variants | `### Variants` |
| Follow-up handling | `### Follow-up handling` |
| Output format | `### Output format` |
| Challenge rules | `### Comms-specific challenge rules` |
| What this skill does NOT do | `### What this section does NOT do` |

## What's new

- **MoSCoW gap message template (Wave 3)** — A new template specifically for the warn-and-flag scenario where stories enter delivery without a MoSCoW rating.

## What stayed the same

- All 8+1 message types and templates are unchanged.
- The hook name `Communication_Drafter` remains the contract; any skill can still call it.
- All 12+ caller skills still produce the same output style.

## What to do

If you were planning to invoke this skill, invoke `ba-playback-and-enablement` (or call the `Communication_Drafter` hook from any skill — same result). The drafting section is self-contained within Playback's SKILL.md.
