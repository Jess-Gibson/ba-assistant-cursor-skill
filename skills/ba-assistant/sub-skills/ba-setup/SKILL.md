---
name: ba-setup
description: >
  First-run personalisation wizard for BA Assistant. Runs after files are installed.
  AskQuestion flow: name/role, domain, paths, Jira, Confluence, Runlayer connectors,
  then pull-in starting work for the workboard. Writes ba-assistant-config.mdc.
  Run /setup to reconfigure.
disable-model-invocation: true
---

# BA Setup — Personalisation Wizard

This skill **personalises** an already-installed BA Assistant. It does **not**
copy skills/rules/commands. If install is missing, stop and run `ba-install` first.

**Audience:** non-developer BAs. Keep questions human. No CLI tokens, no hook
scripts, no extension upsells, no other AI-tool skill folders.

---

## Pre-flight (mandatory before Step 0)

Check that `~/.cursor/skills/ba-assistant/SKILL.md` exists.

If **missing**:

1. Tell the BA: "BA Assistant files are not installed yet. I need to install the package first."
2. Load and run `sub-skills/ba-install/SKILL.md` (or ask for the public repo URL).
3. Only continue this wizard after install verification passes.

Read skills **only** from `~/.cursor/skills/ba-assistant/`.

---

## When this skill runs

- After `ba-install` completes
- Orchestrator Step 1.5: `ba-assistant-config.mdc` missing or still has `[Your Name]`
- User runs `/setup` or says "reconfigure BA assistant"

---

## AskQuestion design rules (mandatory)

**Always use AskQuestion** for setup. Never say “reply in chat with …” when
AskQuestion is available.

**Free-text:**
- Use the panel’s free-text field for name, URLs, keys, custom paths.
- Do **not** invent chips like “Enter my name (Recommended)” that capture nothing.
- If a chip is required for the name question, use exactly one:
  `Type your name in the free-text field` — the typed value is the answer.

**Closed choices:** real chips (role, yes/no). Add `Other` when needed.

**Hard bans:**
- Never mention or search other AI tool skill folders on disk
- Never ask about Claude Code or similar extensions
- Never ask the BA to copy calendar scripts into `hooks/`
- Never show `setx`, env-var jargon, or `default, downloads_default` reply tokens
- Never recommend a wrong initiatives path (`blueprints` is legacy; default is
  `~/.cursor/initiatives`)

---

## Wizard flow

Prefer one panel with 2 related questions when the UI allows. Expected AskQuestion
rounds for a full path: about **8–10** (fewer if they skip Jira/Confluence).
Do not drop domain, Jira, or Confluence to hit a lower count.

### Step 0 — Welcome (short)

```
Welcome to BA Assistant setup. A few quick questions (who you are, your domain,
Jira and Confluence), then we connect tools and fill your workboard.
```

Then Step 1. Do not list every internal step.

---

### Step 1 — Who are you?

**One AskQuestion panel**, two questions.

**A — Name**

> What name would you like to go by?

Prefer freeform only. If one option is required:
- `name` — Type your name in the free-text field

Empty free-text is not an answer; ask once more. Never invent name chips.

**B — Role**

> What is your primary role?

- `ba` — Business Analyst
- `pm` — Product Manager
- `po` — Product Owner
- `pa` — Product Analyst
- `other` — Other (type in the free-text field)

Capture: `profile.name`, `profile.role`.

---

### Step 2 — Domain (keep this — personalises later questions)

Domain context helps the assistant ask thoughtful, relevant questions later.
Do **not** skip this silently.

**AskQuestion:**

> What domain or area do you mainly work in?

Options (none pre-marked as the only “right” answer):
- `payments` — Payments / Fintech
- `platform` — Platform / Infrastructure
- `customer` — Customer Experience / CX
- `data` — Data / Analytics
- `compliance` — Compliance / Regulatory
- `product` — Product / Features
- `other` — Other (type your domain or team name in the free-text field)

Capture: `profile.domain` (and `profile.team` if they typed a team name under Other).

---

### Step 3 — Folders (confirm defaults, do not over-ask)

Silently create `~/.cursor/initiatives` if missing. Seed `_workstream/` with empty
`workboard.json` and `ba-actions.json` if missing. **Do not** ask about calendar
scripts or hooks.

**AskQuestion:**

> I will store your initiatives under `~/.cursor/initiatives` and look for
> meeting files in your Downloads folder. Does that look right?

- `yes` — Yes, use those defaults (Recommended)
- `change_init` — Change where initiatives are stored (type path in free-text)
- `change_dl` — Change the Downloads folder (type path in free-text)

If they change a path, confirm it once. Store in config YAML. Prefer writing
config over lecturing about environment variables. Do not mention `BA_SHARED_REPO_ROOT`
until `/handover`.

Capture: `paths.initiativesRoot`, `paths.downloadsPath`.

---

### Step 4 — Jira (keep this — key for workboard and tickets)

Knowing their Jira site and project is central to a useful setup. Ask clearly;
use free-text for URL and key. Do **not** ask Cloud vs Server.

**AskQuestion panel 1:**

> Do you use Jira for delivery tracking?

- `yes` — Yes
- `later` — Not yet / configure later

If `yes`, **same or next AskQuestion panel** (free-text is the answer):

> What is your Jira site URL? (e.g. https://your-org.atlassian.net)

- `url` — Type the URL in the free-text field
- `skip_url` — Skip URL for now

> What is your main Jira project key? (e.g. FCM or TEAM)

- `key` — Type the project key in the free-text field
- `skip_key` — Skip project key for now

Never use chips like “Enter the URL (Recommended)” with no typed value.

If Jira tools are missing in this chat, note briefly that Step 6 will help them
connect via Runlayer. Do not block setup.

Capture: `workspace.jira.instanceUrl`, `workspace.jira.projectKey`.

---

### Step 5 — Confluence space (keep this — key for docs and hub)

**AskQuestion panel 1:**

> Do you use Confluence for documentation?

- `yes` — Yes
- `later` — Not yet / configure later

If `yes`, **same or next AskQuestion panel**:

> What is your main Confluence space key? (e.g. FSP or TEAM)

- `space` — Type the space key in the free-text field
- `skip_space` — Skip space key for now

> Optional: paste a team hub or parent page URL to use as a starting point

- `hub` — Type the URL in the free-text field
- `skip_hub` — Skip hub link for now

Explain briefly: if they give a hub/space, pull-in can summarise recent pages
there later (with their OK). Do not invent placeholder URL chips.

If Confluence tools are missing, note Step 6 will help connect via Runlayer.

Capture: `workspace.confluence.spaceKey`, `workspace.confluence.parentPageUrl`
(and hub URL if different).

---

### Step 6 — Connect work tools (Runlayer)

Probe this chat for Glean, Outlook, Jira, Confluence, Runlayer. Show a simple
checklist in plain language:

| Tool | Status |
|------|--------|
| Company search (Glean) | Connected / Not connected |
| Email / calendar | Connected / Not connected |
| Jira | Connected / Not connected |
| Confluence | Connected / Not connected |

**AskQuestion:**

> To use email, calendar, Jira, and Confluence from Cursor, connect them through
> Runlayer. What do you want to do?

- `recommended` — Connect the recommended set (Glean, calendar, Jira, Confluence)
- `pick` — Let me choose which ones
- `later` — Skip for now

If they need to connect anything **Missing**:

1. Open **[Runlayer servers](https://myob.runlayer.com/servers)** (SSO).
2. Search for the name (e.g. `Glean`, `Microsoft Outlook Calendar`,
   `Atlassian - Jira`, `Atlassian - Confluence`).
3. **Add to client** → Cursor → Authenticate in Cursor Settings → Tools & MCP.
4. Start a **new chat** and say “continue setup” or rerun `/setup`.

Plain language only. Prefer Glean **via Runlayer** (not a standalone Glean install).
Never ask for API tokens.

---

### Step 7 — Save config

Default draft depth: **standard** (do not ask unless they ask to change it).

Write `~/.cursor/rules/ba-assistant-config.mdc` from
`skills/ba-assistant/ba-profile.template.mdc`.

**Do not overwrite** always-on `ba-profile.mdc` (persona).

Show a **short** preview (name, role, domain, paths, Jira, Confluence). **AskQuestion:**

> Save this setup?

- `write` — Yes, save (Recommended)
- `edit` — Change something
- `skip` — Skip saving for now

---

### Step 8 — Pull in starting work

**Read:** `references/context-bootstrap.md` (follow harvest rules; keep BA-facing
wording plain). Use domain + Jira project + Confluence space from earlier steps
to personalise what you look for and how you phrase questions.

**AskQuestion:**

> Setup is saved. Next I can pull starting work into Cursor so your workboard
> is useful today. What should we do?

- `pull_in` — Pull in starting work now (Recommended)
  (smart email actions if connected, calendar, hub/Jira if connected, then you pick what to keep)
- `connectors` — Help me finish connecting tools first
- `manual` — I will name my initiatives / attach a transcript myself
- `later` — I will come back later

| Choice | Action |
|--------|--------|
| `pull_in` | Consent → smart mail (if available) → calendar → hub/Jira → ask transcripts + initiative names → **review** → seed `ba-actions` + stubs → refresh workboard |
| `connectors` | Return to Step 6 |
| `manual` | Ask initiative names (free-text) and optional `@` transcript; seed workboard |
| `later` | One-screen return note: `/setup`, `/workboard` |

#### Smart mail (when available)

Consent first. ~30 days, capped. Prefer actions **for them** (To: them, name
called out, please/can you, unread/high importance, unreplied when detectable).
BA selects → write only selected items to `ba-actions`. No raw mail dumps.

#### Always ask during pull-in

1. Any meeting transcript to debrief now?
2. Any initiative names to create?
3. Hub/space if Step 5 was skipped?

End with **one** clear next action. Never say “empty workboard is fine” after
a successful pull-in.

---

## Re-run / reconfigure

`/setup` runs this wizard again and updates `ba-assistant-config.mdc`.
Initiative folders are not deleted.

---

## Error handling

- Skipped optionals → write name + role; others `[Configure later]`
- Write failure → show file contents for manual create
- Connectors unclear → “Not confirmed in this chat” and continue
