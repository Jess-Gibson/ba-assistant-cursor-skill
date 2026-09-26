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

## 3. Workspace Operations (`skills/ba-assistant/references/workspace-operations.md`)

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

Optional chat-organisation guidance lives in
`skills/ba-assistant/references/chat-profiles.md`. It is discoverable reference
material only and is not loaded during `SKILL.md` Step 1 bootstrap.

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

The BA Assistant scaffolds initiative folders when you say "create a new initiative called X". `ba-setup` Step 3 owns the convention. The default is:

```
BA_INITIATIVES_ROOT=~/.cursor/initiatives

~/.cursor/initiatives/<slug>/
  SESSION-CONTEXT.md
  confluence-pages.json
  initiative-tracker.md
  Project-hub.md
```

To change this convention:
1. Run `/setup` and configure the initiatives root in `ba-setup` Step 3
2. Set `BA_INITIATIVES_ROOT` to the same root
3. Verify `SKILL.md` Step 2 can resume an initiative from that location

---

## 9. Canvas SDK

The Project Canvas generates `.canvas.tsx` files that require Cursor's Canvas feature. The canvas SDK types are at `~/.cursor/skills-cursor/canvas/sdk/index.d.ts` — this path is managed by Cursor and should work automatically.

If canvas generation fails, check that the Cursor Canvas skill is installed in your IDE.

---

## 10. Cross-initiative Workboard

Recommended if you run more than one initiative at once. `/workboard` follows `references/workboard-procedure.md` (not a sub-skill). First use creates `_workstream/workboard.json` and pairs with `_workstream/ba-actions.json`.

### Calendar feed (fully optional)

The workboard reads `_workstream/calendar-feed.json` when present:

- **Windows + Outlook:** `skills/ba-assistant/references/sample-scripts/get-calendar.ps1`
- **macOS + Calendar.app:** `skills/ba-assistant/references/sample-scripts/get-calendar.mac.sh`
- **Other / none:** skip it; workboard still works

Copy into `~/.cursor/hooks/` and wire `sessionStart` only if you want automation (never silent).

### `/todo` quick capture

`rules/todo-quick-capture.mdc` writes to `ba-actions.json` (not legacy `personal_tasks[]`).

### If you use a custom initiative convention

`/workboard` cross-references initiative state under `BA_INITIATIVES_ROOT`. If your initiatives use a different structure, configure that root in `ba-setup` Step 3 before relying on file cross-references.

---

## 11. Personalisation hooks

Everything `skills-routing.mdc` routes to ships in this package, except these placeholders you fill in yourself:

- **Jira ticket templates** (`[your-jira-templates]`): start from `skills/ba-assistant/references/jira-ticket-format.md` and replace `[YOUR-PROJECT]` / `[your-instance]` as described in Section 5. Point the Jira row in `skills-routing.mdc` at your own template skill.
- **Voice and style** (`[your-voice-and-style rule]`): see "Adding your voice-and-style rule" in Section 1.
- **Bulk working-file sync (not provided):** publishing to devs is `/handover` (`ba-dev-handover`), which only ever publishes confirmed analysis. If you also want bulk sync of working files to a delivery repo, build your own skill; nothing in this package does it.

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
