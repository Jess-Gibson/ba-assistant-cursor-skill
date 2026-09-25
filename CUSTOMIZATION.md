# BA Assistant — Customization Guide

This document explains what to personalize after installing the BA Assistant package. The package ships with generic defaults — customize these to match your role, org, and tooling.

> **New users:** The BA Assistant includes a first-run setup wizard that handles most of this automatically. On first launch, if `ba-profile.mdc` still contains `[Your Name]` placeholders, the wizard will guide you through configuration interactively. You only need this guide if you want to go deeper than what the wizard covers, or to customize manually.

---

## 1. BA Profile Rule (`rules/ba-profile.mdc`)

This is the most important file to customize. It defines your BA persona, commands, living tracker format, and status page structure.

### What to change

| Section | What to do |
|---------|-----------|
| Title and role description | Replace with your name and how you want the assistant to behave |
| Specialist Skills table | Add or remove skills based on your workflow |
| Status Page Standard Format | Customize sections for your org's status reporting needs |
| Communication Style | Adjust to match your preferences |

### Status page sections

The status page format includes these required sections by default:

1. Header (date, stage, PM, BA, Tech Lead)
2. Where We Are (narrative)
3. What Was Achieved Last Week
4. What Is Planned This Week
5. Feature Status
6. Critical Path
7. Outstanding Blockers
8. **Delivery Model** (optional — add cohort/slice tables if your initiative uses them)
9. Living Tracker (RAID, decisions, unknowns, assumptions, risks, dependencies)
10. Confidence Scores
11. Key Artefacts

Section 8 (Delivery Model) is optional. Remove it if your initiatives don't use cohort-based delivery, or rename it to match your org's terminology.

### Adding your voice-and-style rule (optional)

If you want the assistant to draft comms (emails, Slack, meeting invites) in your voice:

1. Create `~/.cursor/rules/your-name-voice-and-style.mdc`
2. Include examples of your writing style from real messages
3. Add a routing entry in `skills-routing.mdc` pointing to your voice rule

---

## 2. Skills Routing (`rules/skills-routing.mdc`)

This rule maps user intents to skills. Customize it for your tooling:

### Jira project configuration

Replace the placeholder Jira project references with your actual project keys:

```
| Jira: Bug / Story / Spike create or format | your-jira-templates | Read example issues via MCP first |
```

If you use a specific Jira project skill for your team's ticket format (customized for your workflow), add it to the routing table and install it separately. See `references/jira-ticket-format.md` for the generic ticket structure the BA Assistant uses by default.

### Removing unused rows

Delete routing rows for skills you haven't installed. The BA Assistant degrades gracefully — it won't break if a routed skill is missing, but removing stale rows keeps things clean.

---

## 3. Workspace Operations (`rules/workspace-operations.mdc`)

### Downloads path

Set the `BA_DOWNLOADS_PATH` environment variable to your downloads folder. The meeting debrief skill uses this to auto-detect new meeting transcripts.

### Scratch file location

The default scratch path is `$LOCALAPPDATA/Temp/cursor-agent-scratch/` (Windows) or `/tmp/cursor-agent-scratch/` (macOS/Linux). Change this if your temp directory is different.

### MCP server names

Update the MCP tool list to match your configured servers:

| Tool | Your server name |
|------|-----------------|
| Jira MCP | (your Jira MCP server name) |
| Confluence MCP | (your Confluence MCP server name) |
| Miro MCP | (your Miro MCP server name, if using) |

---

## 4. Hooks

### Session init hook

The `session-init` hook finds your most recent `SESSION-CONTEXT.md` on session start. Configure it by setting:

- `BA_INITIATIVES_ROOT` — the root folder where your initiative/project folders live
- The hook searches for `SESSION-CONTEXT.md` files under this root

### Snapshot hook

The `snapshot-before-compact` hook backs up your SESSION-CONTEXT.md before Cursor compacts the conversation. No configuration needed — it uses the path set by the session init hook.

---

## 5. Jira Ticket Format (`references/jira-ticket-format.md`)

This reference file defines how the BA Assistant formats Jira tickets. Customize:

- Your Jira project key(s) (replace `[YOUR-PROJECT]`)
- Your Atlassian instance URL (replace `[your-instance].atlassian.net`)
- Ticket field conventions for your team
- Canonical example ticket IDs for the assistant to reference

---

## 6. Regulatory / Compliance Keywords

The Intake Reviewer (`sub-skills/ba-intake-reviewer/SKILL.md`) includes a configurable list of regulatory bodies and compliance keywords to watch for during intake. The default list is:

```
Regulators: [Configure for your jurisdiction]
Standards: [Configure for your industry]
```

Replace these with the regulators and standards relevant to your industry and jurisdiction.

---

## 7. Learnings File

The canonical, persistent copy lives at `~/.cursor/_workstream/learnings.md` — the
installer seeds it there from the package's sample (`skills/ba-assistant/learnings.md`)
the first time you install, and never overwrites it again on reinstall/upgrade once
you have real content. It grows as you run retrospectives. Each learning has:

- A pattern description
- Tags for when to surface it
- A strength level (Candidate → Established → Archived)

You don't need to seed this file — it populates naturally through the `/retro` command. But if your team has shared BA learnings, you can pre-populate entries in `~/.cursor/_workstream/learnings.md` following the format in the file header.

---

## 8. Project Folder Convention

The BA Assistant scaffolds project folders when you say "create a new project called X". The default convention is:

```
<workspace>/blueprints/Project NNN - <slug>/
  docs/blueprints/analysis/
    SESSION-CONTEXT.md
    confluence-pages.json
    initiative-tracker.md
    Project-hub.md
```

To change this convention:
1. Edit the glob patterns in `SKILL.md` (Step 2.5) to match your folder structure
2. Update `session-init` hook search paths
3. Update `execution-router.mdc` resume glob patterns

---

## 9. Canvas SDK

The Project Canvas generates `.canvas.tsx` files that require Cursor's Canvas feature. The canvas SDK types are at `~/.cursor/skills-cursor/canvas/sdk/index.d.ts` — this path is managed by Cursor and should work automatically.

If canvas generation fails, check that the Cursor Canvas skill is installed in your IDE.

---

## 10. Cross-initiative Workboard (inline — Version 10)

Recommended if you run more than one initiative at once. `/workboard` follows `references/workboard-procedure.md` (not a sub-skill). First use creates `_workstream/workboard.json` and pairs with `_workstream/ba-actions.json`.

### Calendar feed (fully optional)

The workboard reads `_workstream/calendar-feed.json` when present:

- **Windows + Outlook:** `skills/ba-assistant/references/sample-scripts/get-calendar.ps1`
- **macOS + Calendar.app:** `skills/ba-assistant/references/sample-scripts/get-calendar.mac.sh`
- **Other / none:** skip it; workboard still works

Copy into `~/.cursor/hooks/` and wire `sessionStart` only if you want automation (never silent).

### `/todo` quick capture

`rules/todo-quick-capture.mdc` writes to `ba-actions.json` (not legacy `personal_tasks[]`).

### If you don't use the initiative-blueprint convention

`/workboard` cross-references `blueprints/<slug>/SESSION-CONTEXT.md` when available. If your initiatives don't live in that structure, describe state conversationally and skip file cross-referencing steps.

---

## 11. Optional Capabilities Referenced in Routing But Not Bundled

`skills-routing.mdc` and `execution-router.mdc` mention a handful of intents that don't have a shipped skill behind them in this package's `skills/` folder. Those rows exist to tell you what a BA might want and where to hook it in — not to claim the skill is ready to use. If one of these triggers matters to you, build the skill yourself and point the routing row at your own skill folder.

### Diagrams (general Mermaid: flows, architecture, journeys, ER charts)
- **Trigger:** "draw this", "diagram", "flowchart", "architecture diagram", "user journey"
- **What it would do:** Generate Mermaid diagrams in markdown for docs/Confluence, for cases broader than the one HTML flowchart template below.
- **Build your own:** No generic reference ships for this. `references/visual-output-format.md` + `references/templates/flowchart.html` cover the bundled interactive HTML flowchart case only — general Mermaid generation would be a separate build.

### Batch Confluence sync from a repo Markdown registry
- **Trigger:** "sync all my docs to Confluence", "batch publish", `confluence-pages.json`, dry-run / `--only` flags
- **What it would do:** A CLI (in your own workspace's `tools/`) that walks a page registry and pushes many Confluence pages at once.
- **Build your own:** Use `skills/publish-docs-to-confluence/SKILL.md` and its `references/confluence-workflow.md` as the single-page pattern to extend into a batch CLI. For one-off pages, the bundled `publish-docs-to-confluence` skill already does the job — no need to build anything.

### Data analyst (warehouse/SQL queries, metrics narrative)
- **Trigger:** "query the warehouse", "pull metrics", "synthesize these logs into a narrative"
- **What it would do:** Warehouse/SQL querying plus narrative synthesis of findings.
- **Build your own:** No generic reference ships for this. `ba-assistant/sub-skills/ba-data-investigation` covers BA-scoped data investigation inside an initiative — a standalone data-analyst skill for broader warehouse/SQL work would be a separate build.

### Jira production analytics (root-cause charts, problem-card deep-dive)
- **Trigger:** "root cause from Jira problem tickets", "problem-card deep-dive", production regression analytics tied to Jira
- **What it would do:** Cross-reference production issues in Jira with root-cause charts, in one of two selectable modes.
- **Build your own:** No generic reference ships for this. `references/jira-ticket-format.md` (see Section 5 above) covers the ticket shape you'd be querying against, but not the analytics workflow itself.

### Sumo Logic troubleshooting
- **Trigger:** "check Sumo logs", "troubleshoot production", "post-release regression watch"
- **What it would do:** Query Sumo Logic and correlate log findings with a release or incident.
- **Build your own:** No generic reference ships for this — it's specific to the Sumo Logic tool. `ba-assistant/sub-skills/ba-data-investigation` is the nearest BA-flavoured analogue if you want a starting structure.

### Full PRD (All-in-One format)
- **Trigger:** "write a full PRD", an all-in-one product requirements doc (distinct from a short requirements synthesis)
- **What it would do:** Produce a complete PRD (goals, scope, requirements, success metrics, etc.) as one artefact.
- **Build your own:** `references/requirement-format.md` and `references/requirements-register-unified-template.md` cover the requirements-register shape BA Assistant already produces — treat those as a starting point, not a finished PRD template, since a full PRD covers more ground than a register.

### Creative brainstorming before scoping
- **Trigger:** "let's brainstorm this feature first", creative exploration before building or specifying scope
- **What it would do:** Explore intent, requirements, and design options before committing to a build.
- **Build your own:** No generic reference ships for this in the package. Check whether your AI environment already offers a general-purpose brainstorming skill before building a BA-specific one.

### Standing sync to a team/delivery repo (`/sync-team-repo`)
- **Trigger:** "sync to team repo", "push to harness", `/sync-team-repo`
- **What it would do:** A gated, file-by-file sync from your local initiative analysis to a shared team or delivery repository, driven off a `TEAM-REPO-HANDOFF.md` file table.
- **Build your own:** `execution-router.mdc`'s "Sync/publish-risk" classification row and its Harness sync path (read the handoff file, hash-compare, require explicit "sync now", never bulk-copy) already describe the gating procedure — you still need to write the skill (or inline procedure) that actually performs the file-by-file copy for your target repo.

### Jira ticket templates for your project (see also Section 5)
- **Trigger:** "create a Jira bug/story/spike", ticket format for your project/instance
- **What it would do:** Format Jira issues to your team's conventions on your Atlassian instance.
- **Build your own:** Start from `skills/ba-assistant/references/jira-ticket-format.md` — the generic ticket structure this package's Jira handling is modeled on. Replace the `[YOUR-PROJECT]` and `[your-instance]` placeholders as described in Section 5.

### Prototyping (iterative build-and-verify loop)
- **Trigger:** "let's prototype this", exploratory build work needing small cycles and assumption-checking
- **What it would do:** Run short build/verify iterations on a spike or proof of concept, distinct from the analysis-only work this package covers.
- **Build your own:** No generic reference ships for this — it's a coding/build workflow, not a BA analysis one. `ba-assistant/sub-skills/ba-data-investigation` is the nearest BA-flavoured analogue if you want a starting structure for the verification-loop discipline.

### Quality review of requirements or design (`qa-checker`)
- **Trigger:** "QA this requirement", "review this design for gaps", pre-handover quality pass distinct from the interrogation flow
- **What it would do:** A standalone quality/completeness review of requirements or design artefacts.
- **Build your own:** `ba-assistant/sub-skills/ba-requirements-interrogator` and `ba-assistant/sub-skills/ba-state-validator` already cover requirement-quality and drift-detection inside BA Assistant's own flow — check whether either already meets the need before building a separate checker.

---

## What NOT to change

These files contain generic BA methodology and should generally be kept as-is:

- `hook-contracts.md` — inter-skill API contracts
- `references/raid-format.md` — RAID table structure
- `references/requirement-format.md` — requirements register format
- `references/visual-output-format.md` — diagram output conventions
- `references/templates/flowchart.html` — HTML template
- Sub-skills marked as GENERIC in the audit (context-capture, current-state-assessment, solution-shaping, stakeholder-strategy, visual-storytelling, requirements-interrogator, ba-story-writing)

Modifying these may break inter-skill contracts. If you need different formats, consider creating org-specific overrides rather than editing the base files.
