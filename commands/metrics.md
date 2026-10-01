---
description: BA Assistant — the four BA quality metrics with trends
---
Run the BA Assistant /metrics command. If `status-data.json` may be stale, run the freshness check in `~/.cursor/skills/ba-assistant/references/status-refresh.md` first (update only what is out of date). Then: `python3 ~/.cursor/_workstream/compute-metrics.py --initiative <slug>` (Windows: `py`). It computes MoSCoW coverage (overall and per scope), structural preflight first-pass rate, requirement interrogation rate and sign-off cycle time from `status-data.json`, with a 7-day trend, and caches them in `metrics-cache.json`. Show its table and warnings as they are: n/a stays n/a, never a fabricated 0%. Then AskQuestion whether to dig into a specific metric.
