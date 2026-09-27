# Jira Ticket Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/jira-ticket-format.md`
**Owner:** this standard (workflow, approval gate, hard rules). Your own optional `jira-templates` skill, if you have one, only adds project-specific rendering.
**Last reviewed:** 2026-05-30

This file is everything the assistant needs to draft and create a Jira ticket. **Nothing here depends on a skill that is not in the package.** Jira calls go through Runlayer (`references/runlayer-atlassian-mcp.md`).

**Where the Jira details come from:** the site is `jira.instanceUrl` and the default project is `jira.projectKey` in `~/.cursor/rules/ba-assistant-config.mdc` (what `/setup` wrote). An initiative can override the project with `status-data.json → initiative.jiraProjectKey`. Ask only if both are missing or still placeholders.

If you have built your own `jira-templates` skill (panel layout, custom fields for your project), read it for rendering. It is optional formatting. If it is not installed, render from `references/user-story-format.md` plus an example issue read from your project via Runlayer.

---

## 1. Layered ownership

Three layers, each owns something distinct:

| Layer | Owns | Lives in |
|---|---|---|
| **Content structure** | What sections a ticket has (Why, AC, Negative case, Scope, etc.) and how they're written | `references/user-story-format.md` |
| **Jira-specific rendering** | ADF panels, panel types, custom fields, canonical example keys | An example issue from your project (read via Runlayer), or your optional `jira-templates` skill |
| **Workflow** | Clarify, draft, **BA approval**, create | This file (§2a, §2g, §9) |

The story-format file is the source of truth for content. Rendering follows your project's own example tickets.

---

## 2. Hard rules (apply to ALL Jira writes)

Independent of project, type, or context.

### 2a. Mandatory clarification gate

Before calling `createJiraIssue` or any material `editJiraIssue` (changes to summary, description, or scope), the BA Assistant MUST run Cursor's `AskQuestion` tool in the same session, unless the user has already provided equivalent structured answers in the current thread.

This rule is non-negotiable. The Anti-Pattern Detector flags Jira writes that skipped clarification.

### 2b. Mirror the canonical example for structure

For every project that has canonical example tickets recorded (for example `status-data.json → initiative.jiraTemplate`, captured at intake), the assistant reads the canonical example via `getJiraIssue` before drafting, and mirrors its structure  -  sections, panels, headings, custom fields. **Structure only, never content.**

For projects without recorded canonical examples, the assistant should produce the ticket against `references/user-story-format.md` and flag in the chat that no canonical Jira example was available.

### 2c. ADF format for writes with panels

When your project's example tickets use coloured panels, the write uses ADF (`contentFormat: "adf"`) with `panel` nodes. Markdown content format drops panels and is not acceptable as a shortcut.

If ADF JSON is large, build it in a UTF-8 `.json` file, parse, and pass the object to the MCP tool. Don't inline it as a string in the chat.

### 2d. Title format

`[Area] Imperative outcome`  -  short, specific, searchable. Independent of project.

Good: `[Onboarding] Reject applications when phone format is invalid`
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

### 2g. BA approval before any create (hard gate)

No `createJiraIssue` (and no material `editJiraIssue`) until the BA has **seen the full draft and approved it**.

1. Confirm which initiative this ticket is for. If it has not been named in this chat, ask. Never draft against a guessed initiative.
2. Show the complete draft in chat (or in a file for long ADF): project key, issue type, summary, description, AC, labels, parent/links.
3. AskQuestion: **Create in Jira** / **Edit first** / **Not yet**.
4. Only on **Create in Jira**: create through Runlayer (`execute_tool` → `createJiraIssue`; use `search_tools` if the live schema is unclear). Report the new key back.
5. Stories also get the Story Readiness Preflight (`_workstream/dor-check.py`, re-run by the `external-write-gate` hook at create time). It checks five structural conditions only (`user-story-format.md` §6); a pass is "Structural preflight passed", not the Definition of Ready. Not passed: the BA's approval dialog names the missing conditions, and an approval is a BA override to log as a tracker decision.

Approval covers the draft as shown. If anything material changes after approval, show it again and re-ask. Several tickets can be approved in one AskQuestion only if every draft was shown.

---

## 3. Content conformance

Tickets must conform to `references/user-story-format.md` (content structure) and follow your project's rendering (example ticket, or your optional `jira-templates` skill).

If the two ever conflict:
- For content structure (sections, what each section contains, INVEST conformance, DoR): `user-story-format.md` wins
- For Jira-specific rendering (which panel type, emoji choice, custom field mapping): the project's rendering wins

If a true conflict appears, raise it as a learnings.md entry so the two files can be reconciled.

---

## 4. Project-specific format

The project key and site come from `ba-assistant-config.mdc` (`jira.projectKey`, `jira.instanceUrl`), with a per-initiative override in `status-data.json → initiative.jiraProjectKey`. If a project has its own ticket conventions, record an example issue key at intake (`initiative.jiraTemplate`) or build your own optional format skill. This file does not change per project.

---

## 5. Pre-write checks (verification considerations)

Before a draft is shown for approval, the BA Assistant runs these verification considerations (plus any extra ones in your optional format skill):

**Always check:**
- Telemetry  -  what events fire, where
- Feature toggling  -  flag, default state, rollout plan
- Geo / market scope (set from the initiative)
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
| Any Jira write | `createJiraIssue` invoked before the BA saw the full draft and chose **Create in Jira** (§2g) | Approval gate skipped |
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

1. **Confirm the initiative** (named in this chat, else ask) and the project key (config / `status-data.json`)
2. **Read this file** for the hard rules, and `references/user-story-format.md` for content structure
3. **Run AskQuestion** for clarification (per 2a)
4. **Fetch the example ticket** via Runlayer `getJiraIssue` (per 2b), if one is recorded. Read your optional format skill only if it is installed
5. **Draft** the ticket content per `user-story-format.md`, render to ADF if your project uses panels
6. **Self-check** against the anti-patterns table (Section 8) and the verification considerations (Section 5)
7. **Show the full draft and get approval** (per 2g). Stop here unless the BA chooses **Create in Jira**
8. **Create** via Runlayer `createJiraIssue`. Stories: the `external-write-gate` hook recomputes the Story Readiness Preflight from the files (it never reads `dorChecks`) and the BA approves in Cursor's dialog

Steps 6 and 7 are mandatory and run before step 8. The Anti-Pattern Detector also runs continuously and will catch issues post-creation, but pre-creation self-check prevents creating tickets that immediately get flagged.

---

## 10. Versioning

v1.0 (2026-05-30). Changes to the hard rules (Section 2) require version bump. Project-specific format files version independently.

---

## 11. Note on the optional jira-templates skill

`jira-templates` is an optional personal skill (for example `~/.cursor/skills/jira-templates/`) that you can build for your own project's rendering conventions. It does not ship with this package and nothing waits on it. Without it, the flow above works end to end through Runlayer.
