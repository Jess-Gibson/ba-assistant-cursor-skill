---
name: ba-solution-evaluation
description: Post-launch BA work — measure actual vs expected outcomes, validate value delivered, identify performance gaps, recommend continue/adjust/sunset decisions. Closes the BABOK loop after delivery.
---

# Skill: Solution Evaluation

## Description

The Solution Evaluation skill performs the **post-launch** BA work that closes the loop on an initiative. It compares actual outcomes against the success metrics agreed at intake, validates whether the original problem was actually solved, identifies causes when performance falls short, and recommends a clear next action: **continue as-is**, **adjust**, or **sunset**.

This is an entire BABOK v3 knowledge area (Solution Evaluation) and the most commonly skipped phase of BA work in practice. Delivery teams move on; the BA closes out the Jira board; the question of whether the thing actually worked goes unanswered. This skill makes the evaluation explicit, evidence-based, and timely.

Solution Evaluation is **not** a retrospective. Retrospective is about *how we worked*; Solution Evaluation is about *whether what we built delivered the value we said it would*.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (evaluation report, post-launch metrics, charts, gap analysis, recommendation doc). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant\SKILL.md → Co-thinking and artefact production protocol` — surface planned artefacts upfront and ask the user to select.

## Mandatory hooks

Solution Evaluation MUST invoke the following:

| Hook | When | Why |
|---|---|---|
| **pm-data-analyst** | Always | Pull actual metrics (Snowflake, Sumo, Segment, FullStory, support ticket volume) for the success metrics defined at intake. No evaluation without evidence. |
| **Visual_Storytelling** | Always | Produce outcome vs target charts, trend lines, adoption curves. Numbers in a table land less than a chart with target lines. |
| **Requirements_Interrogator** (Rethink mode) | When actual ≠ expected | If a requirement isn't delivering the expected outcome, interrogate why before recommending changes. |
| **Risk_and_Tracker** | Always | Log any post-launch issues, regressions, or unmet outcomes as items in the tracker. |
| **Retrospective_and_Learning** | Always | Feed learnings into the BA Assistant's `learnings.md` so future initiatives benefit. |
| **Anti_Pattern_Detector** | Always | Flag patterns observed post-launch (e.g. solution underused → audience misidentified at intake). |

## When to invoke

- **Default cadence:** 2 weeks, 6 weeks, and 12 weeks post-launch per feature/cohort/slice. Adjust based on adoption curve expectations.
- **At pre-defined evaluation milestones** captured at intake (e.g. "review after 100 merchants onboarded").
- **When a stakeholder questions value** ("is this actually working?").
- **Before deciding to fund related/follow-on work** (don't double down before evaluating the first bet).
- **When metrics suggest a problem** (drop in adoption, spike in support tickets, error rates).

## Tasks

1. **Pull the success metrics agreed at intake** — Read the intake summary and Phase 0 confidence scores. What did we say success looks like? If success metrics are vague or missing, flag immediately and recommend going back to revise them (this is itself a finding).

2. **Pull actual data** — Hand off to `pm-data-analyst` with:
   - The success metric definitions
   - The time window since launch
   - The data sources (Snowflake tables, Sumo queries, Segment events, support ticket categories)
   - The cohort/feature/slice scope being evaluated
   Capture the actuals in a comparison table.

3. **Gap analysis** — For each success metric, document: target, actual, gap (absolute and %), direction (better/worse than target), confidence in the data.

4. **Identify causes of gaps** — Where actual ≠ expected, explore why. Possible causes:
   - Solution doesn't do what we thought it would (build problem)
   - Solution works but adoption is low (change/enablement problem)
   - Solution works and is adopted but doesn't move the metric (problem-statement-was-wrong problem)
   - External factor invalidated the assumption (market shift, regulatory change)
   - Measurement is wrong (instrumentation issue, wrong baseline)
   Hand off to `Requirements_Interrogator` (Rethink mode) for any requirement-rooted gaps.

5. **Surface unintended consequences** — Things that got better unexpectedly, things that got worse unexpectedly. Both matter. Examples: a feature improved customer verification pass rate but increased support tickets about confusing error messages.

6. **Validate the original problem** — Is the problem we set out to solve actually solved? Use stakeholder feedback + data + journey observation. A solution can hit its metrics and still not solve the problem (e.g. customer verification pass rate up but customers still drop off at the same point).

7. **Recommend a decision** — Produce a clear continue/adjust/sunset recommendation:
   - **Continue** — outcomes meet targets, no adjustments needed, sustain monitoring
   - **Adjust** — outcomes partially met, specific changes needed (list them)
   - **Sunset** — outcomes not met, problem not solved, costs > value, retire the solution
   Each recommendation must carry rationale, supporting evidence, and an owner for the next action.

8. **Update the living tracker** — Log evaluation outcomes, recommended actions, decisions made, and any new risks surfaced. Cross-link to the original intake decisions.

9. **Update Anti-Pattern Detector watchlist** — If the evaluation reveals a new pattern (e.g. "features without explicit measurement plan at intake consistently fail evaluation"), feed it into the detector's watchlist for future initiatives.

10. **Publish evaluation report** — Produce a Confluence-ready Solution Evaluation Report (see Output Guidelines). Publish to the initiative hub page so stakeholders can see what was delivered and how it performed.

## Typical Questions to Ask

- What were the success metrics we agreed at intake? Are they still the right ones?
- What's the actual data showing? Where are the gaps?
- For each gap: is the solution doing what we built it to do, or is something else going on?
- Has adoption matched expectations? If not, why?
- Have we measured this consistently — same baseline, same time window, same cohort?
- Did anything happen externally (market, regulatory, internal priorities) that changes how we interpret the data?
- Are there unintended consequences (positive or negative) that we didn't predict?
- Is the original problem actually solved? Would the original sponsor agree?
- What would it take to close the gap? Is it worth doing?
- Should we continue, adjust, or sunset?
- What did we learn that should change how we do future initiatives?

## Output Guidelines

### Solution Evaluation Report structure

1. **Header** — Initiative name, scope evaluated (feature/cohort/slice), evaluation window (launch date → today), evaluator, sponsor
2. **TL;DR** — 3-5 sentences: what we built, what we hoped for, what we got, what we recommend
3. **Success metrics — actual vs target** (table)
   | Metric | Target | Actual | Gap | Direction | Data source | Confidence |
4. **Outcome charts** (via Visual_Storytelling) — trend lines with target lines, adoption curves, cohort comparisons
5. **Gap analysis** — per metric, why the gap exists (build / adoption / problem-statement / external / measurement)
6. **Unintended consequences** — positive and negative side effects observed
7. **Problem validation** — is the original problem solved? Yes/Partially/No, with evidence
8. **Recommendation** — Continue / Adjust / Sunset, with rationale and proposed actions
9. **Decisions log** — what was decided, by whom, by when (table format per ba-profile.mdc)
10. **New risks / open questions** — anything this evaluation surfaced that needs follow-up
11. **Learnings for future initiatives** — patterns to feed into Anti-Pattern Detector and `learnings.md`

### Decision recommendation table

| Recommendation | Rationale | Proposed actions | Owner | Decision needed by |
|---|---|---|---|---|

### Living tracker updates

- Move success metrics from "target" to "outcome (actual)" with confidence rating
- Log evaluation decisions in the decisions table (ID, Decision, Owner, Date, Status)
- Add any unmet outcomes as 🧨 risks
- Add any newly discovered unknowns as ❓
- Surface unintended consequences as items requiring stakeholder discussion

## Challenge Rules

- **Don't accept "we'll measure later"** — if success metrics aren't measurable, that's a finding. Recommend going back to define them, but don't fake the evaluation.
- **Don't conflate output with outcome** — "we shipped it" is not an outcome. Use leading and lagging indicators.
- **Don't smooth bad news** — if the solution isn't working, say so plainly. Recommendation must be evidence-based, not politically-easy.
- **Don't skip the problem-validation step** — a solution can hit all its proxy metrics and still fail to solve the original problem.
- **Challenge stale baselines** — if the baseline used at intake is no longer representative (seasonality, external change), say so and recalibrate.
- **Hold the sponsor accountable** — the sponsor signed off the success metrics at intake. They should see the evaluation, not just the BA.
- **Don't let "continue" be the default** — sunsetting things that didn't work is a valid and underused outcome. If outcomes don't justify continued investment, recommend sunset.
- **Cross-reference unintended consequences** — sometimes the "real" value of a solution is in a side effect; sometimes the "real" cost is too.

## Integration with BA Assistant

**Mode (post-Wave 3): M7 — Solution Evaluation.** Per-feature, per-cohort, per-slice scope. Runs post-launch on the cadence above.

**Pre-Wave 3 (current sequential model):** Treat as a post-Phase 6 mini-phase. Invoke after Playback & Enablement completes for a feature.

**Hooks called by this skill:** pm-data-analyst, Visual_Storytelling, Requirements_Interrogator (Rethink), Risk_and_Tracker, Retrospective_and_Learning, Anti_Pattern_Detector.

**Hooks calling this skill:**
- Orchestrator at the post-launch cadence (2/6/12 weeks)
- `/status` when evaluating a feature already past delivery
- Sponsor Engagement when sponsor requests value review
- Change Strategy as part of adoption tracking

**Living tracker updates:** evaluation outcomes, decisions, recommendations, new risks, validated problems.

**Anti-pattern this skill prevents:** "Ship-and-forget". Initiative completes, board archived, nobody knows if it worked. Most expensive untracked failure mode in delivery — funds the next bad bet.
