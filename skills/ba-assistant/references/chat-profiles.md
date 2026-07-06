# Chat profiles (doc — demoted from always-on rule)

**Location:** `~/.cursor/skills/ba-assistant/references/chat-profiles.md` (or docs/)
**Was:** `rules/chat-profiles.mdc` (alwaysApply). Demoted in the always-on restructure — this is user guidance, not agent instruction. D4 also adds a recommended model per profile.

Long threads cause orchestrator drift. Use **new chats** for distinct job types instead of one mega-thread.

| Chat profile | Open when | Skills / rules | Recommended model | Stop when |
|--------------|-----------|----------------|-------------------|-----------|
| **BA initiative — framing/shaping** | Intake, problem framing, workshops, solution options | ba-assistant (lazy) | **Opus + thinking** (Frame/Shape work) | Decision made or artefact shaped — new chat for delivery |
| **BA initiative — discovery/delivery** | Discovery, debrief, slicing detail, story writing | ba-assistant (lazy), meeting-debrief | **Sonnet** (bump to Opus only if gnarly) | Task done — new chat for next task |
| **Status / publish / admin** | `/status`, `/canvas`, `/publish-status`, `/handover`, Jira sync, `/wrap` | publish-docs-to-confluence, ba-project-canvas, ba-dev-handover | **Auto** (unmetered; this is mechanical work) | Page/ticket/handover live |
| **Quick ask** | One factual question, no initiative state | Skip BA orchestrator | **Auto** | Answered |

## Resume discipline

- **Same initiative, new task** → new chat + first message: `BA resume — [task]` (triggers Step 2.75)
- **Mid-thread drift** → `/reanchor` or new chat (prefer new chat if >30 turns)
- **Never** rely on conversation summary alone — the sessionStart hook injects the SESSION-CONTEXT tail; the agent must still Read the full file on BA-resume

## Model discipline (ties to references/activity-map.md)

Default the picker to **Auto** and leave it there. Bump to **Opus + thinking** when opening a framing/shaping chat; drop back to Auto when you switch to a status/admin chat. Thinking off by default everywhere else. The assistant prints a one-line model note on activity transitions (ba-profile.mdc) — it can't switch the model for you.

## Workspace note

Multi-root workspaces are supported. Classify the user's intent, not which folder is open.
