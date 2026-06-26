# Cursor slash commands & button UX — what's possible today

*Wave 4 exploration — May 2026. Based on Cursor 2.4 documentation, the skill system, and how the BA Assistant is wired.*

This document answers the question: **"Slash commands aren't always working — is there a better way? Claude has button prompts."**

Short answer: Cursor does **not** have user-side button prompts (clickable predefined-prompt chips above the input). The closest things are (a) the slash-menu picker for skills and commands, and (b) the assistant-side `AskQuestion` tool that renders clickable options inline. The BA Assistant is built around `AskQuestion` because that's the best available UX for a guided, low-typing experience.

---

## 1. What Cursor actually offers today

| Mechanism | What it is | Where it lives | UX feel |
|---|---|---|---|
| **Slash-menu picker** | Typing `/` opens a searchable menu of skills, commands, MCP tools | Built into Agent chat | Like a command palette — you pick one, the agent loads its instructions |
| **Skills** | `~/.cursor/skills/<name>/SKILL.md` with frontmatter (`name`, `description`, optional `disable-model-invocation: true`) | Global or per-workspace | Appears in slash menu; optionally auto-activates from description keywords |
| **Legacy commands** | `~/.cursor/commands/<name>.md` with frontmatter | Global or per-workspace | Appears in slash menu; prompt body is injected when picked |
| **Always-applied rules** | `~/.cursor/rules/*.mdc` (no `globs` or `alwaysApply: true`) | Loaded into every chat | Can teach the agent to honour in-chat verbs like `/status` even when not in the slash menu |
| **AskQuestion tool** | Assistant-side tool that renders clickable option chips | Built into Agent | Closest thing to "button prompts" — but the agent initiates, not the user |

**Notable absences:**

- No user-initiated button prompts (like Claude's persistent suggestion chips above the input).
- No `commands.json` registry.
- No skill-frontmatter-defined sub-commands (you can't put `/next` in a skill's frontmatter and have it become a slash entry).
- No guarantee that custom verbs like `/status` will show in the slash menu — they only do if they're defined as their own skill or command file.

---

## 2. How the BA Assistant is wired

```
LAYER 1 — Entry points (appear in slash menu)
  ~/.cursor/commands/ba-assistant.md         → "/ba-assistant" or "ba-assistant"
  ~/.cursor/skills/ba-assistant/SKILL.md     → "/ba-assistant" (skill route)

LAYER 2 — Intent routing (always-on rule)
  ~/.cursor/rules/skills-routing.mdc         → "run BA assistant", "/ba-assistant" → load this skill

LAYER 3 — Command semantics (always-on rule)
  ~/.cursor/rules/ba-profile.mdc             → defines /next, /status, /report, /publish-status, /retro, /canvas semantics

LAYER 4 — Orchestrator
  ~/.cursor/skills/ba-assistant/SKILL.md
  ~/.cursor/skills/ba-assistant/instructions.md
  ~/.cursor/skills/ba-assistant/hook-contracts.md

LAYER 5 — Specialist execution
  ~/.cursor/skills/ba-assistant/sub-skills/ba-*/SKILL.md
```

**What this means in practice:**

- `/ba-assistant` works reliably from the slash menu — it's a real entry point.
- `/next`, `/status`, `/canvas`, `/retro`, `/report`, `/publish-status` are **in-session verbs**, not standalone slash commands. They are defined in `ba-profile.mdc` and the orchestrator honours them whenever the user types them in a BA Assistant chat. They may or may not appear in the slash autocomplete — that's outside our control.
- If the slash menu doesn't autocomplete the verb, **typing the word still works** because the always-on rule teaches the agent what they mean.

---

## 3. Recommended UX for BAs (non-coders)

The BA Assistant is designed to minimise the need to remember slash commands. The pattern:

1. **Start once with the slash menu.** Type `/` → pick `ba-assistant` (or say "start BA assistant").
2. **Let the agent drive.** After every reply, the agent ends with `AskQuestion` showing clickable options. The BA clicks options instead of typing.
3. **In-session verbs are conveniences, not requirements.** If the BA forgets `/status`, the assistant will offer "see live status" as an `AskQuestion` option anyway.
4. **Form-style intake (Wave 4).** Workspace setup batches related questions into one or two screens so the BA fills a form instead of answering 8 sequential questions.
5. **Intake canvas (Wave 4).** Optional — the assistant can generate a Cursor Canvas with form fields the BA fills visually, then copies JSON back to chat.
6. **Visible status headers (Wave 4 — enforced).** Every hook prints `> Running: <skill>` so the BA always knows what's happening.
7. **Canvas for visual work.** `/canvas` (or "show me the canvas") opens the 8-tab dashboard beside the chat.

**What we promise:** entry slash works, `AskQuestion` chips after every reply, optional intake canvas, visible status headers, scope-filterable canvas, natural-language intent routing.

**What we do NOT promise:** Claude-style persistent button chips above the input, guaranteed slash autocomplete for every in-session verb, magic button-driven UI.

---

## 4. What we'd need from Cursor to do better

For a fully button-driven non-coder UX (Claude-style), Cursor would need:

- **User-initiated quick-prompt buttons** — a way for a skill to register persistent clickable buttons that appear above the input and inject a predefined prompt when clicked.
- **Skill sub-command registration** — let a skill register multiple slash entries (e.g. `ba-assistant` skill registers `/status`, `/next`, `/canvas` as menu items).
- **Two-way canvas-chat communication** — let a canvas write back to the chat or to a known JSON file the assistant auto-reads (today it's one-way display).

Until then, the BA Assistant works around these gaps using `AskQuestion`, rules-based verb honouring, and the copy-JSON pattern for the intake canvas.

---

## 5. Suggested experiments if Cursor adds features later

Track these for future waves:

| If Cursor adds | Try this |
|---|---|
| User-side button prompts | Convert `/next`, `/status`, `/canvas`, `/retro` to persistent buttons; deprecate the slash-verb pattern |
| Skill sub-command registration | Move `/status`, `/canvas`, etc. from rules to skill frontmatter so they autocomplete reliably |
| Canvas → chat back-channel | Auto-sync intake form canvas into `status-data.json` without the copy-JSON step |
| Voice input | Surface a "say your problem statement" option at intake for accessibility |

---

## 6. Quick reference for the BA Assistant

| What the BA wants to do | What works today |
|---|---|
| Start the BA Assistant | `/ba-assistant` from slash menu, or say "start BA assistant" |
| Get the next 3 actions | Type `/next`, type `next`, or click "what's next?" in an `AskQuestion` chip |
| See live status | Type `/status`, type `status`, or click an `AskQuestion` chip |
| See the visual canvas | Type `/canvas`, say "show the canvas", or click "open canvas" in an `AskQuestion` chip |
| Publish status to Confluence | Type `/publish-status` |
| Run a retro | Type `/retro` |
| Check if things are in sync | Type `/validate-state` (or old `/sync-check` — same thing) |
| Close out and checkpoint | Type `/wrap` — fixes drift, refreshes workboard, suggests new chat |
| See cross-initiative priorities | Type `/workboard` |
| Re-anchor after long thread | Type `/reanchor` — re-reads state files, resumes from current position |
| Fill intake as a form | Pick "form canvas" when the orchestrator offers it at Phase 0 |

---

## 7. Documentation pattern for future skills

When adding a new BA Assistant sub-skill that needs a user-facing verb:

1. Define the verb semantics in `~/.cursor/rules/ba-profile.mdc` (always-on, so the orchestrator honours it).
2. List the verb in the BA Assistant User Guide's command table.
3. Have the orchestrator offer the verb as an `AskQuestion` option when contextually relevant — don't rely on the user remembering it.
4. **Don't** create a standalone `.cursor/commands/<verb>.md` file unless the verb is a true entry point that should work outside a BA Assistant session.

This keeps the slash menu clean, makes verbs discoverable via `AskQuestion`, and avoids cluttering the user's command palette with 20 BA-only verbs.
