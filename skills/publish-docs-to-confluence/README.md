# Publish Docs to Confluence

Optional companion skill for the BA Assistant. Enables `/publish-status` and other Confluence publishing commands. See [SKILL.md](SKILL.md) for the full workflow.

## Requirements

This skill needs a Confluence-capable Atlassian MCP connector configured (this repo's reference setup uses Runlayer  -  see `ba-assistant/references/runlayer-atlassian-mcp.md`). If no such connector is configured, the BA Assistant still works: Confluence publishing is skipped and outputs stay local.

The BA Assistant's `ba-project-canvas` and `ba-state-validator` sub-skills invoke this skill when publishing to Confluence.

## Required MCP tools

- `createConfluencePage`
- `updateConfluencePage`
- `getConfluencePage`
- `searchConfluenceUsingCql`
- `getConfluencePageDescendants`
