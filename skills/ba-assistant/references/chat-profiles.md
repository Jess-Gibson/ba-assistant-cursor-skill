# Chat profiles (doc  -  demoted from always-on rule)

**Location:** `~/.cursor/skills/ba-assistant/references/chat-profiles.md`
**Was:** `rules/chat-profiles.mdc` (alwaysApply). Demoted in the always-on restructure  -  this is user guidance, not agent instruction.

Long threads cause orchestrator drift. Use **new chats** for distinct job types instead of one mega-thread. Leave the model picker on Auto-balance; do not switch models per chat profile.

| Chat profile | Open when | Skills / rules | Stop when |
|--------------|-----------|----------------|-----------|
| **BA initiative  -  framing/shaping** | Intake, problem framing, workshops, solution options | ba-assistant (lazy) | Decision made or artefact shaped  -  new chat for delivery |
| **BA initiative  -  discovery/delivery** | Discovery, debrief, slicing detail, story writing | ba-assistant (lazy), meeting-debrief | Task done  -  new chat for next task |
| **Harness / team-repo sync** | "Sync team repo", push to shared delivery repo | `/sync-team-repo` skill only (if installed) | Push complete |
| **Status / publish / admin** | `/status`, `/canvas`, `/publish-status`, `/handover`, Jira sync, `/wrap`, `/workboard` | publish-docs-to-confluence, ba-project-canvas, ba-dev-handover | Page/ticket/handover live |
| **Quick ask** | One factual question, no initiative state | Skip BA orchestrator | Answered |

## Resume discipline

- **Same initiative, new task** → new chat + first message: `BA resume  -  [task]` (or the initiative name  -  triggers Step 2.75)
- **Mid-thread drift** → `/reanchor` or new chat (prefer new chat if >30 turns)
- **Never** rely on conversation summary alone  -  the sessionStart hook injects the SESSION-CONTEXT tail; the agent must still Read the full file on BA-resume

## Workspace note

Multi-root workspaces are supported. Classify the user's intent, not which folder is open.
