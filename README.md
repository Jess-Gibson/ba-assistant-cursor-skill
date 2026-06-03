# BA Assistant for Cursor

A comprehensive Business Analysis assistant built as a Cursor skill. Designed to support BAs through the full initiative lifecycle — from intake and discovery through delivery, playback, and retrospective.

> Originally designed and built by **Jess Gibson**, Senior BA at MYOB (2025–2026).
> Built iteratively across real BA initiatives using agent-assisted development.

---

## What it does

The BA Assistant is an AI-powered BA thinking partner that runs inside [Cursor](https://cursor.com). It provides:

- **Guided intake** — structured Phase 0 intake with multi-source context gathering (Confluence, Jira, Glean, web)
- **Living tracker** — automatic RAID (Risks, Assumptions, Issues, Dependencies, Decisions) tracking across all phases
- **Feature slicing before stories** — enforced sequencing: problem understanding, current state, requirements, slicing, then delivery definition
- **Interactive project canvas** — 8-tab dashboard with workstream grid, RAID, metrics, and timeline
- **Meeting debrief** — process transcripts into decisions, actions, risks, and requirement changes
- **Workshop design** — 9 facilitation templates from kickoff through change management
- **Anti-pattern detection** — passive monitoring for premature solutioning, scope creep, and missing analysis
- **Retrospectives** — structured learning capture that feeds back into future initiatives
- **Confluence/Jira integration** — status page publishing, ticket creation, and live sync via MCP

### 21 active sub-skills

| Phase | Skills |
|-------|--------|
| Intake | Intake Reviewer |
| Kickoff | Workshop Design |
| Discovery | Current State Assessment, Discovery & Requirements, Requirements Interrogator |
| Slicing | Feature Slicing & Sequencing |
| Solution | Solution Shaping |
| Delivery | Delivery Definition, Jira Sync |
| Playback | Playback & Enablement |
| Evaluation | Solution Evaluation, Retrospective & Learning |
| Change | Change Strategy |
| Cross-cutting | Risk & Tracker, Stakeholder Strategy, Sponsor Engagement, Anti-Pattern Detector, Context Capture, Meeting Debrief, Visual Storytelling, Project Canvas, State Validator |

### Key commands

| Command | What it does |
|---------|-------------|
| `/next` | Top 3 next actions by urgency |
| `/status` | Full current state with canvas and HTML snapshot |
| `/canvas` | Generate/refresh the interactive project dashboard |
| `/report` | Full structured deep-dive report |
| `/retro` | Trigger a retrospective |
| `/reanchor` | Re-read state files when the assistant drifts |

---

## Quick start

```bash
# Clone into your Cursor skills directory
cd ~/.cursor/skills
git clone https://github.com/Jess-Gibson/ba-assistant-cursor-skill.git ba-assistant
```

Then follow the full setup guide in [SETUP.md](SETUP.md).

---

## Requirements

- **Cursor IDE** with Canvas support
- **Jira MCP** and **Confluence MCP** servers configured (recommended)
- Optional: Miro, Glean, Snowflake MCPs

See [SETUP.md](SETUP.md) for detailed installation steps and [CUSTOMIZATION.md](CUSTOMIZATION.md) for personalization options.

---

## Architecture

```
skills/ba-assistant/
  SKILL.md                    # Orchestrator — bootstrap, welcome panel, workstream model
  instructions.md             # Operating principles, phases, commands, tone
  hook-contracts.md           # Inter-skill API registry
  learnings.md                # Cross-initiative patterns (grows over time)
  references/                 # 7 artefact format standards
  sub-skills/                 # 21 active skills + 7 redirect stubs
rules/                        # 10 Cursor rules for routing, behaviour, and session management
hooks/                        # Cross-platform session hooks (PowerShell + Bash)
blueprints/                   # Starter project folder convention
```

---

## License

This project is shared for use by Business Analysts. Attribution to the original author is appreciated.

---

## Contributing

Found something that could be better? PRs welcome. The BA methodology in the sub-skills is based on BABOK, ADKAR, and real-world initiative experience — if you have patterns to contribute, the `/retro` flow is designed to capture exactly that.
