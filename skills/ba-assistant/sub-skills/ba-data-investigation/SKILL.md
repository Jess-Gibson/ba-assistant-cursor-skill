---
name: ba-data-investigation
description: Pairs with the user to gather, question, cross-validate, and debug data before a BA decision (confidence score, priority, risk rating, solution comparison, baseline, or post-launch actual) gets locked in on judgement alone. Invoked by other BA Assistant skills via hooks. Encodes the BA's own data-investigation methodology, not a generic analytics workflow.
---

# Skill: Data Investigation and Evidence Pairing

## Description

This skill exists so that confidence scores, priorities, risk ratings, and solution comparisons inside BA Assistant get backed by real data wherever real data is available  -  instead of defaulting to a gut-feel High/Medium/Low with nothing behind it. It is the canonical data-pairing skill for BA Assistant: every hook listed below routes here, not to the generic `pm-data-analyst` skill.

The method below is not generic analytics practice  -  it's distilled directly from how [BA name] actually investigates data (see `blueprints/Sample-Compliance-Initiative/outputs/acma-success-metrics-25jun.md` as the reference case): state the question precisely, rank every candidate source with a status and a reason, do a row-level sanity pass before trusting any aggregate, annotate SQL so it's auditable, cross-validate against a second source whenever one exists, and treat any disagreement between sources as the finding rather than noise to average away. Assumptions that can't yet be checked don't block  -  they get logged, tagged, and routed back to the calling skill.

## Standards used

- `references/raid-format.md`  -  the Blocking Questions Log and Data Quality Caveats register both feed `ba-risk-and-tracker` as Open Questions / Assumptions in this format.

## When this skill is invoked (hooks)

| Hook ID | Caller | Trigger | Failure mode |
|---|---|---|---|
| `HK-SOL-BDI-viability` | Solution Shaping | Before recording "confidence in viability" or finalising the options table | Warn  -  proceed qualitatively, tag `evidence: qualitative` |
| `HK-SLI-BDI-sizing` | Feature Slicing & Sequencing | Before finalising business priority / sequencing order | Warn  -  proceed qualitatively, tag `evidence: qualitative` |
| `HK-RT-BDI-evidence` | Risk & Tracker | Before setting a new risk's probability/impact level | Warn  -  proceed qualitatively, tag `evidence: qualitative` |
| `HK-INTK-BDI-baseline` | Intake Reviewer (extends hook 2) | During multi-source context gathering, before setting the Problem Clarity confidence score | Warn  -  cap Problem Clarity at Medium until a source is checked or explicitly declined |
| `HK-CSA-BDI-data` | Current State Assessment | Any quantitative slice needed (volumes, failure rates, latency, error counts) | Warn  -  proceed qualitatively, flag gap in the Current State Report |
| `HK-DISC-BDI-validate` | Discovery and Requirements | An assumption or hypothesis needs data validation | Warn  -  proceed with the assumption flagged (⚠️) |
| `HK-EVAL-BDI-actual` | Solution Evaluation | Pulling actual outcome metrics post-launch | Block  -  no evaluation without actuals (unchanged from prior `pm-data-analyst` hook) |

Every caller shows the standard visible status header before invoking: `> Running: Data Investigation → <one-line intent>`.

## Core method

Apply these in order. Skip steps that genuinely don't apply (e.g. step 6 cross-validation has nothing to check against for a brand-new metric) but say so explicitly rather than silently omitting.

### 0. Validate any stakeholder-supplied anchor number before using it as an input

When a decision or calculation is anchored to a number a stakeholder gave verbally or approximately (e.g. "roughly 70,000 merchants", "about a third of them") rather than a number pulled directly from a validated source, treat that number with the same rigor as a warehouse query result before building on it:

- **Confirm the population/segment it refers to**  -  ask or infer precisely which filter set produces that number (e.g. does "70,000" mean OP-enabled merchants, all AU invoicing merchants, or something else?), and check it against an actual query rather than assuming the most obvious reading.
- **Sanity-check the anchor against the real data**  -  if the validated data returns a meaningfully different number for the most likely interpretation, that mismatch is itself a signal  -  either the stakeholder's mental model is approximate (common, and fine) or the interpretation is wrong (needs resolving before the calculation proceeds).
- **State which interpretation was used and why** in the finding, the same way source selection is documented in step 2 below.

Skipping this step is how an anchor number silently becomes the wrong base population for a whole downstream calculation. *(Added 2 Jul 2026, Sample Initiative mid-initiative retro  -  see D-152/D-162 vs D-164.)*

### 1. State the question precisely

Before touching any data, restate: the decision this data will inform, the metric, the grain (daily / per-invoice / per-merchant / per-cohort), the filters, and the time window. If the calling skill's hook didn't supply enough of this, ask before proceeding  -  a vague question produces a query that answers the wrong thing.

### 2. Identify and rank candidate sources

List every plausible source  -  warehouse tables, Jira, Confluence, logs, product telemetry, support tickets. Tag each:

| Status | Meaning |
|---|---|
| ✅ Validated | Confirmed correct grain/definition for this question; safe to use as primary |
| ⚠️ Research-only | Directionally useful but has a known scope/definition mismatch  -  cite the caveat every time it's used |
| ❌ Not used | Considered and rejected  -  state why (wrong grain, no usable split, deprecated) |

Never silently pick a source without listing the alternatives that were considered and rejected.

### 3. State the design principle before querying

Decide and say out loud: rates/shares vs absolute counts (absolute counts are noisy under seasonal/volume swings  -  prefer shares unless the decision genuinely needs a raw count), and the baseline period (name it, and name what's excluded and why  -  e.g. "exclude the EOFY week, it distorts volume").

### 4. Row-level sanity pass before trusting any aggregate

Before running an aggregate query, check for:

- **Duplicate keys**  -  does `SELECT *` return more rows than `SELECT DISTINCT *` (or more rows than distinct primary key)? If yes, quantify the impact as a percentage, not just "there are some duplicates." Decide a dedup rule (e.g. latest row per key via `QUALIFY ROW_NUMBER() OVER (PARTITION BY <key> ORDER BY <tie-break columns>) = 1`) and state the tie-break reasoning.
- **Null-handling gotchas**  -  columns that are `1` or `NULL` (never literal `0`) need `NVL(...)` guards, not `= 0` filters.
- **Sentinel / junk / future dates**  -  check for placeholder dates (year 9999, far-future ERP sentinels) and legitimately-future rows (scheduled records not yet due) that would corrupt a "current" count if not filtered.
- **Divide-by-zero on sparse slices**  -  guard rate calculations with `NULLIF(denominator, 0)`.

State the impact of each issue found as a percentage of rows affected, and whether it's material enough to change the answer.

### 5. Annotate SQL for audit

Tag every clause so a stakeholder  -  or future-you  -  can read the query without re-deriving intent:

```sql
-- [FILTER] <why this filter exists>
-- [DEDUP] <why this tie-break order>
-- [METRIC Mx] <which tracked metric this column produces>
```

### 6. Cross-validate against a second source whenever one exists

Never present a single-source number as ground truth if a second table or system could confirm or contradict it. If two sources disagree:

1. Quantify the gap (volume difference, rate difference, in percentage points).
2. Trace it to a mechanism  -  different grain, different event semantics (e.g. "UI send intent" vs "confirmed gateway delivery"), different join, different completeness lag. Don't stop at "the numbers don't match."
3. State which source is correct **for this decision** and why  -  the answer can differ by decision even when the underlying data doesn't change.

The disagreement itself is a finding worth recording, not a discrepancy to quietly average away.

### 7. Separate "what the data shows" from "what to do about it"

Every finding gets:
- **What the data shows** (the number, objectively)
- **Implication for the decision** (one sentence  -  what this means for the confidence score / priority / risk rating / solution comparison that triggered this hook)

### 8. Maintain a Blocking Questions Log

When a question can't be answered without input from a data-owning stakeholder (engineering, DNA/analytics, another team), log it:

| ID | Question | Blocking? | Why it matters | Owner | Due |
|---|---|---|---|---|---|

Blocking items route to `ba-risk-and-tracker` as Open Questions with the blocking flag preserved. Non-blocking items still get logged  -  they don't disappear just because they're not on the critical path.

### 9. Maintain a Data Quality Caveats register

A numbered, "must stay visible" list of every data-quality issue found (duplicate keys, ambiguous column definitions, partial/lagging data, known gaps). This is not a one-off footnote  -  it persists across the initiative and gets checked before every subsequent query against the same source. Routes to `ba-risk-and-tracker` as Assumptions/Risks.

### 10. Version findings; log what changed on re-validation

When a query or finding is re-run or re-checked, state: what was re-checked, what (if anything) was found wrong and fixed, and the date. Findings are living, not one-shot  -  they get revisited as more data arrives or as bugs are found.

## Output formats

### Full investigation artefact

Used for initiative-level baseline/monitoring design work (`HK-CSA-BDI-data`, `HK-EVAL-BDI-actual`, or when the user asks for a proper metrics/monitoring document). Structure:

```markdown
# [Initiative]  -  [What we're measuring]

**As at:** [date]  **Status:** [draft / validated  -  re-run date]  **Owner:** [name]

## What we're measuring
[The question, framed as a hypothesis: did X cause Y?]

## Design principle
[Rates vs absolute, baseline period + exclusions, and why]

## Validated data sources
| Source | Schema.Table | Use | Status |
|---|---|---|---|

## Key column definitions
| Column | Definition |
|---|---|

## Data quality caveats (must stay visible)
1. ...

## Metrics
[Tiered if there are several  -  each tier gets a one-line "why these metrics" narrative tied to the hypothesis]

## SQL queries
[Annotated per the SQL annotation convention above]

## Cross-table validation
[Comparison table between sources, why rates/counts differ, recommendation on which to use and why]

## Blocking Questions Log
| # | Question | Blocking? | Why it matters | Owner | Due |
|---|---|---|---|---|---|

## Actions to complete
| # | Action | Owner | Due | Status |
|---|---|---|---|---|
```

### Quick decision-grounding answer

Used for the micro-decision hooks (`HK-SOL-BDI-viability`, `HK-SLI-BDI-sizing`, `HK-RT-BDI-evidence`, `HK-INTK-BDI-baseline`, `HK-DISC-BDI-validate`):

```
## Data check: [decision context]
**Question:** [what we needed to know]
**Sources checked:** [primary] vs [cross-check, if one exists]
**Row-level check:** [dedup / nulls / sentinel dates  -  pass/fail + % impact if any]
**Finding:** [the number / fact]
**Cross-validation:** [agree / disagree  -  if disagree, why]
**Confidence:** [High/Medium/Low  -  sample size, recency, single- vs cross-validated]
**Implication for the decision:** [one sentence]
**Open questions for [data owner]:** [if any  -  blocking or not]
```

Don't run the full artefact structure for a micro-decision  -  it's disproportionate. The quick format still applies the same rigor (steps 1-10 above), just reported concisely.

## The reusable pairing prompt

Every hook above fires this before proceeding, unless the calling skill already has a fresh, cross-validated answer in hand from earlier in the session:

```
I don't have hard data behind this [confidence score / priority / risk rating / solution comparison] yet  -  it's a judgement call right now.

[AskQuestion]
- Pull real numbers now  -  I'll investigate [warehouse / Jira / Confluence / logs] for [specific metric]
- You have the data  -  share it and I'll cross-check and fold it in
- Proceed on judgement  -  log as a qualitative assumption in the tracker
- Not needed here  -  data wouldn't change this call
```

If the user picks "pull real numbers now," run the Core Method above and report back in the quick decision-grounding format. If "you have the data," still apply steps 4 (row-level sanity) and 6 (cross-validate if a second source exists) to whatever's shared  -  don't take a pasted number at face value without at least asking about grain, filters, and dedup.

## Tiering  -  when this is a soft nudge vs escalates

Soft nudge by default: the pairing prompt always includes "proceed on judgement" as a valid, un-penalised option. This is not a hard gate.

It escalates only through the existing `ba-anti-pattern-detector` candidate-to-established mechanism  -  no new mechanism is introduced here. If the *same* rating type (e.g. every Solution Shaping viability score) repeatedly skips data with no stated reason across multiple initiatives, the Anti-Pattern Detector's "Ungrounded rating" trigger promotes from WARN to BLOCK per its standard tiering rules.

## MCP / source map

| Data type | Source | Mechanics owned by |
|---|---|---|
| Warehouse / SQL (warehouse) | `user-snowflake-server` MCP | `pm-data-analyst` → `references/warehouse-and-sql.md` (reused here for query execution mechanics, not duplicated) |
| Jira ticket volumes/history | Jira MCP | `ba-jira-sync` |
| Confluence metrics pages | Confluence MCP | this skill, direct read |
| Production/incident data | log/monitoring tool | `sumo-troubleshooting-workflow` |
| Spreadsheet/CSV/telemetry exports | Local file | `pm-data-analyst` (delegate raw analysis mechanics, apply this skill's cross-validation and dedup discipline on top) |

## Relationship to `pm-data-analyst`

`pm-data-analyst` is a separate, generic skill (not written by the BA) built for standalone PM analytics  -  ad hoc CSV/telemetry analysis requested directly by the user outside a BA Assistant decision point. It remains available and untouched for that use.

Inside BA Assistant, `ba-data-investigation` is the canonical data-pairing skill for all 7 hooks listed above. Where the underlying mechanics overlap (running SQL, reading a CSV), this skill delegates the mechanics to `pm-data-analyst`'s `references/warehouse-and-sql.md` rather than duplicating it  -  but the investigation discipline (cross-validation, dedup forensics, annotation, blocking-questions log, caveats register) is owned here, not there.

## Challenge Rules

- **Never present a single-source number as settled fact** if a second source could plausibly confirm or contradict it  -  check, or say explicitly that no second source exists.
- **Never report a discrepancy without attempting to explain the mechanism.** "The numbers don't match" is not a finding; "PA counts UI send intent, the mart counts confirmed gateway delivery  -  that's the 3.3x gap" is a finding.
- **Never let "the data doesn't exist" default to silence.** State it clearly so the calling skill can log a qualitative assumption instead of stalling.
- **Never quantify a data-quality issue qualitatively when a percentage is available.** "Some duplicates exist" is weaker and less actionable than "0.56% of rows are duplicates."
- **Never bury a blocking question inside prose.** It goes in the Blocking Questions Log with an owner and a due date, every time.
