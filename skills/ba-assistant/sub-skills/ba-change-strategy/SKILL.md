---
name: ba-change-strategy
description: Sustained organisational change management using ADKAR — audience impact assessment, change planning, adoption tracking, resistance management. Bridges Playback & Enablement to full change discipline.
---

# Skill: Change Strategy

## Description

The Change Strategy skill manages the **sustained change management discipline** for an initiative. It picks up where Playback & Enablement leaves off — playback prepares one moment of communication and sign-off; Change Strategy plans, executes, and measures the multi-month behaviour change required for an initiative to actually land in the organisation.

This skill is grounded in **ADKAR** (Awareness → Desire → Knowledge → Ability → Reinforcement) — the most widely adopted individual-change framework — applied per impacted audience. Each audience moves through ADKAR at its own pace. The change plan is not a single comms calendar; it's a per-audience plan that meets each audience where they are.

The skill exists because BAs and PMs reliably underestimate the change effort needed. The result: technically successful launches with low adoption, frustrated audiences, fall-back to the old way, and the initiative is judged a failure even though it "shipped". This is one of the most common failure modes in organisational delivery.

This skill is **distinct from Playback & Enablement**. Playback prepares a specific event (a deck, a sign-off, a launch comms). Change Strategy is the sustained 6–12 month discipline that determines whether the change sticks.

## Mandatory hooks

| Hook | When | Why |
|---|---|---|
| **Stakeholder_Strategy** | Always at start | Audience identification draws from the stakeholder map; both must be in sync |
| **Communication_Drafter** (or Playback_and_Enablement if merged) | For audience-specific comms | Per-audience messaging — drafted, not improvised |
| **Visual_Storytelling** | Always | Change roadmap, audience heatmap, adoption dashboard |
| **Sponsor_Engagement** | Always | Sponsor must publicly back the change; political cover is part of Desire (D in ADKAR) |
| **Solution_Evaluation** | Post-launch | Adoption metrics feed into evaluation; change shortfalls explain outcome shortfalls |
| **Risk_and_Tracker** | Always | Resistance, change fatigue, and adoption gaps are tracked risks |
| **Retrospective_and_Learning** | At change milestones | Patterns about what change techniques worked in this org get fed back |

## When to invoke

- **At Phase 1 / M1 Kickoff** — identify the change scope early, get audience identification right before requirements solidify
- **At Phase 4 / M4 Solution Shaping** — solution choices change the change burden (high-burden solutions need more change investment)
- **At Phase 5 / M5 Delivery** — start the Awareness and Desire work in parallel with build
- **At Phase 6 / M6 Playback & Enablement** — execute Knowledge and Ability for each audience
- **Post-launch (M7 Solution Evaluation alongside)** — sustained Reinforcement; adoption tracking; resistance management
- **When adoption metrics dip** — investigate which ADKAR step has broken down
- **When a new audience is identified mid-flight** — re-run change impact for that audience

## Tasks

1. **Identify impacted audiences** — Cross-reference the stakeholder map with the solution scope. For each impacted group, capture:
   - Audience name (be specific — "[Ops team in Location]", not "ops")
   - Approximate size (people count or %)
   - Current state (what they do today)
   - Future state (what they'll do after the change)
   - Change magnitude (low / medium / high / transformational)
   - Voluntary vs mandated change
   - Influence on other audiences (cascading effects)

2. **Assess change impact per audience using ADKAR** — For each audience, rate where they are today on the ADKAR ladder:
   - **A — Awareness:** Do they know this change is coming and why?
   - **D — Desire:** Do they want it to succeed? Or are they neutral / resistant?
   - **K — Knowledge:** Do they know how to operate in the new state?
   - **A — Ability:** Can they actually do it (tools, time, skill, permissions)?
   - **R — Reinforcement:** Will the change stick, or will old behaviours return?
   The lowest score is the constraint. No point pushing Knowledge if Desire is low — they won't engage with the training.

3. **Build a per-audience change plan** — For each audience and each ADKAR step, plan:
   - The intervention (comms, training, demos, peer champions, manager cascade, incentives)
   - The owner (BA / PM / sponsor / line manager / change champion)
   - The timing (lead time before launch)
   - The success measure (how we know the audience has progressed)
   - The frequency (one-off vs sustained)

4. **Design resistance management** — Resistance is normal, not failure. For each audience, identify:
   - Likely sources of resistance (loss of control, fear of skill gap, workload concerns, political concerns)
   - Resistance signal (what we'll observe — complaints, slow adoption, workarounds, escalations)
   - Response (listen, address, escalate, override)
   - Owner

5. **Define adoption metrics per audience** — Adoption is not "did they log in once". For each audience, define:
   - Leading indicator (early signal of adoption — e.g. training completion, first use within 7 days)
   - Lagging indicator (sustained adoption — e.g. weekly active use, % of transactions through new path)
   - Quality indicator (right use — e.g. error rate, escalation rate, support ticket volume)
   - Target value and timeline

6. **Plan reinforcement** — The R in ADKAR is the most commonly skipped step. Plan how the change is sustained 1, 3, 6, 12 months post-launch:
   - Manager check-ins
   - Embedded in performance review or KPI
   - Peer recognition / champion network
   - Tooling defaults that make the new way the easy way
   - Removal of the old way (where appropriate)

7. **Build a change roadmap** — Visual timeline showing per-audience ADKAR progression against initiative milestones. Hand off to Visual_Storytelling.

8. **Coordinate with Playback & Enablement** — Playback owns specific events; Change Strategy owns the sustained plan. Make sure they're aligned, not duplicating.

9. **Coordinate with Sponsor Engagement** — Sponsor needs to publicly back the change (Desire), be visible at key moments (Awareness), and call out non-adoption when it matters (Reinforcement). Build this into the sponsor engagement plan.

10. **Track adoption + resistance + change health** — Sustained dashboard from launch to ~12 months. Adoption metrics, resistance signals, change fatigue (especially when multiple initiatives target the same audience). Surface gaps weekly initially, monthly thereafter.

11. **Handle change saturation** — If the same audience is being asked to absorb multiple concurrent changes, surface this as a 🧨 risk. Saturated audiences underperform across all changes. Recommend sequencing or pausing.

12. **Update the living tracker** — Audience list, ADKAR scores, change plan, adoption metrics, resistance log, change-impacting risks.

## Typical Questions to Ask

### Audience identification
- Who actually changes their behaviour because of this initiative?
- For each impacted group: how many people? Where are they? Are they part of one team or distributed?
- Is the change voluntary or mandated?
- Are there cascading audiences (e.g. ops change affects support, which affects customers)?

### Change magnitude
- For each audience, what's actually changing — a tool, a process, a role, a mindset?
- How big is the change relative to other things this audience is dealing with right now?
- Have they been asked to change recently? Are they change-fatigued?
- What was the last change like for them? Did it land well or poorly?

### ADKAR per audience
- **Awareness:** How will this audience first hear about the change? When? From whom? In what tone?
- **Desire:** Why should they want this to succeed? What's in it for them? What's the cost to them of resisting?
- **Knowledge:** What do they need to know to operate in the new state? Who teaches it? In what format?
- **Ability:** Do they have the tools, time, skill, permissions, and bandwidth to do the new thing? What's missing?
- **Reinforcement:** How will the change stick beyond launch + 30 days? Who reinforces? Through what mechanism?

### Resistance and risk
- Who is likely to resist? Why? What are their valid concerns?
- What signals will tell us resistance is building? Where will we see it first?
- Is the change so significant that some people may exit (voluntary attrition)?
- Are there political dynamics (one team gaining capability another loses)?

### Coordination
- Does this initiative compete with other concurrent changes for the same audience's attention?
- Are line managers aligned and capable of cascading the change?
- Is the sponsor visible at the moments that matter to each audience?

### Post-launch
- What adoption rate counts as success? When?
- What does sustained adoption look like at 90/180/365 days?
- How will we hear about resistance in time to do something about it?

## Output Guidelines

### Audience register

| Audience | Size | Current state | Future state | Change magnitude | Voluntary/Mandated | Cascading effects |
|---|---|---|---|---|---|---|

### Per-audience ADKAR assessment

| Audience | A | D | K | A | R | Constraint |
|---|---|---|---|---|---|---|

(score 🟢 high / 🟡 medium / 🔴 low for each ADKAR step; "Constraint" = the lowest)

### Per-audience change plan

| Audience | ADKAR step | Intervention | Owner | Lead time | Success measure | Frequency |
|---|---|---|---|---|---|---|

### Resistance log

| Audience | Likely source | Signal to watch | Response | Owner | Status |
|---|---|---|---|---|---|

### Adoption metrics

| Audience | Leading indicator | Lagging indicator | Quality indicator | Target | Owner |
|---|---|---|---|---|---|

### Change roadmap (via Visual_Storytelling)

Visual timeline: per-audience ADKAR progression overlaid on initiative milestones (launch, +30 days, +90 days, +180 days).

### Reinforcement plan

| Audience | Reinforcement mechanism | Owner | Cadence | First check date |
|---|---|---|---|---|

### Living tracker updates

- Audience list with ADKAR scores
- Change plan tasks
- Resistance items as 🧨 risks (where material)
- Adoption metrics + actuals
- Change-related decisions (e.g. "Old workflow turned off on date X")

## Challenge Rules

- **Don't equate launch with adoption** — shipping the feature is M5/M6. Adoption is M7/M8 work that lasts months.
- **Don't conflate Playback with Change Strategy** — Playback is an event; Change is a sustained discipline.
- **Don't skip ADKAR steps in sequence** — pushing Knowledge before Desire wastes everyone's time.
- **Don't assume mandated change works** — mandates without Desire produce malicious compliance and reversion.
- **Don't ignore resistance** — surfaced resistance is information; suppressed resistance becomes sabotage.
- **Don't run a single comms plan for all audiences** — each audience needs its own ADKAR plan with its own pace.
- **Don't ignore change saturation** — if the same team has 4 changes hitting them this quarter, all 4 will underperform.
- **Don't let the sponsor opt out** — sponsor visibility is part of Awareness and Desire for senior audiences. If the sponsor won't be visible, flag it.
- **Don't skip Reinforcement** — the change reverts at week 6 if nothing reinforces it.
- **Don't measure "did they use it once"** — measure sustained, quality adoption per audience.
- **Don't blame the audience for poor adoption** — if adoption is low, the change plan was wrong. Diagnose the failed ADKAR step and fix the plan, not the people.

## Integration with BA Assistant

**Mode (post-Wave 3):** M8 — Change Strategy. Sustained across the whole initiative; active from M1 onwards, continues post-launch alongside M7 Solution Evaluation.

**Pre-Wave 3 (current sequential model):** Invoked at Phase 1, sustained across all subsequent phases, continues post-Phase 6.

**Hooks called by this skill:** Stakeholder_Strategy, Communication_Drafter, Visual_Storytelling, Sponsor_Engagement, Solution_Evaluation, Risk_and_Tracker, Retrospective_and_Learning.

**Hooks calling this skill:**
- Kickoff_Preparation at Phase 1 (audience identification)
- Solution_Shaping at Phase 4 (solution choices change the change burden)
- Playback_and_Enablement at Phase 6 (coordinate event with sustained plan)
- Solution_Evaluation post-launch (adoption metrics → change plan adjustments)
- Anti_Pattern_Detector when adoption metrics dip
- `/status` and `/publish-status` (change health on dashboards)

**Living tracker updates:** audience list, ADKAR scores per audience, change plan tasks, resistance log, adoption metrics + actuals, change-impacting risks, sustained reinforcement plan.

**Anti-pattern this skill prevents:** "Shipped but no one uses it". Technical launch succeeds, adoption never materialises, initiative is judged a failure even though delivery was clean. The most common failure mode in organisational change — and entirely preventable with sustained, per-audience change discipline.
