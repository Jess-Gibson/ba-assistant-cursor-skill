# Miro Board Analysis

Optional companion skill for the BA Assistant. Enables workshop board creation, DRAID table sync, and board content extraction.

## Installation

This skill requires a Miro MCP server to be configured. Install it separately by adding the Miro MCP skill from the Cursor marketplace or your organisation's skill repository.

The BA Assistant's `ba-workshop-design`, `ba-risk-and-tracker`, and `ba-meeting-debrief` sub-skills will invoke this skill when working with Miro boards. Without it, the BA Assistant still works — Miro operations are skipped and outputs stay as markdown in chat.

## Required MCP tools

- `layout_create`
- `layout_read`
- `board_list_items`
- `table_sync_rows`
- `table_list_rows`
