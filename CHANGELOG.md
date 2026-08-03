# Changelog

## Version 10 — 2026-08-03

Public package release. Going forward, releases are numbered **Version N** only (next: Version 11).

### Highlights

- **Unified requirements register** + Requirements Interrogator **Mode 4 (Kickoff HLR review)** with human closure before `interrogated`
- **Requirements lifecycle:** `proposed` → `interrogated` → `confirmed` (+ `blockedOn`)
- **Inline `/workboard`** (procedure + format refs) — standalone `ba-workboard` sub-skill **removed**
- **BA actions** store (`ba-actions.json` / `ba-actions-format.md`) replaces legacy `workboard.json → personal_tasks[]`
- **Full `/wrap`** closeout with BA-actions sync gate and AskQuestion runthrough
- **Miro Pass 2b** board inventory + placement; HARD pre-flight gate documented
- **AskQuestion** restored for forks, re-entry, runthroughs, and closure ceremonies (Auto-balance; model-tier nudges removed)
- **Cross-platform** workspace ops + calendar samples (Windows Outlook + macOS)
- **Upgrade script:** `tools/upgrade-ba-assistant.py` (preserves `ba-profile.mdc` and `_workstream` data)

### Breaking changes for existing installs

| Before | After |
|---|---|
| `sub-skills/ba-workboard/` | Inline `references/workboard-procedure.md` |
| `personal_tasks[]` in workboard.json | `_workstream/ba-actions.json` |
| Model-tier nudge on activity change | Removed (use Auto-balance) |

Use `tools/upgrade-ba-assistant.py --package <this-repo> --dry-run` then `--apply`.

### Also included (previously Wave 8 / Wave 9 content)

- `ba-data-investigation` data-pairing hooks
- `ba-dev-handover` gated publish to delivery repo

---

## Earlier public docs

User Guide historically covered Waves 1–7. Version 10 is the first numbered public drop that includes the later work above.
