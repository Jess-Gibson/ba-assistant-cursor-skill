# Unified requirements register  -  template

**Owner:** ba-discovery-and-requirements + ba-requirements-interrogator (Mode 4)  
**Last reviewed:** 2026-07-15  
**Supersedes for new work:** separate `interrogations/kickoff-hlr-review-*.md` session logs; stream-prefixed parents (`HLR-2.1` as F2 parent); `RR-Fx-xx` / `REQ-S1-xx` as primary IDs.

One file per initiative. **Interrogation, kickoff sign-off, and dev handover** all read and write here.

---

## 1. ID scheme (non-negotiable)

| Level | Pattern | Example | Meaning |
|---|---|---|---|
| **High-level requirement** | `HLR-01` … `HLR-99` | `HLR-08` | One numbered capability or delivery outcome (integer only at this level) |
| **Detailed requirement** | `HLR-08.1`, `HLR-08.2`, `HLR-08.21` | `HLR-08.3` | Child under parent `HLR-08`; decimal suffix only |
| **Legacy reference** | `legacyId` field | `RR-F2-03` | Traceability during migration; not used in new work |

**Rules**

- High-level IDs are **never** `HLR-2.9` (that looked like a child under stream 2). Stream (F1–F5) is metadata, not part of the ID.
- Do not create a second register, interrogation log, or kickoff-only requirement list.
- `interrogatorOutput` for handover points to an **anchor in this file**: `outputs/requirements-register.md#hlr-08`.
- Every detailed row names its parent: `parent: HLR-08`.

**Allocation**

- Reserve `HLR-01`–`HLR-30` (example) for **customer go-live-ordered** delivery (timeline strip).
- Allocate `HLR-31`+ for commercial, GTM-only, reporting, architecture, deferred backlog.
- Gaps in numbering are allowed; never reuse a retired HLR number (mark `superseded` in history).

---

## 2. Register file layout

```markdown
---
initiative: [name]
registerVersion: 2
lastUpdated: YYYY-MM-DD
requirementCount: { hlr: N, detail: M }
pipeline: outputs/requirements-lifecycle-pipeline.md
---

# [Initiative]  -  requirements register

## Index (high-level only)

| HLR | Name | Go-live | Status | blockedOn |
|---|---|---|---|---|
| HLR-01 | August awareness in-product messaging | Early Aug 2026 | interrogated | design |
| HLR-02 | Payer preference survey experiment | Early Aug 2026 | proposed | spike |
| … | … | … | … | … |

*Detailed rows: search `parent: HLR-NN` or open the parent section below.*

---

## HLR-01 · [Plain English name] {#hlr-01}

**Stream:** F2 Product delivery (metadata) | **Go-live:** [date or window] | **Legacy:** [old IDs if migrated]

### Requirement statement (parent)

Plain business outcome in one or two sentences (`… so that …` inline). **Omit** the `### I want / so that` heading when the sentence is self-explanatory. Do **not** lock spike/design options (MTR vs help page, patch vs major) in the parent statement unless the user confirmed that option in closure.

### Scope

**In scope:** short bullets (5–7 max)  -  headline boundaries only  
**Out of scope:** short bullets (5–7 max)  -  this HLR's exclusions only, not other HLRs or initiative-wide items  
**Solution options (design-owned):** when applicable  -  labelled options from spike/design, with caveats; final shape not a requirement until closure

*Detail (surfaces per product, cohort rules, legal gates, delivery path) lives in **Products and surfaces**, **Detailed requirements** (business-level `Requirement` column), and **Closure blockers**  -  not in Scope.*

### Products and surfaces

| Product | Surfaces | Delivery path | Notes |

### Delivery metadata

| Field | Value |
|---|---|
| status | proposed / interrogated / confirmed / … |
| blockedOn | none / spike / design / … |
| kickoffRoom | Ready for story / Spike first / … |
| reqType | functional / compliance / … |
| designNeeded | UX + copy / none / … |
| platformRelease | Patch / 26.7 / n/a |
| signedOff | Name, date |

### Detailed requirements

| ID | Requirement | User story | Type | MoSCoW | status | legacyId |
|---|---|---|---|---|---|---|
| HLR-01.1 | … | As a … I need … so that … | Functional | Must | proposed | RR-F3-28 |
| HLR-01.2 | … | … | … | … | … |  -  |

### Acceptance (HLR-level)

- …

### Handover readiness

| Gap | Owner | Closes when |

### Linked elements

- Decisions: D-xxx
- Risks: R-xxx
- Spikes: AURORA-xxxx
- Open questions: Q-xxx
- Stories: (when sliced)

### Interrogation history

| Date | Summary |
|---|---|
| 2026-07-14 | Audience expanded to all AU in-product users; ARL path = Patch |

---

## HLR-02 · [Next parent] {#hlr-02}

… repeat block …

---

## Constraints and enablers (not requirements)

[unchanged pattern  -  CON-, assumptions]

---

## Legacy ID manifest

See `requirements-id-migration-manifest.md` for old → new mapping during v1 → v2 migration.
```

---

## 2a. Scope writing rules ([BA name] preference, 15 Jul 2026)

| Rule | Guidance |
|---|---|
| **Length** | In scope and Out of scope are **short bullet lists** (typically 5–7 bullets each). One line per bullet; no sub-bullets, no paragraphs. |
| **Content** | Scope = **headline boundaries** only. Enough to orient a reader in 10 seconds. |
| **Detail placement** | Product/surface breakdown → **Products and surfaces** table. Behaviour, cohort, legal, telemetry → **Detailed requirements** `Requirement` column. Blockers and TBCs → **Closure blockers** or **Delivery metadata**. Evidence and decisions → **Linked elements** + **Interrogation history**. |
| **Out of scope** | List only what could be **mistaken as part of this HLR**. Plain language; **do not** reference other HLR numbers or cross-HLR tables. |
| **In scope** | Same: plain-language headlines. Do not restate child rows verbatim. |
| **Solution in requirement** | Parent statement and child `Requirement` column = **business outcome only**. Spike hosts (MTR, help page), patches, and build paths → **Solution options** + Products table after design/closure  -  not locked in the requirement row. |
| **`interrogated` without user** | **Never.** Step 3 closure ceremony with explicit user confirm on each field before register write. Evidence from tracker ≠ human review. |

---

## 2b. Register edit permissions ([BA name] preference, 15 Jul 2026)

| Parent or child `status` | Agent may edit without asking [BA name] |
|---|---|
| `proposed` (draft / in interrogation) | **Yes**  -  full section writes during Mode 4 Q&A and draft-for-review |
| `interrogated` | **No**  -  no content edits (scope, children, parent statement, products table, metadata prose) unless [BA name] explicitly approves that HLR edit in the current thread. **Exception:** append **Interrogation history** row when [BA name] closes an interrogation; update Index `status` / `blockedOn` only when [BA name] says confirm `interrogated` or assigns lifecycle in closure. |
| `confirmed` | **No**  -  any content change requires explicit [BA name] approval (same as interrogated; stricter for handover). |

**Cross-HLR alignment:** Do not edit an `interrogated` or `confirmed` parent to "stay consistent" with a draft HLR elsewhere. Propose the diff; wait for approval.

**Gate line when editing register:** `Gate: register-edit: PASS` (proposed or approved) / `FAIL` (interrogated/confirmed without approval).

**Anti-pattern:** Rewriting scope, children, or acceptance hints on HLR-04 while drafting HLR-07 without [BA name] sign-off on HLR-04.

**Good (HLR-01 example):**

```markdown
**In scope:**
- Dismissible in-product regulatory-change message
- Payment and invoice surfaces; [Organisation] Business, AccountRight Live, Solo, Assist
- Help/FAQ link; CVP-aligned copy
- AccountRight Live patch delivery; legal review (PT-105)
- AU in-product audience (TBC [Team Member])

**Out of scope:**
- Product settings or behaviour changes
- Later messaging waves (defaults explanation, mandatory notice)
- Payer-facing features
- Out-of-product GTM comms
```

**Bad:** Long bullets with decision IDs, rationale, or child-level behaviour duplicated from the detailed table.

---

## 3. Write-up effort by status (unchanged logic)

| Parent `status` | What exists in the HLR block |
|---|---|
| `proposed` | Index row + one-line capture under parent; optional stub heading |
| `interrogated` | Full block through **Detailed requirements**; handover gap filled |
| `confirmed` | Full block; `blockedOn: none`; signedOff set; all Must children at least `interrogated` |

Detailed children follow the same lifecycle independently where they can be handed over separately.

---

## 4. What is derived (do not edit as source of truth)

| Artefact | Generated from |
|---|---|
| Kickoff summary slide/table | Index + `kickoffRoom` column |
| Timeline backbone / Miro | Index sorted by go-live + HLR name |
| `/handover` requirements pack | All `status: confirmed` parents and children |
| Confluence requirements page | Published export; register wins on conflict |

Regenerate or patch derived docs after register changes; never fork requirement text.

---

## 5. Relation to `requirement-format.md`

- Lifecycle enums (`status`, `blockedOn`) unchanged.
- `interrogatorOutput` may be **in-file anchor** (`#hlr-08`) instead of external `interrogations/*.md`.
- Type prefixes (`BR-`, `FR-`) optional on **detailed** rows; parent is always `HLR-NN`.

---

## 6. Anti-patterns

| Do not | Do instead |
|---|---|
| Second file for kickoff interrogation | Append **Interrogation history** on the parent section |
| `HLR-2.9` as a parent | Next free integer `HLR-09` |
| Bare IDs in stakeholder comms | Name from Index table |
| Bulk-copy register to backbone | Export index columns only |
| Long Scope bullets with decision IDs and child detail | Short Scope bullets; detail in **Detailed requirements** column (template §2a) |
| Cross-HLR references in Out of scope | Plain-language exclusions for this HLR only |
