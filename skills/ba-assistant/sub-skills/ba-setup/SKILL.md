---
name: ba-setup
description: >
  First-run personalisation wizard for BA Assistant. Runs after files are installed.
  Guides name, role, paths (~/.cursor/initiatives), Jira/Confluence, MCP/Runlayer help,
  output depth. Writes ba-assistant-config.mdc. Then offers guided first tasks.
  Run manually any time to reconfigure.
disable-model-invocation: true
---

# BA Setup — Personalisation Wizard

This skill **personalises** an already-installed BA Assistant. It does **not**
copy skills/rules/commands. If install is missing, stop and run `ba-install` first.

---

## Pre-flight (mandatory before Step 0)

Check that `~/.cursor/skills/ba-assistant/SKILL.md` exists.

If **missing**:

1. Tell the BA: "BA Assistant files are not installed yet. I need to install the package first."
2. Load and run `sub-skills/ba-install/SKILL.md` (or ask for the public repo URL).
3. Only continue this wizard after install verification passes.

Also prefer reading **this** installed skill file under `~/.cursor/skills/ba-assistant/`,
not a stale copy under `.claude/skills/`.

---

## When this skill runs

- After `ba-install` completes
- Orchestrator Step 1.5: `ba-assistant-config.mdc` missing or still has `[Your Name]`
- User runs `/setup` or says "reconfigure BA assistant"

---

## AskQuestion design rules (mandatory)

**Closed choices only** go in AskQuestion chips (role, domain, yes/no, depth, next task).

**Free-text never goes in AskQuestion.** For name, URLs, project keys, space keys,
custom paths, and document links:

1. Ask in normal chat prose: "Reply with your name as you want it on artefacts."
2. Wait for the user's next message.
3. Do **not** invent options like "Enter my name (Recommended)" or "Other — enter the URL".

If you already broke this rule, apologise once and ask them to type the value in chat.

---

## Wizard flow

Work through steps **sequentially**. Group only related closed choices in one AskQuestion panel.

### Step 0 — Welcome

```
Welcome to BA Assistant setup.

This short wizard personalises the assistant for you:
  - Your name and role
  - Where initiative folders live
  - Jira / Confluence (optional)
  - MCP connections (optional)
  - How much detail to draft by default

Files are already installed. After this, I will help you try your first task.
```

Then Step 1.

---

### Step 1 — Who are you?

**Name (free-text in chat):**

> What name should appear on initiative artefacts and Confluence pages?
> Reply with the name in your next message.

**Role (AskQuestion only):**

> What is your primary role?

Options:
- `BA` — Business Analyst
- `PM` — Product Manager
- `PO` — Product Owner
- `Other` — I will type my role in chat

Capture: `profile.name`, `profile.role`.

---

### Step 2 — Organisation context

**AskQuestion:**

> What team or domain do you work in? (Optional)

Options:
- `payments` — Payments / Fintech
- `platform` — Platform / Infrastructure
- `customer` — Customer Experience / CX
- `data` — Data / Analytics
- `compliance` — Compliance / Regulatory
- `other` — Other / skip
- If they need a custom team name: ask them to type it in chat after selecting `other`

Capture: `profile.team`, `profile.domain`.

---

### Step 2.5 — Machine paths

Persist as user environment variables when possible (Windows: `setx`; macOS/Linux: shell profile). Also store the same values in `ba-assistant-config.mdc` so the assistant can read them without a restart.

| Variable | What | Default offered |
|---|---|---|
| `BA_INITIATIVES_ROOT` | Root for initiative folders | `~/.cursor/initiatives` |
| `BA_DOWNLOADS_PATH` | Meeting transcripts / downloads | `~/Downloads` |
| `BA_SHARED_REPO_ROOT` | Shared delivery repo for `/handover` | skip until first handover |

**AskQuestion for closed choice only:**

> Where should initiative folders be created?

Options:
- `default` — Use `~/.cursor/initiatives` (Recommended)
- `custom` — I will type a different path in chat

Same pattern for downloads. If `custom`, wait for the typed path. Create `~/.cursor/initiatives` if using the default and it is missing. Warn if a custom path does not exist yet (do not force-create custom paths without confirmation).

---

### Step 2.6 — Workstream seed + calendar

Ensure:

1. `~/.cursor/_workstream/` exists
2. Empty `workboard.json` if missing (`initiatives: []`, `last_refreshed: null`)
3. Empty `ba-actions.json` if missing (`schema_version: 1`, `actions: []`)
4. Point to `_workstream/README.md` when present

**AskQuestion:**

> Want a calendar feed for `/workboard`?

Options:
- `yes_copy` — Yes — copy the OS sample into `~/.cursor/hooks/`
- `docs_only` — Show me the sample path only
- `skip` — Skip for now

| OS | Sample |
|---|---|
| Windows | `references/sample-scripts/get-calendar.ps1` |
| macOS | `references/sample-scripts/get-calendar.mac.sh` |

Never wire hooks silently. Calendar is optional. Workboard works without it.

---

### Step 3 — Jira workspace

**AskQuestion:**

> Do you use Jira?

Options:
- `yes_cloud` — Yes — Jira Cloud
- `yes_server` — Yes — Jira Server / Data Center
- `no` — No / Not yet

If yes: ask in **chat** for instance URL and project key (free-text). Do not put URLs in AskQuestion options.

**MCP check:** Look for Jira/Atlassian MCP tools. If missing, show:

```
Jira MCP not detected in this chat.
To connect: Cursor Settings → Tools & MCP → add your organisation's
Jira / Atlassian server (or Runlayer connector if that is how your org ships it).
You can skip and configure later, then rerun /setup.
```

Capture: `workspace.jira.instanceUrl`, `workspace.jira.projectKey`.

---

### Step 4 — Confluence workspace

**AskQuestion:** yes / no.

If yes: ask space key and optional parent page URL in **chat** (free-text).

MCP check same as Jira (Confluence / Atlassian / Runlayer).

---

### Step 4.5 — MCP and Runlayer help

After Jira/Confluence answers, give a short plain-language block:

```
Integrations (optional, you can do this later):
1. Open Cursor Settings → Tools & MCP
2. Enable the Jira and Confluence servers your organisation approves
3. If your organisation uses Runlayer, add the Runlayer connectors your admin named
4. Complete any sign-in prompts
5. Start a new chat and rerun /setup if you want me to re-check

I will not ask you to paste API tokens into chat.
```

**AskQuestion:**

> Do you want step-by-step MCP / Runlayer help now?

Options:
- `guide_now` — Yes — walk me through it
- `later` — Later — continue setup

If `guide_now`: open SETTINGS guidance from `SETUP.md` → Configuring MCP integrations, check which MCP namespaces exist in this session, and tick what is connected vs missing. Do not invent credentials.

---

### Step 5 — Domain knowledge docs

**AskQuestion:** yes Confluence URL / yes other URL or path / skip.

If yes: wait for typed URL/path in chat.

---

### Step 6 — Output preferences

**AskQuestion:**

> Default output depth?

Options:
- `minimal` — Sketches; ask before full artefacts
- `standard` — Practical artefacts at each step (Recommended)
- `comprehensive` — Full artefacts unless I say otherwise

Capture: `profile.defaultDraftDepth`.

---

### Step 7 — Write config (do not destroy persona)

Write personalised config to:

`~/.cursor/rules/ba-assistant-config.mdc`

Use `skills/ba-assistant/ba-profile.template.mdc` as the content base (replace placeholders).

**Do not overwrite** `~/.cursor/rules/ba-profile.mdc` if it is the always-on persona rule
(frontmatter `alwaysApply: true` and "BA Collaboration Profile"). That file stays as shipped.

Show a short preview, then AskQuestion: write / edit / skip.

If `write`: confirm "Config written. BA Assistant is personalised for [name]."

Also set `paths.initiativesRoot` and `paths.downloadsPath` in the config YAML so the
assistant can read them even before a Cursor restart.

---

### Step 8 — Guided first tasks (mandatory help)

Do **not** jump straight into Phase 0 without offering choices.

**AskQuestion:**

> Setup complete. What should we do next?

Options:
- `set_up_workboard` — Set up my workboard now (`/workboard`)
- `debrief_meeting` — Try meeting debrief — attach a permitted transcript, then `/debrief`
- `start_initiative` — Start my first initiative — Phase 0 intake
- `mcp_help` — Help me finish MCP / Runlayer connections
- `explore` — Show commands and skills first
- `later` — I will come back later

Behaviour:

| Choice | Action |
|--------|--------|
| `set_up_workboard` | Run `/workboard` procedure; explain empty start is normal |
| `debrief_meeting` | Tell them to export a permitted Teams transcript, `@` attach it, run `/debrief` |
| `start_initiative` | Welcome panel → Phase 0 intake |
| `mcp_help` | Repeat Step 4.5 guide and re-check tools |
| `explore` | Show command table + User Guide path + suggest `/workboard` or start initiative next |
| `later` | Leave a one-screen "how to come back" note: `/ba-assistant`, `/setup`, `/workboard` |

Always end Step 8 with at least one clear next action the BA can take without being a developer.

---

## Re-run / reconfigure

`/setup` or "reconfigure BA assistant" runs this wizard again and updates
`ba-assistant-config.mdc`. Initiative folders are not deleted.

---

## Error handling

- Optional fields skipped → write config with name + role; other fields `[Configure later]`
- Write failure → show full file contents for manual create
- MCP inconclusive → note "MCP status: unconfirmed" and continue

---

## What the config enables

- Personalised artefact names
- Pre-filled Jira/Confluence context at intake
- Default draft depth
- Known initiatives root (`~/.cursor/initiatives` by default)
