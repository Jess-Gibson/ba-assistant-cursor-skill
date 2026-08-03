---
name: ba-setup
description: >
  First-run setup wizard for BA Assistant. Triggered automatically on first install when ba-profile.mdc
  contains placeholder values. Guides the user through: name, role, Jira/Confluence workspace,
  MCP availability check, domain knowledge docs, output preferences. Writes personalised ba-profile.mdc.
  Run manually any time to reconfigure.
---

# BA Setup — First-Run Wizard

This skill runs **automatically on first install** and any time you need to reconfigure your BA Assistant environment. It writes a personalised `ba-profile.mdc` rule file that the orchestrator reads on every session.

---

## When this skill runs

The orchestrator (SKILL.md Step 1.5) detects first-run by checking:
- Does `~/.cursor/rules/ba-profile.mdc` exist?
- If it exists, does it contain `[Your Name]`?

If either is true, this wizard runs before the welcome panel.

---

## Wizard flow

Work through these steps **sequentially using AskQuestion at each step**. Do not batch all questions into one screen — users need to absorb and respond to each topic. However, group closely related micro-questions (e.g. Jira key + instance URL) into a single AskQuestion panel.

### Step 0 — Welcome

Display a friendly introduction before asking anything:

```
👋 Welcome to BA Assistant!

This is a 2-minute setup that personalises the assistant for your workspace.
It configures:
  • Who you are and your role
  • Your Jira and Confluence workspace
  • Which MCP integrations are available
  • Your preferred output depth

After setup, the assistant is ready to run your first initiative. Let's go.
```

Then immediately present Step 1 via AskQuestion.

---

### Step 1 — Who are you?

**Collect:**
- Your name (free-text — this will appear in artefacts and Confluence pages)
- Your role

**AskQuestion:**
> What's your name and role? (These appear in initiative artefacts.)

Options:
- `BA` — Business Analyst
- `PM` — Product Manager  
- `PO` — Product Owner
- `Other` — (free-text)

Capture: `profile.name` (free-text from user), `profile.role`.

---

### Step 2 — Your organisation context

**Collect:**
- Team or organisation name (used in artefact headers; optional — skip if solo)
- Domain focus (optional — helps surface relevant learnings)

**AskQuestion:**
> What team or domain do you work in? (Optional — helps the assistant tailor outputs.)

Options:
- `payments` — Payments / Fintech
- `platform` — Platform / Infrastructure
- `customer` — Customer Experience / CX
- `data` — Data / Analytics
- `compliance` — Compliance / Regulatory
- `other` — Other / I'll skip this
- Free-text: enter your team name

Capture: `profile.team`, `profile.domain`.

---

### Step 2.5 — Machine paths (environment variables)

One-time machine setup — these used to live in always-on rules; they belong here now (always-on restructure).

**Collect and persist as user environment variables** (Windows: `setx`; macOS/Linux: shell profile export):

| Variable | What | Default offered |
|---|---|---|
| `BA_INITIATIVES_ROOT` | Root folder containing initiative folders (SESSION-CONTEXT.md etc.) | `~/.cursor/blueprints` |
| `BA_DOWNLOADS_PATH` | Where meeting transcripts and downloads land | `~/Downloads` |
| `BA_SHARED_REPO_ROOT` | Devs' shared delivery repo (only if using `/handover` — skip otherwise) | (none — ask when first handover runs) |

**AskQuestion:** confirm each default or supply a path. After capture, verify each path exists (`Test-Path` / `[ -d ]`) and warn on misses. The session-init hook and `ba-dev-handover` read these.

**Optional:** offer the Claude Code install (extension `anthropic.claude-code` — steps in SETUP.md) as a one-time extra. Skip freely.

---

### Step 2.6 — Workstream seed + calendar (Version 10)

Create the cross-initiative working folder if missing:

1. Ensure `~/.cursor/_workstream/` exists.
2. If missing, seed empty `workboard.json` (`initiatives: []`, `last_refreshed: null`, no new `personal_tasks` writes).
3. If missing, seed empty `ba-actions.json` per `references/ba-actions-format.md` (`actions: []`, `schema_version: 1`).
4. Copy or point to `_workstream/README.md` from the package if available.

**OS detect for calendar sample (optional):**

| OS | Sample | Notes |
|---|---|---|
| Windows | `references/sample-scripts/get-calendar.ps1` | Outlook desktop COM |
| macOS | `references/sample-scripts/get-calendar.mac.sh` | Apple Calendar via `osascript` |
| Other / skip | none | Workboard works without calendar |

**AskQuestion:**
> Want a calendar feed for `/workboard`?

Options:
- `yes_copy` — Yes — copy the OS sample into `~/.cursor/hooks/` and I'll wire sessionStart later (or now if you confirm)
- `docs_only` — Show me the sample path; I'll set it up myself
- `skip` — Skip — no calendar for now

Never wire hooks silently. Calendar is optional.

---

### Step 3 — Jira workspace

**Collect:**
- Jira instance URL (`[org].atlassian.net` or self-hosted)
- Primary project key (e.g. `PROJ`, `TEAM`)

**AskQuestion:**
> Do you use Jira?

Options:
- `yes_cloud` — Yes — Jira Cloud (`[org].atlassian.net`)
- `yes_server` — Yes — Jira Server / Data Center
- `no` — No / Not yet — I'll configure later

If `yes_cloud` or `yes_server`, prompt for:
- Instance URL (free-text)
- Primary project key (free-text, e.g. `PROJ`)

Capture: `workspace.jira.instanceUrl`, `workspace.jira.projectKey`.

**MCP check:** After collecting details, check if Jira MCP tools are available in the current session (look for `mcp__jira_*` or `mcp__atlassian_*` tools). If **not** available, show inline setup hint:

```
⚠️ Jira MCP not detected. To enable Jira read/write from the assistant:
   See SETUP.md → "Configuring MCP integrations" for Atlassian setup instructions.
   You can skip this for now and configure it later.
```

---

### Step 4 — Confluence workspace

**Collect:**
- Confluence space key (e.g. `TEAM`, `ENG`)
- Parent page URL for new pages (optional)

**AskQuestion:**
> Do you use Confluence for documentation?

Options:
- `yes` — Yes
- `no` — No / Not yet

If `yes`, prompt for:
- Space key (free-text)
- Parent page URL (free-text, optional — press enter to skip)

Capture: `workspace.confluence.spaceKey`, `workspace.confluence.parentPageUrl`.

**MCP check:** Same as Jira — look for `mcp__confluence_*` tools. If not available, show the same setup hint pointing to SETUP.md.

---

### Step 5 — Domain knowledge docs

**Purpose:** Give the assistant context about your product domain so it can ask smarter questions and avoid generic guidance.

**AskQuestion:**
> Do you have any existing documents, Confluence pages, or URLs the assistant should know about for domain context?

Options:
- `yes_confluence` — Yes — I'll paste a Confluence page URL
- `yes_doc` — Yes — I'll paste a URL or file path
- `no` — No / Skip for now

If user provides a URL or path: save to `profile.domainDocs[]` as a list. The Intake Reviewer will consult these at Phase 0.

---

### Step 6 — Output preferences

**AskQuestion:**
> What output depth do you prefer by default?

Options:
- `minimal` — Minimal — sketches, outlines. I'll ask before full artefacts.
- `standard` — Standard *(recommended)* — reasonable artefacts at each step, declared upfront.
- `comprehensive` — Comprehensive — full artefacts at every step.

Capture: `profile.defaultDraftDepth`.

---

### Step 7 — Write ba-profile.mdc

Using all captured values, write a personalised `ba-profile.mdc` to `~/.cursor/rules/ba-profile.mdc`.

**Template:** Use `skills/ba-assistant/ba-profile.template.mdc` as the base. Replace all `[Placeholder]` values with captured values.

Show the user a preview of what will be written:

```
Here's your ba-profile.mdc:

Name: [captured name]
Role: [captured role]
Team: [captured team]
Jira: [instance URL] / Project: [project key]
Confluence: [space key]
Default depth: [minimal/standard/comprehensive]

Write this to ~/.cursor/rules/ba-profile.mdc?
```

**AskQuestion:**
- `write` — Yes, write it
- `edit` — Let me change something
- `skip` — Skip for now

If `write`: write the file. Confirm with: "✓ ba-profile.mdc written. BA Assistant is now configured for [name]."

---

### Step 8 — Offer to start first initiative

**AskQuestion:**
> Setup complete! What would you like to do next?

Options:
- `start_initiative` — Start my first initiative — run BA Assistant intake now
- `explore` — Show me the commands and skills first
- `later` — I'll come back when I'm ready

If `start_initiative`: exit wizard and return to SKILL.md Step 2 (welcome panel). The orchestrator then proceeds to Phase 0 intake.

---

## Re-run / reconfigure

The user can re-run setup at any time by typing `/setup` or saying "reconfigure BA assistant". The wizard runs again and overwrites `ba-profile.mdc`. Existing initiative files (blueprints, trackers) are not affected.

---

## Error handling

- If the user skips all optional fields: write a minimal `ba-profile.mdc` with the name and role only. All other fields default to `[Configure later]`.
- If file write fails: surface the error, show the content that would have been written, and ask the user to create the file manually with the shown content.
- If MCP check is inconclusive: proceed without blocking — note "MCP status: unconfirmed" in the profile.

---

## What ba-profile.mdc enables

Once written, `ba-profile.mdc` enables:

- **Personalised artefacts** — name appears in Confluence pages, initiative trackers, status pages
- **Pre-filled workspace context** — Intake Reviewer skips "what's your Jira project?" — it already knows
- **Smarter MCP routing** — Jira Sync and Confluence Publish use configured instance URL / space key
- **Domain-aware intake** — Intake Reviewer reads domain docs to ask smarter questions
- **Session default** — draft depth preference loaded at every session start
