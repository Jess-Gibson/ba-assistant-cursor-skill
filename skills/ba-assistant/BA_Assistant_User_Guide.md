# BA Assistant — User Guide

*Updated: June 2026 — covers Wave 1 through Wave 7 changes.*

This guide introduces the **BA Assistant**, a multi-skill system for business analysts and product managers that takes an initiative from earliest conception through delivery and post-launch evaluation. Use it to orient yourself and others on how the system works, what to expect, and how to interact with it effectively.

---

## What changed recently

If you've used the BA Assistant before, here's what's new:

| Change | What it means for you |
|---|---|
| **Active workstreams** replace sequential phases | Workstreams (Intake through Eval & Retro) can run in parallel for different parts of an initiative — e.g. Feature A in Delivery while Feature B is still in Discovery. Single-feature initiatives still run linearly (backwards compatible). |
| **Scope navigator (Wave 3)** | Everything — modes, status, tracker, MoSCoW — can be scoped to `initiative`, `feature`, `cohort`, or `slice`. |
| **MoSCoW per scope (Wave 3)** | Must/Should/Could/Won't ratings for every requirement, per scope. Captured at Discovery; warn-and-flag gate at Delivery Definition before stories ship. |
| **Complexity signal at intake (Wave 3)** | Phase 0 asks whether the initiative is `lean`, `standard`, or `full`. Lean skips deep interrogation hooks and goes straight to scope + RAID. |
| **21 active skills (Wave 5)** | Was 20 in Wave 3 — State Validator added in Wave 5 for cross-document consistency checks. |
| **New skills (Wave 1)** | `Solution Evaluation` (post-launch), `Sponsor Engagement` (Standish #1 factor), `Change Strategy` (ADKAR), `Workshop Design`, `Meeting Debrief`. |
| **Hook contracts registry (Wave 3)** | `hook-contracts.md` documents every inter-skill call so the system stays maintainable. |
| **Jira template at intake (Wave 4)** | Phase 0 asks for a template Jira story; all future tickets follow that structure. |
| **Visible status headers (Wave 4 — enforced)** | Every hook now starts with `> Running: <skill>` so you always see what the assistant is doing. |
| **Form-style intake (Wave 4)** | Workspace setup batches related questions into one or two screens rather than 8 sequential asks. |
| **Intake form canvas (Wave 4)** | Interactive React canvas lets you fill intake fields visually; the assistant reads from it. |
| **Draft depth preference (Wave 4)** | At session start, choose `minimal`, `standard`, or `comprehensive` output volume — independent of initiative complexity. Override per artefact any time. |
| **Co-thinking protocol (Wave 4)** | At every interrogation moment the assistant surfaces what it knows, what it doesn't know, its recommendation, the trade-off, and asks your take — before producing any artefact. |
| **Canonical ownership & conflict resolution (Wave 5)** | Clear rules for which file owns which facts (tracker vs status-data.json vs SESSION-CONTEXT). When files disagree, canonical source wins automatically. |
| **State Validator skill (Wave 5)** | Cross-document consistency checks — detects drift between tracker, status-data.json, Jira, and Confluence. Runs silently on resume; on demand via `/validate-state`. |
| **Active learnings surfacing (Wave 6)** | Patterns from `learnings.md` surface automatically at key inflection points (new requirement, workstream transition, workshop design, etc.) — never blocking, always informational. |
| **Learnings lifecycle (Wave 6)** | Patterns tracked as `candidate` (1 initiative), `established` (2+), or `archived` (6+ months inactive). Established patterns trigger stronger warnings. |
| **Standards index (Wave 7)** | Artefact standards live in `references/` — every sub-skill produces outputs conforming to these standards. Anti-Pattern Detector flags non-conformant output. |
| **Scope label naming rule (Wave 5)** | Stakeholder-facing output uses real business context names ("Payment Gateway Migration"), never abstract BA codes ("Feature A"). Internal IDs stay in data models only. |
| **New commands** | `/metrics`, `/reanchor`, `/audit-standards`, `/validate-state`, `/wrap`, `/workboard` — see Commands section. |
| **First-run wizard (Wave 7)** | On first install, the assistant detects unconfigured `ba-profile.mdc` and guides you through setup — name, role, Jira/Confluence details, MCPs, domain docs. |
| **Fast-track mode (Wave 7)** | For time-critical initiatives (<2 weeks), activates lightweight checkpoints and parallel-track mode to maintain rigour at speed. |

---

## Why use the BA Assistant

The BA Assistant makes complex analysis work faster, clearer, and less stressful. It:

- Guides you through each workstream so you never wonder "what's next?"
- Surfaces unknowns, risks, assumptions, and dependencies without blocking progress
- Adapts to the size and complexity of the initiative — lean for small/clear, deep for large/uncertain
- Supports **dual-track** work — discovery and delivery can run in parallel for different features or cohorts
- Helps break work into independently valuable slices before epics and stories
- Tracks all moving parts (requirements, risks, decisions, actions, sign-offs) in a single living tracker, scoped by initiative/feature/cohort/slice
- Pushes for evidence-based decisions, validates assumptions, and ensures stories are genuinely ready before development
- Captures MoSCoW priority for every requirement per scope, and warns when a story is about to ship without one
- Drafts the actual human-facing communications you'd otherwise have to write
- Generates the visuals that make initiatives easier to communicate
- Closes the loop post-launch — measures actual vs expected outcomes (Solution Evaluation)
- Learns across initiatives — patterns identified on one initiative inform the next

---

## How it works

At the centre is the **BA Initiative Orchestrator**, which coordinates **21 active specialist skills**. The orchestrator asks focused questions, accepts partial answers, and organises responses into structured outputs. It never stops you from moving forward — it records missing inputs and suggests how to obtain them.

### The living tracker

The Assistant maintains a single living tracker. **Every item is scoped** (initiative / feature / cohort / slice):

- ✅ **Knowns** — facts and confirmed requirements
- ❓ **Unknowns** — information not yet obtained
- ⚠️ **Assumptions** — beliefs without evidence
- 🧨 **Risks** — events that could negatively impact the initiative
- 🚧 **Dependencies** — other teams, systems, or approvals required
- 📌 **Decisions** — choices made, with rationale, owner, date
- 🎯 **Actions (Wave 3 — first class)** — owner, due date, status, source meeting, age
- 🔍 **Validation items** — hypotheses or assumptions to test
- ⏳ **Deferred items** — tasks or slices deliberately postponed
- ✅ **Sign-offs** — artefacts and decisions that need approval

### Confidence scores

The Assistant tracks confidence (High / Medium / Low) across six areas:

- Problem clarity
- Requirements completeness
- Dependency awareness
- Compliance readiness
- Solution viability
- Definition of ready

These tell you where the initiative is strong and where more work is needed. They update as new information arrives.

### Visible status headers (Wave 4 — enforced)

Every time the orchestrator delegates to a sub-skill, you'll see a header like:

```
> Running: Intake Reviewer → extracting context, building living tracker
> Running: Requirements Interrogator (Discovery workstream) → problem statement
> Running: Project Canvas → generating initial 8-tab canvas + HTML snapshot
✓ Intake Reviewer complete — 3 unknowns logged, complexity = standard
```

This is the single biggest UX improvement for BAs new to coding-style interfaces. You always see what's running and when it's done.

---

## Commands

Slash commands trigger orchestrator-driven flows. Type the slash in chat; if Cursor's slash menu doesn't pick it up, just type the command word and the orchestrator will still respond.

| Command | What it does |
|---|---|
| `/next` | Top 3 next actions across all active workstreams and scopes, ranked by urgency, unblock potential, and critical-path criticality |
| `/status` | Full current state — workstream grid, feature status, critical path, blockers, living tracker, MoSCoW coverage, confidence scores. Triple-output: chat + canvas + HTML snapshot |
| `/publish-status` | Generate and publish the formal status page (Confluence + HTML snapshot) |
| `/report` | Full comprehensive report — all major outputs in a single document, ready to share |
| `/snapshot` | Living tracker snapshot — high-risk items, unresolved unknowns, what changed since last view |
| `/canvas` | Generate or refresh the interactive project canvas (8 tabs) |
| `/retro` | Trigger a retrospective — workstream-completion (quick), mid-initiative (deeper), or closure (comprehensive) |
| `/metrics` | Pull and display all four metrics with per-scope breakdown and trend. Quick check-in without the full status output |
| `/reanchor` | Re-read the orchestrator and active project state files. Use when a long thread has drifted — skills not firing, status headers missing, workstream model forgotten |
| `/audit-standards` | Run a conformance check against all reference standards across the live initiative. Reports artefacts that don't conform |
| `/validate-state` | Mid-session drift report (read-only). Diffs SESSION-CONTEXT vs tracker, checks status-data.json, flags stale Confluence pages, optional Jira delta. Offers fix options but does not auto-write |
| `/wrap` | End-of-session closeout. Runs `/validate-state` first, then promotes unpromoted items to tracker, refreshes workboard, suggests starting a new chat |
| `/workboard` | Cross-initiative priorities view. Shows all initiatives, top tasks, today's meetings, sync status |

**Note on Cursor slash menus:** Cursor doesn't currently offer Claude-style button prompts. The assistant uses `AskQuestion` with clickable options for every decision point, which is the closest equivalent. Slash commands may or may not appear in the autocomplete menu — typing the command word in chat always works because the orchestrator honours them. See `slash-commands-ux.md` for documented patterns.

---

## Active workstreams (replaces sequential phases)

Instead of a strict 0 → 6 phase sequence, the Assistant treats each phase as an **active workstream** that can run for any scope (initiative, feature, cohort, slice). The concept has had three names — "Phases" originally, "Modes" in Wave 3, **"Workstreams"** now. All three are the same thing; the user-facing UI uses the friendly workstream name, and internal data models keep the `M0`–`M8` codes as precise cross-references.

| Workstream (what you'll see) | Internal code | Scope | What it does |
|---|---|---|---|
| **Intake** | M0 | Initiative | PM brief, complexity signal, workspace setup, initial RAID, canvas init |
| **Kickoff** | M1 | Initiative or feature | Workshop design, D1 kickoff, sponsor alignment |
| **Discovery** | M2 | Initiative / feature / cohort | Current state, requirements (MoSCoW per scope), experiments, validation |
| (within Discovery) Current State Assessment | M2a | Feature / cohort | Evidence-based "as-is" — diagrams, code dives, source vetting, workshops |
| **Slicing & Sequencing** | M3 | Initiative | Slice into independently valuable pieces; critical path; impact mapping |
| **Solution** | M4 | Feature / cohort | Future state, options, ADRs, schema-field validation, JTBD lens |
| **Delivery** | M5 | Feature / cohort / slice | Epics, stories, spikes, DoR, **MoSCoW warn-and-flag gate** |
| **Playback** | M6 | Initiative or feature | Sign-offs, training, comms drafting, change strategy execution |
| **Eval & Retro** | M7 + retro | Feature / scope-aware | Post-launch evaluation + workstream-completion / mid-initiative / closure retros |
| **Change** | M8 | Initiative (sustained) | Change strategy execution across the org |

Workstream states: **🟢 Done** / **🔵 Active** / **⏸ Paused** / **○ Not started** / **· N/A**. In-progress is always shown in **blue** (never amber or brown).

**Backwards compatible:** if your initiative is single-scope and linear (one feature, one cohort), workstreams run in the old sequential order. You won't notice the change. Dual-track teams benefit from running Discovery on Feature B while Delivery is active on Feature A.

**Workstream-aware anti-patterns:** the Anti-Pattern Detector watches for things like Solution active without Discovery complete for the same scope, Delivery active across 3+ scopes without resource declaration, customer change with no change plan, and late discovery.

---

## Project Canvas (`/canvas`)

The **Project Canvas** is an interactive dashboard that opens beside the chat in Cursor. It gives you a visual, tabbed overview of your initiative's state — no scrolling through long markdown trackers.

### Scope navigator (Wave 3)

Above the tabs is a scope navigator: choose `Initiative`, `Feature: <name>`, `Cohort: <name>`, or `Slice: <name>`. Every tab filters to that scope. Switch scope to drill in or zoom out.

### What it shows (8 tabs)

| Tab | What's in it |
|---|---|
| **Overview** | Stage, workstream strip, stakeholder-readable stats (days to deadline / features on track / blockers / decisions confirmed), "where we are right now" narrative, top blockers grid, where each scope is, confidence table |
| **Workstreams** | SVG grid — scopes (rows, cohorts indented under their feature) vs the 8 workstreams (Intake → Eval & Retro). Cells coloured by state (🟢 Done / 🔵 Active / ⏸ Paused / ○ Not started / · N/A). Compact horizontal legend below + recent workstream changes log |
| **Features & Delivery** | Feature status table with active workstreams, Jira tickets with MoSCoW column, MoSCoW priority matrix per cohort |
| **Timeline** | Swimlane Gantt — bars per workstream, milestones, dependencies, today marker |
| **Dependencies** | Interactive visual graph — click any node to highlight its upstream and downstream chain |
| **Traceability** | Interactive requirement → slice → story → ADR flow; requirements show MoSCoW pills |
| **Critical Path & Actions** | Milestone table, this-week actions, key dependencies, MoSCoW warnings for unrated stories |
| **RAID & Tracker** | Decisions table, risks, open questions, assumptions, **action register**, MoSCoW warnings — filterable by scope |

### How it works

The canvas gathers context from your project's blueprint folder (`SESSION-CONTEXT.md`, `initiative-tracker.md`, solution options, `status-data.json`), plus Jira and Confluence if available. All data is embedded directly in the canvas file — no external calls at runtime.

### When it generates

- When you run `/canvas` (explicit)
- When you run `/status` or `/publish-status` (canvas refreshes alongside)
- After Phase 0 intake (auto-generated, sparse at this stage — that's expected)
- After any workstream completion gate (auto-refresh)
- When you first use the BA Assistant on an existing project

### Self-bootstrapping

You don't need to have used the BA Assistant before. The canvas skill asks what sources exist and gathers from whatever's available — repo files, Jira, Confluence, or just what you tell it. It adapts to your project's maturity: early-stage projects will have sparser tabs with prompts explaining what to add next.

### Opening the canvas

Canvas files are saved as `.canvas.tsx` in the `canvases/` folder of your workspace project. To view them interactively:

1. Open Cursor Command Palette (Cmd/Ctrl+Shift+P)
2. Search "Cursor: Open Canvas"
3. Select the canvas from the list

Or click the "Canvases" icon in the sidebar. The canvas opens as a live interactive panel beside the chat, with clickable tabs, multi-select feature filters, interactive graphs, and collapsible sections.

---

## Intake — what to expect (Wave 1–4)

### Complexity signal (Wave 3 — Phase 0 opener)

Before deep intake, the assistant asks: **is this lean, standard, or full?**

| Level | Use when | Intake depth |
|---|---|---|
| **Lean** | Small enhancement, well-understood, clear scope | Skips deep problem and metric interrogation; goes straight to scope + RAID + go |
| **Standard** | Most initiatives — moderately complex | Runs full intake conversation; conditional Sponsor Engagement, Current State Assessment, Workshop Design |
| **Full** | Large, ambiguous, multi-team, regulatory | Full intake + mandatory Sponsor Engagement + Current State Assessment + Workshop Design |

You can override mid-flight if the initiative turns out to be more or less complex than first thought.

### Form-style workspace setup (Wave 4)

The assistant batches workspace context questions into one or two screens (rather than 8 sequential prompts):

**Screen 1 — Workspace IDs:**
- Jira project key
- Confluence space + parent page link
- All-in-one / intake doc link (or "I'll paste it")
- Slack / Teams channel

**Screen 2 — Templates and context:**
- **Jira template story (Wave 4 — new)** — paste a key, "use most recent", or skip
- Repositories in scope
- Source of intake
- Stakeholders already involved

Leave fields blank if you don't know — gaps are logged as unknowns.

### Multi-source context gathering (Wave 2)

Hook 2 searches Confluence, Jira, Glean (enterprise + code), and the web for existing context. Every source is vetted for freshness, AI-generated content, and authority. You get a report with confidence signals and choose which sources to read in full.

### Intake form canvas (Wave 4 — optional)

For BAs who prefer a visual form to chat-style intake, the assistant can generate an **interactive intake form canvas** — a React panel with input fields for every intake item. Fill it in, save, and the assistant reads from the saved JSON. See `intake-form.canvas.tsx` example in the canvas templates.

---

## Output modes

When generating long outputs, the Assistant tailors the format:

- **Thinking mode** — conversational explanation of the situation and reasoning. Useful for brainstorming or coaching.
- **Quick summary** — concise bullet snapshot of current state and next steps.
- **Confluence-ready** — polished, table-driven document ready to paste into Confluence or share with stakeholders.
- **Workshop plan** — structured agenda and activity list for facilitating group sessions.

Specify your preference: `/report quick summary`, `/report confluence-ready`, etc. Default is structured output.

---

## Skills (21 active)

You don't need to invoke skills by name — the orchestrator calls them as needed. But it helps to know what's available. **Skills marked "(merged in)" are sections within a host skill, not standalone files.**

### Core workflow skills (workstream-driven)

| Skill | Workstream | Purpose |
|---|---|---|
| `Intake_Reviewer` | Intake (M0) | PM brief, complexity signal, workspace setup, multi-source context, JTBD-tagged problem |
| `Workshop_Design` *(absorbs Kickoff Preparation)* | Kickoff (M1) | Workshop facilitation, kickoff agendas, group sessions |
| `Discovery_and_Requirements` | Discovery (M2) | Current state, requirements with MoSCoW matrix per scope, **(merged in: Experiment & Validation)** |
| `Current_State_Assessment` | Discovery (M2a) | Evidence-based "as-is" — diagrams, code dives, source vetting, workshops |
| `Feature_Slicing_and_Sequencing` | Slicing & Sequencing (M3) | Independently valuable slices, dependency diagram, **(merged in: Critical Path & Priority)**, impact mapping |
| `Solution_Shaping` | Solution (M4) | Future state, options, ADRs, JTBD-segmented (functional/emotional/social) |
| `Story_Writing` *(absorbs Delivery Definition, Definition of Ready)* | Delivery (M5) | Epics, stories, spikes, AC, **(merged in: Definition of Ready)**, **MoSCoW warn-and-flag gate** |
| `Playback_and_Enablement` | Playback (M6) | Sign-offs, training, **(merged in: Communication Drafter)** |
| `Solution_Evaluation` *(NEW Wave 1)* | Eval & Retro (M7) | Post-launch — measure actual vs expected outcomes; continue/adjust/sunset |
| `Retrospective_and_Learning` | Eval & Retro (retro half) | Workstream-completion / mid-initiative / closure retros; updates `learnings.md` |

### Sustained-relationship skills (NEW Wave 1)

| Skill | Purpose |
|---|---|
| `Sponsor_Engagement` | Sustains the executive sponsor relationship (Standish CHAOS #1 success factor) |
| `Change_Strategy` | Manages organisational change using ADKAR (Awareness, Desire, Knowledge, Ability, Reinforcement) |

### Cross-cutting skills (run in support)

| Skill | Purpose |
|---|---|
| `Risk_and_Tracker` | Maintains the living tracker (scoped, with action register), progress dashboard |
| `Stakeholder_Strategy` | Identifies, analyses, and engages stakeholders; produces RACI |
| `Requirements_Interrogator` | Three modes: Discovery, Rethink, In-flight — with JTBD lens |
| `Meeting_Debrief` *(NEW Wave 1)* | Processes meeting transcripts/notes; updates tracker, requirements, OQs, actions |
| `State_Validator` *(NEW Wave 5)* | Cross-document consistency checks — detects drift between tracker, status-data.json, Jira, and Confluence. Runs silently on resume; on demand via `/validate-state` |

### Passive skills (run continuously)

| Skill | What it watches for |
|---|---|
| `Anti_Pattern_Detector` | Premature solutioning, skipped slicing, missing stakeholders, missing MoSCoW, workstream-aware combinations (Solution active without Discovery complete, Delivery across 3+ scopes without resource declaration, late discovery, workstream thrashing), dormant learnings (Wave 6), non-conformant artefact output (Wave 7) |
| `Schema_Field_Validator` | Triggered when a data model field is proposed — checks if it belongs |
| `Context_Capture` | Scans every user message for new facts, decisions, blockers, OQs, scope changes, stakeholder context, and corrections. Writes to `SESSION-CONTEXT.md` in real time with an inline `📝` confirmation. Does not interrupt conversation flow. |

### Support skills (invoked by other skills)

| Skill | Produces |
|---|---|
| `Visual_Storytelling` | Diagrams, charts, one-pagers, dashboards, journey maps |
| `Project_Canvas` *(now hosts Status Data Model)* | Interactive 8-tab canvas + `status-data.json` schema + HTML snapshot |
| `Jira_Sync` | Read/write Jira tickets; respects template captured at intake |

### Skills that were merged (Wave 3) — no functionality lost

| Was standalone | Now inside | Why |
|---|---|---|
| `Kickoff_Preparation` | `Workshop_Design` | Kickoff is a workshop |
| `Critical_Path_and_Priority` | `Feature_Slicing_and_Sequencing` | Same job, two angles |
| `Definition_of_Ready` | `Story_Writing` | DoR is a quality gate inside delivery |
| `Status_Data_Model` | `Project_Canvas` | Data model is canvas infrastructure |
| `Experiment_and_Validation` | `Discovery_and_Requirements` | Experiments validate requirements |
| `Communication_Drafter` | `Playback_and_Enablement` | Comms is cross-cutting; placed under most-frequent caller |

---

## MoSCoW per scope (Wave 3)

Every requirement gets a MoSCoW rating per scope (initiative / feature / cohort / slice). A single requirement can be `Must` for cohort A and `Could` for cohort B. The matrix is captured at Discovery & Requirements.

**The warn-and-flag gate (at Story Writing):**

Before a Jira story ships, the assistant checks: does this story have a MoSCoW rating for its scope? If not:

- `/status` shows a MoSCoW warning
- `/next` includes "Capture MoSCoW for stories X, Y, Z"
- A draft message is queued to the PM asking for ratings
- The story can still ship if the PM overrides — but the override is logged in the tracker

This is **warn-and-flag, not hard block** — it doesn't stop rolling cohorts or fast-moving teams, but it never lets MoSCoW silently fall off the radar.

---

## Draft depth preference (Wave 4)

At the start of every session, the assistant asks how much output you want by default:

| Level | What you get | Best for |
|---|---|---|
| **Minimal** | Sketches, outlines, candidate options. The assistant asks before producing any full artefact. | Early-stage thinking, brainstorming, co-shaping |
| **Standard** *(default)* | Reasonable artefacts at each step, declared upfront with selection before drafting. | Most sessions |
| **Comprehensive** | Full artefacts at every step unless you say otherwise. | Confident in direction, want everything generated up front |

Draft depth is independent of initiative complexity — complexity controls how deep *intake* goes; draft depth controls how much *output* each skill produces. Override per artefact any time by saying so in chat.

---

## Co-thinking protocol (Wave 4)

The assistant is a thinking partner, not a production line. At every interrogation moment — problem statement, success metric, requirement, decision, slice — it surfaces:

1. **What I know** — facts with evidence and sources
2. **What I don't know** — explicit knowledge gaps (in chat, not buried in draft text)
3. **My recommendation** — a clear take with reasoning
4. **The trade-off** — what's given up either way
5. **Ask your take** — clickable options including disagreement and free-text

The assistant iterates on your response **before** producing any artefact. Producing the artefact in the same turn as the first interrogation question is the failure mode this protocol prevents.

Before a skill drafts more than one artefact, it declares them:

```
What I'll produce next (Skill: <name>)

1. <artefact> — <purpose> — <size>
2. <artefact> — <purpose> — <size>

Selection: [Produce all] [Produce 1 only] [None — discuss first]
```

---

## Canonical ownership & conflict resolution (Wave 5)

Multiple state files track your initiative. Each owns specific facts:

| Fact type | Canonical source | Derived to |
|---|---|---|
| Narrative RAID (decisions, reasoning, evidence) | `initiative-tracker.md` | status-data.json, canvas RAID tab, status page |
| Structured decisions (ID, owner, date) | `status-data.json` (synced from tracker) | canvas, status page |
| Ticket statuses | `status-data.json` (synced from Jira) | canvas, status page |
| Workstream states (per scope) | `status-data.json` | canvas, status page |
| Confidence scores | `status-data.json` | canvas, status page |
| Session-scoped notes (today's tentative decisions) | `SESSION-CONTEXT.md` | promoted to tracker at session end |
| Cross-initiative patterns | `learnings.md` | Anti-Pattern Detector watchlist |

**When files disagree:**

- **Tracker wins** for narrative facts (decisions, RAID, OQs, assumptions)
- **status-data.json wins** for machine-derived facts (Jira ticket statuses, workstream computation)
- **Most recently human-modified wins** for facts that could be either — the State Validator reports timestamps and asks you to confirm
- **SESSION-CONTEXT.md is never canonical** for facts that should outlive the session — at session end, decisions get promoted to the tracker

The **State Validator** (see Skills section) enforces consistency between these files and flags drift automatically.

---

## Active learnings surfacing (Wave 6)

A file called `learnings.md` persists across initiatives. Between intake and retros, the orchestrator now actively surfaces relevant patterns at key inflection points:

| Inflection | What surfaces |
|---|---|
| New requirement entering the register | Patterns about requirements, interrogation, or the requirement's domain |
| Workstream transitions to active | Patterns specific to that workstream (Discovery, Slicing, Delivery, etc.) |
| New stakeholder added | Stakeholder or engagement patterns |
| Spike created or assigned | Patterns about spikes (outcome capture, stalled spikes, scope creep) |
| Workshop being designed | Patterns about facilitation, attendance, debrief, Miro |
| Confluence page being published | Patterns about page hierarchy, supersede markers, status pages |
| Bulk file operation proposed | Patterns about sync, content review, currency checks |

**How it looks in chat:**

```
💡 **Learning from previous initiatives:** [one-line pattern]. [Application to current context]. [What I'll do unless you say otherwise]
```

Learnings never block — they are informational. The assistant picks the single most relevant pattern per inflection point. Say "skip the learning" if not relevant.

### Learnings lifecycle (Wave 6)

Each pattern has a lifecycle status:

| Status | Meaning | Behaviour |
|---|---|---|
| **Candidate** | Observed in 1 initiative | Warns but does not block |
| **Established** | Observed in 2+ initiatives | Blocks by default (override logged) |
| **Archived** | No activity in 6+ months | Skipped unless explicitly invoked |

Promotions and demotions happen automatically. The State Validator flags inconsistencies in the learnings file.

---

## Standards index (Wave 7)

Artefact standards live in `references/`. Sub-skills produce outputs conforming to these standards — workflow stays in sub-skills; output structure is owned by the standard.

| Standard | Owns format for | Used by |
|---|---|---|
| `visual-output-format.md` | Diagrams, interactive HTML, design system | Visual Storytelling, Project Canvas |
| `canvas-data-model.md` | status-data.json schema, canvas tabs, metrics | Project Canvas, all status-data writers |
| `user-story-format.md` | Stories, spikes, bugs, enablers, DoR checklist | Story Writing |
| `raid-format.md` | RAID, decisions, open questions | Risk & Tracker, Discovery & Requirements |
| `status-page-format.md` | Confluence status pages | Project Canvas (HTML snapshot) |
| `requirement-format.md` | Requirement register, MoSCoW matrix, JTBD | Discovery & Requirements |
| `jira-ticket-format.md` | Cross-cutting Jira write rules | Jira Sync, project-specific Jira skills |

The Anti-Pattern Detector flags non-conformant output. The State Validator cross-checks live artefacts against their standard at end-of-session.

---

## Scope label naming (Wave 5)

When the assistant produces stakeholder-facing text — `/status`, `/next`, status emails, playback materials — scope labels use **real business context names**, not abstract BA codes.

| Bad (BA jargon) | Good (real business context) |
|---|---|
| "Feature A is on track" | "Payment Gateway Migration is on track" |
| "Cohort B paused" | "Inactive Accounts paused until LEGAL-2" |

Internal IDs (`F-A`, `C-B`) appear only in data models and code — never in text you or your stakeholders read.

---

## Three behaviours worth knowing about

### Workspace setup (Phase 0)

Before doing deep work, the Assistant confirms (now as a form, Wave 4):

- Jira project + template story
- Confluence space + parent page
- All-in-one / intake doc link
- Slack / Teams channel
- Repos in scope
- Source of intake
- Stakeholders already involved

This prevents the Assistant from making assumptions later. If you skip workspace setup at the start, the Assistant will ask before any tool action.

### Self-critique on outputs

After every major output, the Assistant runs a quick self-critique:

- What am I assuming?
- What would a senior BA push back on?
- What's missing?

The critique is surfaced transparently — not hidden. You'll see lines like "*Self-critique: I'm assuming [Stakeholder Name] is the right decision-maker for ADR-01 — should we verify this?*"

### Cross-initiative learnings (enhanced Wave 6)

A file called `learnings.md` persists across initiatives. The Retrospective skill writes patterns, watchlist items, and skill refinements to it at retros. The Intake Reviewer reads it at the start of every new initiative. And since Wave 6, the orchestrator **actively surfaces** relevant patterns at key inflection points during work — see the "Active learnings surfacing" section above.

Each pattern carries a lifecycle status (`candidate` → `established` → `archived`) and an evidence log. Established patterns (confirmed across 2+ initiatives) trigger stronger warnings; candidates carry an advisory note. Archived patterns (6+ months inactive) are skipped unless explicitly invoked.

This means recurring failure modes get caught earlier and more frequently — not just at intake or retros, but in the moment when the pattern is about to repeat.

---

## How to work with the Assistant

1. **Provide context** — share the PM's all-in-one, existing documents, transcripts, or notes. More context = better guidance.
2. **Set your draft depth** — at session start, choose `minimal`, `standard`, or `comprehensive` output volume. Override per artefact any time.
3. **Use the form intake** — Wave 4 batches workspace setup questions; fill what you know, leave blanks for gaps.
4. **Answer honestly** — it's fine to say "I don't know" or "I need to ask compliance." The Assistant logs unknowns and suggests next steps.
5. **Use commands** — `/next` when stuck, `/status` for a live snapshot, `/report` for a full document, `/snapshot` for the tracker, `/validate-state` to check sync, `/wrap` to close out a session.
6. **Choose output modes** — specify `quick summary`, `confluence-ready`, `thinking`, or `workshop plan` when generating a summary or report.
7. **Switch scope** — on the canvas, drill into a feature or cohort to see only its workstreams, tracker, MoSCoW.
8. **Push back** — if the Assistant flags a risk or suggests an action, you can accept, question, or defer. If you proceed at risk, the decision is logged.
9. **Engage the co-thinking** — when the assistant surfaces what it knows, what it doesn't know, and its recommendation, give your take before it produces artefacts. This is where the best analysis happens.
10. **Iterate** — workstreams loop back. You can loop into discovery after slicing, update requirements during solution shaping, raise change tickets during delivery. The Assistant adapts.
11. **Drop meeting transcripts** — after meetings, paste the transcript; `Meeting_Debrief` extracts decisions, actions, OQs, and updates relevant skills/tracker.
12. **Ask for visuals** — "show me the dependency diagram", "make me a one-pager for this", "draft a stakeholder email." The Assistant produces them.
13. **Use `/reanchor` in long threads** — if the assistant feels like it's drifted or skills aren't firing, `/reanchor` re-reads all state files and resumes from the current position.
14. **Check cross-initiative priorities** — `/workboard` shows all initiatives, top tasks, today's meetings, and sync status in one view.

---

## Quality criteria — what good looks like

The Assistant measures the quality of its own outputs against:

| Measure | What it tells us |
|---|---|
| Idea → engineering start time | How fast the initiative moves from ambiguity to action |
| Rework rate after engineering starts | Whether requirements and stories changed mid-flight |
| Decision reversal rate | Quality of decisions made under uncertainty |
| Stakeholder surprise rate | Whether playbacks and check-ins are landing |
| Risk realisation rate | How many identified risks actually happened |
| Definition of ready hit rate | % of stories actually ready when picked up |
| MoSCoW coverage rate | % of requirements with a MoSCoW rating for their scope before story ship |
| Sign-off cycle time | How long sign-offs take from request to approval |
| Requirement interrogation rate | % of requirements challenged before being accepted into the register |
| Solution evaluation outcome | Post-launch: % of features measured against expected metrics |

These get surfaced in `/snapshot` and especially in `/retro` outputs.

---

## Tips for new BAs

- **Don't worry about having all the answers.** The Assistant handles incomplete information and prompts you when something is missing.
- **Think aloud.** When unsure, explain your reasoning. The Assistant uses your thought process to guide you.
- **Challenge yourself.** The Assistant will ask tough questions. Be honest if you don't know — it's better to log an assumption than to guess.
- **Use the critical path tracker.** Pay attention to long-lead items like compliance reviews, design, or external approvals. Start these early.
- **Slice before you write stories.** Always break into features first. This reduces risk and makes sequencing easier.
- **Validate assumptions.** Run experiments or POCs for assumptions that could make or break the solution. Experiment & Validation lives inside Discovery now.
- **Keep the tracker current.** Capture decisions, risks, assumptions, dependencies, and actions as they arise. This prevents surprises and supports clean handovers.
- **Trust the interrogator.** If a requirement seems obvious, that's exactly when Requirements Interrogator should run. Documentation captures what was written. Interrogation captures what was meant.
- **Use the JTBD lens.** "When [situation], I want to [motivation], so I can [outcome]" surfaces functional, emotional, and social dimensions that "user story" format alone misses.
- **Ask for visuals early.** A diagram surfaces dependencies that text hides.
- **Pay attention to surfaced learnings.** When the assistant says "Learning from previous initiatives...", it's drawing from real patterns — consider whether it applies before dismissing.
- **Run `/validate-state` when you're unsure.** It's read-only and fast — tells you if anything has drifted without changing anything.
- **Use `/wrap` at the end of every session.** It promotes tentative decisions to the tracker, catches unpromoted items, and suggests a fresh chat for the next task.

---

## When something has changed

Requirements and scope evolve. When they do:

- **A requirement has changed mid-flight?** Invoke Requirements Interrogator in Rethink mode (or In-flight mode if development has started). It surfaces the delta and identifies what's affected across PRD, Confluence, Jira, and code.
- **A pattern keeps appearing?** Invoke `/retro` mid-initiative. The Retrospective skill captures the pattern and updates the Anti-Pattern Detector's watchlist so future occurrences are caught earlier.
- **A stakeholder is surprised?** That's a signal Stakeholder Strategy and Playback need to be refreshed. Update the engagement plan.
- **A workstream completed for one scope but not another?** That's fine — that's dual-track. Just keep the workstream tracker honest. The canvas will show it visually.
- **Something feels out of sync?** Run `/validate-state` for a read-only drift report. It diffs SESSION-CONTEXT vs tracker, checks status-data.json, and flags stale Confluence pages. Run `/wrap` at the end of a session to fix all drift and close out cleanly.

The Assistant doesn't expect a clean linear flow. It expects change.

---

## In summary

The BA Assistant is a thinking partner, not a note-taker. It co-thinks with you at every interrogation point, structures your outputs to conform to defined standards, keeps you honest about what's known and unknown, validates its own state across files, supports dual-track delivery, and produces the artefacts that would otherwise eat your time — visuals, draft communications, ticket drafts, retrospectives, and post-launch evaluations.

It surfaces learnings from previous initiatives at the moment they're relevant, enforces ownership rules so files stay consistent, and catches its own anti-patterns before you have to.

Use it to work faster, communicate more clearly, make smarter decisions, and ship initiatives with fewer surprises downstream — and to learn from every initiative so the next one runs better.
