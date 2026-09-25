# Standards index

Reverse lookup: which standard owns which artefact format, and which skills use it.
This is a maintenance-time reference (auditing conformance, or checking whether a
standard already exists before building a new sub-skill), not something a sub-skill
needs to consult at runtime. Each sub-skill already declares the specific standards
it needs in its own "Standards used" section, that declaration is the one that
matters turn to turn.

| Standard | Owns format for | Used by |
|---|---|---|
| `references/visual-output-format.md` | All diagrams, interactive HTML, design system | all visual-producing skills (ba-visual-storytelling absorbed W10) |
| `references/canvas-data-model.md` | status-data.json schema, canvas tabs, metric computation | ba-project-canvas, all status-data writers |
| `references/user-story-format.md` | Stories, spikes, bugs, enablers, DoR checklist | ba-story-writing |
| `references/raid-format.md` | RAID, decisions, open questions | ba-risk-and-tracker, ba-discovery-and-requirements |
| `references/status-page-format.md` | Confluence status pages | ba-project-canvas (HTML snapshot) |
| `references/requirement-format.md` | Requirement register, MoSCoW matrix, JTBD | ba-discovery-and-requirements |
| `references/jira-ticket-format.md` | Cross-cutting Jira write rules (positioning file) | any project-specific Jira skill |
| `references/activity-map.md` | Activity grouping, invocation types, model tier per skill | execution-router, ba-profile, all sub-skills |
| `references/workstreams.md` | Optional M0–M8 glossary (names, purpose, scopes, states, gates) | hook-contracts labels; not loaded at orchestrator bootstrap |
| `references/canonical-ownership.md` | Which state file owns which facts; conflict rules | ba-state-validator, all state writers |
| `references/co-thinking-protocol.md` | Co-thinking before draft, AskQuestion authoring, skill handoff headers | all artefact-producing sub-skills, hook-contracts |
| `references/ears-translation.md` | How a confirmed register requirement is rendered into EARS form at handover export (source register stays as-is) | ba-dev-handover |
| `references/dev-handover-format.md` | Handover artefact shapes, handover note, shared-repo folder convention, confirmed-vs-working boundary | ba-dev-handover, ba-state-validator |
| `references/markdown-readability.md` | Stakeholder `.md` layout (enablement, comms, debriefs), dark-mode safe, Support call scripts | ba-playback-and-enablement, publish-docs-to-confluence, comms/outputs drafts |

A team publishing into its own internal shared repo (a private company workspace, not this public one) can add a repo-profile reference under `references/shared-repo-profiles/<profile>.md` documenting that repo's tree, status map, and purity rules, and add a row here pointing `ba-dev-handover` at it. No such profile ships in this public skill; the generic path in `dev-handover-format.md` §2 is the default.

Adding a standard, or a new consumer of one, updates this table in the same change.
