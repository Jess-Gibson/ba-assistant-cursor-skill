﻿# Jira Ticket Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/jira-ticket-format.md`
**Owner:** `jira-templates` skill (workflow and full format detail, if configured), this standard (positioning and high-level rules)
**Last reviewed:** 2026-05-30

This reference is a **positioning file**. The detailed format definition for your project's Jira tickets — ADF panels, mandatory custom fields, canonical example issue IDs, panel type quick reference, verification considerations, full templates for Bug / Story / Spike — lives in your project-specific `jira-templates` skill (structured as a separate top-level skill in `.cursor/skills/`).

This file exists to:
1. Make Jira format discoverable as part of the references index
2. Define the contract between `references/user-story-format.md` (the WHAT of a ticket) and your project-specific `jira-templates` skill (the HOW for Jira specifically)
3. Capture cross-cutting rules that apply to any Jira write, independent of project-specific conventions

---

## 1. Layered ownership

Three layers, each owns something distinct:

| Layer | Owns | Lives in |
|---|---|---|
| **Content structure** | What sections a ticket has (Why, AC, Negative case, Scope, etc.) and how they're written | `references/user-story-format.md` |
| **Jira-specific rendering** | ADF panels, panel types, emoji headings, project custom fields, canonical example IDs, panel layouts | `jira-templates/SKILL.md` (your project-specific skill) |
| **Workflow** | When to clarify, when to draft, when to create the ticket, the mandatory `AskQuestion` gate | `jira-templates/SKILL.md` (your project-specific skill) |

The two files are read together when producing a Jira ticket. The story-format file is the source of truth for content; the Jira-templates file is the source of truth for how that content gets rendered into Jira-specific structures.

---

## 2. Hard rules (apply to ALL Jira writes)

Independent of project, type, or context.

### 2a. Mandatory clarification gate

Before calling `createJiraIssue` or any material `editJiraIssue` (changes to summary, description, or scope), the BA Assistant MUST run Cursor's `AskQuestion` tool in the same session, unless the user has already provided equivalent structured answers in the current thread.

This rule is non-negotiable. The Anti-Pattern Detector flags Jira writes that skipped clarification.

### 2b. Mirror the canonical example for structure

For every project that has canonical example tickets recorded (FCM has examples for Bug, Story, Spike, Story with panels, dense Spike), the assistant reads the canonical example via `getJiraIssue` before drafting, and mirrors its structure â€” sections, panels, headings, custom fields. **Structure only, never content.**

For projects without recorded canonical examples, the assistant should produce the ticket against `references/user-story-format.md` and flag in the chat that no canonical Jira example was available.

### 2c. ADF format for writes with panels

When the ticket type requires coloured panels (FCM Bug, Story, Spike), the write uses ADF (`contentFormat: "adf"`) with `panel` nodes. Markdown content format drops panels and is not acceptable as a shortcut.

If ADF JSON is large, build it in a UTF-8 `.json` file, parse, and pass the object to the MCP tool. Don't inline it as a string in the chat.

### 2d. Title format

`[Area] Imperative outcome` â€” short, specific, searchable. Independent of project.

Good: `[Onboarding] Reject Fiserv applications when phone format invalid`
Bad: `Bug in onboarding`, `Investigation needed`, `Fix the thing from yesterday`

### 2e. Type correctness

- Bug = something broken vs. expected behaviour
- Story = new user-visible or system-observable value
- Spike = time-boxed investigation with a written deliverable, not code
- Enabler = technical work that unblocks future stories (per `user-story-format.md`)

Mixing types (e.g. a Bug that's actually scope expansion, or a Story that's actually investigation) gets rejected.

---

## 3. Content conformance

Tickets must conform to **both** `references/user-story-format.md` (content structure) and the project-specific format file (`jira-templates/SKILL.md` for your project).

If the two ever conflict:
- For content structure (sections, what each section contains, INVEST conformance, DoR): `user-story-format.md` wins
- For Jira-specific rendering (which panel type, emoji choice, custom field mapping): your project-specific `jira-templates/SKILL.md` wins

If a true conflict appears, raise it as a learnings.md entry so the two files can be reconciled.

---

## 4. Project-specific format files

Currently:

| Project | Format file | Site |
|---|---|---|
| [YOUR-PROJECT] | `jira-templates/SKILL.md` | [your-instance].atlassian.net |

When new projects need their own ticket conventions (different panel layouts, different custom fields, different canonical examples), they get their own format skill following the same pattern. The references/jira-ticket-format.md file (this one) doesn't expand; the project-specific skill is the source of detail.

---

## 5. Pre-write checks (standard verification considerations)

Before a ticket gets created, the BA Assistant runs these standard verification checks (adapt to your project-specific format skill where applicable):

**Always check:**
- Telemetry â€” what events fire, where
- Feature toggling â€” flag, default state, rollout plan
- Geo scope (e.g. regional scope for your initiative)
- Unhappy paths â€” including UI behaviour for each
- Flow variants â€” which flows does this hit

**Context-dependent (only if relevant):**
- Error handling
- Stakeholder sign-off / review
- Usability and accessibility
- Loading states
- Empty / zero / max states
- Audit & compliance
- Backward compatibility

Every item that applies must end up in one of three places:
1. **In scope** â€” covered by an acceptance criterion
2. **Out of scope** â€” explicitly listed
3. **Clarify with user** â€” flagged, not silently dropped

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
3. **Read the project-specific format skill** (e.g. `jira-templates/SKILL.md` for your project) for rendering, if one exists
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

## 11. Creating your own jira-templates skill

When you are ready to create project-specific Jira templates, create a skill at `~/.cursor/skills/jira-templates/SKILL.md` (or a project-specific name). This skill should define your ADF panel layouts, required custom fields, canonical example ticket IDs, and any team-specific conventions.

See `CUSTOMIZATION.md` for guidance on what to include.

