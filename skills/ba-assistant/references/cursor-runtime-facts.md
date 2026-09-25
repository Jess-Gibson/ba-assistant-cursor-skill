# Cursor runtime facts (BA Assistant)

**Audience:** cleanup / tooling agents (Claude Code or Cursor) editing this skill.
**Not** a turn-by-turn operating guide. Do not load on BA-resume unless changing harness wiring.

**Verified:** 23 Sep 2026 in a live Cursor Agent session against
[Cursor Skills docs](https://cursor.com/docs/skills.md),
[Cursor Rules docs](https://cursor.com/docs/context/rules),
and [Cursor staff forum note on description capping](https://forum.cursor.com/t/skill-descriptions-are-truncated-in-initial-agent-context/163761).

---

## Hard vs soft (read this first)

| Kind | What it is | Examples here |
|---|---|---|
| **Hard (harness)** | Cursor injects or blocks without trusting the model | `alwaysApply` rules (full body every turn); slash command body pasted into that message; lifecycle hooks in `hooks.json` / `critical-gates.mdc` |
| **Soft (convention)** | Text the model is told to follow; drift is silent | "Bootstrap: read instructions + hook-contracts"; "one primary skill"; "never read all sub-skills"; SKILL.md Step 2 resume flow |

Most of the BA orchestrator's load discipline is **soft**. Treat duplicate instructions as a documentation smell (risk of double `Read`), not as two harness loads.

---

## Facts (answered)

### 1. Router bootstrap vs SKILL.md bootstrap  -  same intent, not double inject

- `execution-router.mdc` is always-on: its **full text** is in context every turn. The line "Bootstrap: `instructions.md` + `hook-contracts.md`" is an instruction to the model.
- `ba-assistant/SKILL.md` is **not** auto-injected. Only the skill catalog entry (name + description) is preloaded; the body arrives when the agent `Read`s it or the user invokes `/ba-assistant` / `@`.
- `instructions.md` and `hook-contracts.md` enter context only via `Read` (or `@`).
- **No harness double-load.** Cost doubles only if the model `Read`s the same path twice in one turn.

### 2. Slash commands run alongside always-on rules, not instead of them

- `.cursor/commands/*.md` (e.g. `/reanchor`, `/debrief`) inject their **full command body** into that user message.
- Always-on rules (router, profile, gates) stay in context. Invoking a command does **not** suppress the orchestrator.
- Design assumption that is now safe: `execution-router.mdc` §7 owns the re-entry **card**; a command should only add **deltas** (e.g. a Downloads check), not a second full resume script.
- Cursor's `/migrate-to-skills` converts commands to skills with `disable-model-invocation: true`. A repo's BA verbs are still classic command files unless migrated.

### 3. No automatic partial file inject

- Applied rules: whole body when included.
- Skills: progressive (catalog → `SKILL.md` when relevant → references when `Read`). Documented and real.
- Agent `Read` can use `offset`/`limit`, but bootstrap text usually says "read `hook-contracts.md`", so agents pull the whole file.
- Changelog / history sections in a bootstrap file are dead weight on every intentional load.

### 4. "Never read all sub-skills" is soft only

- Not enforced by hooks or the harness.
- Long threads can quietly re-bulk-load "just in case"; nothing will flag it.
- Hard gates in this package are the ones actually registered in `hooks/hooks.json`: DoR, shared-repo leak, and the unpromoted-state stop/preCompact check. Miro preflight, em dash, and nested-PowerShell safety are written/manual guidance only  -  no hook script ships for them yet. None of this covers sub-skill Read counts.

### 5. Skill `description` frontmatter is always-on catalog cost (with a silent cap)

- Cursor (and Claude Code Agent Skills) preload skill **metadata** so the model can decide relevance. Full `SKILL.md` is on demand.
- With a large catalog (user globals + project + plugins), Cursor **silently shortens or drops** descriptions. Paths remain; `/skill-name` still works; **auto-discovery weakens**. Cap behaviour is documented by Cursor staff on the forum, not as a published max count in product docs.
- Description length matters for **every** skill under `~/.cursor/skills` and project skills, not only `ba-assistant`.

### Cursor vs Claude Code in this workspace

If your setup has an equivalent instruction telling Claude Code **not** to auto-engage BA the way a Cursor `execution-router` does, remember the facts above are about **Cursor Agent**  -  do not assume Claude Code injects `alwaysApply` rules the same way.

---

## Recommendations (cleanup priorities)

Ordered by impact vs effort. Do local (`~/.cursor/`) first; sync to a public repo only deliberately.

### P0  -  Stop duplicate instructions (cheap, high leverage)

1. **Single bootstrap owner.** Keep the "read `instructions.md` + `hook-contracts.md`" list in **one** place (`execution-router.mdc` §3 **or** `SKILL.md` Step 1). The other becomes a one-line pointer. Removes double-`Read` risk.
2. **Commands = delta on §7.** For `/reanchor`, `/next`, `/workboard`, `/status`, etc.: command file states only extras beyond the router re-entry card. Delete restated "read SESSION-CONTEXT, build the card" blocks from commands if §7 already owns them.
3. **Trim skill `description` fields.** Short; **trigger phrases first** (survive truncation). Apply to all skills in the catalog, not only this one. Prefer `/skill-name` or slash commands for must-run flows.

### P1  -  Cut bootstrap weight

4. **Split `hook-contracts.md`.** Keep active contracts + conventions in the bootstrap file. Move changelogs, deprecation narratives, and historical summaries to a separate history file (read only when editing hooks or auditing waves).
5. **Keep `SKILL.md` lean.** Point to references; do not restate router §7 or full command lists inside the skill body.

### P2  -  Discipline and discovery

6. **Periodic soft-gate check.** In long BA threads or after tooling edits, spot-check that the turn did not `Read` a pile of `sub-skills/*/SKILL.md` before the first user-visible reply. Optional later: a stop-hook that counts those Reads (only if misses keep recurring).
7. **Scope noisy skills.** Use `paths:` or `disable-model-invocation: true` for skills that should not compete in the always-visible catalog (file-specific or slash-only workflows).
8. **Do not rely on auto-discovery for critical BA verbs.** Keep `/next`, `/reanchor`, `/workboard`, `/debrief` as explicit commands (or migrated skills with disable-model-invocation).

### Explicit non-goals

- Do not invent a harness "partial load" of markdown sections; split files instead.
- Do not add always-on rules that duplicate skill bodies (always-on is the expensive path).
- Do not treat this facts file as bootstrap reading material.

---

## Sources (for re-verify)

| Source | Use |
|---|---|
| https://cursor.com/docs/skills.md | Progressive load, description, paths, disable-model-invocation |
| https://cursor.com/docs/context/rules | alwaysApply vs intelligent vs globs; full rule body when applied |
| https://forum.cursor.com/t/skill-descriptions-are-truncated-in-initial-agent-context/163761 | Silent description cap; front-load triggers; `/skill-name` guaranteed |
| Anthropic Agent Skills best practices | Metadata always / body on demand (Claude Code parallel) |
| This repo: `rules/execution-router.mdc`, `rules/critical-gates.mdc`, `commands/*.md` | Soft vs hard split for BA |

If Cursor publishes a documented catalog-size or description-budget number, update Fact 5 and drop the forum citation as primary.
