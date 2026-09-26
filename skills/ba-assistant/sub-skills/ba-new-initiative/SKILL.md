---
name: ba-new-initiative
description: >
  Scaffold a brand new initiative or short-term piece of work: capture a draft brief,
  create the local analysis folder with starter state files, and confirm one-time
  workspace context (Jira, Confluence, Slack, repos). Invoke on "create a new project
  called X", "start a new initiative called X", "new project: X", "set up a project
  for X", or when the resume flow finds no existing initiative folder matching what
  the user describes. Replaces the old welcome-panel and project-initialisation flow
  that used to live inline in ba-assistant/SKILL.md.
---

# Skill: New Initiative Setup

Light scaffolding, not a ceremony. No welcome panel, no draft-depth dial, no
complexity-tier UI. Get the folder and state files in place, confirm the handful of
facts every later skill needs, then hand off to the real work.

## Standards used

- `references/workspace-operations.md`  -  initiative folder convention, `BA_INITIATIVES_ROOT`, shell/platform rules for the folder-creation step

## When to invoke

- Trigger phrases: "create a new project called X", "start a new initiative called X",
  "new project: X", "set up a project for X".
- Or: the BA-resume flow in `ba-assistant/SKILL.md` looked for an initiative matching
  what the user described and found none.

If neither applies, skip this skill. Resuming an existing initiative never runs this.

## Flow

1. **Confirm the name and size.** If not already explicit, ask via `AskQuestion`:
   the name (suggest a kebab-case slug), and whether this is a full initiative or a
   short-term/quick piece of work. Take the user's own words for this, it is not a
   formal category.
2. **Confirm the location.** Default: `$BA_INITIATIVES_ROOT/{slug}/` (default root
   `~/.cursor/initiatives`  -  see `references/workspace-operations.md`). Short-term:
   `$BA_INITIATIVES_ROOT/short-term/{slug}/`. Follow that reference's folder
   convention exactly, do not invent a different layout.
3. **Create the folder and starter files**, using the exact filenames the workspace
   convention expects:
   ```
   {slug}/ (or short-term/{slug}/)
       README.md                <- starter template, one paragraph, kept current
       SESSION-CONTEXT.md       <- starter template
       initiative-tracker.md    <- starter template, empty RAID tables
       Project-hub.md           <- starter template
       confluence-pages.json    <- empty array []
       outputs/
       debriefs/
   ```
4. **Fill the starter templates** with: project name, today's date, BA = current
   user (`[BA name]` by default), and empty headers for problem statement, success
   metrics, stakeholders, RAID (Decisions / Risks / Open Questions / Assumptions /
   Dependencies / Sign-offs), confidence scores (all starting Unknown), and a blank
   Confluence + Jira workspace context block (filled in step 5).
4b. **Write `README.md`** — the one file a human (or a later closeout pass) can open
   cold and understand what this folder is, without reading the tracker. Keep it
   short and let it grow with the initiative:
   - Initiative name and one-paragraph problem statement (placeholder until Phase 0
     confirms it)
   - PM, Sponsor, Tech Lead, BA (`[BA name]` by default)
   - Links to the live Confluence hub/status page and the Jira project, once known
   - Status line: `Active` (only ever flipped by a closeout pass, to
     `Closed — see outcome summary below`)
   This is an index, not a competing source of truth: decisions and RAID stay owned
   by `initiative-tracker.md`. Refresh the README at phase gates. Generate or
   refresh a canvas only after `/canvas`, `/status`, or a direct user request.
5. **Capture workspace context once**, batched into one or two `AskQuestion` panels,
   not a sequential interview:
   - Jira project key (e.g., PROJ, SW)
   - Jira issue type templates, if this project uses custom ones
   - Confluence space and parent page
   - Slack channel for initiative comms (e.g. `#sample-initiative`)
   - Repos in scope, if technical
   Cache this in `status-data.json -> initiative` (or the tracker if `status-data.json`
   doesn't exist yet) so no later skill re-asks. `ba-intake-reviewer` reads this cache
   before asking its own workspace-context question.
6. **Multi-source research**, before asking the user to restate anything they may
   already have documented. Search, in this order, in parallel where possible:
   - **Confluence** (Runlayer -> `searchConfluenceUsingCql` or `atlassian__search`) for
     pages matching the initiative name, keywords, related domains.
   - **Jira** (Runlayer -> `searchJiraIssuesUsingJql`) for existing epics, stories,
     problem cards, spikes.
   - **Glean, enterprise** (`enterprise-search` skill) for docs, Slack threads, email,
     design docs, RFCs.
   - **Glean, code** (`code-exploration` skill), for technical initiatives, to check
     whether this has been built before.
   - **Web** (`WebSearch` tool) for regulations, vendor docs, industry standards, news.

   Report findings in one structured response with confidence signals per source
   (last updated, author, authority, a recommendation), then ask via `AskQuestion`
   which sources to read in full.

   **Regulator gate (mandatory):** if the work touches a regulator or regulatory
   framework ([regulator], APRA, ACCC, ASIC, OAIC, ATO, AusPayNet, AML/CTF, Privacy
   Act / APP, CDR, PCI DSS, GDPR, PSD2/PSD3, CCPA, or cues like "regulatory mandate",
   "interchange reform", "compliance deadline"), web search is mandatory regardless
   of complexity. Read the regulator's own publication directly, internal Confluence
   summaries are secondary evidence. If WebSearch isn't available, do not proceed
   past source vetting without acknowledging the external view is missing.

   **AI source verification (mandatory):** for any source flagged as AI-written,
   verify every Confluence/Jira ID it cites returns 200 OK before quoting a claim
   from it. Any 404'd ID means the whole source is untrusted, recommend ignoring it
   entirely. All IDs verified means "AI-assisted, references verified", use sparingly
   with citation to the verified primary source.

   **Skip-acknowledgement:** tell the user what was searched and what was skipped,
   and why, one line per source category. Never silently skip a source.

   **If a tool is unavailable**, degrade gracefully and say so (missing Confluence/Jira:
   ask for URLs or epic keys; missing Glean: note the gap; missing WebSearch: note the
   gap). Never silently skip.

   Write findings to `SESSION-CONTEXT.md`. `ba-intake-reviewer` reads this instead of
   re-searching.
7. **Confirm and hand off.** Tell the user where the folder is and what the research
   found, then go straight into whatever they actually asked for, typically Phase 0
   intake (`ba-intake-reviewer`). No output-mode question, no complexity dial, no panel.

## What this does not do

- Does not render a welcome UI panel.
- Does not ask about draft depth (minimal/standard/comprehensive) as a separate dial.
- Does not generate a canvas. Canvas is on demand only (`/canvas`, `/status`), never
  automatic.
- Does not run the full Phase 0 intake conversation itself. That is
  `ba-intake-reviewer`'s job once this scaffolding and research exist.
