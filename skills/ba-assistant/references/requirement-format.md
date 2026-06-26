# Requirement Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/requirement-format.md`
**Owner:** ba-discovery-and-requirements (workflow), this standard (format)
**Last reviewed:** 2026-05-30

This file is the canonical source for requirement structure, requirements register schema, MoSCoW matrix layout, and JTBD format. Any sub-skill writing requirements MUST conform to this standard. Pulls from `references/raid-format.md` for any assumptions or risks raised during discovery.

---

## 1. Where requirements live

| Location | What | Canonical for |
|---|---|---|
| `<initiative>/requirements/register.md` | Narrative requirement entries | Requirement content, evidence, history |
| `<initiative>/requirements/moscow-matrix.md` | Per-scope MoSCoW classification | Prioritisation per scope |
| `status-data.json â†’ stories[].linkedRequirements` | Story-to-requirement traceability | Forward linkage |
| Confluence requirements page | Published view for stakeholders | Sharing only â€” derived |

The register.md file is the source of truth. The MoSCoW matrix and Confluence views are derived.

---

## 2. Requirement types

| Type | Prefix | When |
|---|---|---|
| **Business requirement** | `BR-` | A business outcome or capability the initiative must deliver |
| **Functional requirement** | `FR-` | Specific system behaviour |
| **Non-functional requirement** | `NFR-` | Performance, security, compliance, accessibility, reliability |
| **Compliance requirement** | `COMP-` | Driven by regulatory or legal obligation; cannot be deprioritised by business choice |
| **Constraint** | `CON-` | Hard limit imposed by environment, contract, or platform; not negotiable |
| **Assumption** | (see `references/raid-format.md`) | Not a requirement; lives in RAID |

ID numbering is unique within each type. BR-001 and FR-001 can coexist. Within a type, numbers don't reuse.

---

## 3. Requirement entry structure

Each requirement in `register.md`:

```markdown
### BR-005 Â· Merchant identity must be verified to NZ AML/CFT Act standard
**Type:** Business requirement (compliance-driven)
**Status:** Confirmed
**Priority (initiative-level):** Must
**Owner:** [Compliance lead] + [BA]
**Source:** Compliance interview 18 Apr 2026; AML/CFT Act 2009 reference
**Created:** 2026-04-18
**Last reviewed:** 2026-05-25
**Interrogator output:** `interrogations/BR-005.md`

**Statement:**
The system must verify merchant identity (individual or business) to a standard that satisfies the NZ AML/CFT Act 2009 customer due diligence requirements, including standard CDD for low-risk merchants and enhanced CDD for high-risk merchants.

**Rationale:**
Regulatory obligation. Failure to meet this standard exposes the organisation to civil penalties and operational restrictions. Risk-rated approach is permitted under the Act.

**Acceptance for "met":**
- Standard CDD performed for all merchants in low-risk category
- Enhanced CDD performed for all merchants in medium and high-risk categories
- Verification records retained per Act requirements
- Annual independent audit can confirm compliance

**Linked elements:**
- Decisions: D-04 (vendor X selection)
- Risks: R-12 (vendor capacity)
- Stories: PROJ-001, PROJ-002, PROJ-003
- Slices: SL-02, SL-07
- Out-of-scope items: (none for this requirement)

**History:**
- 2026-04-18: Identified during compliance interview
- 2026-04-25: Statement refined after interrogator pass
- 2026-05-02: Confirmed with sponsor and compliance
- 2026-05-25: Reviewed; no change
```

### Required fields

| Field | Type | Allowed values |
|---|---|---|
| `id` | string | Type prefix + number |
| `title` | string | One sentence, "must" / "should" wording |
| `type` | enum | business / functional / non-functional / compliance / constraint |
| `status` | enum | `draft` / `confirmed` / `superseded` / `descoped` / `deferred` |
| `priorityInitiative` | enum | must / should / could / wont (MoSCoW at initiative level) |
| `owner` | string | Named individual or pair |
| `source` | string | Where this came from (specific) |
| `createdAt` | date | |
| `interrogatorOutput` | string | Path to interrogator artefact; required for `status: confirmed` |
| `statement` | string | The requirement itself, in clear language |
| `rationale` | string | Why this matters |
| `acceptanceForMet` | list | How we'll know the requirement is satisfied |
| `linkedElements` | object | Decisions, risks, stories, slices, OOS |

### Status transitions

```
draft â†’ confirmed (interrogator pass complete; stakeholder agreement)
draft â†’ descoped (decided not to pursue)
confirmed â†’ superseded (replaced by new requirement; supersededBy link required)
confirmed â†’ deferred (deferred to future initiative; reason logged)
superseded / descoped / deferred â†’ confirmed (rare; with explicit re-confirmation)
```

---

## 4. Requirements register layout

`register.md` is organised by **type**, then **scope**. Each requirement appears under its primary scope. Cross-scope requirements appear under "Initiative-wide".

```markdown
# Requirements register â€” <Initiative name>

## Summary
- Total requirements: N (BR: x, FR: y, NFR: z, COMP: a, CON: b)
- Confirmed: N Â· Draft: N Â· Other: N
- Interrogator coverage: N% (target: â‰¥95% for confirmed)

## Initiative-wide
### BR-001 Â· ...
### COMP-21 Â· ...

## Cohort A â€” High-risk merchants
### BR-005 Â· ...
### FR-014 Â· ...

## Cohort B â€” Standard merchants
### BR-006 Â· ...

## Quick T2P pilot
### BR-009 Â· ...

## Out of scope (recorded for context)
### OOS-01 Â· Self-service onboarding for sole traders
**Out because:** Out of scope for initiative; deferred to FY27 roadmap.
**Decision link:** D-08
```

---

## 5. MoSCoW matrix

MoSCoW is **per scope**, not just initiative-wide. A requirement can be a `Must` at the initiative level but `Could` for a specific scope, if that scope is targeting an MVP that doesn't include it.

### Matrix layout

| Requirement | Initiative | Cohort A | Cohort B | Quick T2P |
|---|---|---|---|---|
| BR-005 â€” AML/CFT identity verification | M | M | M | M |
| BR-013 â€” Customer-facing decline messaging | S | M | S | C |
| FR-014 â€” High-risk routing logic | M | M | â€” | â€” |
| NFR-04 â€” <500ms verification latency at p95 | S | S | S | M |

Cell values:
- `M` â€” Must
- `S` â€” Should
- `C` â€” Could
- `W` â€” Won't (for this scope)
- `â€”` â€” Not applicable to this scope

### Override rule

If the initiative-level priority is `Must`, no scope can have it as `C` or `W` without an explicit decision logged. The Anti-Pattern Detector flags downward overrides without a decision link.

### Re-prioritisation

MoSCoW values are reviewed at each phase gate. Changes are logged in the requirement's `History` section. Repeated changes (>2 per requirement per month) trigger a flag â€” sign of unstable scope.

---

## 6. JTBD format (when applicable)

Jobs to be Done sit alongside requirements. Not every initiative needs them; use when the user perspective is important (customer-facing features, new product capabilities) and skip for pure technical work.

Format:

```markdown
### JTBD-01 Â· When a merchant applies to accept payments, they want to know quickly whether they're approved, so they can plan opening their business

**Situation:** Merchant has decided to use [Your Organisation] for payment processing and submitted application
**Motivation:** Wants to plan their first trading day with confidence
**Expected outcome:** Decision (approval / decline / more info needed) within hours, not days

**Forces pushing toward this solution:** Speed, predictability, ability to plan
**Forces pulling away:** Complexity of compliance checks, manual review queue depth

**Anxiety:** "What if I get declined and have to start over?"
**Habit:** Previous payment processors took days; merchant expects the same

**Functional / Emotional / Social aspects:**
- Functional: get an answer
- Emotional: feel confident the answer is fair
- Social: be able to communicate timeline to staff and customers

**Related requirements:** BR-013 (decline messaging), NFR-04 (latency), BR-005 (identity verification)
```

---

## 7. Acceptance for "met" wording

This is the requirement equivalent of acceptance criteria. Specific, observable, falsifiable.

**Good:**
- "Enhanced CDD performed for all merchants in medium and high-risk categories" (observable in audit log)
- "Verification latency <500ms at p95 under sustained 100 RPS load" (measurable)
- "Decline reason codes match Reason Code Register SO-04 verbatim" (verifiable by inspection)

**Bad:**
- "System is secure" (untestable)
- "Process is efficient" (no threshold)
- "Compliance is met" (recursive â€” that's literally the requirement)
- "Works well for users" (no measure)

If the requirement can't be written with specific acceptance, that's a signal it needs interrogation first. Don't confirm a requirement that can't be tested.

---

## 8. Interrogator coupling

Every requirement marked `status: confirmed` must have an `interrogatorOutput` path pointing to a real file. The Requirements Interrogator skill produces these artefacts.

If a requirement is confirmed without interrogation:
- The Anti-Pattern Detector flags `Requirement confirmed without interrogator pass`
- The `requirementInterrogationRate` metric (per `canvas-data-model.md`) reflects the gap

Re-interrogation happens when:
- A requirement's statement changes after confirmation
- A linked decision is reversed
- A new dependency is identified that materially affects the requirement

---

## 9. Out-of-scope recording

Out-of-scope items get IDs and entries too. The point is to capture "we considered this and decided not to" so it doesn't get re-litigated in the next phase.

```markdown
### OOS-01 Â· Self-service onboarding for sole traders
**Considered during:** Phase 1 discovery
**Decision date:** 2026-04-30
**Decision link:** D-08
**Reason out of scope:** Sole trader compliance pattern differs significantly enough to warrant separate initiative. Estimated ~3 weeks additional discovery and a different risk model.
**Revisit conditions:** If sole trader applicant volume exceeds X% of total inbound, reconsider for FY27.
```

OOS entries don't carry MoSCoW values. They're informational.

---

## 10. Confluence requirements page

Published view, derived from `register.md`. Structure:

1. Header: initiative name, last refreshed timestamp, link to register source
2. Summary table (total counts, coverage)
3. MoSCoW matrix (table from Section 5)
4. Requirements grouped by scope, then type
5. Each requirement shown collapsed by default; expand for full detail
6. Out-of-scope section at the end
7. Footer with format version

Published page is regenerated from register.md, not edited directly in Confluence. State Validator catches drift.

---

## 11. Anti-patterns (Anti-Pattern Detector triggers)

| Watching | Trigger | Anti-pattern |
|---|---|---|
| Discovery and Requirements | Requirement marked `status: confirmed` without `interrogatorOutput` path | Requirement confirmed without interrogator pass |
| Discovery and Requirements | Requirement has no `acceptanceForMet` content | Untestable requirement |
| Discovery and Requirements | Requirement statement uses vague terms ("user-friendly", "performant", "secure") without measurable definition | Vague requirement |
| Feature Slicing | Story created linking to a requirement that doesn't exist in register | Untraceable story |
| Discovery and Requirements | Initiative `Must` priority downgraded to `Could` or `Won't` at scope level without decision link | Scope override without decision |
| Discovery and Requirements | MoSCoW values for one requirement changed >2 times in 30 days | Unstable scope |
| Discovery and Requirements | OOS entry created without decision link | Out-of-scope without decision audit trail |
| Discovery and Requirements | Compliance requirement (COMP-) priority set to anything other than `Must` | Compliance optionalisation |

---

## 12. Worked example â€” minimal requirement entry

```markdown
### NFR-04 Â· Verification latency must be <500ms at p95 under sustained load
**Type:** Non-functional
**Status:** Confirmed
**Priority (initiative-level):** Must
**Owner:** [Tech Lead]
**Source:** Architecture review 5 May 2026
**Created:** 2026-05-05
**Interrogator output:** `interrogations/NFR-04.md`

**Statement:**
Identity verification round-trip (from API call dispatched to response received) must be less than 500ms at the 95th percentile under sustained load of 100 requests per second.

**Rationale:**
Verification latency directly affects merchant onboarding completion time. Internal threshold for completion drop-off acceleration is 5 minutes total onboarding time. Verification is one of three latency-sensitive steps; budgeting 500ms here preserves the overall budget.

**Acceptance for "met":**
- Load test in pre-prod confirms <500ms p95 at sustained 100 RPS for 30 minutes
- Production monitoring SLO set at 500ms p95 with alerting
- 24-hour soak test shows no degradation

**Linked elements:**
- Decisions: D-04 (vendor X)
- Risks: R-12 (vendor capacity at launch)
- Stories: PROJ-010 (load test setup)
- Slices: SL-02 (verification pipeline)

**History:**
- 2026-05-05: Identified during architecture review
- 2026-05-08: Interrogator pass confirmed measurable threshold
- 2026-05-15: Confirmed with tech lead and PM
```

---

## 13. Versioning

v1.0 (2026-05-30). Changes to required fields, new requirement type, or MoSCoW rule changes require version bump.

