---
name: ba-kickoff-preparation
description: SUPERSEDED in Wave 3 by ba-workshop-design. Kickoff is now Template 1 inside Workshop Design. Kept as redirect for backwards compatibility.
---

# Skill: Kickoff Preparation (SUPERSEDED)

> ⚠️ **This skill was superseded on Wave 3 of the BA Assistant consolidation.**
>
> Kickoff preparation is now **Template 1 — Initiative Kickoff (D1)** inside `ba-workshop-design`.
>
> All kickoff workshop content (attendees, agenda, pre-read, facilitation tips, success criteria, decisions sought, question bank) lives in:
>
> **`~/.cursor/skills/ba-assistant/sub-skills/ba-workshop-design/SKILL.md`**

## Why superseded

Workshop facilitation is a single discipline. Kickoff, current state, discovery, slicing, solution shaping, refinement, playback, retro, and change kickoff workshops all share the same engine — attendee logic, pre-read drafting, agenda design, facilitation patterns, real-time capture, post-workshop debrief routing. Having one skill per workshop type duplicated that engine.

Workshop Design owns the engine; templates handle the type-specific differences.

## Where to find content

| Old content (in this file) | New location (in `ba-workshop-design/SKILL.md`) |
|---|---|
| Tasks (participant ID, agenda, questions, facilitation, capture) | "Common tasks across all templates" |
| Kickoff agenda | "Template 1 — Initiative Kickoff (D1)" → Agenda |
| Kickoff question bank | "Template 1" → Decisions sought + Facilitation tips |
| Kickoff attendee logic | "Template 1" → Attendees + identification logic |
| Kickoff outcome capture | "Common tasks" → Post-workshop debrief (hands off to `ba-meeting-debrief`) |

## For agents reading this file

If you arrived here looking for kickoff preparation guidance, redirect to `ba-workshop-design` and use Template 1. The hook contracts in `instructions.md` Skill-to-skill hooks table have been updated to call `ba-workshop-design` directly.
