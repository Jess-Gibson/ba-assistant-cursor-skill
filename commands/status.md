---
description: BA Assistant — full status in chat, with quality metrics (canvas is separate: /canvas)
---
Run the BA Assistant /status command per `~/.cursor/skills/ba-assistant/SKILL.md`: sync Jira first, then give the chat status (workstream grid, critical path, blockers, living tracker). For the metrics section run `python3 ~/.cursor/_workstream/compute-metrics.py --initiative <slug>` (Windows: `py`) and show its table; do not compute the formulas by hand. Do not render the canvas or HTML snapshot here: end with an AskQuestion when it helps decide or move, offering `/canvas` if the user wants the visual. If no BA initiative is active in this workspace, say so — do not invent one.
