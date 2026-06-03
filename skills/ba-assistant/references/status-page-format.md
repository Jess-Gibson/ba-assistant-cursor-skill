# Status Page Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/status-page-format.md`
**Owner:** ba-status-page-publisher (workflow), this standard (format)
**Last reviewed:** 2026-05-30

This file is the canonical source for Confluence status page structure. Any sub-skill publishing or updating a status page MUST conform to this standard. Pulls from `references/canvas-data-model.md` for data structure and `references/raid-format.md` for RAID rendering.

---

## 1. Page identity

### Naming convention

Every status page follows: `Status as at <DD Mon YYYY> — <Initiative name>`

Examples:
- `Status as at 30 May 2026 — [Initiative Name]`
- `Status as at 06 Jun 2026 — Feature Alpha Pilot`

Date is the day the page is published, not the day data was last refreshed. If data is stale at publish time, the freshness note in the header flags it.

### Page hierarchy

Status pages live under: `<Initiative space> / <Initiative name> / Status updates / <page>`

Each new status page is created as a child of the `Status updates` parent. The previous status page is marked superseded (see Section 9).

### Page ID tracking

The page ID is recorded in `confluence-pages.json`:

```json
{
  "type": "status-page",
  "initiative": "[initiative-slug]",
  "pageId": "1245891",
  "title": "Status as at 30 May 2026 — [Initiative Name]",
  "createdAt": "2026-05-30",
  "parentPageId": "1102453",
  "supersedes": "1238472"
}
```

---

## 2. Required sections (in order)

A conformant status page has these sections in this order:

1. Header banner
2. TL;DR (3-5 bullets)
3. Outcome health
4. Quality metrics
5. Workstream and scope grid
6. Top focus this week
7. RAID summary
8. Decisions and open questions
9. Sign-offs
10. Upcoming milestones
11. Detail / appendix links
12. Footer (freshness + audit info)

Sections are not collapsible by default. Sections that have no content for this period show "No change since last status" rather than disappearing — silence is ambiguous.

---

## 3. Section: Header banner

ADF `note` panel at top of page. Required content:

```
📊 Status as at <DD Mon YYYY> · <Initiative name>

Sponsor: <name>
PM: <name> · BA: <name> · Tech lead: <name>
Phase: <current phase>
PM approval state: <pending / approved / TBC>
Data freshness: <ISO timestamp from status-data.json computedAt>
Supersedes: <link to previous status page>
```

If `pmApproval.status` is not `approved`, a DRAFT banner appears immediately below the header banner:

```
⚠️ DRAFT — pending PM approval (<approver name>, requested <date>)
```

The DRAFT banner has a red `error` panel background to make it visually unmissable.

---

## 4. Section: TL;DR

ADF `success` panel. 3-5 bullets max. Each bullet is one sentence.

What goes in:
- The single most important outcome update
- Any change in overall trajectory since last status
- Any new blocker or risk that needs sponsor attention
- The single most important next-week focus

What doesn't:
- Process metrics
- Detail that's covered in later sections (TL;DR is for executive scanning, not summary of summary)
- Hedged language ("we're on track, mostly, although there are some things") — pick a position

Example TL;DR:

> - Cohort A delivery on track for 6 Jun launch; legal sign-off SO-03 the last critical-path item
> - Feature Alpha pilot in production with 12 merchants live; no incidents in first week
> - Cohort B paused pending vendor capacity confirmation (R-12); decision needed by 10 Jun
> - Manual review queue back within SLA after temporary reviewer reassignment

---

## 5. Section: Outcome health

A small grid showing the three outcome signals (Wave 6 — outcome health concept). Subjective and explicitly captured from the BA / PM, not derived from data.

| Signal | This period | Trend vs last | Notes |
|---|---|---|---|
| Sponsor confidence | 4/5 | → | Sponsor signed off on Cohort A scope last week |
| Stakeholder alignment | 4/5 | ↗ | Compliance and Tech Lead aligned on vendor X after spike outcome |
| Initiative-to-outcome confidence | 🟢 | → | On track for stated success metrics |

If any signal is red or trending down, a "What changed" line below explains.

If outcome health hasn't been captured this period, the section shows:

> ⚠️ Outcome health not refreshed since <date>. Process metrics below may overstate health.

This is the honesty gate. Don't generate a status page that hides outcome reality behind green process metrics.

---

## 6. Section: Quality metrics

Pull from `metrics-cache.json` (per `references/canvas-data-model.md` Section 4). Render as table:

| Metric | Value | Trend | Threshold | Notes |
|---|---|---|---|---|
| MoSCoW coverage — Cohort A | 92% | → | ≥80% | ✓ |
| MoSCoW coverage — Cohort B | 64% | ↘ | ≥80% | 🔴 below threshold |
| DoR hit rate — Cohort A | 78% | → | ≥70% | ✓ |
| DoR hit rate — Cohort B | n/a | — | ≥70% | No DoR checks this period |
| Requirement interrogation rate — overall | 91% | → | ≥95% | 🟡 below target |
| Sign-off cycle time (median) | 6.5 days | ↗ | ≤5 days | 🔴 above target |

Rules:
- `n/a` shown literally for missing data, not fabricated 0%
- Threshold breaches flagged with 🔴; near-misses with 🟡; healthy with ✓
- Trend arrows: ↗ improving, → stable, ↘ degrading
- Notes column for context, not for explaining away

If outcome health is amber or red (per Section 5), this section is rendered collapsed by default with a note: "Process metrics — outcomes need attention first."

---

## 7. Section: Workstream and scope grid

The grid from `status-data.json → workstreams`. Render as table with workstreams as rows and scopes as columns.

|  | Initiative | Cohort A | Cohort B | Feature Alpha |
|---|---|---|---|---|
| Intake | ✅ Complete | — | — | — |
| Discovery | — | ✅ Complete | 🟡 Active | ✅ Complete |
| Solution shaping | — | 🟡 Active | ⚪ Not started | ✅ Complete |
| Feature slicing | — | ✅ Complete | ⚪ Not started | ✅ Complete |
| Delivery | — | 🟢 Delivering | ⚪ Not started | 🟢 Delivering |
| Verification | — | ⚪ Not started | ⚪ Not started | 🟡 Active |
| Closure | — | ⚪ Not started | ⚪ Not started | ⚪ Not started |

State emoji mapping:
- ⚪ not_started
- 🟡 active
- 🟢 delivering (delivery workstream only)
- 🟠 blocked
- ⏸ paused
- ✅ complete

A scope with `blocked` or `paused` state must have a one-line reason directly below the grid.

---

> **Optional section — Delivery Model (optional):** Include this section only if the initiative uses cohort-based or phased delivery. Omit entirely for initiatives without cohort or wave-based rollout.

## 8. Section: Top focus this week

3-5 items. Each item is:

- **Title** (one line, active voice)
- **Owner** (named person)
- **By when** (specific date, not "this week")
- **Status** (in flight / blocked / waiting / done)

Drawn from `/next` logic at time of publication. The point of this section is to give the sponsor or PM something to do or notice.

---

## 9. Section: RAID summary

Pull from `status-data.json → raid`. Show:

- New since last status (highlighted)
- Changed status since last status (highlighted)
- Top 5 open risks by likelihood × impact
- All active issues
- Dependencies due in next 14 days
- All currently unvalidated assumptions

Each entry shows: ID, title, owner, status, target date (where applicable). Detail links to the tracker.

Do NOT inline full RAID content — that lives in the tracker. The status page shows the headline view.

Format conforms to `references/raid-format.md`.

---

## 10. Section: Decisions and open questions

Two sub-sections.

**Decisions made this period:** list new decisions from `status-data.json → decisions` with `date` in this status window. Each shows ID, title, owner, status, and a one-line rationale. Decisions reversed in this window get a 🔄 marker.

**Open questions blocking progress:** all `status: open` questions with `blocks` populated, sorted by `targetAnswerDate`. Each shows ID, question, owner to answer, target date. Ageing OQs (>14 days open) flagged with 🟡; >30 days with 🔴.

Format conforms to `references/raid-format.md`.

---

## 11. Section: Sign-offs

Active sign-offs only (status `pending` or recently `approved`).

| ID | Artefact | Approver | Requested | Status | Notes |
|---|---|---|---|---|---|
| SO-03 | Legal sign-off on customer-facing decline messaging | Legal lead | 2026-05-25 | 🟡 Pending (5 days) | Critical path for Cohort A |
| SO-04 | Reason Code Register | Compliance + Legal | 2026-05-15 | ✅ Approved 2026-05-22 | v1 baseline |

Sign-offs in `status: pending` for >7 working days are flagged with 🔴.

---

## 12. Section: Upcoming milestones

Pull from `status-data.json → milestones`. Show milestones with `targetDate` in the next 30 days OR status `at-risk` regardless of date.

| Milestone | Target | Status | Owner | Critical path? |
|---|---|---|---|---|
| Legal sign-off complete | 6 Jun 2026 | 🟡 At risk | Legal lead via PM | Yes |
| Cohort A go-live | 13 Jun 2026 | 🟢 On track | Tech Lead | Yes |
| Cohort B vendor capacity confirmation | 10 Jun 2026 | 🟠 Blocked | Tech Lead | Yes |

Status colour matches the milestone `status` value.

---

## 13. Section: Detail / appendix links

Bulleted list of links:

- Initiative tracker (Confluence page link)
- Project canvas (link to interactive HTML attached to space)
- Requirements register
- Decision log (if separate)
- Recent meeting debriefs (last 2-3 only)
- Related Confluence pages (limit 5; if more, link to a parent page)

---

## 14. Section: Footer

ADF `info` panel at bottom of page. Required content:

```
📋 Page audit

Generated: <ISO timestamp>
Generated by: BA Assistant
Source: status-data.json @ <ISO timestamp>
Conforms to: status-page-format.md v1.0
Supersedes: <previous status page link>
Next planned update: <date>
```

If any source data is stale (>24 hours old at generation), the footer flags it.

---

## 15. Superseding previous status pages

When a new status page is published:

1. Create the new page first
2. Verify the new page renders correctly
3. Update the previous page by adding a banner at the top:

```
⚠️ This status page has been superseded.

For the current status, see: <link to new page>

This page is preserved for historical reference.
```

4. Update `confluence-pages.json` and `superseded-pages.json` (per Wave 5 State Validator)

Never delete the previous page. Historical status pages are part of the audit trail and should remain readable.

---

## 16. PM approval gate

If `pmApproval.status` is `pending`, the status page publishes but with DRAFT banner. The page is still useful internally even when not yet PM-blessed.

Sub-skills must NOT silently auto-publish status pages with sponsor-visible distribution while `pmApproval.status` is anything other than `approved`. Two-step rule:
- Publish to Confluence: OK with DRAFT banner
- Notify sponsor or wider audience: requires `pmApproval.status: approved`

The Anti-Pattern Detector flags any wider-distribution comms drafted while PM approval is pending.

---

## 17. Output anti-patterns

| Watching | Trigger | Anti-pattern |
|---|---|---|
| Status page publisher | Page published without TL;DR or with TL;DR >5 bullets | TL;DR breach |
| Status page publisher | Outcome health section absent or stale >14 days | Outcomes ignored — process metrics may mislead |
| Status page publisher | Previous status page not marked superseded after new one published | Stale status page live |
| Status page publisher | Page published without DRAFT banner when `pmApproval.status` not approved | Approval gate bypassed |
| Status page publisher | RAID inline with full narrative content (should link to tracker) | Status page becoming tracker |
| Status page publisher | Threshold breaches in metrics rendered as green | Metric gaming |
| Status page publisher | Section omitted entirely (vs marked "No change since last") | Silent omission |

---

## 18. Worked example header

```
📊 Status as at 30 May 2026 · [Initiative Name]

Sponsor: [name]
PM: [name] · BA: [Your Name] · Tech lead: [name]
Phase: Phase 3 — Feature slicing (Cohort A delivery in flight)
PM approval state: ✅ Approved (v3, 28 May 2026)
Data freshness: 2026-05-30T16:10:00+13:00
Supersedes: Status as at 23 May 2026

📌 TL;DR

- Cohort A delivery on track for 6 Jun launch; legal sign-off SO-03 the last critical-path item
- Feature Alpha pilot in production with 12 merchants live; no incidents in first week
- Cohort B paused pending vendor capacity confirmation (R-12); decision needed by 10 Jun
- Manual review queue back within SLA after temporary reviewer reassignment
```

---

## 19. Versioning

v1.0 (2026-05-30). Changes to section order, new mandatory section, or threshold rule changes require version bump. The footer always carries the format version the page was generated against, so historical pages remain interpretable.
