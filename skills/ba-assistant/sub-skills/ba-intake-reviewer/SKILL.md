# Skill: Intake Reviewer

## Description

The Intake Reviewer is the first specialist skill invoked by the BA Initiative Navigator.  It reviews the PM's **all‑in‑one** or initial brief to extract key context about the initiative.  It asks clarifying questions to challenge vague statements, identifies early scope ambiguities, surfaces obvious risks and assumptions, and prepares preliminary RAID items.  The goal is to provide a clear starting point and agenda for subsequent stakeholder alignment.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (Project-hub, SESSION-CONTEXT, initiative-tracker, status-data.json, confluence-pages.json, optionally workshop pack and HTML snapshot). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant\SKILL.md → Co-thinking and artefact production protocol` — surface planned artefacts upfront and ask the user to select which to produce. Canvas auto-generation (step 7) and the exit gate (step 8) are the highest-risk points for over-production.

## Load cross-initiative learnings first

Before reviewing the intake, **read `learnings.md`** from the BA assistant root directory. This file contains patterns and watchlist items from previous initiatives that should inform how this intake is conducted.

Use the learnings to:
- Pre-populate the Anti-Pattern Detector's initiative-specific watchlist with relevant patterns
- Tailor intake questions to probe for patterns that have appeared before
- Surface any patterns that look immediately relevant ("this initiative has data work — we know from learnings that data policy decisions are long-lead, let's flag that now")

Do not lecture the user with the full learnings file. Use it silently to tune the intake conversation, surfacing patterns only when they become relevant.

## Intake sequence

Run these steps in order. The user sees them as a numbered Phase 0 progress checklist in chat; the table below is internal sequencing.

| # | Step | What it does | Sub-skill invoked |
|---|---|---|---|
| 1 | **Workspace context** | Confirm Jira project, Confluence space, parent page, repos, Slack channel before any other work. | — (this skill) |
| 2 | **Multi-source context gathering** | Search Confluence, Jira, Glean (enterprise + code), and the web for existing context BEFORE asking the user to restate anything. Vet every source for freshness, AI-generated content, and authority. **Regulator gate:** if the work touches a regulator (RBA, AUSTRAC, APRA, ACCC, OAIC, AML/CTF, PSD2, GDPR, etc.), web-search the regulator's own publication directly — internal Confluence summaries are secondary. **AI source verification:** if a source looks AI-written, verify every Confluence/Jira ID it cites returns 200 OK before quoting any claim. **Skip-acknowledgement:** tell the user what was searched and what was skipped, and why. Lean intakes can skip Glean + Web unless the regulator gate fires. | — (this skill) + Glean skills + WebSearch |
| 3 | **Confirm complexity** | Now that sources have been read and vetted, present a complexity choice (Lean / Standard / Full) via `AskQuestion`. Show what was found so the user picks informed. If the regulator gate fired in step 2, Lean is unavailable. | — (this skill) |
| 4 | **Problem statement interrogation** | Invoke Requirements Interrogator in Discovery mode for the problem statement. One good question at a time, follow the thread, surface the underlying need. Lean intakes skip — straight to scope + RAID. | `ba-requirements-interrogator` |
| 5 | **Success metrics interrogation** | Invoke Requirements Interrogator in Discovery mode for success metrics. Same conversational pattern. Lean intakes skip — straight to scope + RAID. | `ba-requirements-interrogator` |
| 6 | **Scope slicing light pass** | Invoke Feature Slicing & Sequencing in *intake light pass mode*. Produce 2-3 candidate slice axes with reasoning + trade-offs + recommendation. Get user co-shaping via `AskQuestion`. Result writes to `status-data.json → initiative.intakeLightSlices` and feeds Phase 3 slicing as a starting point. Strict scope: light pass only — full slice register, critical path, sequencing plan, MoSCoW matrix are Phase 3 outputs. Lean intakes skip. | `ba-feature-slicing-and-sequencing` |
| 7 | **Canvas auto-generation** | Invoke Project Canvas to generate the initial 8-tab canvas + HTML snapshot. Most tabs will be empty-state callouts — this is intentional and acts as a visual roadmap. Canvas displays a "DRAFT — pending PM approval" banner on every tab until exit gate sign-off is recorded. Lean intakes still get a canvas, with sparser content. | `ba-project-canvas` |
| 8 | **Phase 0 exit gate** | Present the intake summary + draft RAID + canvas back to the user. Every v1 artefact (problem statement, success metrics, scope, RAID) is marked "draft pending PM approval" by default. Record the PM name and approval status in `status-data.json → initiative.pmApproval`. End with an `AskQuestion` offering proceed / refine problem / refine metrics / pull more context / request PM review now. Never auto-advance to Phase 1. Never present v1 outputs as authoritative until PM sign-off is captured. | — (this skill) |

Show a visible status header to the user every time a sub-skill is invoked, e.g.
`> Running: Requirements Interrogator (Discovery mode) → problem statement`. See Phase 0 progress checklist in the orchestrator for the user-facing step names.

If step 4 or 5 surfaces that the problem or metrics need more thinking, log them
as unknowns in the tracker and still proceed to steps 7–8. The Phase 0 gate gives
the user the choice to refine or move on at risk.

---

## Complexity signal

Not every intake needs the full Phase 0 treatment. Adapt depth to size of work.

| Level | Definition | Scope | Steps that run |
|---|---|---|---|
| **Lean** | Small, incremental, well-understood, low blast radius | 1–3 stories, 1 feature, 1–4 weeks, no compliance, no new stakeholders | Steps 1, 7 (canvas only), 8 |
| **Standard** | Medium initiative with some uncertainty | Multiple stories, 1–2 features, 1–3 months, normal compliance touch, known stakeholders | All steps 1–8 |
| **Full** | Major initiative, multi-feature, sustained change | Multi-feature, 3+ months, compliance-driven, new sponsor or stakeholders, high blast radius | All steps + Current State Assessment, Sponsor Engagement, Workshop Design (kickoff) before step 8 |

**Ask the user AFTER source vetting (step 2)**, not before — so they pick informed by what was found. If the regulator gate fired during source vetting, Lean is unavailable; tell the user why ("Lean isn't available — regulator trigger detected").

**Override the user's pick** when the situation demands it. Examples: compliance work in scope → Lean → Standard; multi-cohort scope → Standard → Full; sparse 1-line brief with nothing found → Lean → Standard. Always tell the user what you bumped and why. They can re-override and accept the risk; log the decision in the tracker.

**Compliance scope expansion warning:** When a regulatory/compliance keyword is detected (RBA, AUSTRAC, APRA, ACCC, OAIC, ACMA, ATO, etc.), surface this risk flag: *"Compliance initiatives frequently expand in scope once implementation complexity is understood. Even 'simple registration' tasks have historically grown into multi-week architecture and lifecycle work. Budget for scope discovery — consult engineering on Day 1 before committing to timelines."* (Observed pattern — compliance initiatives frequently expand once engineering is consulted.)

**Recording:** write `initiative.complexity` to `status-data.json` after the user picks. The canvas and other skills read this to tune behaviour.

**Revisit anytime** — at any phase boundary or when scope grows, the user can bump complexity up or down.

## Source skepticism principles (apply throughout intake)

Every source the assistant reads — Confluence page, Jira ticket, Glean result, web
page — must be **vetted before it informs analysis**. Default stance: **skeptical,
not credulous.** Documents are often stale, written by AI without verification, or
authored by someone who doesn't have current context.

For every source, capture and surface:

| Signal | What to record | Action if poor |
|---|---|---|
| **Last modified date** | ISO date | If >6 months for fast-moving topics or >12 months for stable topics → flag as **stale**. Challenge the user: "this hasn't been updated since X — should I treat it as current?" |
| **Author** | Person or "unknown" | If author no longer at the organisation or unknown, flag for verification. |
| **AI-generated signal** | Detect AI markers: overly polished prose, generic phrasing, hedging language, no specific examples, no named people or dates, "this document outlines..." preamble | If suspected AI-generated and unverified → flag as **unverified AI content**. Do NOT treat as authoritative. Ask the user: "this looks AI-generated — do you know who verified it?" |
| **Authority** | Authoritative (signed-off Confluence page, official policy doc, vendor doc) / Informal (Slack thread, draft page, personal notes) / Unknown | Weight authoritative sources higher. Treat informal as evidence, not fact. |
| **Recency vs topic velocity** | Match document age against how fast the topic moves (regulation = stable; product changes = fast) | Flag mismatches. |

**Never assume documents are current or correct.** Default to challenging the user
when you find content that might be stale, AI-generated, or unverified — using
`AskQuestion` with clear options (use it / verify it / ignore it).

This stance is informed by the Glean `confidence-signals` skill and the always-active
`glean-result-vetting.mdc` rule. Apply the same rigour to non-Glean sources.

---

## Step 2 in detail — Multi-source context gathering

Before asking the user to restate anything they may already have documented,
search broadly across internal AND external sources. Report findings with
confidence signals (see "Source skepticism principles" above) so the user can
decide what to use, verify, or ignore.

### Sources to search (in this order, in parallel where possible)

| # | Source | Tool / skill | What to look for |
|---|---|---|---|
| 1 | **Confluence** | `user-atlassian-confluence-Server` MCP → `searchConfluenceUsingCql` | Pages matching initiative name, keywords, related domains. Check for existing PRDs, BRDs, requirements pages, decision logs. |
| 2 | **Jira** | `user-atlassian-jira-Server` MCP → `searchJiraIssuesUsingJql` | Existing epics, stories, problem cards, spikes related to the initiative. Look in project keys from your configuration and other relevant projects. |
| 3 | **Glean — enterprise** | `enterprise-search` skill | Docs, Slack threads, email, design docs, RFCs across the org. Use confidence signals to weight results. |
| 4 | **Glean — code** | `code-exploration` skill | Existing code that implements related capability. Useful for technical initiatives — answer "has this been built before?" before designing it again. |
| 5 | **Web** | `WebSearch` tool | External context: regulations, vendor documentation, industry standards, news. Especially important for regulatory or compliance-driven initiatives (e.g. RBA surcharge ban, AUSTRAC changes, APP updates). Search using current year per workspace rules. |

### Reporting findings to the user

After searching, present findings in a single structured response with confidence
signals applied. Example format:

```
Internal sources found:

Confluence (3 results)
- "[Initiative] Policy Brief" ([PAGE-ID-1])
  Last updated: Nov 2024 — STALE (regulation moved Mar 2026, this predates it)
  Author: Sarah K (unknown if still relevant)
  Authority: Informal — draft page, never signed off
  Recommendation: read for historical context but verify against current regulation
- "[System] Architecture Overview" ([PAGE-ID-2])
  Last updated: May 2026 — CURRENT
  Author: [Tech Lead]
  Authority: Authoritative — linked from architecture hub
  Recommendation: read in full
- "[Initiative] Implementation Notes (draft)" ([PAGE-ID-3])
  Last updated: Apr 2026
  Author: AI-generated per page header, no human verifier listed
  Authority: UNVERIFIED AI CONTENT
  Recommendation: DO NOT treat as authoritative — ask the team who reviewed it

Jira (2 results)
- PROJ-001 "[Feature X] epic" — status: Closed, Sept 2025 (potentially stale)
- PROJ-002 "[Initiative] impact analysis" — status: In Progress, opened Apr 2026

External sources found:

Web (5 results)
- RBA "Review of Card Payments Regulation" final report (rba.gov.au, Mar 2026) — authoritative
- AusPayNet response to RBA consultation (Apr 2026) — authoritative
- News: "Retail bodies welcome surcharge ban" (Apr 2026) — informational only
- ...
```

Then present an `AskQuestion`:

> Which sources should I read in detail before continuing intake?
> [Read all current/authoritative sources] [Read only the Confluence + Jira items I marked authoritative] [Skip — I'll tell you what's relevant] [Verify the AI-generated content first by asking the team]

### Regulator gate (mandatory)

If the work touches a regulator or regulatory framework — RBA, AUSTRAC, APRA, ACCC, ASIC, OAIC, ATO, AusPayNet, AML/CTF, Privacy Act / APP, CDR, PCI DSS, GDPR, PSD2/PSD3, CCPA, or generic cues like "surcharge ban", "interchange reform", "compliance deadline" — **web search is mandatory regardless of complexity.**

Always read the regulator's own publication directly. Internal Confluence summaries are secondary evidence, never primary. Surface the regulator source to the user separately from internal sources, with a recency check. If WebSearch isn't available, block intake — don't proceed past source vetting without acknowledgement that the external view is missing.

### AI source verification (mandatory)

For every source flagged as "unverified AI content", verify every Confluence/Jira ID it cites returns 200 OK (use `getConfluencePage` / `getJiraIssue`) before quoting any claim. Record the result in `confluence-pages.json` under the source's entry.

- If any cited ID is 404 → the source has fabricated references and CANNOT be trusted for any claim. Flag the whole source as untrusted; default recommendation is "ignore entirely".
- If all cited IDs verify → downgrade to "AI-assisted, references verified" and use sparingly with citation back to the verified primary source.

### Skip-acknowledgement

At the end of source vetting, tell the user what was searched and what was skipped, and why. A skipped source must be acknowledged, not silent. One line per source category is enough.

### When MCP or Glean is unavailable

If a tool is not connected or authentication fails, **degrade gracefully**:

- Confluence / Jira MCP missing → tell the user, ask if they have key page URLs or epic keys to share manually.
- Glean missing → skip those sources, note in the findings report ("Glean not available — couldn't search Slack / enterprise docs").
- WebSearch missing → skip, note the gap.

Never silently skip a source. The user must always see what was searched and
what wasn't.

---

## Workspace setup

At the start of intake (step 1), confirm workspace context. Batch related questions into one or two `AskQuestion` panels rather than 8 sequential questions — the user is filling in a form, not being interviewed.

Capture:

- **Jira project key** — e.g. PROJ, TEAM
- **Jira template story** (optional) — paste a key (e.g. `PROJ-XXXX`) to use its structure as the template for new stories, or "use most recent" to pick the project's latest, or "skip" (ask again at Delivery Definition). Stored as `initiative.jiraTemplateKey`.
- **Confluence space + parent page** — record page IDs in `confluence-pages.json`
- **All-in-one / intake doc link** — Confluence URL, PM brief, BRD, PRD, or pasted text
- **Repositories** — if technical
- **Slack / Teams channel** — where initiative comms happen
- **Source of the intake** — verbal / all-in-one doc / Confluence / BRD / Jira ticket
- **Stakeholders already involved** — who's been engaged, where the conversations are captured

If the user only knows half the answers, leave blanks and log gaps as unknowns in the tracker.

Cache the workspace context so every subsequent skill can write Jira / Confluence / Slack outputs without re-asking.

### Confluence hierarchy mapping (mandatory at Phase 0)

If the initiative has an existing Confluence space or hub page:

1. **Query the hierarchy** — use `getConfluencePageDescendants` to map all existing child pages under the initiative hub
2. **Create `confluence-pages.json`** — record every page with its `pageId`, `parentPageId`, `title`, and `url`. Include feature parent pages and analysis hub pages.
3. **Define parent rules** — document in `SESSION-CONTEXT.md` which parent page new pages should be created under (e.g., "Feature B pages → parent = `<id>`"). This prevents pages being created under the wrong parent.
4. **Record in SESSION-CONTEXT.md** — add the full page hierarchy table so every session starts with correct Confluence structure.

This prevents the common pattern of pages being created ad-hoc under wrong parents, requiring later audits and moves.

## Tasks

Run these in order. The first two are about workspace setup and prior art before any user-facing conversation about the brief. The middle tasks form the visible intake conversation. The last few close out Phase 0.

1. **Workspace context** – Confirm Jira project, Confluence space + parent page, repos, Slack channel, intake doc link, Jira template story (optional). Cache for all subsequent skills. Batch as one or two `AskQuestion` panels.
2. **Multi-source context gathering** – Search Confluence, Jira, Glean (enterprise + code), and the web for existing context. Vet every source for freshness, AI-generated content, and authority. Apply the regulator gate, AI source verification, and skip-acknowledgement (see sections above). Ask the user which sources to read in full.
3. **Confirm complexity** – Now that sources are known, present a complexity `AskQuestion` (Lean / Standard / Full) with the source-vetting findings visible. If the regulator gate fired, Lean is unavailable.
4. **Context extraction** – Summarise the PM's all-in-one or early brief: problem, objective, proposed success metrics, high-level scope, stakeholders, deadlines, constraints. Translate into a concise summary suitable for kickoff. Pull in anything relevant found in step 2.
5. **Interrogate the problem statement** – Invoke Requirements Interrogator in Discovery mode. One good question at a time. Surface: who experiences the problem, what does it cost them, how are they dealing with it today, what would change without it. Output → provisional problem statement marked "draft — pending PM approval".
6. **Interrogate success metrics** – Invoke Requirements Interrogator in Discovery mode. Surface: what behaviour changes if this works, how would we know, what data already exists, what's the smallest measurable signal. Output → provisional metric statement(s) marked "draft — pending PM approval".
7. **Scope slicing light pass** – Invoke `ba-feature-slicing-and-sequencing` in *intake light pass mode*. Surface 2-3 candidate slice axes (by workstream / by cohort / by feature) with rationale + trade-offs + recommendation. Get user co-shaping via `AskQuestion`. Output → `status-data.json → initiative.intakeLightSlices` and a Decision row in the tracker. Strict scope: light pass only — no full slice register, no sequencing plan, no MoSCoW matrix (those are Phase 3). Lean intakes skip.
8. **Questions for PM** – For everything *other than* problem, success metrics, and slicing axes (stakeholders, deadlines, constraints, untested claims from source material, missing baselines), build the `questions-for-pm.md` list per the Output Guidelines template. Put each question to the user in chat — they may have the answer informally from the PM (capture with verbal provenance), or it goes on the list for the PM-BA alignment meeting.
9. **Scope and out-of-scope exploration** – Challenge proposed scope: what's in, what's out, what dependencies on other teams or systems exist, where might scope creep occur.
10. **Early RAID identification** – Highlight obvious Risks, Assumptions, Issues, and Dependencies. Record in preliminary RAID log (handed to Risk & Tracker skill). Decisions table format: `ID | Decision | Owner / Made by | Date | Status`.
11. **Auto-generate canvas + HTML snapshot** – Invoke Project Canvas to generate the initial 8-tab canvas + `status-snapshot.html`. Canvas displays a "DRAFT — PENDING PM APPROVAL" banner on every tab until PM sign-off is recorded. Tabs will be sparse at this stage — that's expected. Tell the user: *"Canvas generated at `<path>`. It's mostly empty-state at this point — it will fill in as we work through the phases. All v1 outputs are marked draft pending PM approval."*
12. **Prepare kickoff agenda items** – Suggest agenda points and questions for the stakeholder kickoff meeting based on gaps identified. Hand to Kickoff Preparation skill.
13. **Phase 0 exit gate** – Present the intake summary table + draft RAID + confidence scores + canvas link + `questions-for-pm.md`. Confirm PM name and capture approval status in `status-data.json → initiative.pmApproval`. Make the approval state visible everywhere v1 outputs appear (canvas banner, project hub, status page). End with `AskQuestion`: proceed to Phase 1 / request PM review now (draft message) / refine problem statement / refine success metrics / pull more context first. Never auto-advance.

## Typical Questions to Ask

- What problem are we solving and who experiences it?  Why is it important now?
- What measurable outcome would indicate success (e.g., KPIs, targets)?
- What is the proposed high‑level scope?  What features or processes are in scope?  What is explicitly out of scope?
- Who are the key stakeholders (PM, sponsors, compliance, legal, design, operations, engineering)?
- Are there any fixed deadlines or regulatory dates?
- What known constraints (budget, resourcing, policy) exist?
- Have any assumptions been made about compliance, design, or technical feasibility?
- Are there known risks or dependencies already?

## Output Guidelines

The Intake Reviewer should produce:

- **Intake summary table** – A concise table capturing problem, objective, success metrics, high‑level scope, stakeholders, deadlines, constraints, assumptions, and initial RAID items. Clear labels and short phrases rather than long paragraphs.
- **`questions-for-pm.md`** – A structured list of questions for the PM that surfaced during source reading and interrogation. This is a primary Phase 0 output, not a side artefact. Goal: a pre-D1 PM-BA alignment meeting with this list as the agenda.
- **Kickoff agenda suggestions** – A short agenda outline for the first stakeholder meeting, highlighting key alignment points and decisions that need to be made early.
- **Preliminary RAID log** – A draft list of risks, assumptions, issues, and dependencies identified during intake. Pass this to the Risk & Tracker skill for ongoing management.

### `questions-for-pm.md` template

```markdown
# Questions for PM — [Initiative name]

Generated during Phase 0 intake by [BA name]. To be reviewed with [PM name] before D1 kickoff.

Each question came from one of: source critique (reading a Confluence page / Jira ticket / regulator doc surfaced an assumption or untested claim); interrogation (drafting problem statement / metrics / scope generated a question the BA couldn't answer alone); stakeholder gap (a stakeholder mentioned in sources but not yet engaged).

Status legend: `informal` = PM answered verbally (provenance captured) · `open` = needs PM input · `blocked` = can't progress past intake without this.

| ID | Question | Source / Trigger | Status | PM answer (if informal) | Provenance |
|---|---|---|---|---|---|
| Q-01 | [question] | [source] | open / informal / blocked | [verbal answer if any] | [date + how heard] |

**Pre-D1 alignment recommendation:** [30 / 45 / 60 min] meeting between PM and BA before D1 kickoff with these questions as the agenda.
```

## Challenge Rules

The Intake Reviewer challenges vague or unjustified statements immediately but does not deep‑dive into discovery.  When something is unclear:

- State the ambiguity succinctly and propose a clarifying question.
- If an assumption is unstated, call it out: “It seems we’re assuming X.  Should we validate that?”
- Highlight potential scope creep if the PM’s description is broad or unspecific.  Suggest clearly defining what is out of scope.
- Do not block progress; simply capture questions and assumptions and proceed to kickoff preparation.

