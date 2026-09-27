---
description: BA Assistant — the four BA quality metrics with trends
---
Run the BA Assistant /metrics command: `python3 ~/.cursor/_workstream/compute-metrics.py --initiative <slug>` (Windows: `py`). It computes MoSCoW coverage (overall and per scope), DoR hit rate, requirement interrogation rate and sign-off cycle time from `status-data.json`, with a 7-day trend, and caches them in `metrics-cache.json`. Show its table and warnings as they are: n/a stays n/a, never a fabricated 0%. Then AskQuestion whether to dig into a specific metric.
