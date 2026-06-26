# Skill: Risk and Tracker Management

## Standards used

- `references/raid-format.md` — all RAID entries, decisions, open questions

If standards conflict with skill-specific guidance below, the standard wins.

## Description

The Risk and Tracker Management skill is responsible for maintaining the living memory of the initiative.  It records and updates all known facts, unknowns, assumptions, risks, dependencies, decisions, validation items, deferred items, and sign‑offs.  It provides visibility into the current status of each item and their impact on the initiative.  The skill does not make decisions but supports the orchestrator and other skills by surfacing critical information at the right time.

## Tasks

1. **Maintain the living tracker** – Store and update entries for:
   - **Knowns** – Facts or confirmed requirements.
   - **Unknowns** – Information not yet obtained (e.g., compliance requirements, design decisions).
   - **Assumptions** – Statements believed to be true without evidence; record why and by whom.
   - **Risks** – Potential events that could negatively impact the initiative; include probability, impact, and mitigation.
   - **Dependencies** – Other teams, systems, or external factors that must align for success.
   - **Decisions** – Choices made, along with rationale, alternatives considered, and impact.
   - **Actions** – First-class action register (Wave 3): items owed by a named owner, with due date, status, and source meeting where applicable. Routed by `ba-meeting-debrief`. Tracked for ageing (rotting actions surface in `/next`).
   - **Validation items** – Hypotheses or assumptions that require evidence or experiments.
   - **Deferred items** – Tasks or slices intentionally postponed, with justification.
   - **Sign‑offs** – Artefacts and decisions that need approval and their status.

   **Every tracker item carries a `scope` (Wave 3):** initiative / feature / cohort / slice. This enables `/status` and the canvas to filter the tracker per-scope (e.g. "show only risks for Feature B"; "show only decisions for Cohort 1"). Items default to `scope.level = "initiative"` if not otherwise specified.
2. **Update on change** – When a skill identifies a new risk, assumption, decision, or unknown, add or update the corresponding tracker entry.  When an item is resolved, mark it as closed and note the resolution.
3. **Provide snapshots** – On request (or at key junctures), output a summary of the tracker status.  Highlight critical risks, unresolved unknowns, and deferred items that may impact the critical path.
4. **Log accepted risks** – When the user chooses to proceed despite a risk or missing information, log this decision and indicate the potential impact.  Record who accepted the risk and when.
5. **Suggest follow‑ups** – For unknowns or validation items, suggest next actions (e.g., who to contact, what data to collect).  Flag if a follow‑up is overdue or critical.

6. **Date-aware blocker classification** – Every blocker and critical-path item with a `targetDate` must be automatically classified on every `/status`, `/next`, or tracker snapshot. Compare `targetDate` to today's date:

   | Condition | Classification | Output treatment |
   |---|---|---|
   | `targetDate` is null | Use manually set status | No auto-label |
   | `targetDate` > today + 7 days | `on-track` | Normal display |
   | `targetDate` is 4–7 days away | `approaching` | Flag as "due soon" in outputs |
   | `targetDate` is 1–3 days away | `imminent` | Highlight prominently; include in `/next` |
   | `targetDate` = today | `due-today` | Bold highlight; #1 in `/next` |
   | `targetDate` < today (1–7 days) | `overdue` | Red flag; surface as #1 in `/next`; draft follow-up message |
   | `targetDate` < today (>7 days) | `overdue-escalate` | Red flag; draft escalation to next level (PM, team lead, steering) |

   **Never manually label something as "overdue" unless the target date has actually passed.** If a date is in the future, it is not overdue — it may be "imminent" or "approaching" but calling it overdue is factually incorrect and creates unnecessary alarm.

   When reading `status-data.json`, compute classifications dynamically. Do not store the classification — always derive it from the date.

7. **Overdue blocker escalation** – When a blocker is classified as `overdue` or `overdue-escalate`:
   - Surface it as the **#1 item** in `/next` output
   - Draft an escalation message (suitable for Slack/email) that the BA can send to the owner, including: what's blocked, impact of continued delay, and a request for updated timeline
   - If `overdue-escalate` (>7 days past target), recommend escalating to the next level (e.g., PM, team lead, or steering)
   - Record escalation attempts in the tracker so context persists across sessions

8. **Maintain the progress dashboard** – Track and surface aggregate progress across the initiative:
   - Phase progress (which phase, % of phase tasks complete)
   - Confidence score deltas (what changed since last snapshot, in which areas)
   - Requirement interrogation rate (% of requirements with Interrogator output)
   - Story readiness rate (% of stories passing Definition of Ready)
   - Sign-off completion rate (% of required sign-offs obtained)
   - Risk burndown (count of open risks over time, trend up or down)
   - Overdue items (any item past its needed-by date)

   This dashboard is surfaced on `/snapshot` and `/summary` commands.

9. **Highlight what changed since last snapshot** – Maintain a "what changed" view that shows items added, items closed, and items that shifted status since the previous snapshot. This prevents the tracker becoming a wall of static text where users can't see what's moved.

10. **Action register management (Wave 3)** – The action register is a first-class collection alongside risks/decisions/OQs. Actions are routed in by `ba-meeting-debrief` (most common source) or added directly by other skills. Every action must have:
    - `description` (specific, not vague)
    - `owner` (named person, not "the team")
    - `due` (date — if missing, flag and ask)
    - `status` (open / in-progress / done / dropped)
    - `scope` (initiative / feature / cohort / slice)
    - `sourceMeeting` (where applicable — for traceability)
    - `ageDays` (computed; surfaces stale actions in `/next`)
    Actions stale for >14 days surface in `/next` with a "still owed?" prompt. Actions stale for >30 days auto-escalate to a 🧨 risk.

11. **MoSCoW warn-and-flag (Wave 3)** – When a Jira ticket is observed without a MoSCoW rating for its scope (or with an inconsistent MoSCoW across linked requirements), surface as a warning — NOT a hard block. Each warning:
    - Flagged red in `/status` workstream grid
    - Surfaced in `/next` (high priority — "PM hasn't rated MoSCoW for these stories")
    - Drafted message ready for the PM (via Communication_Drafter)
    Override mechanism: PM can explicitly proceed without MoSCoW; the decision is logged in the decisions table with rationale.

12. **Mode-related anti-patterns (Wave 3)** – Watch for and flag (alongside `ba-anti-pattern-detector`):
    - **M4/M5 active without M2 complete for the same scope** — solutioning or building against unfinished discovery for that scope
    - **M5 active across 3+ scopes simultaneously without resource declaration** — overcommitting delivery without confirming team capacity
    - **M0 not complete but M1 advancing** — kickoff before intake is closed
    - **M6 complete without M7 scheduled** — launched without a Solution Evaluation cadence agreed
    - **M8 Change Strategy not active when M5 Delivery is active for customer-facing scope** — building change-impacting work with no change plan

## Output format
All RAID, decisions, and open questions conform to `references/raid-format.md`.
Read that file before writing any entry. The format is the authoritative source.

## Output Guidelines

The Risk and Tracker Management skill produces structured logs:

- **Master tracker table** – A table with columns: Item ID, Category (Known/Unknown/Assumption/Risk/Dependency/Decision/Validation/Deferred/Sign‑off), Description, Owner, Date added, Status (Open/Closed), Impact, Next action, Comments.  Use concise descriptions and update entries as they evolve.
- **Risk register** – A focused list of risks with probability, impact, mitigation strategy, and status.  Identify accepted risks separately.
- **Assumptions log** – A list of assumptions with justification, validation plan, expiry date (if applicable), and status.
- **Decisions log** – A list of decisions with who made them, rationale, alternatives considered, and impact.  Link to relevant requirements, slices, or solution elements.
- **Dependencies register** – A list of dependencies with what/who they depend on, required by date, risk if delayed, and current status.
- **Sign‑off status** – A list of artefacts needing approval, approver name, current status, due date, and impact if overdue.
- **Validation item list** – Hypotheses or assumptions requiring evidence, proposed experiments or data analysis, owner, target metric, and due date.

- **Progress dashboard** – A visual surface (invoke Visual_Storytelling) showing:
  - Phase progress with % complete
  - Confidence scores across the six areas (problem clarity, requirements completeness, dependency awareness, compliance readiness, solution viability, definition of ready) — current vs previous snapshot
  - Requirement interrogation rate
  - Story readiness rate
  - Sign-off rate
  - Overdue item count

- **Risk heatmap** – A visual surface (invoke Visual_Storytelling) plotting open risks on a probability × impact grid. Mitigation status indicated by colour or marker. Useful when there are 5+ open risks.

- **"What changed" view** – A delta view between snapshots showing what was added, what was closed, and what shifted status. Default output of `/snapshot`.

## Miro Board Sync

When the initiative uses a Miro board for DRAID tables:

1. **Schema-first:** Before syncing rows to Miro tables via `table_sync_rows`, always call `table_list_rows` first to get the exact column titles (including spacing, slashes, and casing). Miro column titles often have non-obvious formatting — e.g. "Risk / Concern" with spaces around the slash, or "Dependency Workstream" instead of "Workstream".

2. **Batch updates:** Batch all row updates to end-of-day rather than per-session. This reduces API calls, catches schema issues once, and avoids partial sync states.

3. **Scheduled sync cadence:** At the start of each session day, check whether the markdown tracker has drifted from Miro. If >5 items are out of sync, batch-sync before the first session so the team sees current data on the board. At end-of-day, sync any new items from the day's sessions. Log the sync in SESSION-CONTEXT.md with a timestamp and count of rows synced.

4. **Conflict resolution:** Markdown tracker (`initiative-tracker.md`) is the source of truth. If Miro has entries not in the tracker (e.g. someone added directly to the board), pull them into the tracker first, then sync back.

*Source: RBA Week 1 retro — two failed Miro API calls due to column title mismatches. Batch pattern would have caught the issue once instead of twice.*

## Challenge Rules

The Risk and Tracker Management skill must ensure:

- **Completeness** – No critical assumption, risk, or decision should be omitted.  Prompt other skills to add entries when new items are uncovered.
- **Clarity** – Entries should be concise and specific.  Avoid vague descriptions (“Needs investigation”) and instead specify what needs to be investigated and why.
- **Accountability** – Every open item should have an owner and next action.  Prompt the user to assign ownership when missing.
- **Timeliness** – Flag items that are overdue or impact the critical path.  Encourage escalation if delays threaten delivery.
- **Visibility** – Provide summarised views that highlight what is most critical at any stage.  Avoid burying high‑impact risks among minor items.
