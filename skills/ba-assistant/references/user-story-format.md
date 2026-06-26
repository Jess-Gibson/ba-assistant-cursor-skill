# User Story Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/user-story-format.md`
**Owner:** ba-story-writing (workflow), this standard (format)
**Last reviewed:** 2026-05-30

This file is the canonical source for ticket structure. Any sub-skill producing a Jira ticket, a story draft, a spike ticket, a bug, or an enabler MUST conform to this standard. Anti-Pattern Detector flags non-conformant output.

For Jira-specific formatting (panels, custom fields, emoji conventions, FCM template structure), see also `references/jira-ticket-format.md` (the standard for how a story is *rendered in Jira specifically*, vs how its content is structured here).

---

## 1. Ticket types

Five types, distinct purposes, different structures.

| Type | Purpose | Lives where in workflow |
|---|---|---|
| **Story** | Deliver user-facing or system-observable value | Delivery |
| **Spike** | Investigate to reduce uncertainty | Solution shaping or delivery |
| **Bug** | Fix unintended behaviour in production or pre-prod | Verification or post-launch |
| **Enabler** | Technical work that doesn't deliver user-observable value but unblocks future work | Delivery |
| **Chore** | Routine maintenance, no decision content (rare; prefer not to create chores from BA work) | Delivery |

Type drives structure. Don't write spikes shaped like stories or stories shaped like spikes.

---

## 2. Story structure

### Title

Format: `As a [persona], I want [capability], so that [outcome]`

Or the more concise form when persona is unambiguous: `[Capability] so [outcome]`

**Good:** "As a merchant in onboarding, I want to upload my certificate of incorporation, so that KYB verification can complete."
**Bad:** "Upload certificate" (no outcome, no persona, no capability frame)

### Required sections

```markdown
## Why
[1-2 sentences. Why does this matter? What outcome are we enabling?]

## Acceptance criteria
Given [precondition]
When [action]
Then [observable outcome]

And [additional behaviour, if needed]

## Negative case
[What should NOT happen. What's explicitly out of scope or excluded.]

## Scope
[Initiative / feature / cohort / slice this story belongs to. Must match a scope in status-data.json.]

## Linked requirements
[List of BR-XXX or similar requirement IDs this story implements. Must trace to at least one.]

## Linked slice
[SL-XX identifier from feature slicing. Required for any story past Phase 3.]

## DoR checklist
[Definition of Ready criteria â€” see Section 6]

## Definition of Done
[Specific to this story. What does "done" actually mean â€” tested, deployed, monitored, documented?]
```

### Optional sections

- `## Technical notes` â€” for technical context the dev team needs but isn't business-facing
- `## Mockups / visuals` â€” link to or embed visuals
- `## Out of scope` â€” explicit exclusions (different from Negative case; out-of-scope is "we considered this and won't do it here")
- `## Dependencies` â€” other tickets that must complete first
- `## Risks` â€” story-specific risks (not initiative-level)

### INVEST conformance

Every story must pass INVEST. If it can't, restructure or split.

| Letter | Check |
|---|---|
| **I**ndependent | Can this story ship without strict ordering against another story in the same scope? If no, the dependency must be explicit. |
| **N**egotiable | Are acceptance criteria descriptive enough to deliver but not prescriptive enough to lock implementation choices? |
| **V**aluable | Does the story produce observable outcome (user-facing or system-observable)? If only technical change, consider Enabler instead. |
| **E**stimable | Does the team have enough context to estimate? If "we'll know after the spike", create a Spike first. |
| **S**mall | Will this fit in one sprint? If not, split. |
| **T**estable | Are acceptance criteria written so success is binary? "Performant" fails; "responds in <500ms at p95 under 100 RPS" passes. |

---

## 3. Spike structure

Spikes investigate. They produce an **outcome**, not a feature.

### Title

Format: `Spike: investigate [question or uncertainty]`

**Good:** "Spike: investigate whether vendor X's ID verification API can meet our 95% confidence threshold on our test dataset"
**Bad:** "Spike: ID verification" (no question, no outcome shape)

### Required sections

```markdown
## Question being answered
[The specific question this spike investigates. One sentence. The spike either answers it or returns "still uncertain, here's why".]

## Why this is a spike, not a story
[What uncertainty exists that prevents writing a normal story? Be specific.]

## Time-box
[Hours or days. Spikes have a hard time-box. If the investigation isn't conclusive by the end, the spike closes with "inconclusive" status and a follow-up plan.]

## Method
[How will the question be investigated? Code prototype, data analysis, vendor call, document review, etc.]

## Acceptance for closure
- [ ] The question is answered with evidence, OR
- [ ] The time-box has been spent and the spike is marked inconclusive with a clear next step

## Outcome capture
[At closure, this section gets filled in:
- Answer: [What did we learn?]
- Evidence: [What does the answer rest on?]
- Linked ADR: [If the answer drives a decision worth recording]
- Follow-up: [Stories, requirements, risks that emerged]]

## Scope
[Initiative / feature / cohort this spike serves]
```

### Spike anti-patterns

- Spike with no time-box â†’ reject; spikes are bounded by definition
- Spike with no specific question â†’ reject; "investigate the API" isn't a question
- Spike that closes without filling in the Outcome capture section â†’ reject; the knowledge dies otherwise
- Spike open >2 sprints â†’ Anti-Pattern Detector triggers stalled spike review

---

## 4. Bug structure

### Title

Format: `Bug: [system] [unintended behaviour] [trigger condition]`

**Good:** "Bug: KYC verification returns 500 when merchant uploads PDF certificate with >5MB file size"
**Bad:** "Bug: upload broken" (no trigger, no behaviour, no system)

### Required sections

```markdown
## Observed behaviour
[What is happening that shouldn't be]

## Expected behaviour
[What should happen instead]

## Reproduction steps
1. ...
2. ...
3. ...

## Environment
[Where was this observed? Prod, staging, specific cohort, specific browser?]

## Severity
[critical | high | medium | low â€” see Severity rubric in your project-specific jira-templates skill]

## Impact
[Who is affected and how. Number of customers, business impact, compliance impact.]

## Root cause hypothesis
[If known. If not, leave blank â€” engineering will investigate.]

## Linked story / requirement
[What was the bug masking? Which story or requirement does the bug violate?]

## Scope
[Which scope owns the fix?]
```

---

## 5. Enabler structure

Enablers are technical work that doesn't deliver user-observable value but unblocks future work. They need to be defended differently from stories.

### Title

Format: `Enabler: [technical change] so [downstream capability]`

**Good:** "Enabler: migrate ID verification calls to dedicated SQS queue so we can independently scale verification throughput"
**Bad:** "Refactor the verification module" (no downstream rationale)

### Required sections

```markdown
## What changes
[Specific technical change]

## Why this matters
[What downstream capability this enables. Be specific â€” vague "improves maintainability" claims fail this section.]

## Without this enabler, what breaks or doesn't happen
[The case for prioritising. If nothing concrete breaks, the enabler is probably not justified now.]

## Acceptance criteria
[Observable system change â€” even if not user-facing. "X service publishes to queue Y" is observable. "Code is cleaner" is not.]

## Risk of doing this
[Technical risk of the change itself]

## Risk of NOT doing this
[What does the future cost look like if this is deferred]

## Scope
[Which scope this serves]
```

---

## 6. DoR checklist (applies to stories and enablers)

```markdown
## Definition of Ready
- [ ] Acceptance criteria are specific and testable
- [ ] Negative case is documented (what should NOT happen)
- [ ] Linked to at least one requirement (BR-XXX)
- [ ] Linked to a slice (SL-XX)
- [ ] No outstanding dependencies blocking start
- [ ] Estimable by the team (or accompanied by a sized Spike)
- [ ] Scope is clear (which feature / cohort / slice)
- [ ] Edge cases identified (at least 2)
- [ ] Compliance / security implications assessed (or marked N/A with reason)
```

A story that passes DoR on first attempt is a `pass` in `status-data.json â†’ dorChecks`. Partial passes (1-2 missing) are `partial`. Multiple missing items make it `fail`.

---

## 7. Acceptance criteria patterns

### Given / When / Then

Default form for stories. Pre-condition / action / observable outcome.

```
Given the merchant has submitted all required documents
When the AI ID verification returns a confidence score below 95%
Then the application routes to manual review with the score and rationale visible to the reviewer
```

### Rule-based (table form) for criteria with many variants

When acceptance criteria have multiple input Ã— outcome combinations, use a table:

| Risk score | Doc verification | Sanctions check | Expected route |
|---|---|---|---|
| <30 | Pass | Pass | Auto-approve |
| <30 | Pass | Block | Compliance review |
| 30-70 | Any | Any | Manual review |
| >70 | Any | Any | Manual review (high-risk flag) |

### Negative case (mandatory)

Every story has a Negative case section explicitly stating what should NOT happen. This catches the failure mode where stories pass acceptance with happy-path-only checks and produce regressions.

**Good negative case:**
> The application MUST NOT auto-approve when sanctions check returns a positive match, regardless of risk score.

**Bad negative case:**
> The application should work correctly.

---

## 8. Output anti-patterns

| Watching | Trigger | Anti-pattern |
|---|---|---|
| Any skill producing a ticket | Story has no Negative case section | Happy-path only â€” missing negative case |
| Any skill producing a ticket | Story lacks linked requirement | Untraceable story |
| Any skill producing a ticket | Story past Phase 3 lacks linked slice | Slice not assigned |
| Any skill producing a ticket | Acceptance criteria contain vague terms ("performant", "user-friendly", "robust") without measurable definition | Non-testable AC |
| Any skill producing a ticket | Spike has no time-box | Unbounded investigation |
| Any skill producing a ticket | Spike outcome capture is empty on closure | Spike knowledge loss |
| Any skill producing a ticket | Enabler "Why this matters" is vague maintenance language | Unjustified enabler |
| Any skill producing a ticket | Bug has no reproduction steps | Untriageable bug |

---

## 9. Examples

### Example: Good story

```markdown
**Title:** As a merchant in onboarding, I want to see why my verification failed, so that I know whether to provide more info or seek support.

## Why
Merchants currently get a generic "could not verify" message. Support tickets for this state are 12% of post-onboarding contact volume. Clear reason codes (sanitised for fraud-prevention reasons) reduce that load and improve merchant experience.

## Acceptance criteria
Given a merchant application has been declined at the verification stage
When the decline notification is sent
Then the merchant sees one of the approved reason codes from the Reason Code Register (see SO-04)
And the message includes the support contact channel

| Decline reason | Customer-facing message |
|---|---|
| Documents below quality threshold | "We couldn't read your documents clearly. Please resubmit." |
| Identity mismatch | "Some details didn't match. Please contact support to review." |
| Sanctions or compliance block | "We're unable to proceed at this time. Please contact support." |

## Negative case
The application MUST NOT reveal which specific check failed (fraud-coaching risk). The reason code is intentionally generalised.

## Scope
feature_cohort_a (high-risk merchants)

## Linked requirements
BR-013, COMP-26

## Linked slice
SL-07

## Definition of Done
- Decline messaging shows approved reason code
- Reason codes match Reason Code Register SO-04 (legal-approved)
- A/B test confirms reduction in "what does this mean" support tickets â‰¥30% over 4 weeks
```

### Example: Good spike

```markdown
**Title:** Spike: investigate whether vendor X's ID verification can meet our 95% confidence threshold against our test dataset of 500 merchant samples

## Question being answered
Does vendor X's published 97% accuracy hold on OUR data, or does it degrade on the document mix and edge cases specific to our merchant population?

## Why this is a spike, not a story
We can't write integration stories until we know whether vendor X actually meets the threshold. If it doesn't, vendor Y is the fallback and integration architecture differs.

## Time-box
3 days (24 hours of focused investigation work)

## Method
1. Build sandbox integration against vendor X's test endpoint
2. Run our anonymised 500-sample dataset through it
3. Compare confidence scores against ground truth from our manual review historical data
4. Report aggregate accuracy and per-document-type breakdown

## Acceptance for closure
- [ ] Confidence score distribution documented for our dataset
- [ ] Pass / fail against 95% threshold confirmed with evidence
- [ ] OR time-box exhausted with clear "still uncertain because X" note

## Outcome capture
[To be filled at closure]

## Scope
feature_cohort_a
```

---

## 10. Versioning

This standard is v1.0 (2026-05-30). Significant changes (new ticket type, new mandatory section, INVEST refinement) increment the version. Sub-skills referencing this file should not hard-code section names; if a section gets renamed, the reference still resolves.

