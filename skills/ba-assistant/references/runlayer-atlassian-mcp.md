# Atlassian (Jira + Confluence) via Runlayer MCP

the BA's Atlassian integrations route through **`user-runlayer-plugin`**, not direct `user-atlassian-*` servers.

## Invocation pattern

**Fast path:** For known Atlassian tools listed in **Common tools** below, call `execute_tool` directly; skip `search_tools`.

1. **Discover** (only when the tool is **not** in Common tools, or you need the live parameter schema):
   - `CallMcpTool` → server `user-runlayer-plugin`, tool `search_tools`
   - Args: `{ "meta": "<why you need this>", "query": "<capability, e.g. update Confluence page>", "top_k": 5 }`

2. **Execute**:
   - `CallMcpTool` → server `user-runlayer-plugin`, tool `execute_tool`
   - Args: `{ "tool_name": "<exact name from search_tools>", "arguments": { ... } }`

Use the **underlying Atlassian tool names** from search results (e.g. `updateConfluencePage`, `searchJiraIssuesUsingJql`, `getJiraIssue`). Do not prefix with `atlassian__` unless search_tools returns that form.

## Cloud IDs ([Organisation])

| Site | Use as `cloudId` |
|---|---|
| Confluence (`your-confluence.atlassian.net`) | `<confluence-cloud-uuid>` |
| Jira (`your-jira.atlassian.net`) | `<jira-cloud-uuid>` |

**Jira JQL:** always pass the **Jira cloud UUID**. Using the wrong site URL or the Confluence cloud ID fails for Jira JQL. Resolve real UUIDs via `getAccessibleAtlassianResources` (or set them in `ba-profile.mdc` / setup).

**Resolve dynamically** when unsure: `execute_tool` with `tool_name: "atlassian__getAccessibleAtlassianResources"` (or `_2` on Jira bundle) and `{}`, then pick the resource whose URL matches the target site.

## Common tools

| Task | `tool_name` | Key `arguments` |
|---|---|---|
| Confluence search (Rovo) | `atlassian__search` | `{ "query": "..." }` |
| Confluence CQL | `searchConfluenceUsingCql` | `{ "cloudId": "<confluence UUID>", "cql": "..." }` |
| Update Confluence page | `updateConfluencePage` | `{ "cloudId", "pageId", "body", "contentFormat": "markdown" }` |
| Create Confluence page | `createConfluencePage` | `{ "cloudId", "spaceId", "body", "title?", "parentId?" }` |
| Jira search (Rovo) | `atlassian__search_2` | `{ "query": "..." }` |
| Jira JQL | `searchJiraIssuesUsingJql` | `{ "cloudId": "<your-jira-cloud UUID>", "jql", "fields?", "maxResults?" }` |
| Read Jira issue | `getJiraIssue` | `{ "cloudId": "<your-jira-cloud UUID>", "issueIdOrKey", "fields?", "responseContentFormat?": "adf" }` |
| Create Jira issue | `createJiraIssue` | `{ "cloudId", "projectKey", ... }` per search_tools schema |
| Edit Jira issue | `editJiraIssue` | `{ "cloudId", "issueIdOrKey", ... }` per search_tools schema |

## Schema discovery

Use **Common tools** + cloud IDs above for known calls. Call **`search_tools`** only for tools not listed there or when the argument shape is uncertain. Legacy `mcps/user-atlassian-*` cached schemas may be stale after the Runlayer migration.

## Other MCP servers (not Runlayer)

| Server | Role |
|---|---|
| `user-runlayer-plugin` | Jira, Confluence, Glean, Slack, etc. |
| `plugin-miro-miro` | Primary Miro (DSL, tables, layout) |
| `user-miro-desktop` | Miro fallback (stickies, delete) |
| `user-snowflake-server` | warehouse SQL (`query_snowflake`) |
