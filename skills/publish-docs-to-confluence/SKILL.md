---
name: publish-docs-to-confluence
description: >-
  Canonical Confluence documentation skill: create or update pages, sync local Markdown (specs, PRDs, reports, retros), fix broken wiki links, embed content, attach assets, and link Jira issues. Use whenever the user mentions Confluence, wiki, publish documentation, space, parent page, or "put this on Confluence", even without naming this skill. Atlassian MCP: user-runlayer-plugin execute_tool direct (skip search_tools for known tools). See ba-assistant/references/runlayer-atlassian-mcp.md for the Confluence cloudId. For Jira ticket shape, see ba-assistant/references/jira-ticket-format.md.
---

# Publish Docs to Confluence

Publish or update Confluence pages from local Markdown (e.g. specs, PRDs, audits). Uses **Runlayer** (`user-runlayer-plugin` → `execute_tool` direct). See [runlayer-atlassian-mcp.md](../ba-assistant/references/runlayer-atlassian-mcp.md).

## When to Use

- User asks to "publish [file] to Confluence" or "update the Confluence page"
- Syncing `docs/specs/*.md` or `docs/inputs/prd/*.md` to a known Confluence page
- Creating a new Confluence page under a parent (e.g. child of Release Plan page)
- Fixing broken links on Confluence (e.g. relative `.md` links that don't resolve)

## MCP (best / fastest / cheapest)

1. **Server:** `user-runlayer-plugin` → `execute_tool` only.
2. **cloudId:** Confluence cloud UUID for your site (e.g. `your-confluence.atlassian.net`). Do not use the Jira UUID for pages. See [runlayer-atlassian-mcp.md](../ba-assistant/references/runlayer-atlassian-mcp.md) for how to resolve it.
3. **Skip `search_tools`** for `updateConfluencePage`, `createConfluencePage`, `getConfluencePage`, `searchConfluenceUsingCql`.
4. **Skip** `getAccessibleAtlassianResources` unless the site is unknown (it almost never is once configured).
5. Pin from `_workstream/atlassian-cloud-ids.json` → `confluence.cloudId`.

## Publication controls

For a multi-page knowledge base, material update, or large reference page, use [publish-manifest-template.md](references/publish-manifest-template.md) before any Confluence write. It separates evidence and reader decisions from API mechanics.

### 1. Gather and select

- Start with the reader job and the questions the content must answer.
- Record each material claim in the fact ledger: source, date, intended page, and publish, summarise, link, exclude, or confirm decision.
- Prefer recent confirmed evidence. Do not silently reconcile conflicting records.
- Confirm the information architecture before drafting. Each page needs a distinct reader job. Link to an operational source rather than copying it when it does not.

### 2. Review, freeze, and approve

- Treat `reviewed`, `confirmed`, and `interrogated` artefacts as read-only. Propose a concise diff and obtain approval before changing them.
- For stakeholder-facing Markdown, apply the BA Assistant's markdown readability standard (`ba-assistant/references/markdown-readability.md`) before showing the draft.
- Create a named presentation copy when publishing needs transformations. Keep the reviewed source frozen.
- Record two approvals: content approval for facts and reader usefulness, then release approval for the exact frozen source, title, format, and target. A changed source, title, parent, format, or split requires new release approval.

### 3. Choose the operation

- **Create:** a new page with a completed manifest row.
- **Full replacement:** a page body can safely be replaced in the intended format.
- **Micro-edit:** a bounded banner, notice, or redirect. Apply the micro-edit route below before preparing a full body.
- **Manual HTML paste:** required only when the user needs Confluence-specific layout or table styling that the API cannot preserve.

Do not publish if approval is absent, the source is not frozen, the manifest does not match the approved architecture, or the presentation copy contains local paths, relative links, placeholders, withdrawn-page markers, or stale draft wording.

## Core Workflow

### 4. Resolve Confluence target

- **Update existing page:** Page ID is often in the URL: `.../pages/<pageId>/Page+Title`. Use that `pageId` for `updateConfluencePage`.
- **Create new page:** Need `cloudId`, `spaceId`, and optionally `parentId`.

### 5. cloudId

Resolve the Confluence cloud UUID for your site once (see [runlayer-atlassian-mcp.md](../ba-assistant/references/runlayer-atlassian-mcp.md)) and pin it in `_workstream/atlassian-cloud-ids.json` → `confluence.cloudId` so it doesn't need re-resolving every session.

### 6. Preflight payload and links

- Measure the final body after all conversions. When it exceeds a conservative safe limit, split it before calling the API at a reader-meaningful boundary.
- Give every part its own manifest row, title, target, and visible Part A / Part B navigation.
- Replace every placeholder, relative Markdown link, local-file link, and sibling draft link using the final Confluence URL map.

### 7. Call API (no discovery hop)

- **Update:** `execute_tool` → `updateConfluencePage` with `{ cloudId, pageId, body, contentFormat: "markdown" }`.
- **Create:** `execute_tool` → `createConfluencePage` with `{ cloudId, spaceId, body, title?, parentId?, contentFormat: "markdown" }`.
- Read the source `.md` file and pass its entire content as `body`.

### Micro-edits: banners, notices, and one-line redirects

Classify the request as a micro-edit before reading or preparing a full publish payload. Then fetch one representative page in its stored format.

- If the page contains Confluence-only macros, extensions, embedded resources, or other content the requested format cannot preserve, do not replace the entire body.
- State the limitation plainly and give the user the exact short text to paste in the Confluence editor.
- Use whole-page HTML or ADF replacement only if the user explicitly asks for it after the limitation is known.
- Do not delegate a known, single-page micro-edit solely to work around this limitation.

### 8. Make links work in Confluence

Relative links (e.g. `[doc.md](doc.md)` or `../specs/feature.md`) do **not** work when the page is viewed in Confluence. Replace them with **full GitHub (or Git) URLs** for your repo so they open from Confluence:

- Repo base: `https://github.com/YOUR_ORG/YOUR_REPO/blob/main/` (adjust branch if not `main`)
- Example: `.../docs/specs/<filename>.md`

Convert all such links in the Markdown **before** publishing so the Confluence page has clickable links.

### 9. Verify and close the release

After every create or update:

1. Read the page back in its stored format.
2. Confirm title, parent, live status, reader-facing first section, and critical facts.
3. Confirm rendered tables and expected hub, child, sibling, operational-source, and internal-anchor links.
4. Record the page ID, live URL, frozen-source version, source date, reviewer, and verification date in the manifest or page registry.
5. Update the local mirror from draft to published only after these checks pass.

For historic pages, record `keep`, `banner`, `archive candidate`, or `delete candidate` before changing them. Check inbound links and obtain explicit user approval before archive or deletion. An old date is not evidence that a page is obsolete.

### 10. Optional: repo-specific publish scripts

If the project has a script (e.g. `node scripts/confluence-*.cjs`) that expands relative links to absolute GitHub URLs, use it before calling `updateConfluencePage`. **Prefer plain markdown** for tables where Confluence's markdown renderer is used (embedded HTML may show as raw text).

## Tool Reference

| Action   | Tool                       | Via Runlayer `tool_name` | Required args                          |
|----------|----------------------------|--------------------------|----------------------------------------|
| Update   | updateConfluencePage       | `updateConfluencePage`   | cloudId, pageId, body                  |
| Create   | createConfluencePage       | `createConfluencePage`   | cloudId, spaceId, body                  |
| Resolve  | getAccessibleAtlassianResources | `atlassian__getAccessibleAtlassianResources` | (none)              |

Optional: `contentFormat: "markdown"` for both update and create. For create, pass `title`, `parentId` (for child pages), and `spaceId` from the parent or space.

## Table Column Widths

Confluence Cloud ignores `colgroup` / `col` / `style="width:..."` when set via API. Use the **`data-colwidth`** attribute on every `<th>` and `<td>` element instead. This is the format Confluence's editor stores internally.

### Rules

1. **Set `data-colwidth` on every cell**, not just headers. Confluence derives column width from cell attributes, not `colgroup`.
2. **Values are unitless pixels.** The default table width is 760px. Distribute across columns proportionally.
3. **Use `data-layout="full-width"`** on `<table>` for wide tables (e.g. 4+ columns or content-heavy). The `data-colwidth` ratios still apply.
4. **Size columns to content.** ID/number columns: 40-60px. Short labels: 150-200px. Description/paragraph columns: 350-500px. Avoid equal-width defaults.

### Example (4-column table)

```html
<table data-layout="full-width">
<thead><tr>
  <th data-colwidth="40">Step</th>
  <th data-colwidth="160">Stage</th>
  <th data-colwidth="420">What happens</th>
  <th data-colwidth="140">Provider</th>
</tr></thead>
<tbody><tr>
  <td data-colwidth="40">1</td>
  <td data-colwidth="160">ABN Entry</td>
  <td data-colwidth="420">Merchant enters ABN, validated against ABR...</td>
  <td data-colwidth="140">ABR + CreditorWatch</td>
</tr></tbody>
</table>
```

### Common width presets

| Column type | Width | Examples |
|---|---|---|
| Row number / step # | 40-60px | `#`, `Step`, single-digit IDs |
| Short label | 120-180px | Status, Category, Provider |
| Medium text | 200-300px | Stage name, Check name |
| Long description | 350-500px | "What happens", "Detail", requirements |
| Full-width (2-col) | 200 + 560 | Label + description pair |

### When using `contentFormat: "markdown"`

Markdown tables do **not** support `data-colwidth`. If you need column width control, use `contentFormat: "html"` with the `data-colwidth` pattern above. Prefer HTML format for any page with tables where column proportions matter.

## Common pitfalls

- **Empty or missing arguments:** Passing `{}` or omitting `body`/`cloudId`/`pageId` causes "Unexpected end of JSON input" or similar. Always pass the full required set.
- **Relative .md links:** After publish, local paths appear as plain text or broken. Replace with full `https://github.com/YOUR_ORG/YOUR_REPO/blob/main/...` URLs in the source before publishing.
- **Wrong server:** Confluence tools go through **`user-runlayer-plugin`** (`execute_tool` direct), not legacy `user-atlassian-*` servers. Do not `search_tools` first for create/update.
- **Wrong cloudId:** Jira UUID on Confluence (or Confluence UUID on Jira) fails with "isn't explicitly granted". Use Confluence UUID for pages only.
- **Equal-width table columns:** Confluence defaults to equal widths. Always use `data-colwidth` on `<th>` and `<td>` elements when publishing via HTML. See §Table Column Widths above.

For MCP descriptor paths and exact parameter shapes, see [references/confluence-workflow.md](references/confluence-workflow.md).
