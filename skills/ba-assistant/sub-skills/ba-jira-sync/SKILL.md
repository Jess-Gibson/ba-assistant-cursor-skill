# Skill: Jira Sync

## Description

Queries Jira for current ticket statuses and updates `status-data.json` before any status output is generated. This ensures that `/status`, `/publish-status`, canvas refreshes, and HTML snapshots reflect real Jira state â€” not stale assumptions.

## When to invoke

- **Mandatory** before `/status` or `/publish-status`
- **Mandatory** before generating or refreshing the canvas or HTML snapshot
- **On request** when the user asks "what's the latest on tickets?"
- **At session start** if the last sync was >24 hours ago

## Tasks

### 1. Read ticket list from status-data.json

Read `status-data.json` in the initiative's analysis folder. Extract all `tickets[].key` values.

If `status-data.json` does not exist, read `SESSION-CONTEXT.md` and `confluence-pages.json` to identify known Jira keys (look for `[PROJ-*]` keys or similar patterns from your configured project).

### 2. Query Jira for each ticket

For each ticket, call `getJiraIssue` with:
- `cloudId`: the project's Atlassian cloud ID (stored in `confluence-pages.json` or use site URL)
- `issueIdOrKey`: the ticket key
- `fields`: `["status", "summary", "assignee", "customfield_10007"]` (status, summary, assignee, sprint)

**Do NOT request `expand: "changelog"`** unless specifically investigating what changed. Changelogs are verbose and consume context.

### 3. Compare and update

For each ticket, compare the Jira response to the current `status-data.json` entry:

| Field | If different |
|---|---|
| `status.name` | Update `tickets[].status` |
| `assignee.displayName` | Update `tickets[].assignee` |
| `customfield_10007[0].name` | Update `tickets[].sprint` |
| `customfield_10007[0].endDate` | Update `tickets[].sprintEndDate` |

Set `tickets[].lastJiraSync` to current ISO 8601 timestamp.

### 4. Surface changes

After syncing, produce a short change summary:

```
Jira sync complete ([date]):
- PROJ-001: To Do â†’ In Progress ([Team Member])
- PROJ-002: Sprint N â†’ Sprint N+1
- No other changes
```

If any ticket has changed status, flag it so the calling skill (canvas, status page) knows to regenerate.

### 5. Handle errors

- If a ticket key returns 404 (deleted or moved), log it as a warning and remove from `tickets[]`
- If the Jira MCP is unavailable, log the failure and proceed with stale data â€” but add a warning to the status output: "Jira sync failed â€” ticket statuses may be stale"
- Never block status generation on a Jira failure â€” degrade gracefully

## Configuration

The skill needs:
- **Cloud ID or site URL** â€” stored in `confluence-pages.json` or `SESSION-CONTEXT.md`
- **Ticket keys** â€” from `status-data.json` or SESSION-CONTEXT
- **MCP server** â€” `user-atlassian-jira-Server`

## Integration

| Caller | When |
|---|---|
| ba-project-canvas | Before any status output generation |
| ba-project-canvas | Before canvas refresh |
| /status command | Step 0 (before generating chat status) |
| /publish-status command | Pre-publish checklist step 1 |

## MCP tool reference

Read the tool schema at `mcps/user-atlassian-jira-Server/tools/getJiraIssue.json` before calling. Required parameters: `cloudId`, `issueIdOrKey`. Optional: `fields`, `expand`.

