---
name: ba-setup
description: >
  First-run personalisation wizard for BA Assistant. Runs after files are installed.
  Guides name, role, paths (~/.cursor/initiatives), Jira/Confluence, Runlayer connectors
  (Glean, Outlook, Jira, Confluence), output depth, then Context Bootstrap so the
  workboard is usable on day one. Writes ba-assistant-config.mdc. Run /setup to reconfigure.
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

Also read skills **only** from the installed tree:
`~/.cursor/skills/ba-assistant/`. Do not search other skill folders on the machine.

---

## When this skill runs

- After `ba-install` completes
- Orchestrator Step 1.5: `ba-assistant-config.mdc` missing or still has `[Your Name]`
- User runs `/setup` or says "reconfigure BA assistant"

---

## AskQuestion design rules (mandatory)

Use **AskQuestion** for setup questions. Prefer one panel with clear prompts.

**How free-text works in AskQuestion:**
- Cursor's AskQuestion panel includes a free-text field (often labelled like
  "Other" or shown under the options).
- For open answers (name, URL, project key, custom path), tell the BA to type
  in that free-text field. Do **not** invent chips such as
  "Enter my name (Recommended)" that look like answers but capture nothing.
- For closed lists (role, domain, yes/no, depth), use real option chips, plus
  an `Other` chip when needed.

**Anti-patterns (never do these):**
- A recommended chip that says "Enter my name" / "Enter the URL" with no typed value
- Asking the BA to abandon AskQuestion and "reply in chat" when AskQuestion is available
- Mentioning or searching other AI tool skill directories on disk

---

## Wizard flow

Work through steps **sequentially**. Group related questions in one AskQuestion panel when it helps.

### Step 0 — Welcome

```
Welcome to BA Assistant setup.

This short wizard personalises the assistant for you:
  - Your name and role
  - Where initiative folders live
  - Jira / Confluence (optional)
  - Runlayer connectors (Glean, Outlook, Jira, Confluence)
  - How much detail to draft by default
  - Context bootstrap so your workboard is not empty

Files are already installed. After this, I will help you connect tools and pull in starting work.
```

Then Step 1.

---

### Step 1 — Who are you?

Present **one AskQuestion panel** with two questions.

**Question A — Name (free-text is the answer):**

> What name would you like to go by?

Prefer freeform / custom text if AskQuestion supports it (no chips needed).
If the tool requires at least one option, use **exactly one**:
- `name` — Type your name in the free-text field (then submit)

Rules:
- The typed string is `profile.name`. Selecting a chip with an empty free-text
  field is not an answer; ask once more.
- Never invent name chips ("Jess", "Enter my name", etc.).

**Question B — Role (chips + Other free-text):**

> What is your primary role?

Options:
- `ba` — Business Analyst
- `pm` — Product Manager
- `po` — Product Owner
- `pa` — Product Analyst
- `other` — Other (type your role in the free-text field)

Capture: `profile.name` from free-text; `profile.role` from the chip or Other text.

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

If yes: ask in the **same or next AskQuestion** for instance URL and project key,
using free-text fields (options like "Type the URL below" / "Type the project key below").
Do not use fake chips that claim to be the URL.

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

If yes: ask space key and optional parent page URL via AskQuestion free-text fields
(type below). Do not invent placeholder URL chips.

MCP check same as Jira (Confluence / Atlassian / Runlayer).

---

### Step 4.5 — Connectors (Runlayer) + capability check

BA Assistant works without connectors, but it is far less useful. Mail actions,
calendar, Jira, Confluence, and company search need governed connectors.

**Read and follow:** `references/context-bootstrap.md` sections 1–3.

1. **Probe this chat** for Glean, Outlook mail/calendar, Jira, Confluence, Runlayer.
2. Show a Connected / Missing / Unknown checklist.
3. **AskQuestion** (multi-select if available):

> Would you like to install connectors via Runlayer so BA Assistant can use
> Glean, Outlook mail/calendar, Jira, and Confluence?

Options:
- `all_recommended` — Yes — set up the recommended set (Glean, Outlook calendar, Jira, Confluence)
- `pick` — Let me choose which ones
- `glean` — Glean via Runlayer only
- `outlook` — Outlook mail and/or calendar
- `jira_conf` — Jira and Confluence
- `later` — Later — continue without connectors

If they pick any connectors that are **Missing**:

1. Point them to **[Runlayer servers](https://myob.runlayer.com/servers)**
   (or their org’s equivalent).
2. Tell them to **search** for the server name (e.g. `Glean`, `Microsoft Outlook`,
   `Microsoft Outlook Calendar`, `Atlassian - Jira`, `Atlassian - Confluence`).
3. Use **Add to client** → Cursor, then Authenticate under Cursor Settings → Tools & MCP.
4. Ask them to **start a new chat** and say “re-check connectors” or rerun `/setup`.

**Important:** Prefer **Glean via Runlayer**. Do not instruct BAs to install a
standalone unmanaged Glean MCP. Older “Glean MCP not approved” notes refer to that
unmanaged path, not Runlayer’s Glean server.

Never ask for API tokens in chat. If Runlayer SSO fails, explain pilot/group access
may be required and continue with manual paste-in options.

---

### Step 5 — Hub / space URL (domain anchor)

**AskQuestion:**

> Do you have a Confluence space, team hub, or folder URL I should scan for context?

Options:
- `yes` — Yes — I will type the URL in the free-text field
- `skip` — Skip for now

If yes: capture URL into config / bootstrap notes. Full scan happens in Step 8.

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

### Step 8 — Context bootstrap + first useful workboard (mandatory)

Do **not** jump straight into Phase 0. Do **not** treat an empty workboard as success
unless the BA explicitly skipped bootstrap.

**Read and follow:** `references/context-bootstrap.md` sections 4–6.

**AskQuestion:**

> Personalisation is done. Next we fill Cursor with your real work so `/workboard` is useful.

Options:
- `full_bootstrap` — Run Context Bootstrap now (Recommended)
- `connectors_first` — Finish missing Runlayer connectors first, then bootstrap
- `manual_only` — I will name initiatives / attach transcripts only
- `debrief_meeting` — Debrief a transcript now
- `explore` — Show commands first
- `later` — Come back later

| Choice | Action |
|--------|--------|
| `full_bootstrap` | Run harvest: smart mail (if connected) → calendar → hub/Confluence → Jira → ask for transcripts + initiative names → **review** → seed `ba-actions` + initiative stubs → `/workboard` refresh |
| `connectors_first` | Return to Step 4.5; after re-check, offer bootstrap again |
| `manual_only` | Ask for initiative names (free-text) and any transcript `@` attaches; seed workboard; skip mail |
| `debrief_meeting` | Guide `@` attach + `/debrief`, then offer bootstrap or workboard |
| `explore` | Command table + User Guide; still recommend bootstrap before deep work |
| `later` | One-screen return note: `/setup`, “run context bootstrap”, `/workboard` |

#### Smart mail rules (when mail capability exists)

Consent first. Last ~30 days, capped results. Prefer emails that look like **actions for them**:

- Primarily To: them (not only large CC), when detectable
- Their name called out with a request (“can you”, “please”, “action”, “need you to”)
- Unread / high importance
- No clear reply from them / looks incomplete, when detectable

Show candidates → BA selects → write only selected items to `ba-actions`.
Never auto-dump raw mail into the workboard.

#### Always ask during bootstrap

1. Any transcripts to debrief now?
2. Any initiative names to create under `BA_INITIATIVES_ROOT`?
3. Hub/space URL if Step 5 was skipped?

End Step 8 with **one** clear next action (usually the top open BA action or first initiative).

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
