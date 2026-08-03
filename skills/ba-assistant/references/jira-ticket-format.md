# Jira Ticket Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/jira-ticket-format.md`
**Owner:** `jira-templates` skill (workflow and full format detail), this standard (positioning and high-level rules)
**Last reviewed:** 2026-05-30

This reference is a **positioning file**. The detailed format definition for PROJ Jira tickets  -  ADF panels, mandatory custom fields, canonical example issue IDs, panel type quick reference, verification considerations, full templates for Bug / Story / Spike  -  lives in the existing `jira-templates` skill (already structured as a separate top-level skill in `.cursor/skills/`).

This file exists to:
1. Make Jira format discoverable as part of the references index
2. Define the contract between `references/user-story-format.md` (the WHAT of a ticket) and `jira-templates` (the HOW for Jira specifically)
3. Capture cross-cutting rules that apply to any Jira write, independent of PROJ specifics

---

## 1. Layered ownership

Three layers, each owns something distinct:

| Layer | Owns | Lives in |
|---|---|---|
| **Content structure** | What sections a ticket has (Why, AC, Negative case, Scope, etc.) and how they're written | `references/user-story-format.md` |
| **Jira-specific rendering** | ADF panels, panel types, emoji headings, PROJ custom fields, canonical example IDs, panel layout for PROJ-4277 / PROJ-4275 | `jira-templates/SKILL.md` |
| **Workflow** | When to clarify, when to draft, when to create the ticket, the mandatory `AskQuestion` gate | `jira-templates/SKILL.md` |

The two files are read together when producing a Jira ticket. The story-format file is the source of truth for content; the Jira-templates file is the source of truth for how that content gets rendered into Jira-specific structures.

---

## 2. Hard rules (apply to ALL Jira writes)

Independent of project, type, or context.

### 2a. Mandatory clarification gate

Before calling `createJiraIssue` or any material `editJiraIssue` (changes to summary, description, or scope), the BA Assistant MUST run Cursor's `AskQuestion` tool in the same session, unless the user has already provided equivalent structured answers in the current thread.

This rule is non-negotiable. The Anti-Pattern Detector flags Jira writes that skipped clarification.

### 2b. Mirror the canonical example for structure

For every project that has canonical example tickets recorded (PROJ has examples for Bug, Story, Spike, Story with panels, dense Spike), the assistant reads the canonical example via `getJiraIssue` before drafting, and mirrors its structure  -  sections, panels, headings, custom fields. **Structure only, never content.**

For projects without recorded canonical examples, the assistant should produce the ticket against `references/user-story-format.md` and flag in the chat that no canonical Jira example was available.

### 2c. ADF format for writes with panels

When the ticket type requires coloured panels (PROJ Bug, Story, Spike), the write uses ADF (`contentFormat: "adf"`) with `panel` nodes. Markdown content format drops panels and is not acceptable as a shortcut.

If ADF JSON is large, build it in a UTF-8 `.json` file, parse, and pass the object to the MCP tool. Don't inline it as a string in the chat.

### 2d. Title format

`[Area] Imperative outcome`  -  short, specific, searchable. Independent of project.

Good: `[Onboarding] Reject Fiserv applications when phone format invalid`
Bad: `Bug in onboarding`, `Investigation needed`, `Fix the thing from yesterday`

### 2e. Stories describe the problem, not the solution

Stories are written from the **business perspective**. The BA Assistant does not make implementation, architecture, or technical design decisions  -  those belong to engineers and architects.

**What goes where:**

| Section | Written at | Contains |
|---|---|---|
| Story (As a / I want / So that) | Business level | The user or business need |
| Context | Business level | Why this work matters, the problem being solved |
| In scope / Out of scope | Business level | Business behaviours and boundaries |
| Acceptance criteria | Business level | Observable outcomes  -  Given/When/Then from user perspective |
| Tech Details | Implementation level | Service names, code paths, event names, API references, links to solution design docs or ADRs |

**Rules:**
- A BA or PM must be able to read everything above Tech Details without needing to know the codebase
- Service names, class names, event names, and code paths belong in Tech Details only
- When a solution has been designed and documented (Confluence page, ADR), **link to it from Tech Details**  -  do not restate implementation detail in the story body
- Engineers add implementation specifics to Tech Details as they design the solution  -  the BA does not prescribe these

This rule applies to Stories, Spikes, and Bugs. The existing anti-pattern "no solutioning inside a Bug" is a subset of this rule.

### 2f. Type correctness

- Bug = something broken vs. expected behaviour
- Story = new user-visible or system-observable value
- Spike = time-boxed investigation with a written deliverable, not code
- Enabler = technical work that unblocks future stories (per `user-story-format.md`)

Mixing types (e.g. a Bug that's actually scope expansion, or a Story that's actually investigation) gets rejected.

---

## 3. Content conformance

Tickets must conform to **both** `references/user-story-format.md` (content structure) and the project-specific format file (`jira-templates/SKILL.md` for PROJ).

If the two ever conflict:
- For content structure (sections, what each section contains, INVEST conformance, DoR): `user-story-format.md` wins
- For Jira-specific rendering (which panel type, emoji choice, custom field mapping): `jira-templates/SKILL.md` wins

If a true conflict appears, raise it as a learnings.md entry so the two files can be reconciled.

---

## 4. Project-specific format files

Currently:

| Project | Format file | Site |
|---|---|---|
| PROJ (your-jira-cloud) | `jira-templates/SKILL.md` | your Jira site |

When new projects need their own ticket conventions (different panel layouts, different custom fields, different canonical examples), they get their own format skill following the same pattern. The references/jira-ticket-format.md file (this one) doesn't expand; the project-specific skill is the source of detail.

---

## 5. Pre-write checks (the verification considerations from jira-templates)

Before a ticket gets created, the BA Assistant runs the verification considerations from `jira-templates/SKILL.md` Section "Verification considerations":

**Always check:**
- Telemetry  -  what events fire, where
- Feature toggling  -  flag, default state, rollout plan
- Geo scope (e.g. AU & NZ for PROJ)
- Unhappy paths  -  including UI behaviour for each
- Flow variants  -  which flows does this hit

**Context-dependent (only if relevant):**
- Error handling
- Stakeholder sign-off / review
- Usability and accessibility
- Loading states
- Empty / zero / max states
- Audit & compliance
- Backward compatibility

Every item that applies must end up in one of three places:
1. **In scope**  -  covered by an acceptance criterion
2. **Out of scope**  -  explicitly listed
3. **Clarify with user**  -  flagged, not silently dropped

Silence on an always-check item that applies is itself an anti-pattern.

---

## 6. Linking discipline

Every ticket created must link to:

- Its parent epic or initiative (or explicit "none with reason")
- The requirements it implements (BR-, FR-, NFR-, COMP- IDs per `requirement-format.md`)
- Its slice (SL- ID per feature slicing)
- Related Confluence pages (max 5)

Tickets without traceability links flag in the Anti-Pattern Detector.

---

## 7. PM approval interaction

Tickets can be created in Jira while `pmApproval.status` is `pending`. They live in the backlog with DRAFT or `Awaiting PM` label until approval clears. The Anti-Pattern Detector flags:

- Tickets moved into a sprint while initiative PM approval is `pending`
- Tickets created without the DRAFT/Awaiting PM label when PM approval is `pending`

This is the same gate as the status page DRAFT banner. Creation OK; advancement requires approval.

---

## 8. Output anti-patterns (Anti-Pattern Detector triggers)

| Watching | Trigger | Anti-pattern |
|---|---|---|
| Any Jira write | `createJiraIssue` or material `editJiraIssue` invoked without prior `AskQuestion` clarification in session | Clarification gate skipped |
| Any Jira write | Write uses `contentFormat: "markdown"` when panels are required | Markdown shortcut |
| Any Jira write | Canonical example for this issue type exists in project but was not fetched before draft | Canonical example not mirrored |
| Any Jira write | Ticket type doesn't match content (e.g. Bug type used for new feature work) | Type mismatch |
| Any Jira write | Ticket title doesn't follow `[Area] Imperative outcome` format | Title convention breach |
| Any Jira write | Ticket created without parent epic / initiative link OR explicit "none with reason" | Untraceable parent |
| Any Jira write | Ticket created without linked requirements | Untraceable requirements |
| Any Jira write | Story moved into active sprint while initiative PM approval `pending` | Approval gate bypassed at sprint level |
| Any Jira write | Always-check verification consideration omitted with no explanation | Silence on always-check item |
| Any Jira write | AC text names specific services, classes, events, or code paths instead of business outcomes | Implementation detail in AC |

---

## 9. How sub-skills invoke this standard

A sub-skill producing a Jira ticket follows this sequence:

1. **Read this file** (`references/jira-ticket-format.md`) for the hard rules
2. **Read `references/user-story-format.md`** for content structure
3. **Read the project-specific format skill** (e.g. `jira-templates/SKILL.md`) for rendering
4. **Run AskQuestion** for clarification (per 2a)
5. **Fetch canonical example** via `getJiraIssue` (per 2b)
6. **Draft** the ticket content per `user-story-format.md` structure
7. **Render** to ADF per project-specific format file
8. **Self-check** against the anti-patterns table (Section 8)
9. **Create** via `createJiraIssue` with the ADF object

Step 8 is mandatory and runs before step 9. The Anti-Pattern Detector also runs continuously and will catch issues post-creation, but pre-creation self-check prevents creating tickets that immediately get flagged.

---

## 10. Versioning

v1.0 (2026-05-30). Changes to the hard rules (Section 2) require version bump. Project-specific format files version independently.

---

## 11. Note on the existing jira-templates skill

The `jira-templates` skill currently lives at `~/.cursor/skills/jira-templates/` as a top-level skill, not a sub-skill of `ba-assistant`. This is fine and doesn't need to change. The reference-guides refactor isn't moving it; it's just being referenced from this file so the standards index can point to it.

If a future change wants to bring it under `ba-assistant/sub-skills/` for consistency, that's a separate refactor and out of scope for the reference-guides work.
