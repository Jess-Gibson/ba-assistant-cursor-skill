# Skill: Current State Assessment

## Description

The Current State Assessment skill builds a deep, evidence-based understanding of how things work **today** — across process, system, data, people, customer journey, pain points, compliance, and tribal knowledge — **before** any requirements extraction or solution shaping happens. It triangulates across code, documentation, people, and data to surface the real picture, including where sources disagree and where knowledge only lives in people's heads.

This skill exists because "current state" is one of the most under-invested phases of analysis. Teams jump from a vague problem statement straight to solutions without understanding what's actually happening today, and miss workarounds, edge cases, compliance gaps, and tribal knowledge that the solution will collide with later.

## When to invoke

- **At the start of Phase 2 (Discovery & Requirements)** — before any requirement extraction begins, unless the current state is already documented and verified.
- **When the user explicitly asks** — "map the current state", "what's happening today", "let's understand how this works now", "I need to assess the current state before we design anything".
- **When Discovery & Requirements encounters a gap** that requires understanding existing behaviour to resolve.
- **When solutioning is happening prematurely** — Anti-Pattern Detector should flag this and trigger Current State Assessment before solution work continues.

## Mandatory hooks

| # | Hook | What it does | Skill invoked |
|---|---|---|---|
| 1 | **Visual outputs** | Every assessment ends with at least one Mermaid diagram per relevant lens (process, system, data flow, journey, pain heatmap). | `ba-visual-storytelling` |
| 2 | **Data analysis handoff** | Any quantitative slice (volumes, failure rates, latency, error counts) is delegated to the data analyst skill, not duplicated here. | `pm-data-analyst` |
| 3 | **Stakeholder identification** | Use Stakeholder Strategy to identify who must be interviewed or invited to workshops. | `ba-stakeholder-strategy` |
| 4 | **Code exploration** | When the initiative is technical, use Glean code search to understand existing implementations before relying on docs alone. | Glean `code-exploration` |
| 5 | **Source skepticism** | Apply the source vetting principles from `ba-intake-reviewer` to every source read. Flag stale, AI-generated, or unverified content. | — (inherit from intake-reviewer) |

If hook 1 or 2 is skipped, the Anti-Pattern Detector flags it.

## Source skepticism stance

This skill inherits the source vetting principles from `ba-intake-reviewer`. Every source — Confluence page, runbook, system diagram, vendor doc, Glean result, person's recollection — is vetted before it informs the current state picture.

Default stance: **skeptical, not credulous.** Documents are often stale. People's recollections are often partial. Code is the source of truth for "what the system does" but not for "how the business actually uses it." Triangulate before declaring anything as fact.

## Lenses of current state (pick the relevant ones — not all every time)

Different initiatives need different lenses. Pick deliberately based on what the initiative needs. A regulatory change probably needs compliance + process + data lenses heavily. A technical migration needs system + data + code lenses. Customer-facing changes need journey + pain points.

| Lens | What it answers | Typical artefacts |
|---|---|---|
| **Process** | How does the work actually happen end-to-end today? Who does what when? What's the happy path vs the exception path? | BPMN-style or simplified Mermaid flowchart, swimlane diagram |
| **System** | What services/applications are involved? How do they connect? What are the integration points? Where does data come from and go to? | Mermaid architecture diagram, sequence diagram for key flows |
| **Data** | What data exists, where does it live, who owns it, what's the flow, what's the quality, what's the volume? | Mermaid ER diagram, data flow diagram, data quality summary table |
| **People** | Who does what? What's manual vs automated? Where are the workarounds? Who has the knowledge? Who's the single point of failure? | RACI table, "day in the life" narrative |
| **Customer journey** | What does the customer experience today, end-to-end? What are the touchpoints, decisions, drop-offs, frustrations? | Mermaid journey diagram, customer touchpoint map |
| **Pain points** | Where does it break, what's slow, what's expensive, what's risky, what gets escalated? | Pain heatmap table (frequency × severity), incident summary |
| **Compliance / risk** | What controls exist, what's the audit trail, where are the gaps, what's the risk appetite, what's regulated? | Control mapping table, regulatory obligation list |
| **Tribal knowledge** | What lives only in someone's head and isn't documented anywhere? Who has it? What's the bus factor? | Tribal knowledge register (knowledge item → owner → bus factor → documentation gap) |

## Source triangulation principles

A strong current state assessment never trusts a single source. For every claim about current state, triangulate across:

| Source | What it tells you | What it doesn't tell you |
|---|---|---|
| **Code** | What the system technically does. Source of truth for behaviour. | How the business uses it. What's documented as intended vs what's actually used. What workarounds exist outside the system. |
| **Documentation** | What the system was intended to do. What the team thinks happens. | Whether the docs are current. Whether actual behaviour matches. What changed and wasn't updated. |
| **People** | What actually happens in practice. Workarounds. Edge cases. Pain. | Comprehensive coverage (people remember some things, forget others). Objective fact. Recent changes they weren't part of. |
| **Data** | Volumes, frequencies, failure rates, patterns. Source of truth for "what really happens at scale." | Why things happen. Who decided what. Process intent. |

**Where sources disagree is where the truth lives.** Surface disagreements explicitly. Don't smooth them over — they're often pointing at a gap, a workaround, or a hidden requirement.

## Tasks

Run these in order. Phase 2 of an initiative begins with these tasks before requirement extraction.

1. **Scope the assessment** — Which lenses are relevant? Don't run all eight by default. Confirm scope with the user via `AskQuestion`. Output: list of lenses + reasoning.

2. **Inventory existing sources** — Use Confluence MCP, Jira MCP, Glean enterprise, Glean code, and any prior current state docs to find what's already documented. Apply source vetting (freshness, AI-flag, authority). Hand stale or AI-generated sources to the user with explicit "treat with caution" flags.

3. **Plan source triangulation** — For each lens, identify the code, docs, people, and data sources to consult. Note where you're relying on a single source (risk flag).

4. **Code exploration** (if technical) — Use Glean `code-exploration` to find the relevant repos, services, and key flows. Read enough to confirm or challenge what the docs say. Note discrepancies.

5. **People interviews and workshops** — Use the Workshop crafting section below to design specific interventions when knowledge lives in people's heads. Don't default to "send a survey" — workshops are usually higher fidelity for tribal knowledge.

6. **Data slice handoff** — Any volume, failure rate, latency, or quality metric is delegated to `pm-data-analyst`. Provide the query intent; let the data analyst skill produce the actual query and analysis.

7. **Build the current state picture per lens** — For each lens in scope, produce a narrative + at least one diagram (Mermaid). Highlight pain points and tribal knowledge gaps inline.

8. **Identify gaps and disagreements** — Where do sources disagree? Where do docs not match reality? Where is tribal knowledge a bus factor risk? Where are compliance controls assumed but not verified? Log each as an open question or risk.

9. **Produce the Current State Report** — Structured artefact (see Output Guidelines below). Hand off to Discovery & Requirements so requirement extraction is grounded in actual current state.

10. **Update the living tracker** — Pain points → potential requirements (flag for Discovery). Tribal knowledge gaps → risks. Compliance assumptions → open questions. Disagreements between sources → open questions or assumptions.

11. **Auto-refresh the canvas** — Update the canvas with current state diagrams and pain heatmap (canvas auto-refreshes after major outputs per `ba-project-canvas` rules).

## Tribal knowledge extraction methods

When a current state lives mostly in people's heads, choose the right intervention based on how much is unknown, how many people hold the knowledge, and how distributed it is.

| Method | When to use | Effort |
|---|---|---|
| **1:1 interview** | Knowledge is concentrated in one or two people; depth matters more than breadth. | Low |
| **"Day in the life" narrative** | Operational process where the steps matter and the worker has the context. Get them to walk through a real recent day. | Low |
| **Process mapping workshop** | Multiple people contribute to the process; you need their collective view, not just one perspective. | Medium |
| **System theatre / role play** | Complex interactions across systems and humans; teams play roles to surface decisions and handoffs. | Medium |
| **Journey mapping workshop** | Customer experience needs to be understood across touchpoints and over time. | Medium |
| **"5 whys" / root cause workshop** | Pain points are well-known but the underlying cause isn't. | Low |
| **Asynchronous knowledge capture** | Knowledge is widely distributed; people are remote; depth less critical than breadth. | Low (per person), medium (total) |
| **Shadowing** | Process is hard to articulate; you need to observe to understand. | High |

For each method, the skill should produce a **specific intervention plan** — not a generic template. See Workshop crafting below.

## Workshop crafting

When invoked to design a workshop, produce a full plan that a BA could run without further design work. Output structure:

| Section | Content |
|---|---|
| **Objective** | What specific knowledge are we trying to extract? Stated as an outcome. |
| **Why this workshop, not a different method** | Brief rationale for choosing this method over interviews / async / shadowing. |
| **Attendees** | Named (where possible) or by role. Mandatory vs optional. Why each person is needed. |
| **Pre-read** | Material to send beforehand. Specific reading time estimate. |
| **Timed agenda** | Block-by-block with durations. Start → end. |
| **Activities** | Specific exercises with materials, instructions, and time per activity. Not "discuss the process" — "spend 15 minutes individually writing each step on a sticky note, then 20 minutes clustering them on the wall." |
| **Facilitation notes** | What to do if the conversation gets stuck. What to do if one person dominates. What to do if scope drifts. |
| **Output capture template** | What artefact the workshop produces. Who captures it. How it gets shared. |
| **Post-workshop actions** | What happens with the output. What gets fed back to attendees. What gets logged in the tracker. |

A workshop plan from this skill should be usable as-is, not require the BA to design the activities themselves.

## Output guidelines — Current State Report structure

The skill produces a single Current State Report at the end of the assessment. Structure:

1. **Summary** — 3-5 sentences: what we assessed, what we found, what's the headline.
2. **Scope of assessment** — Which lenses, why, what's out of scope.
3. **Sources consulted** — Table with source / type / freshness / authority / confidence. Includes flagged stale or AI-generated sources.
4. **Current state per lens** — One section per lens in scope. Each section contains: narrative (current state), Mermaid diagram, pain points (with severity + frequency), tribal knowledge gaps, open questions.
5. **Source triangulation summary** — Where sources agreed, where they disagreed, what we resolved, what's still unresolved.
6. **Pain heatmap** — Table: pain point / lens / severity / frequency / who's affected / evidence source. Sorted by impact.
7. **Tribal knowledge register** — Table: knowledge item / current owner / bus factor (1-5) / documentation gap / risk if owner unavailable.
8. **Compliance / risk picture** — Controls observed, controls assumed but not verified, gaps, regulatory obligations.
9. **Open questions and assumptions** — Logged for Discovery & Requirements to address.
10. **Recommended next steps** — Specific interventions to fill gaps (interviews to run, data to query, workshops to hold).

Output modes (per master instructions): `thinking`, `quick summary`, `confluence-ready`, `workshop plan`. Default to `confluence-ready` for the final report; offer `quick summary` for early drafts.

## Mandatory visual outputs

At least one Mermaid diagram per relevant lens. Use `ba-visual-storytelling` skill to invoke. Minimum set:

| Lens | Diagram |
|---|---|
| Process | Swimlane flowchart |
| System | Architecture diagram (boxes + arrows + integration points) |
| Data | Data flow diagram or simplified ER |
| Customer journey | Journey diagram |
| Pain points | Pain heatmap table (rendered as a styled table, not a chart) |

If a lens is in scope but no diagram is produced, flag it as incomplete.

## Challenge rules

The Current State Assessment must be rigorous without being exhausting:

- **Never present a single-source current state as fact.** If only one source informs a claim, say so explicitly.
- **Challenge stale documentation.** If a Confluence page hasn't been updated in 12+ months for a fast-moving system, surface it as caveat.
- **Resist solutioning.** If the user starts proposing solutions during current state work, gently park them: "log that for solution shaping — let's finish understanding what's there first."
- **Flag tribal knowledge as risk.** If a knowledge item has bus factor 1 (one person holds it), it goes in the risk register, not just the tribal knowledge register.
- **Don't over-scope.** Not every initiative needs all 8 lenses. Pick deliberately. Confirm scope upfront.
- **Surface disagreements rather than smoothing them.** If two stakeholders describe the same process differently, that's data, not noise. Capture both versions and the disagreement.

## Handoff to Discovery & Requirements

When the Current State Report is complete:

- Pain points → candidate requirements (flag for Discovery to interrogate via Requirements Interrogator)
- Tribal knowledge gaps → risks (flag for Risk & Tracker)
- Compliance assumptions → open questions for Discovery to validate with compliance/legal
- Source disagreements → open questions for Discovery to resolve through targeted interviews
- Recommended next steps → input for Discovery's interview plan and workshop plan

Discovery & Requirements should never have to map the current state itself — that work has been done. Discovery focuses on what's needed; Current State Assessment provides the what-we-have foundation.
