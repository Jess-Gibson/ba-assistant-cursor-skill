# Confluence publishing workflow reference

## MCP server and tools

- **Server:** `user-runlayer-plugin`
- **Pattern:** `execute_tool` direct for Common tools (skip `search_tools`). Cost ladder: [runlayer-atlassian-mcp.md](../../ba-assistant/references/runlayer-atlassian-mcp.md)
- **Confluence `cloudId`:** resolve your site's Confluence cloud UUID once (see [runlayer-atlassian-mcp.md](../../ba-assistant/references/runlayer-atlassian-mcp.md)) and pin it in `_workstream/atlassian-cloud-ids.json`.

### updateConfluencePage

- **Runlayer `tool_name`:** `updateConfluencePage`
- **Required:** `cloudId`, `pageId`, `body`
- **Optional:** `title`, `status` ("current" | "draft"), `spaceId`, `parentId`, `contentFormat` ("markdown" | "adf"), `versionMessage`
- Use `contentFormat: "markdown"` when sending Markdown.

### createConfluencePage

- **Runlayer `tool_name`:** `createConfluencePage`
- **Required:** `cloudId`, `spaceId`, `body`
- **Optional:** `title`, `parentId`, `contentFormat` ("markdown" | "adf"), `isPrivate`, `subtype` ("live")
- Use `parentId` to create a child page under an existing page.

### getAccessibleAtlassianResources

- **Rare.** Only if site/cloudId is unknown.
- **Runlayer `tool_name`:** `atlassian__getAccessibleAtlassianResources`
- **Arguments:** `{}`

## Example Confluence targets (project-specific)

- **Site:** `your-confluence.atlassian.net`
- **Page / space IDs:** Resolve from the Confluence URL or initiative `confluence-pages.json`
- **cloudId:** pinned Confluence UUID above (also `_workstream/atlassian-cloud-ids.json`)

## Link conversion for Confluence

Relative `.md` links in the source do not resolve when the page is viewed in Confluence. Replace them before publication:

- Links to local source material use full Git hosting URLs for **your** repository.
- Links to pages in the same knowledge base use their final live Confluence URLs.
- Local paths, draft placeholders, and sibling `kb-*.md` links must not remain in a publish copy.

| Source pattern | Replace with |
|----------------|--------------|
| `[file.md](file.md)` | `[file.md](https://github.com/YOUR_ORG/YOUR_REPO/blob/main/path/to/file.md)` |
| `[label](../other/path.md)` | Full URL to that path on the default branch (or pinned SHA for stability). |

**Base URL pattern:** `https://github.com/<ORG>/<REPO>/blob/<branch>/`

Apply the same idea for any other relative `.md` or `../` links before publishing. Record expected links in the publication manifest, then verify them after read-back.

## Calling the MCP tool

Use `CallDynamicTool` with:

- `namespace`: `"user-runlayer-plugin"`
- `toolName`: `"execute_tool"`
- `arguments`: `{ "tool_name": "updateConfluencePage", "arguments": { "cloudId": "<confluence-cloud-uuid>", "pageId": "...", "body": "...", "contentFormat": "markdown" } }`

Do **not** call `search_tools` first for create/update/get when the tool name is already known.
