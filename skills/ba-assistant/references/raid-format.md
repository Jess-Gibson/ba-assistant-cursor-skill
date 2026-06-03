# RAID Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/raid-format.md`
**Owner:** ba-risk-and-tracker (workflow), this standard (format)
**Last reviewed:** 2026-05-30

This file is the canonical source for RAID structure, decision log structure, open question structure, and assumption tracking. Any sub-skill writing to the initiative tracker, status-data.json, or any RAID-derived output MUST conform to this standard.

RAID applies to: Risks, Assumptions, Issues, Dependencies. Decisions and Open Questions are tracked alongside but are distinct.

---

## 1. Where RAID lives

Two locations, distinct ownership:

| Location | What lives there | Canonical for |
|---|---|---|
| `initiative-tracker.md` | Narrative entries with reasoning, evidence, history | Source of truth for RAID content |
| `status-data.json → raid` | Structured derived view | Source of truth for IDs, dates, owners, statuses |

When a narrative entry in the tracker is updated, the structured view in `status-data.json` re-derives on next Project Canvas regeneration. The tracker is the human-edited source; the JSON is the machine view.

---

## 2. Risk format

Risks are things that *might* happen and *would matter*.

### In `initiative-tracker.md`

```markdown
### R-12 · Vendor ID verification capacity may be insufficient at launch
**Likelihood:** Medium
**Impact:** High
**Owner:** [Tech Lead name]
**Status:** Open
**Source:** Requirements Interrogator (8 May)
**Created:** 2026-05-08
**Last reviewed:** 2026-05-25

**Description:**
Vendor X's published capacity is 2000 verifications per minute. Our projected launch volume is 800 per minute steady-state, with spikes to 3000+ during onboarding campaigns. Capacity may be a hard ceiling during marketing pushes.

**Mitigation:**
Pre-negotiated capacity uplift clause in contract; load test against 3x projected volume before go-live; build fallback queue with degraded UX rather than failed onboarding.

**Trigger to escalate:**
If vendor responds with "no uplift available" or load test shows degradation at <2x volume.

**History:**
- 2026-05-08: Identified during requirements interrogation
- 2026-05-15: Mitigation strategy confirmed with tech lead
- 2026-05-25: Reviewed; status unchanged
```

### In `status-data.json`

```json
{
  "id": "R-12",
  "title": "Vendor ID verification capacity may be insufficient at launch",
  "likelihood": "medium",
  "impact": "high",
  "owner": "[Tech Lead]",
  "status": "open",
  "source": "interrogator",
  "createdAt": "2026-05-08",
  "lastReviewedAt": "2026-05-25",
  "mitigation": "Pre-negotiated capacity uplift; load test 3x volume; fallback queue",
  "linkedTickets": []
}
```

### Required fields

| Field | Type | Allowed values |
|---|---|---|
| `id` | string | `R-NN` pattern |
| `title` | string | One sentence, ends with "may", "could", or describes the potential negative outcome |
| `likelihood` | enum | `low` | `medium` | `high` |
| `impact` | enum | `low` | `medium` | `high` |
| `owner` | string | Named individual, not "TBD" |
| `status` | enum | `open` | `mitigated` | `realised` | `closed` |
| `source` | enum | `interrogator` | `pre-mortem` | `incident` | `manual` | `external` |
| `createdAt` | date | ISO format |
| `mitigation` | string | Required if status is `open` or `mitigated`. If empty, AntiPattern Detector triggers. |

### Risk status transitions

```
open → mitigated (mitigation is in place; risk is reduced but not eliminated)
open → realised (the risk has happened; convert to issue or incident)
open → closed (the conditions for the risk no longer apply)
mitigated → realised (mitigation insufficient)
mitigated → closed
```

### Anti-patterns

- Risk with no `owner` or `owner: "TBD"`
- Risk with `status: open` and no mitigation
- Risk where likelihood × impact would suggest "high" but `status` has been "open" >30 days with no progress
- Risk that's actually an issue (it has already happened) — should be in the Issues section

---

## 3. Assumption format

Assumptions are things we're *taking as true* without explicit verification.

### In `initiative-tracker.md`

```markdown
### A-04 · Vendor X's response times will hold at projected launch volume
**Confidence:** Medium
**Owner:** [Tech Lead]
**Status:** Untested
**Source:** Solution shaping (3 May)
**Validation plan:** Load test in pre-prod with anonymised production replay (target 1 June)
**Created:** 2026-05-03

**Description:**
We're assuming vendor X's <500ms p95 response time holds at our projected launch volume of 800 verifications per minute. Their published benchmarks are at 500/min; we haven't independently verified at our scale.

**If this assumption is wrong:**
Verification latency could push merchant onboarding completion times >5 min, which is the documented threshold for completion drop-off acceleration. Likely revenue impact.

**History:**
- 2026-05-03: Identified during solution shaping
- 2026-05-20: Validation plan agreed
```

### Required fields

| Field | Type | Allowed values |
|---|---|---|
| `id` | string | `A-NN` |
| `title` | string | Stated AS the assumption ("X will...") not as a question |
| `confidence` | enum | `low` | `medium` | `high` |
| `owner` | string | Named individual |
| `status` | enum | `untested` | `validated` | `invalidated` | `superseded` |
| `validationPlan` | string | Required if status is `untested`. How and when will we test? |
| `ifWrong` | string | What's the impact if this assumption fails? |

### Assumption expiry rule

Assumptions with `status: untested` and `createdAt` older than 30 days surface as anti-patterns. Old untested assumptions become silent foundations of decisions. Either validate or explicitly accept the risk.

---

## 4. Issue format

Issues are things that *are happening now* and matter.

```markdown
### I-03 · Manual review queue is at 3-day age, breaching 24-hour SLA
**Severity:** High
**Owner:** [Compliance Ops Lead]
**Status:** Active
**Source:** Operations metric review (24 May)
**Started:** 2026-05-22

**Description:**
Manual review queue currently has 47 items aged >24 hours, with the oldest at 3 days. SLA breach affecting customer-promised onboarding times.

**Action in progress:**
Two reviewers temporarily reassigned from BAU; root cause analysis underway to determine whether this is a volume spike or a quality regression in AI risk scoring (sending too many cases to manual).

**Resolution criteria:**
- Queue back to <24-hour age
- Root cause identified and remediation plan in place
```

### Required fields

| Field | Type | Allowed values |
|---|---|---|
| `id` | string | `I-NN` |
| `title` | string | States what IS happening, not what might |
| `severity` | enum | `low` | `medium` | `high` | `critical` |
| `owner` | string | Named individual |
| `status` | enum | `active` | `resolved` | `accepted` |
| `actionInProgress` | string | What's being done now |
| `resolutionCriteria` | string | How we'll know it's resolved |

---

## 5. Dependency format

Dependencies are things outside your direct control that you need.

```markdown
### DEP-05 · Legal sign-off on customer-facing decline messaging
**Type:** Internal
**Owner (us):** [BA Name]
**Owner (them):** [Legal lead]
**Status:** Pending
**Target date:** 6 June 2026
**Last contact:** 25 May 2026

**Description:**
Customer-facing decline messages need legal review for fraud-coaching risk and clarity. Three message variants need approval before merchant-facing implementation can ship.

**Critical path?** Yes — blocks Phase 5 delivery for Cohort A.

**Escalation path:**
If not received by 3 June, escalate via PM to legal team lead.

**History:**
- 2026-05-15: Initial request sent with v1 message variants
- 2026-05-20: Feedback received; v2 sent
- 2026-05-25: Awaiting v2 approval
```

### Required fields

| Field | Type | Allowed values |
|---|---|---|
| `id` | string | `DEP-NN` |
| `title` | string | What we need, not who from |
| `type` | enum | `internal` | `external` | `regulatory` | `vendor` |
| `ownerUs` | string | Who owns chasing |
| `ownerThem` | string | Who can provide it |
| `status` | enum | `pending` | `received` | `at-risk` | `blocked` |
| `targetDate` | date | When we need it |
| `criticalPath` | boolean | Whether this dependency blocks downstream work |
| `lastContact` | date | Auto-flag if >7 days without contact for at-risk dependencies |

### Dependency staleness rule

Dependencies with `status: pending` and `lastContact` >7 working days trigger an anti-pattern: "stale dependency contact." Out of sight, out of mind is how external owners drop your request.

---

## 6. Decision format

Decisions are *made*, not pending. Decisions have rationale and alternatives. Decisions can be reversed but the original is preserved with a `supersededBy` link.

```markdown
### D-04 · Use vendor X for ID verification
**Date decided:** 12 May 2026
**Owner:** [Tech Lead] with [PM] and [BA] input
**Status:** Confirmed
**Scope:** feature_cohort_a, feature_cohort_b
**Linked ADR:** ADR-04

**Rationale:**
Vendor X selected over Vendor Y based on:
- 40% cost difference at projected volume
- 2-week shorter integration time
- Regulatory coverage matches our jurisdictions

**Alternatives considered:**
1. Vendor Y — higher cost, marginally better accuracy on edge cases
2. Build in-house — rejected due to 6-month timeline vs 6-week vendor integration

**Trade-offs accepted:**
- Vendor X has 1.5 percentage points lower published accuracy on identity documents from emerging markets
- Mitigation: route low-confidence cases to manual review (this was always part of the design)

**Reversal conditions:**
If vendor X consistently misses SLA in pre-prod load testing, decision reopens for review.
```

### Required fields

| Field | Type | Allowed values |
|---|---|---|
| `id` | string | `D-NN` |
| `title` | string | What was decided, in active voice |
| `date` | date | When decided |
| `owner` | string | Decision-maker (not just facilitator) |
| `status` | enum | `tentative` | `confirmed` | `reversed` |
| `rationale` | string | Required; specific |
| `alternativesConsidered` | array | At least 1; "no alternative was considered" is itself a flag |
| `scope` | array | Which scopes does this apply to |
| `linkedADR` | string | If a formal ADR exists |
| `supersededBy` | string | If reversed, points to the new decision ID |

### Decision anti-patterns

- Decision with no rationale → reject
- Decision with no alternatives considered → flag for review
- Decision marked `confirmed` that's actually tentative (no sponsor or PM acknowledgement)
- Decisions accumulating in tracker but missing from `status-data.json → decisions` → Project Canvas regeneration not running

---

## 7. Open question format

Open questions are *known unknowns* that need answers.

```markdown
### OQ-08 · Should rejected applications retain a record we'd re-show on re-application?
**Owner to answer:** [PM]
**Asked by:** [BA Name]
**Date raised:** 18 May 2026
**Target answer date:** 2 June 2026
**Status:** Open
**Blocks:** SL-07 (decline messaging slice)

**Context:**
If a merchant is rejected and re-applies later, do we surface "you previously applied" in any form? Implications for fraud (re-applying with different details), customer experience (frustration of starting over), data retention (compliance constraints).

**Options surfaced:**
- A. Show "previously applied" message
- B. Treat each application as net new
- C. Show "previously applied" only if same legal entity / same beneficial owners

**Decision tracking:**
This will become a decision (D-XX) once answered. Until then, blocks the decline messaging design.
```

### Required fields

| Field | Type |
|---|---|
| `id` | `OQ-NN` |
| `question` | The question stated clearly |
| `ownerToAnswer` | Named individual |
| `askedBy` | Who raised it |
| `dateRaised` | ISO date |
| `targetAnswerDate` | ISO date |
| `status` | `open` | `answered` | `deferred` | `abandoned` |
| `blocks` | What can't proceed until answered |

### Open question ageing rule

Open questions in `status: open` for >14 days without movement (no `lastContact`-equivalent activity) trigger an anti-pattern. Ageing OQs become silent foundations of subsequent decisions.

---

## 8. Cross-RAID rules

**ID uniqueness:** R, A, I, DEP, D, OQ are independent number-spaces. R-12 and A-12 can coexist. Within a type, numbers don't reuse.

**Conversion paths:**
- Risk that realises → becomes an Issue (note "Converted from R-XX" in the new Issue)
- Open question that's answered → becomes a Decision (link with "Resolved OQ-XX")
- Assumption that's invalidated → consider whether it converts to a Risk

**Sign-off interaction:**
Decisions that require formal approval link to a `SO-XX` entry in `status-data.json → signOffs`. Decision status stays `tentative` until the sign-off is `approved`.

**State Validator interaction:**
Drift between RAID in `initiative-tracker.md` and `status-data.json → raid` is caught by the State Validator. The tracker wins on conflict (per Wave 5 ownership rules).

---

## 9. Output anti-patterns (Anti-Pattern Detector triggers)

| Watching | Trigger | Anti-pattern |
|---|---|---|
| Any RAID write | Required field missing | RAID entry incomplete |
| Any RAID write | Status transition outside valid set | Invalid status transition |
| Any risk | `status: open` for >30 days, no `lastReviewedAt` update | Stale risk |
| Any assumption | `status: untested`, age >30 days | Ageing untested assumption |
| Any dependency | `status: pending` for >7 working days without `lastContact` update | Stale dependency contact |
| Any open question | `status: open` for >14 days, no movement | Ageing open question |
| Any decision | Marked `confirmed` without sponsor or PM acknowledgement in same period | Decision confirmed without alignment |
| Any RAID entry | Owner is "TBD" or unnamed | Ownerless RAID |
| Decision log | Decisions accumulating in tracker but missing from `status-data.json` | Canvas regeneration lagging |

---

## 10. Versioning

v1.0 (2026-05-30). Changes to required fields, new RAID type, or new status enum values require version bump.
