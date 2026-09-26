---
description: BA Assistant — chat-thread checkpoint: capture, validate, hand over
---
Use `/wrap` to close the current chat thread cleanly. It is not an end-of-day procedure and must not refresh the workboard, scan Downloads, reconcile the calendar, or walk every BA action. Use `/workboard end-of-day` or the workboard's End of Day button for that broader operating routine.

**Never a meeting-recall pass.** File debrief or meeting content only if it was already produced in this chat. Never read `calendar-feed.json` or ask what happened in today's meetings — that systematic recall belongs to `/workboard end-of-day` (run daily), not `/wrap`.

The steps below are the full procedure. Do not open `sync-procedures.md` for `/wrap`. Read the active initiative's canonical files before writing: `SESSION-CONTEXT.md`, `initiative-tracker.md` where present, `status-data.json` where present, plus every output or debrief created or changed in this chat.

**Guiding assumption:** assume the user will never re-open this chat transcript and you will never read it again either. If something they told you, decided, or produced here isn't written to a canonical file by the end of `/wrap`, it's gone. When in doubt about whether something is "material enough" to persist, persist it.

Do these in order:

1. **Capture the chat.** Reconcile this thread against the active initiative artefacts. Ensure meeting debriefs, decisions, actions, risks, assumptions, dependencies, open questions, outputs, and material corrections raised in chat are recorded in the appropriate Markdown, JSON, or tracker artefact. Do not claim an item is captured unless the relevant file contains it.

2. **Check chat outputs.** For every material artefact, plan, decision, table, visual, or stakeholder draft produced in this chat, confirm its durable location. Persist anything that exists only in chat, unless the user explicitly asked for a chat-only draft. Do not duplicate generated display artefacts when their canonical source is already current.

3. **Validate state (chat-scoped, lightweight).** Check only the items this chat added or changed for unpromoted markers (`DEC-`, `RISK-`, `OQ-`, `ACT-`, `DEP-`) against `initiative-tracker.md`. Promote the clear ones and tag `[promoted]`; leave ambiguous items visible for the user. Do not re-diff the entire `SESSION-CONTEXT.md` or run a full `status-data.json` sweep — `/workboard end-of-day` does that across every initiative once a day, so repeating it per chat is wasted work. If an action was created or changed in this chat, sync only those BA actions and regenerate `ba-actions.md`.

4. **Checkpoint.** Update the active `SESSION-CONTEXT.md` with a dated closeout entry that states the current position, the next concrete action, open blockers, and links or paths to material outputs. Do not refresh cross-initiative status or infer workboard health. This is the last step — no handoff block.

If a requested or created output does not have a clear canonical home, say so rather than inventing one. If Jira, email, or a source system cannot be checked, record unable to check and continue.
