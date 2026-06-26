# Skill: Discovery and Requirements

## Standards used

- `references/requirement-format.md` — requirement register, MoSCoW matrix per scope, JTBD format, OOS recording, interrogator coupling
- `references/raid-format.md` — any RAID entries (assumptions, risks, open questions) raised during discovery

If standards conflict with skill-specific guidance below, the standard wins.

## Description

The Discovery and Requirements skill performs the deep work of understanding the current state, eliciting requirements, and surfacing unknowns.  It synthesises information from transcripts, stakeholder interviews, existing documents, system repositories, data sources, and operational insights.  The skill ensures requirements are captured early and updated iteratively, with clear traceability back to evidence.  It distinguishes between high‑level requirements (what we want) and lower‑level requirements (how it should behave) and organises them into functional, non‑functional, compliance/legal, data/reporting, design/content, operational/process, and acceptance categories.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (requirements register, current state map, interrogation logs, JTBD breakdowns, MoSCoW matrix). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant\SKILL.md → Co-thinking and artefact production protocol` — surface planned artefacts upfront and ask the user to select. Pair with the co-thinking journey at every interrogation point (gaps + assumptions surfaced before drafting).

## Mandatory hooks

### Hook 0 — Current State Assessment (run first if not already done)

Before extracting any requirements, this skill MUST verify that the **Current State
Assessment** (`ba-current-state-assessment`) has been completed for this initiative.

Check for a Current State Report in the project analysis folder. If one does not
exist, or if it's stale (>3 months old for fast-moving initiatives), invoke the
Current State Assessment skill FIRST. Do not proceed with requirements extraction
until the current state is properly understood.

Why: requirements extracted without grounded current state understanding tend to
restate problems, miss workarounds, ignore tribal knowledge, and conflict with
compliance controls that nobody documented. Discovery is much faster and higher
quality when it consumes a current state report instead of trying to map current
state inline.

If the user pushes back on running Current State Assessment ("we already know the
current state, just get the requirements down"), challenge once with specifics
("we know the happy path — do we know the exception flows / compliance gaps /
tribal knowledge?") and let them proceed at risk if they confirm. Log "skipped
Current State Assessment" as an assumption in the tracker.

### Hook 1 — Requirements Interrogator (per requirement)

Before any requirement is accepted into the requirements register, this skill
MUST invoke **Requirements Interrogator** in Discovery mode for that requirement.

This is the single most important hook in the entire BA assistant. Documented
requirements are not understood requirements. The Interrogator surfaces what
the requirement actually means — who the consumer is, what question they need
to answer, what already exists, what would change without it. Without this
hook, requirements get translated to design decisions on the basis of
assumptions, which is the most common and expensive failure mode in delivery.

A requirement may only enter the register once the Requirements Interrogator
has produced a **confirmed provisional requirement statement** — a statement
the user has explicitly validated as correctly capturing the underlying need.

If the interrogation surfaces that the requirement needs rethinking, is
out of scope, or should be deferred, log it in the tracker under the
appropriate category (❓ unknown, ⏳ deferred, or ⚠️ assumption) and do
not add it to the requirements register until the underlying need is
re-interrogated and a confirmed statement is produced.

## Tasks

1. **Pull existing requirements first** – Before asking the user anything, check what already exists. If MCP connections to Confluence and Jira are available, query for existing requirements pages, BRDs, epics, and stories related to this initiative. Don't ask the user to re-state what's already documented.

2. **Transcript analysis** – When the user provides a transcript (interview, workshop, meeting), run a structured analysis:
   - Extract themes by speaker and topic
   - Cluster statements into candidate requirements
   - Flag contradictions across speakers
   - Identify pain points with quantitative signals (frequency, severity)
   - Surface decisions made and decisions deferred
   - Note unanswered questions
   - Produce a candidate requirements list with evidence weighting (single source / multi-source / data-backed)

3. **Codebase discovery** – When the initiative is technical and the user has access to relevant repositories, run a codebase discovery flow:
   - Identify the services and modules in scope
   - Search by keyword for existing implementations
   - Map data flows and integration points
   - Identify what's already built that could be extended vs what needs to be new
   - Surface technical debt or constraints discovered along the way

4. **Consume the Current State Report** – Read the Current State Report produced by `ba-current-state-assessment` (hook 0). This skill no longer maps current state inline — that work belongs to the Current State Assessment skill. Use the report's pain points, tribal knowledge gaps, compliance picture, and open questions as input to requirements extraction. If anything in the report is unclear, ask Current State Assessment to clarify before extracting requirements that depend on it.

5. **Stakeholder interviews** – Generate targeted question sets for each stakeholder type (PM, compliance, legal, engineering, operations, design, service design) based on scope.  Tailor questions to *this initiative*, not generic stakeholder type templates. Capture their answers and summarise themes and gaps.

6. **Requirement extraction and interrogation** – For each candidate requirement extracted from transcripts, documents, current state analyses, or stakeholder responses:
   - **Invoke Requirements Interrogator** in Discovery mode
   - Only requirements with a PROCEED verdict enter the register
   - Each requirement carries: identifier, provisional statement (from Interrogator), evidence weight, source, dependencies, acceptance criteria (if known), confirmed by whom
   - Classify by type (functional / non-functional / compliance-legal / data-reporting / design-content / operational-process / acceptance)

7. **Missing requirement detection** – Identify when a requirement has not been explicitly stated but is implied or needed.  Ask probing questions to surface it.  Note requirements that cannot yet be answered and log them as unknowns.

8. **Evidence gathering** – Suggest data queries or analysis to validate assumptions or quantify pain points. Provide concrete query templates where the data source is known (e.g., Snowflake query for volume, Sumo query for error rate).

9. **Requirements documentation** – Produce both high-level and lower-level requirement lists with unique identifiers and traceability to evidence.  Ensure compliance/legal requirements are captured separately. Every requirement links back to its Interrogator output and evidence source.

10. **Hand-off and updates** – Pass the requirement set to other skills (e.g., slicing, solution shaping) and update it as new information emerges.  Highlight any requirement changes that impact scope or solution direction. When a requirement changes after a solution exists, invoke Requirements Interrogator in Rethink mode.

11. **Canonical document rule** – When creating a new requirements register or consolidating requirements from multiple sources:
    - **In the same session**, mark any superseded documents with a prominent "SUPERSEDED" banner pointing to the new canonical document
    - Update `confluence-pages.json` with any new pages and mark superseded entries with a `note` field
    - Update `SESSION-CONTEXT.md` file index to reflect which document is authoritative
    - If the superseded document exists on Confluence, update it with the superseded banner in the same session — do not defer this cleanup
    - The goal is: at the end of any session that creates a canonical document, there should be **zero ambiguity** about which document to read for requirements

12. **Requirements lifecycle states** – Every requirement in the register carries a state. State transitions are recorded with date, owner, and reason (lightweight change history — not full requirements management tooling).

    **Lifecycle states:**

    | State | Meaning | Set when |
    |---|---|---|
    | `proposed` | Stated by a stakeholder; not yet interrogated | A candidate requirement is extracted from a transcript, doc, or conversation |
    | `interrogated` | Requirements Interrogator has produced a provisional statement | Discovery mode interrogation complete |
    | `accepted` | PM/PO has explicitly confirmed the provisional statement | User has explicitly validated the provisional statement |
    | `in-flight` | Story exists in Jira; development started | First story moves to In Progress |
    | `delivered` | All linked stories Done; feature shipped | Last story moves to Done + deployed |
    | `evaluated` | Solution Evaluation has measured outcome vs target | Solution_Evaluation skill has produced its report for this requirement |
    | `deferred` | Acknowledged but explicitly not progressing this cycle | Decision logged |
    | `rejected` | Determined not to be a real requirement; will not progress | Decision logged with rationale |

    **Change history per requirement** — keep a lightweight log inline with each requirement:

    | Date | From state | To state | Reason | Owner |
    |---|---|---|---|---|

    Also log: *content changes* (when the wording or scope of the requirement changes). Each change carries date, what changed, why, and triggers `Requirements_Interrogator` in **Rethink mode** automatically.

    **Why this matters:**
    - Sponsor and stakeholders can see which requirements are mature (accepted/in-flight/delivered) vs immature (proposed/interrogated)
    - Solution Evaluation knows what to evaluate (only `delivered` requirements)
    - In-flight requirement changes are surfaced and trigger impact assessment (preventing silent scope drift)
    - Retro can analyse where the most drop-off happens (e.g. "lots of `proposed` requirements never reached `accepted` — why?")

    **What this is NOT** — this is not a full requirements management tool. No version trees, no traceability matrices to atomic test cases. Just state + lightweight change history.

13. **MoSCoW per scope (matrix) — Wave 3** – Every requirement carries a **MoSCoW matrix**: rather than a single Must/Should/Could/Won't rating, each requirement is rated separately for each scope it applies to (initiative, each feature, each cohort/slice). The PM (or PO) is the source of truth for MoSCoW ratings. The BA captures and structures them.

    **Rating values:**

    | Rating | Meaning | Effect on delivery gate |
    |---|---|---|
    | **Must** | Required for this scope to ship; without it, scope is incomplete | Blocks scope sign-off if not delivered |
    | **Should** | Important; should be in unless there's a strong reason to drop | Surfaces in gate review; descope must be logged as decision |
    | **Could** | Desirable; included if capacity allows | Optional — no gate impact |
    | **Won't** | Explicitly out of scope this cycle | Excluded from delivery; logged in deferred items |

    **Matrix structure (recorded per requirement):**

    | Requirement | Initiative | Feature A | Feature B | Cohort 1 (under B) | Cohort 2 (under B) | Slice X |
    |---|---|---|---|---|---|---|
    | REQ-001 (KYB check) | Must | — | Must | Must | Should | — |
    | REQ-002 (Audit log) | Must | Must | Must | Must | Must | Must |
    | REQ-003 (Pre-fill data) | Could | — | Should | Must | — | Could |

    Each cell records: rating, ratedBy (the PM/PO who set it), date, and rationale (optional but encouraged for Must/Won't).

    **Capture flow:**
    1. When a requirement moves to `interrogated` state (after Requirements_Interrogator runs), prompt the PM with: *"What's the MoSCoW for REQ-XXX in each of these scopes: [list scopes]?"*
    2. If the PM gives a single rating without scope context, ask: *"Does this Must apply at initiative level (every scope must deliver it), or only at certain scopes?"*
    3. Default to the most senior known scope (initiative) if the PM is unable to scope-rate yet. Flag as `needs scoping` in the matrix.
    4. Recapture when a new scope (feature/cohort/slice) is added — prompt the PM to rate existing requirements for the new scope.

    **Warn-and-flag gate (Wave 3 — not a hard block):**
    - Any Jira story being moved into `In Progress` without a MoSCoW rating for its scope triggers a **warning** (red in `/status` workstream grid, flagged in Tracker tab → MoSCoW warnings section).
    - The PM can explicitly proceed (override) — the decision is logged in the decisions table with rationale.
    - The warning persists in `/status` and on the canvas until either the MoSCoW is rated or the override is logged.
    - Stories with `Won't` rating for their scope auto-flag as anti-pattern ("building something explicitly out of scope").
    - Stories with `Could` rating that are blocking critical-path delivery for a `Must` requirement flag as anti-pattern ("low-priority work blocking high-priority").

    **Why this matters:**
    - The same requirement can be Must for one cohort but Could for another (e.g. for KYC/KYB Project 002, "Audit log" is Must for the Existing OIP cohort but Could for the New OP cohort).
    - Forces the PM to commit to scoping decisions explicitly rather than rolling forward with ambiguity.
    - Gives the BA defensible evidence in playback about why specific scope was/wasn't delivered.
    - Surfaces MoSCoW gaps automatically rather than discovering them at delivery review.

    **What this is NOT** — this is not budget allocation, story estimation, or sprint planning. MoSCoW captures intent ("how important is this for THIS scope"), not capacity.

## Typical Questions to Ask

- **Current state understanding:**  What are the current processes involved in this scope?  Which systems or services are used?  Where does data flow?  What manual or workaround steps exist?  What pain points or failure modes have been reported?  Are there documented process maps or do we need to create them?
- **Stakeholder elicitation:**  For each stakeholder type, ask relevant questions:
  - *PM/Product*: What outcome are we targeting?  What defines success?  What cannot change?  What trade‑offs are acceptable?
  - *Compliance/Legal*: What regulations or policies apply?  Are there minimum/maximum retention periods?  Do we need audit trails, consents, or approvals?
  - *Engineering*: Which systems are impacted?  What unknowns exist technically?  What data is stored where?  What architectures are feasible?  What spikes are needed?
  - *Operations*: How is the process executed today?  Where do things break?  What tools and workarounds are used?  What would make it easier?
  - *Design/Service*: What user journeys are affected?  Do we need new UI or content?  What is the desired user experience?
- **Requirement capture:**  What must the system do to solve the problem?  Are there constraints on performance, latency, availability, scalability?  Are there security or privacy requirements?  Are there data reporting requirements?  Are there operational support requirements?  Are there design content requirements?  What are the acceptance criteria?
- **Missing inputs:**  What have we not asked?  Who else should we talk to?  What data might confirm or disprove our assumptions?  Are there unspoken requirements we’re assuming?

## Output format
Requirements, MoSCoW matrices, and JTBD entries conform to `references/requirement-format.md`. Read that file before writing any requirement entry. The format is the authoritative source.

## Output Guidelines

The Discovery and Requirements skill should produce:

- **Current state map definitions** – For each process/system/data flow, describe the current state in bullet form and provide diagram definitions in Mermaid or PlantUML.  Include pain points and failure modes.
- **Stakeholder interview summaries** – A table or bullet list capturing each stakeholder’s key points, open questions, and any requirements they specified.
- **Requirements lists** – Two lists:
  - *High‑level requirements*: broad statements of intent that align with the problem and solution scope.
  - *Lower‑level requirements*: detailed behaviour, including functional requirements (features/capabilities), non‑functional requirements (performance, security, availability), compliance/legal requirements, data/reporting requirements, design/content requirements, operational/process requirements, and acceptance considerations.
  Each requirement should include: identifier (e.g., REQ‑001), description, type, priority (high/medium/low — legacy field, retained for cross-system compatibility), source, dependencies (if any), acceptance criteria (if known), **lifecycle state** (proposed / interrogated / accepted / in-flight / delivered / evaluated / deferred / rejected), a **change log** (date | from state | to state | reason | owner; plus any content changes), and a **MoSCoW matrix** (per scope — initiative / each feature / each cohort or slice — see Task 13).
- **Missing requirements log** – A list of requirements that are suspected or implied but not yet confirmed.  For each, note the stakeholder to consult and questions to ask.  Mark them as unknowns in the tracker.
- **Evidence suggestions** – Recommended data queries or analysis to validate assumptions and quantify pain points.  Describe what data to collect and what metrics to analyse.

## Challenge Rules

The Discovery and Requirements skill must ensure completeness without drowning in detail:

- If transcripts or documentation are absent, note that limitation and suggest stakeholder interviews or data analysis to fill gaps.
- If requirements are stated vaguely, prompt for measurable criteria or specific conditions (“What volume should the system handle?”).  If the user cannot answer, record it as a missing requirement.
- Distinguish between what is stated and what is assumed; challenge assumptions and encourage validation.
- Encourage data‑driven thinking: ask if there is data to support pain points or success metrics.  Suggest simple analysis tasks.
- Do not commit to solution directions; remain focused on understanding the problem and what is needed.

---

## Experiment and Validation (Wave 3 — merged from ba-experiment-and-validation)

This section absorbs the former `ba-experiment-and-validation` skill. Experimentation is part of the discovery loop — every assumption surfaced in Discovery and Requirements is a candidate for an experiment, POC, or data analysis to validate before it becomes a requirement. Keeping these as separate skills meant the BA had to deliberately switch context to validate something they'd just discovered.

### Experiment description

The Experiment and Validation work encourages evidence-based decision making. It proposes experiments, proof-of-concepts (POCs), and data analyses to validate assumptions, reduce risk, and confirm whether solutions will achieve desired outcomes. The skill integrates product thinking with analytics, focusing on what data is needed, how to collect it, and how to interpret it. It helps avoid overbuilding and ensures decisions are informed by real evidence rather than guesswork.

### Experiment tasks

1. **Identify assumptions and hypotheses** — Review the requirements (especially `proposed` and `interrogated` lifecycle states), slicing, and solution documents to identify assumptions that require validation (e.g., "Users will adopt the new flow," "System X can handle double the throughput," "Reducing the error rate by 20% will improve satisfaction"). Each assumption is recorded in the tracker (⚠️ Assumption) with a `validation` field pointing to its experiment plan.
2. **Propose experiments or POCs** — For each assumption or hypothesis, suggest an appropriate experiment or POC. Define what will be measured, how to measure it, and what success looks like. Experiments can include usability tests, A/B tests, shadow traffic tests, or small pilots with a subset of users.
3. **Define metrics** — Specify the success metrics and thresholds for each experiment. Align metrics with the success criteria defined in intake (problem framing) and with MoSCoW ratings (Must requirements need stronger validation).
4. **Plan data collection** — Describe how data will be collected: what tracking needs to be implemented, which databases or logs to query (invoke `pm-data-analyst` for warehouse queries), and whether any tooling changes are required.
5. **Interpretation guidelines** — Provide guidance on how to interpret results. Warn about common pitfalls (small sample sizes, biased samples, confounding variables) and suggest how to draw conclusions.
6. **Update decisions** — Based on experiment outcomes, recommend whether to proceed, iterate, or abandon a solution. Update the RAID and decision logs with findings. If the experiment invalidates an assumption underlying a requirement, trigger `Requirements_Interrogator` in **Rethink mode** for that requirement.

### Experiment typical questions

- What assumptions are we making that could materially impact the success of this initiative? How can we validate them?
- What experiments or POCs can we run to validate these assumptions? Can we run them without building the entire solution?
- What user data or metrics will tell us whether the solution meets our objectives? How should we track these metrics?
- How will we run the experiment (time-boxed pilot, A/B test, synthetic load test)? Who will be involved? What is the timeline?
- What would success look like? What threshold or change would indicate that our assumption is correct or incorrect?
- How will we collect data? Do we need to add instrumentation? Who will analyse the results?
- What are potential biases or pitfalls in this experiment? How can we mitigate them?
- How will experiment results feed back into requirements, slicing, or solution decisions? What decisions depend on these outcomes?

### Experiment outputs

- **Assumption and hypothesis list** — A list of key assumptions/hypotheses with their potential impact and whether they are validated, refuted, or untested. Link each assumption to the requirement(s) or solution element(s) it affects.
- **Experiment/Pilot plan** — For each assumption, define:
  - *Objective* (what you want to learn or validate)
  - *Method* (A/B test, pilot, usability test, technical POC)
  - *Metrics* (quantitative and qualitative)
  - *Success criteria* (thresholds or expected changes)
  - *Duration* (how long the experiment runs)
  - *Data collection plan* (what to log, how to instrument, who analyses — invoke `pm-data-analyst` if warehouse data is involved)
  - *Ownership* (who is responsible)
- **Results interpretation guidance** — A short guideline on how to analyse experiment data, what constitutes meaningful results, and how to avoid misinterpretation.
- **Decision recommendations** — Based on the outcomes, recommend actions (continue, iterate, pivot, stop). Update the tracker with the decision and rationale. If the experiment changes a requirement's understanding, trigger `Requirements_Interrogator` Rethink mode.

### Experiment challenge rules

- **Avoid purely qualitative assumptions** — Encourage quantifiable tests where possible. If qualitative input is necessary (user interviews), suggest structured methods and sampling strategies.
- **Warn about common pitfalls** — Small sample sizes, lack of control groups, confounding factors, measurement bias. Suggest ways to mitigate or interpret results cautiously.
- **Tie back to metrics** — Ensure experiments link to the KPIs or success metrics defined earlier. If metrics are missing, prompt to define them.
- **Iterate** — If an experiment fails or results are ambiguous, suggest revising and running another test rather than abandoning the initiative entirely.
- **Communicate results** — Advise on how to present experiment outcomes to stakeholders (via `Communication_Drafter` for messaging and `Visual_Storytelling` for charts), emphasising what was learned and how it impacts the plan.

### Migration note (Wave 3)

This content was previously the `ba-experiment-and-validation` skill. The standalone skill is now a SUPERSEDED marker; all experimentation work runs in-line with discovery and requirements.
