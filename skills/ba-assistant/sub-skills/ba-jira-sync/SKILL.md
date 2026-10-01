---
name: ba-jira-sync
description: Refreshes ticket statuses in status-data.json with one JQL query, when the last sync is 60 minutes old or more.
disable-model-invocation: true
---

# Skill: Jira Sync

## Description

Queries Jira for current ticket statuses and updates `status-data.json` before any status output is generated. This ensures that `/status`, `/publish-status`, canvas refreshes, and HTML snapshots reflect real Jira state  -  not stale assumptions.

## When to invoke

- From `references/status-refresh.md` (used by `/status`, `/canvas`, `/publish-status`, `/metrics`), when `validate-state.py` reports the last sync 60 minutes old or more, or never
- **On request** when the user asks "what's the latest on tickets?" or says "refresh"
- Not on resume: the re-entry card shows the sync age instead

## Tasks

### 1. Read ticket list from status-data.json

Read `status-data.json` in the initiative's analysis folder. Extract all `tickets[].key` values.

If `status-data.json` does not exist, read `SESSION-CONTEXT.md` and `confluence-pages.json` to identify known Jira keys (look for `PROJ-*`, `SPD-*`, or similar patterns).

### 2. One JQL query (never one call per ticket)

Call `searchJiraIssuesUsingJql` once with:
- `cloudId`: the Jira cloud UUID (`references/runlayer-atlassian-mcp.md`)
- `jql`: `key in (<all tickets[].key>)` plus, when the initiative has epics, `OR parent in (<jiraEpics>)` so new stories are found. Over 100 keys: split into batches of 100.
- `fields`: `["status", "summary", "assignee", <sprint field>]` where `<sprint field>` is `jira.sprintField` in `ba-assistant-config.mdc` (default `customfield_10007`; sites differ: if sprint comes back empty, find the Sprint field id in one `getJiraIssue` response and save it to config)
- `maxResults`: 100

**Do NOT request `expand: "changelog"`** except for the few tickets whose status changed and that show on the canvas timeline (`startedAt` / `doneAt`). Changelogs are verbose and consume context.

### 3. Compare and update

For each ticket, compare the Jira response to the current `status-data.json` entry:

| Field | If different |
|---|---|
| `status.name` | Update `tickets[].status` |
| `assignee.displayName` | Update `tickets[].assignee` |
| `<sprint field>[0].name` | Update `tickets[].sprint` |
| `<sprint field>[0].endDate` | Update `tickets[].sprintEndDate` |

Set `tickets[].lastJiraSync` to the current ISO 8601 timestamp on every ticket the query returned (changed or not), so the next freshness check knows they are current.

### 4. Surface changes

After syncing, produce a short change summary:

```
Jira sync complete (19 May 2026, 3:05 PM):
- PROJ-4300: To Do → In Progress ([Team Member])
- PROJ-4301: Sprint 37 → Sprint 38
- No other changes
```

If any ticket has changed status, flag it so the calling skill (canvas, status page) knows to regenerate.

### 5. Handle errors

- If a ticket key returns 404 (deleted or moved), log it as a warning and remove from `tickets[]`
- If the Jira MCP is unavailable, log the failure and proceed with stale data  -  but add a warning to the status output: "Jira sync failed  -  ticket statuses may be stale"
- Never block status generation on a Jira failure  -  degrade gracefully

## Configuration

The skill needs:
- **Cloud ID or site URL**  -  stored in `confluence-pages.json` or `SESSION-CONTEXT.md`
- **Ticket keys**  -  from `status-data.json` or SESSION-CONTEXT
- **MCP server**  -  see `references/runlayer-atlassian-mcp.md` for the invocation pattern and cloud ID handling. Prefer `user-runlayer-plugin` (fast path: `execute_tool` with `searchJiraIssuesUsingJql` directly, skip `search_tools`). If that server is not available in this session, fall back to the official Atlassian MCP if one is connected. Never call a server that is not actually present in this session  -  check what's available before assuming a name.

## Integration

| Caller | When |
|---|---|
| `references/status-refresh.md` | When the last sync is 60 minutes old or more (`/status`, `/canvas`, `/publish-status`, `/metrics`) |
| User | "what's the latest on tickets?", "refresh" |

## MCP tool reference

Use the **Common tools** table in `references/runlayer-atlassian-mcp.md` for `searchJiraIssuesUsingJql`'s exact `tool_name` and arguments (`cloudId`, `jql`; optional `fields`, `maxResults`). Do not rely on cached schema files from an older direct Atlassian MCP  -  those go stale; call `search_tools` instead if the argument shape is uncertain.
