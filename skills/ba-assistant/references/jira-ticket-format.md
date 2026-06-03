> **Configure this file with your Jira project key, instance URL, and canonical example tickets.**

# Jira Ticket Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/jira-ticket-format.md`
**Owner:** Your project-specific Jira skill (workflow and full format detail), this standard (positioning and high-level rules)
**Last reviewed:** 2026-05-30

This reference is a **positioning file**. The detailed format definition for Jira tickets — ADF panels, mandatory custom fields, canonical example issue IDs, panel type quick reference, verification considerations, full templates for Bug / Story / Spike — lives in your project-specific Jira skill (configure one for your Jira project).

This file exists to:
1. Make Jira format discoverable as part of the references index
2. Define the contract between `references/user-story-format.md` (the WHAT of a ticket) and your project-specific Jira skill (the HOW for Jira specifically)
3. Capture cross-cutting rules that apply to any Jira write, independent of project-specific specifics

---

## 1. Layered ownership

Three layers, each owns something distinct:

| Layer | Owns | Lives in |
|---|---|---|
| **Content structure** | What sections a ticket has (Why, AC, Negative case, Scope, etc.) and how they're written | `references/user-story-format.md` |
| **Jira-specific rendering** | ADF panels, panel types, emoji headings, project custom fields, canonical example IDs, panel layout for PROJ-001, PROJ-002 (configure your canonical examples) | your project-specific Jira skill/SKILL.md |
| **Workflow** | When to clarify, when to draft, when to create the ticket, the mandatory `AskQuestion` gate | your project-specific Jira skill/SKILL.md |

The two files are read together when producing a Jira ticket. The story-format file is the source of truth for content; your project-specific Jira skill is the source of truth for how that content gets rendered into Jira-specific structures.

---

## 2. Hard rules (apply to ALL Jira writes)

Independent of project, type, or context.

### 2a. Mandatory clarification gate

Before calling `createJiraIssue` or any material `editJiraIssue` (changes to summary, description, or scope), the BA Assistant MUST run Cursor's `AskQuestion` tool in the same session, unless the user has already provided equivalent structured answers in the current thread.

This rule is non-negotiable. The Anti-Pattern Detector flags Jira writes that skipped clarification.

### 2b. Mirror the canonical example for structure

For every project that has canonical example tickets recorded (your project may have examples for Bug, Story, Spike, Story with panels, dense Spike), the assistant reads the canonical example via `getJiraIssue` before drafting, and mirrors its structure — sections, panels, headings, custom fields. **Structure only, never content.**

For projects without recorded canonical examples, the assistant should produce the ticket against `references/user-story-format.md` and flag in the chat that no canonical Jira example was available.

### 2c. ADF format for writes with panels

When the ticket type requires coloured panels ([YOUR-PROJECT] Bug, Story, Spike), the write uses ADF (`contentFormat: "adf"`) with `panel` nodes. Markdown content format drops panels and is not acceptable as a shortcut.

If ADF JSON is large, build it in a UTF-8 `.json` file, parse, and pass the object to the MCP tool. Don't inline it as a string in the chat.

### 2d. Title format

`[Area] Imperative outcome` — short, specific, searchable. Independent of project.

Good: `[Onboarding] Reject applications when phone format invalid`
Bad: `Bug in onboarding`, `Investigation needed`, `Fix the thing from yesterday`

### 2e. Type correctness

- Bug = something broken vs. expected behaviour
- Story = new user-visible or system-observable value
- Spike = time-boxed investigation with a written deliverable, not code
- Enabler = technical work that unblocks future stories (per `user-story-format.md`)

Mixing types (e.g. a Bug that's actually scope expansion, or a Story that's actually investigation) gets rejected.

---

## 3. Content conformance

Tickets must conform to **both** `references/user-story-format.md` (content structure) and the project-specific format file (your project-specific Jira skill/SKILL.md for your project).

If the two ever conflict:
- For content structure (sections, what each section contains, INVEST conformance, DoR): `user-story-format.md` wins
- For Jira-specific rendering (which panel type, emoji choice, custom field mapping): your project-specific Jira skill/SKILL.md wins

If a true conflict appears, raise it as a learnings.md entry so the two files can be reconciled.

---

## 4. Project-specific format files

Currently:

| Project | Format file | Site |
|---|---|---|
| [YOUR-PROJECT] ([your-instance]) | your project-specific Jira skill/SKILL.md | [your-instance].atlassian.net |

When new projects need their own ticket conventions (different panel layouts, different custom fields, different canonical examples), they get their own format skill following the same pattern. The references/jira-ticket-format.md file (this one) doesn't expand; the project-specific skill is the source of detail.

---

## 5. Pre-write checks (the verification considerations from your project-specific Jira skill)

Before a ticket gets created, the BA Assistant runs the verification considerations from your project-specific Jira skill/SKILL.md Section "Verification considerations":

**Always check:**
- Telemetry — what events fire, where
- Feature toggling — flag, default state, rollout plan
- Geo scope (e.g. [Your geo scope])
- Unhappy paths — including UI behaviour for each
- Flow variants — which flows does this hit

**Context-dependent (only if relevant):**
- Error handling
- Stakeholder sign-off / review
- Usability and accessibility
- Loading states
- Empty / zero / max states
- Audit & compliance
- Backward compatibility

Every item that applies must end up in one of three places:
1. **In scope** — covered by an acceptance criterion
2. **Out of scope** — explicitly listed
3. **Clarify with user** — flagged, not silently dropped

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

---

## 9. How sub-skills invoke this standard

A sub-skill producing a Jira ticket follows this sequence:

1. **Read this file** (`references/jira-ticket-format.md`) for the hard rules
2. **Read `references/user-story-format.md`** for content structure
3. **Read the project-specific format skill** (e.g. your project-specific Jira skill/SKILL.md) for rendering
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

## 11. Note on project-specific Jira skills

Configure a project-specific Jira skill (following the same pattern as this reference) for your Jira project conventions. It can live as a top-level skill or sub-skill — the reference index points to it from this file.

If a future change wants to bring it under `ba-assistant/sub-skills/` for consistency, that's a separate refactor and out of scope for the reference-guides work.
