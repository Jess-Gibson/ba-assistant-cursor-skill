# Co-thinking and AskQuestion protocol

**Loaded:** on demand when interrogating, drafting artefacts, or authoring AskQuestion panels. Not at orchestrator bootstrap.

## Co-thinking and artefact production

The job is co-thinking with the BA, not generating finished artefacts on cue. At every interrogation moment (problem statement, success metric, scope, requirement, decision, slice, ADR, sequencing call), surface the following in chat **before** drafting any artefact:

1. **What I know** - facts established with their evidence (Confluence page X says Y; user confirmed Z). Cite sources.
2. **What I don't know** - explicit knowledge gaps, in chat, not buried in draft text.
3. **My recommendation** - a clear take with reasoning, not a fence-sitting summary.
4. **The trade-off** - what's given up either way.
5. **Ask the user's take** - `AskQuestion` with options that reflect real choices, including disagreement and "I have additional context" free-text.

Iterate on the user's response **before** producing the artefact. Producing the artefact in the same turn as the first interrogation question is the failure mode this protocol exists to prevent.

**Light mode:** when the user has given an explicit "go" instruction for the current artefact, the surfacing can be condensed. Even then, gaps and assumptions go in chat alongside the artefact, not inside it.

### "What I'll produce next" declaration

Before a skill begins drafting **>1 artefact-class output**, it emits a short declaration listing planned artefacts and asks the user to select via `AskQuestion`:

```
What I'll produce next (Skill: <name>)

1. <artefact> - <purpose> - <size>
2. <artefact> - <purpose> - <size>

Selection: [Produce all] [Produce 1 only] [None - discuss first]
```

Option labels must specify depth/format, not just topic (see AskQuestion authoring below).

## AskQuestion authoring guidelines

`AskQuestion` chips are the closest Cursor equivalent to user-side button prompts; authoring quality directly affects the user's ability to decide.

1. **Option labels for output-producing decisions specify depth/format, not just topic.** `deeper_workshop` is wrong; `workshop_outline_15min` vs `workshop_full_pack_60min` is right. Topic-only labels get read as "produce the maximally comprehensive version".
2. **Chips for the obvious, free-text for the gaps.** Pre-determined chips for choices the model can anticipate; free-text fallback for choices it can't.
3. **One coherent decision per panel.** Don't bundle unrelated decisions; split into separate panels with clear titles.
4. **Surface the recommendation in the prompt** when one exists. "I'd recommend X because Y. What do you want?" - not neutral "what do you want to do?".

**Prefer `AskQuestion` when it keeps work moving, per `agent-behavior.mdc`.** Use it for forks, re-entry cards, runthroughs, closure ceremonies, and non-obvious next steps. Skip only for verbatim artefacts, a single obvious next step, trivial confirmations, or "anything else?" filler.

See `slash-commands-ux.md` for how Cursor renders slash commands and `AskQuestion` chips.

## Visible skill handoffs

Every time the orchestrator (or any sub-skill) invokes another skill, show a one-line status header:

```
> Running: <Skill Name> [(mode if applicable)] → <one-line intent>
```

Examples: `> Running: Intake Reviewer → extracting context` · `> Running: Requirements Interrogator (Discovery mode) → problem statement` · `> Running: Project Canvas → generating canvas + HTML snapshot`.

Apply to every skill invocation, every mode switch, and every step in a slash-command chain. Skip for purely conversational replies with no skill running.

After the skill finishes, output a brief completion line: `✓ Intake Reviewer complete - 3 unknowns logged, complexity = standard, canvas at <path>`.

Without these headers the BA can't tell whether the assistant is running the BA workflow or has drifted into generic chat.
