---
description: BA Assistant — read-only drift report across state files
---
Run the BA Assistant /validate-state command (skills/ba-assistant/sub-skills/ba-state-validator): read-only divergence report for the current initiative (tracker vs status-data vs SESSION-CONTEXT vs canvas vs Confluence). Offer fix options; do not auto-write initiative artefacts.

**Always include `/todo` (ba-actions):** after the drift scan, run `sync-ba-actions` per `references/ba-actions-format.md` §3. Upsert BA-owned/coordinated commitments from SESSION-CONTEXT and the tracker into `_workstream/ba-actions.json`, regenerate `_workstream/ba-actions.md`, print `Gate: ba-actions-sync`. Initiative files stay report-only until the user approves propagation.
