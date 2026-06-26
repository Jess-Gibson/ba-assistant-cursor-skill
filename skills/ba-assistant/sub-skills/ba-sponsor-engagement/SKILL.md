---
name: ba-sponsor-engagement
description: Sustained sponsor cadence, pre-decision briefings, political cover, exec narrative, escalation. Standish CHAOS #1 success factor â€” distinct from broad stakeholder strategy.
---

# Skill: Sponsor Engagement

## Description

The Sponsor Engagement skill manages the **sustained relationship with the executive sponsor** throughout the initiative. The sponsor is not a generic stakeholder â€” they are the single person whose funding, political cover, and decision-rights make the initiative possible. The Standish Group's CHAOS research has consistently identified **executive sponsorship as the #1 predictor of project success**, ahead of methodology, team skill, or scope clarity.

This skill is **distinct from Stakeholder Strategy**. Stakeholder Strategy is broad (everyone impacted) and shallow per person. Sponsor Engagement is narrow (typically 1-2 people) and deep â€” cadence, pre-briefing, political navigation, exec-friendly narrative, escalation paths, and funding/scope protection.

This skill exists because BAs and PMs reliably under-invest in sponsor engagement when they're busy. The result: sponsor finds out late, makes uninformed decisions, withdraws political cover at the wrong moment, or kills the initiative when a quick conversation would have saved it.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (sponsor profile, pre-brief, status updates, escalation drafts, engagement plan, decision-trees). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant\SKILL.md â†’ Co-thinking and artefact production protocol` â€” surface planned artefacts upfront and ask the user to select. The RBA dry-run produced a full sponsor profile on a single user-yes â€” this rule prevents that.

## Mandatory hooks

| Hook | When | Why |
|---|---|---|
| **Communication_Drafter** (or Playback_and_Enablement if merged) | Always | Sponsor emails, pre-reads, status updates â€” drafted, not improvised |
| **Visual_Storytelling** | Before any sponsor briefing | One-page exec summaries, decision trees, outcome charts â€” not detailed delivery views |
| **Risk_and_Tracker** | Always | Surface sponsor-impacting risks (funding, scope, political); track sponsor decisions |
| **Stakeholder_Strategy** | At Phase 0 / M0 | Sponsor identification cross-references the broader stakeholder map |
| **Solution_Evaluation** | Post-launch | Sponsor sees outcome reports, not just delivery completion |

## When to invoke

- **At Phase 0 / M0 Intake** â€” identify the sponsor (if missing or unclear, that's itself a finding)
- **Before every major decision moment** â€” pre-brief the sponsor so they don't hear it cold
- **On agreed cadence** â€” typically fortnightly or monthly 1:1, plus quarterly steering
- **When budget or scope is at risk** â€” sponsor needs early warning, not late surprise
- **When timeline slips materially** â€” same
- **When a cross-team blocker appears** â€” sponsor's political cover may be needed
- **At every gate** â€” sponsor sign-off on phase/mode exits where applicable
- **Post-launch** â€” sponsor sees the Solution Evaluation report, not just "we shipped it"

## Tasks

1. **Identify the sponsor** â€” At intake, ask explicitly: who is the executive sponsor? If the answer is unclear ("the steering committee", "my manager and his manager", "TBC") that's a ðŸ§¨ risk to log immediately. An unsponsored initiative is a high-mortality initiative.

2. **Build a sponsor profile** â€” Capture:
   - Name, role, level (which exec tier)
   - What they personally care about (their KPIs, their political position, their narrative)
   - Their preferred communication style (detailed deck / one-page / verbal only / Slack)
   - Their meeting cadence preference (weekly 15min / fortnightly 30min / monthly hour / ad-hoc only)
   - Pre-read preference (read everything in advance / bullet points only / no pre-read, brief verbally)
   - Decision style (data-driven / instinct-driven / consensus-seeking / unilateral)
   - Who else the sponsor relies on for confidence in this initiative (CFO, peer exec, board member)
   - Past initiatives â€” what's the sponsor's pattern? Detail-driven? Withdraws when busy? Aggressive escalator? Avoids hard conversations?

3. **Establish a cadence and document it** â€” Agree the recurring touchpoint, format, and content. Document explicitly. Cancel reactively, not proactively â€” once a cadence is dropped it's hard to restart.

4. **Build a sponsor engagement plan** â€” Map known decision moments (intake sign-off, scope confirmation, solution selection, delivery commitment, launch decision, post-launch evaluation) and plan how the sponsor will be engaged at each. Each entry: trigger, format, audience, pre-read, decision needed, owner.

5. **Pre-brief before decision moments** â€” Sponsor should never first hear a request for a decision in a meeting where the decision is being made. Provide a 1:1 pre-brief (verbal or written) at least 48 hours before so they can:
   - Ask their questions privately (saving face)
   - Surface political concerns we don't know about
   - Pre-align with peer execs
   - Refine the request before it's surfaced publicly

6. **Translate BA work into exec narrative** â€” Sponsors don't want the requirements register; they want: what problem, what value, what risk, what decision needed, what cost. Translate every artefact through this lens before presenting to the sponsor. Coordinate with `Visual_Storytelling` for one-pagers.

7. **Surface political cover needs early** â€” Sometimes the BA/PM needs the sponsor to back them publicly (e.g. when another team is blocking, when scope creep is being requested, when a hard "no" is needed). Surface these needs in the next cadence call, with the ask framed clearly: "I need you to do X in Y forum because Z."

8. **Track sponsor decisions explicitly** â€” Every sponsor decision gets a row in the decisions table (per BA profile): `ID | Decision | Made by | Date | Status`. If the sponsor verbally agrees but it's never written down, it's not a decision â€” it's a hope.

9. **Escalation playbook** â€” Define in advance: under what conditions will we escalate? Through what channel? Who escalates (BA / PM / Tech Lead / sponsor's delegate)? This avoids the "should I escalate this?" loop that wastes weeks.

10. **Handle sponsor change** â€” If the sponsor leaves or is replaced mid-initiative, treat it as a critical event. Re-run sponsor profile + engagement plan with the new person; don't assume continuity.

11. **Sponsor-facing outputs** â€” Maintain a dedicated set of artefacts for sponsor consumption: monthly exec one-pager, decision log, RAID summary (top 3 risks only), outcome dashboard post-launch. These are *distinct from* the working BA artefacts.

12. **Update living tracker** â€” Sponsor commitments, sponsor risks, sponsor-pending decisions, sponsor sign-off status.

## Typical Questions to Ask

### At intake
- Who is the executive sponsor for this initiative? (If unclear â†’ ðŸ§¨ risk)
- What does success look like to them personally? (Often different from the team's view)
- What's the worst outcome from their perspective? What would cause them to lose interest or pull the plug?
- Have they sponsored similar initiatives? How did those go?
- Who do they rely on for confidence in this initiative (CFO, peer exec, board member)?

### Cadence planning
- How often does the sponsor want to be updated, and in what format?
- What's the existing cadence (steering committee, monthly 1:1, all-hands)? Do we fit there, or do we need a new touchpoint?
- Who else needs to be in sponsor-facing forums (CFO, legal, peer business units)?

### Before decision moments
- Has the sponsor been pre-briefed? When? How did they respond?
- Are there political concerns they haven't surfaced? (Ask the sponsor's delegate or chief of staff if one exists)
- Have peer execs been pre-aligned? Is anyone likely to challenge in the room?
- Is the ask framed in the sponsor's language (value, risk, cost, decision)?

### Sustained engagement
- Has the sponsor been silent for more than the agreed cadence? (Silence often means disengagement â€” investigate)
- Has anything changed in the sponsor's world that affects this initiative (their KPIs, their boss, their org)?
- Have we asked the sponsor for political cover when we needed it? Did they provide it?

## Output Guidelines

### Sponsor profile

| Field | Value |
|---|---|
| Name | |
| Role | |
| Personal stake | What they care about |
| Communication preference | |
| Cadence preference | |
| Pre-read preference | |
| Decision style | |
| Relies on | Other execs / data sources |
| Past initiative pattern | |
| Political concerns | |

### Sponsor engagement plan

| Decision moment | Trigger | Format | Audience | Pre-read | Decision needed | Owner | Date |
|---|---|---|---|---|---|---|---|

### Sponsor decision log (subset of main decisions table)

| ID | Decision | Made by (sponsor) | Date | Status | Documented in |
|---|---|---|---|---|---|

### Monthly exec one-pager template (sponsor-facing)

- What we shipped this month (1-2 bullets)
- What's in flight (1-2 bullets, no detail)
- Decision needed from you (yes/no + by when)
- Top 3 risks (1 line each)
- Sustained progress chart (Visual_Storytelling)

### Escalation playbook

| Trigger condition | Channel | Escalator | Sponsor action expected | SLA |
|---|---|---|---|---|

## Challenge Rules

- **Don't accept "we don't have a sponsor"** â€” find one or flag the initiative as high-risk. Unsponsored initiatives reliably underperform.
- **Don't accept "the steering committee is the sponsor"** â€” committees don't sponsor; individuals do. Find the individual.
- **Don't conflate stakeholder updates with sponsor engagement** â€” broad stakeholder comms â‰  sponsor 1:1s. Both are needed.
- **Don't let the cadence drift** â€” once dropped, hard to restart. Hold the line on the agreed touchpoint.
- **Don't surface decisions cold** â€” pre-brief is non-negotiable for material decisions.
- **Don't write to the sponsor in BA-speak** â€” exec narrative is value/risk/cost/decision. Translate or hand off to `Communication_Drafter` and `Visual_Storytelling`.
- **Don't paper over silence** â€” if the sponsor has gone quiet, investigate. Silence is rarely neutral.
- **Don't let sponsor decisions live verbally** â€” written log, owner, date. No exception.
- **Don't survive a sponsor change passively** â€” re-engage formally, re-confirm scope, re-confirm appetite. New sponsor is a new initiative.
- **Don't let the sponsor become a single point of failure** â€” identify a sponsor-deputy where possible; build relationships with peer execs the sponsor relies on.

## Integration with BA Assistant

**Mode (post-Wave 3):** Cross-cutting capability (like Risk & Tracker). Active across all scopes throughout the initiative lifecycle.

**Pre-Wave 3 (current sequential model):** Invoked at Phase 0 (sponsor identification) and then sustained across all subsequent phases.

**Hooks called by this skill:** Communication_Drafter, Visual_Storytelling, Risk_and_Tracker, Stakeholder_Strategy, Solution_Evaluation.

**Hooks calling this skill:**
- Intake_Reviewer at Phase 0 (sponsor identification is part of intake)
- Solution_Shaping before major design decisions (sponsor pre-brief)
- Delivery_Definition before commitment to scope (sponsor sign-off)
- Playback_and_Enablement before launch (sponsor go/no-go)
- Solution_Evaluation post-launch (sponsor sees outcomes)
- `/status` and `/publish-status` (sponsor-facing outputs)

**Living tracker updates:** sponsor profile, engagement plan, sponsor decisions log, sponsor-impacting risks, sponsor sign-offs.

**Anti-pattern this skill prevents:** "Surprised sponsor". Sponsor first hears about a problem in a forum where they're expected to make a decision, can't, gets defensive, withdraws cover. Or: sponsor goes silent, BA assumes consent, sponsor cancels initiative when next reviewed. Both are catastrophic and entirely preventable.

