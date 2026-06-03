# Publish Docs to Confluence

Optional companion skill for the BA Assistant. Enables `/publish-status` and other Confluence publishing commands.

## Installation

This skill requires a Confluence MCP server to be configured. Install it separately by copying your Confluence publishing skill into this directory, or create one following the MCP tool schemas for your Confluence instance.

The BA Assistant's `ba-project-canvas` and `ba-state-validator` sub-skills will invoke this skill when publishing to Confluence. Without it, the BA Assistant still works — Confluence publishing is skipped and outputs stay local.

## Required MCP tools

- `createConfluencePage`
- `updateConfluencePage`
- `getConfluencePage`
- `searchConfluenceUsingCql`
- `getConfluencePageDescendants`
