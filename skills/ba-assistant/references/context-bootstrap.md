# Context bootstrap (first-run / cold start)

**Owner:** `ba-setup` Step 8 (and `/setup` re-runs that choose bootstrap)  
**Goal:** Make `/workboard` useful on day one by pulling real work into Cursor,
with the BA reviewing every candidate before anything is written.

BA Assistant works without connectors, but mail scan, Jira, Confluence, and
company search need them. Prefer **Runlayer-governed** connectors over ad-hoc MCP.

---

## 1. Capability check (always run before harvest)

Inspect tools available **in this chat**. Tick what you can see:

| Capability | Typical signals | Needed for |
|---|---|---|
| Runlayer gateway | `user-runlayer` / `user-runlayer-plugin` tools | Install help, server list |
| Glean (via Runlayer) | Glean search / chat / `outlook_search` / `meeting_lookup` | Mail, meetings, company search |
| Outlook mail | Glean `outlook_search` **or** Outlook MCP tools | Action candidates from email |
| Outlook calendar | `meeting_lookup` **or** Outlook Calendar MCP / calendar-feed script | Workboard meetings |
| Jira | Atlassian / Jira MCP tools | Assigned work → initiative stubs |
| Confluence | Atlassian / Confluence MCP tools | Hub scan, recent pages |

Show the BA a plain checklist: Connected / Missing / Unknown.

**Do not** tell them to install a standalone Glean MCP. At MYOB, Glean is
available as a **Runlayer server**. Older Confluence notes that mark “Glean MCP
not approved” refer to the unmanaged vendor MCP, not the Runlayer-governed path.

---

## 2. Runlayer connector setup (when something is Missing)

### MYOB (default for this package’s enablement)

1. Open **[Runlayer servers](https://myob.runlayer.com/servers)** (SSO).
2. Search for the server name the BA chose (examples below).
3. Open it → **Add to client** / connect for **Cursor**.
4. In Cursor: **Settings → Tools & MCP** → Authenticate / enable the new server.
5. **Start a new chat** (tools often only appear after a fresh session), then
   re-run `/setup` or say “re-check connectors”.

| BA wants | Search on servers page for | Why |
|---|---|---|
| Company search + mail via Glean | `Glean` | Enterprise search, Outlook mail search, meetings |
| Mail (direct) | `Microsoft Outlook` or `Microsoft Outlook Mail` | Email when Glean mail is unavailable |
| Calendar | `Microsoft Outlook Calendar` | Upcoming meetings for workboard |
| Jira | `Atlassian - Jira` | Tickets, JQL |
| Confluence | `Atlassian - Confluence` | Pages, spaces |

Also useful: [Runlayer plugins](https://myob.runlayer.com/plugins) for account
connections. Pilot access is Entra group-scoped; if login fails, they need the
Runlayer pilot group (see org onboarding), not a BA Assistant bug.

### Other organisations

Same pattern: open your org’s Runlayer servers URL, search, Add to client,
authenticate in Cursor, new chat, re-check.

Never ask the BA to paste API tokens into chat.

---

## 3. AskQuestion: what to set up

Present **one panel** (multi-select if the UI allows; otherwise sequential):

> BA Assistant is much stronger with these connected. Which should we set up now?

Options:
- `glean` — Glean via Runlayer (search + often mail/meetings)
- `outlook_mail` — Outlook mail
- `outlook_cal` — Outlook calendar
- `jira` — Jira
- `confluence` — Confluence
- `all_recommended` — All of the above (Recommended for first-time BAs)
- `skip_connectors` — Skip connectors for now (manual paste-in only)

For each Missing selection: walk the Runlayer steps above for that server only.
Then re-check capabilities.

---

## 4. Harvest (opt-in, after connectors or with graceful degrade)

**AskQuestion:**

> Ready to pull starting context into Cursor?

Options:
- `full` — Full bootstrap (Recommended): smart mail + calendar + hub/Jira if connected
- `mail_only` — Mail actions only
- `hub_jira` — Hub URL + Jira + Confluence only
- `manual` — I will paste initiatives / attach transcripts only
- `skip` — Skip; show empty workboard guidance

### 4a. Smart mail scan (only if mail capability exists)

Consent first. Then search roughly the **last 30 days**, capped (e.g. 25–40 hits).

Prefer signals that look like **actions for this BA**:

- Addressed primarily to them (To: them, not only huge CC lists when detectable)
- Body/subject calls them out by name or “can you / please / action / need you to”
- Unread or high importance
- No clear reply from them in the thread (incomplete / unreplied), when detectable
- Deadlines, reviews, sign-offs, “waiting on you”

**Do not** dump full email bodies into `ba-actions.json` or initiative files.
Store: short action title, optional due hint, `source: email`, optional message id/link.

Present candidates in AskQuestion (or a short numbered list + multi-select).
Only write selected items via `/todo` / `ba-actions` format.

If mail tools are missing: say so, offer Runlayer Outlook/Glean setup, continue.

### 4b. Calendar / meetings

Pull next 7 days (and optionally last 14 days with transcripts).
Offer: flag meetings for later `/debrief` if a transcript exists or can be attached.

### 4c. Hub / space URL

Ask for a Confluence space, team hub, or folder URL (free-text).
If Confluence/Glean connected: summarise recent pages the BA authored or that sit
under that hub into `_workstream/domain-context.md` (short themes + links, not
full page dumps). Suggest initiative folder names from clusters.

### 4d. Jira

If connected: list issues assigned to / watched by the BA (cap results).
Ask which map to initiative stubs under `BA_INITIATIVES_ROOT`.

### 4e. Manual cold-start (always available)

AskQuestion / free-text:

- Any meeting transcripts to debrief now? (`@` attach → `/debrief`)
- Any initiative names to create as empty folders + workboard rows?
- Any hub/space URL if not already given?

---

## 5. Seed workboard (after review)

1. Write accepted actions to `_workstream/ba-actions.json` (+ regenerate `.md`)
2. Create agreed initiative stubs (folder + minimal SESSION-CONTEXT if appropriate)
3. Update `workboard.json` initiatives list
4. Run `/workboard` refresh procedure
5. Show: open actions, initiatives, today’s meetings, **one** recommended next click

Never say “empty is normal” after a successful bootstrap. Empty is only OK when
the BA explicitly skipped harvest.

---

## 6. Privacy and safety

- Explicit consent before mail/calendar harvest
- Review before write
- No secrets or tokens in chat or state files
- Prefer titles over PII-heavy bodies in canonical files
- PII safety rules for the workspace still apply
