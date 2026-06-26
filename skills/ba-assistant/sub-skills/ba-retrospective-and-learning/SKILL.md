# Skill: Retrospective and Learning

## Description

The Retrospective and Learning skill captures what worked, what didn't, and
what to do differently — and ensures those learnings actually change behaviour
in the next phase or next initiative.

It runs at phase boundaries (quick), mid-initiative when something has gone
wrong (deeper), and at initiative close (comprehensive). The outputs feed
back into other skills: the Anti-Pattern Detector gains new watchlist items,
the Definition of Ready gets refined criteria, the Requirements Interrogator
learns where interrogation could have gone deeper.

The goal is not "do a retro." The goal is to make the next initiative better
than the last one.

## When to invoke

| Trigger | Mode |
|---|---|
| Pre-mortem trigger present (see Type 0 triggers above) and user accepts the offer | Type 0 (Pre-mortem) |
| User says "what could go wrong", "I'm a bit nervous about this", "let's pre-mortem this" | Type 0 (Pre-mortem) |
| Workstream-completion gate for any scope | Type 1 (lightweight) |
| Phase boundary (backwards-compatible single-scope work) | Type 1 (lightweight) |
| Mid-initiative when something has gone wrong or off track | Type 2 (deeper) |
| Significant change of direction (scope change, descope, pivot) | Type 2 (deeper) |
| After an incident or unexpected issue | Type 2 (deeper) |
| `ba-anti-pattern-detector` flags a workstream-related anti-pattern | Type 2 (deeper, scoped) |
| User says "let's pause and reflect", "what could we have done better", "how did that go", "looking back" | Type 2 (deeper) |
| Initiative close | Type 3 (comprehensive) |
| Major workstream completion (whole feature done) | Type 3 lite — comprehensive but feature-scoped |

### Scope of the retro (Wave 3)

Every retro now declares its **scope** — what is being reflected on. The scope determines who participates and what data is pulled:

| Scope | Triggered by | Typical participants | Data pulled |
|---|---|---|---|
| **Initiative** | M0 complete, M8 complete, initiative close, major scope change | Full team (PM, BA, Tech Lead, sponsor) | All modes, all features, all cohorts, all tracker items |
| **Feature** | Feature completes M6 Playback, or mid-feature pause | PM, BA, Tech Lead, feature owner | That feature's modes, cohorts/slices under it, tracker items scoped to it |
| **Cohort / Slice** | Cohort/slice completes M5 Delivery or M6 Playback | BA, Tech Lead, cohort owner | That cohort/slice's mode history, tracker items, MoSCoW changes, anti-pattern flags |

The retro output (`retro-<scope>-<date>.md`) is tagged with its scope so multiple retros can coexist without overwriting each other.

## Core principle

**Retrospectives must change behaviour.**

A retro that produces a list of observations but no concrete changes is a
waste of time. Every retro output must include:
- Specific patterns identified
- Specific actions to be taken
- Specific updates to other skills or processes
- Owners and timelines for those actions

If a learning can't be acted on, surface that as a gap — don't just record it.

## Cross-initiative learnings file

This skill is responsible for maintaining `learnings.md` at the BA assistant root.
This file is the persistent memory across initiatives — it survives initiative
close and is read by Intake_Reviewer at the start of every new initiative.

### When to write to learnings.md

- **At Type 3 (closure retro):** Always update the file with new patterns,
  watchlist items, skill refinements, and an initiative log entry.
- **At Type 2 (mid-initiative retro):** Update only when a pattern is
  confirmed (not just an incident) and the team agrees it should carry forward.
- **At Type 1 (phase / workstream-completion retro):** Do not write to learnings.md. Workstream-level
  learnings stay within the initiative.

### What to write

Only patterns, watchlist items, and skill refinements that meet these criteria:

1. **Cross-initiative applicability** — would this matter on a different initiative, or is it specific to this one?
2. **Actionable** — does this tell the next initiative to do something specific, or is it just an observation?
3. **Persistent** — is this likely to be relevant for the next 3+ initiatives, or just a one-off?

If any answer is no, the learning stays in the initiative-specific retro doc, not in learnings.md.

### Format

Append to the appropriate table in learnings.md following the format defined there. Do not bloat the file — each entry should be one line if possible.

## Four modes

### Type 0 — Pre-mortem (triggered)

**When:** Before a major decision, workstream gate, or commitment where things going wrong would be expensive. NOT triggered at every gate — only when the orchestrator detects warranted signals or the user explicitly invokes.

**Duration:** 5-15 minutes of conversation.

**Output:** 3-5 specific risks added to the tracker with mitigations.

### Triggers (proactive)

The orchestrator offers a pre-mortem when ANY of these conditions are present:

| Signal | Why pre-mortem is warranted |
|---|---|
| Regulatory keyword detected at intake (RBA, AUSTRAC, APRA, ACCC, OAIC, ATO, PSD2, GDPR) | Regulatory work has expensive failure modes |
| Customer-facing scope entering Delivery (M5) for the first time | First production exposure has unknowns no review will catch |
| Sponsor or PM has expressed hesitation in any meeting debrief in the last 14 days | Sponsor reluctance is the strongest pre-failure signal |
| A scope is being committed AND `pmApproval.status` is anything other than `approved` | Committing before approval is itself a pre-failure pattern |
| `learnings.md` flags this initiative class has previously gone off track | History of similar initiatives failing means this one carries inherited risk |
| User says "I'm a bit nervous about this", "this feels risky", "what could go wrong" | Self-reported uncertainty is high-quality signal |
| Workshop Design (Template 1 — Kickoff) is being designed for a high-stakes initiative | Better to surface fears before the room, not in it |
| A spike is being planned with >2 weeks effort | Long spikes have outcome uncertainty; pre-mortem clarifies what would constitute success |

When ANY trigger is present, propose:

> "Before we commit, want me to run a pre-mortem? 5-15 minutes. It's basically: if this goes badly, what would be the cause? Surfaces risks while we can still cheaply add mitigations."

If the user declines, log the decline in the tracker with reason. Don't offer again for the same trigger in the same session.

### Conversation pattern

Mirror Requirements Interrogator: conversation, not checklist. Start with the killer question:

> "Imagine it's three months from now and this has gone badly. What's the first thing you'd say went wrong?"

Then follow the thread. Useful prompts to draw on (pick the ones that surface real risk, not all of them):

**On the weakest link:**
- What assumption are we making that we have the least evidence for?
- If exactly one thing in our plan turned out to be wrong, which one would hurt most?
- Where are we relying on someone or something we haven't talked to recently?

**On precedent:**
- Has this kind of work failed before in this org? What was the cause?
- Are we doing something for the first time? What's the closest analogous thing that worked?
- What's a pattern in `learnings.md` that applies here?

**On exclusions:**
- Who's not in the room who should be?
- What expert opinion haven't we sought?
- What's a stakeholder group that hasn't been consulted yet?

**On timing:**
- What's the long-lead item we haven't started yet?
- If our timeline slips by 2 weeks, what breaks?
- What dependency is silently aging?

### Output format

```
Pre-mortem — <scope> — <date>
Trigger: <which trigger fired, or "user-invoked">

Imagined failure mode 1: <specific failure>
- Likelihood: <Low/Med/High>
- Impact: <Low/Med/High>
- Mitigation: <specific action — owner — by when>

Imagined failure mode 2: <specific failure>
- Likelihood, impact, mitigation as above

Imagined failure mode 3: <specific failure>
- Likelihood, impact, mitigation as above

Tracker updates: <N risks added with IDs>
```

Each imagined failure mode that gets logged becomes a 🧨 risk in the tracker with a `source: pre-mortem` tag so future retros can review which pre-mortem risks realised vs which didn't (this is itself a learning signal).

### Closing the loop

At the next workstream gate for the same scope, the orchestrator reads back the pre-mortem risks and asks: "Pre-mortem flagged these <N> risks. Status of each?" Risks that realised, were mitigated, or proved unfounded get logged. After 3+ pre-mortems, the assistant can calibrate: "your pre-mortems correctly identified <X%> of realised risks — worth doing on this initiative class."

This calibration data feeds the cross-initiative learnings — a pre-mortem that consistently catches real failures is itself an established pattern worth surfacing.

### Type 1 — Phase / workstream-completion retro (lightweight)

**When:** End of any phase, before moving to the next.
**Duration:** 5-10 minutes of conversation.
**Output:** 1-3 items to carry forward.

The phase retro is quick. Three questions:

1. What worked well in this phase that we should keep doing?
2. What slowed us down or caused rework?
3. What's one thing we'll do differently in the next phase?

Output is brief — a 3-bullet summary that updates the tracker. Don't run a
heavy retrospective here; the goal is course correction, not formal review.

### Type 2 — Mid-initiative retro (deeper)

**When:** Something has gone wrong, scope has shifted significantly, the team
is recalibrating.

**Conversation pattern:** Mirror Requirements Interrogator — conversation, not
checklist.

Start with:
> "Tell me what's not working. What's the symptom that prompted this retro?"

Then follow the thread:
- What was the original assumption that turned out to be wrong?
- When did we first notice the signal? Why didn't we act sooner?
- What was the root cause — process, information, skill, judgment?
- What would have prevented this earlier?
- What do we change now to recover, and what do we change to prevent recurrence?

Output: a recovery plan + a learning that updates other skills.

### Type 3 — Closure retro (comprehensive)

**When:** Initiative is complete or being closed.
**Duration:** 30-60 minutes of conversation.
**Output:** Full retrospective document + updates to other skills.

### Success analysis (mandatory branch in Type 3)

Type 3 retros are biased toward failure analysis by default. This branch corrects that.

For every closure retro, also walk through:

1. **What worked unexpectedly well?** Not what we planned to work — what surprised us with how well it went.
2. **What was the cause?** Process, person, tool, timing, external factor, lucky break?
3. **Is it replicable?** Could we do this on purpose next time, or was it situational?
4. **If replicable, what specifically would we do?** Concrete action — same shape as failure-side learnings.
5. **If not replicable, what was the situational factor?** Worth logging so we recognise the same conditions next time.

### Why this matters

Patterns of success are at least as valuable as patterns of failure. The retro skill's existing principle is "patterns earn changes to skills." A success pattern earns the same — a positive trigger in Anti-Pattern Detector that recognises the conditions and recommends the action.

Example: "On 3 initiatives where we did Workshop Design Template 1 with the sponsor's pre-brief done >48 hours ahead, kickoffs landed with sponsor visibly aligned. Pattern: pre-brief lead time matters. Action: make the 48h pre-brief a default, not optional, for sponsor-attended kickoffs."

### Output format extension

Add to the existing Type 3 closure retro output:

```
Successes (carry forward):

1. [Specific thing that worked unexpectedly well]
   Cause: [process / person / tool / external / luck]
   Replicable: [yes / no / situational]
   Action: [what to do next time, OR which conditions to recognise]
   Skill update: [skill name] — [what changes]

2. ...
```

Both failure patterns and success patterns get drafted as skill diffs (see "Draft the diffs" mechanism below).

Walk through each phase in turn:

1. **Phase intake / kickoff**
   - What did we get right at intake that paid off later?
   - What did we miss that we wish we'd caught?

2. **Discovery & Requirements**
   - Which requirements were genuinely understood vs assumed?
   - Where did we solution ahead of understanding?
   - Were any requirements added/removed/changed late? Why?

3. **Feature Slicing & Sequencing**
   - Did our slices deliver value as expected?
   - Did the sequencing hold up, or did we re-sequence?
   - Were critical path items started early enough?

4. **Solution Shaping**
   - Did we genuinely consider multiple options, or default to one?
   - Were our spike/ADR estimates accurate?
   - How many ADRs were reversed or revisited?

5. **Delivery Definition**
   - DoR hit rate — what % of stories were actually ready?
   - Where did rework happen, and what caused it?
   - Were AI-pairing effort estimates accurate?

6. **Playback & Enablement**
   - Did stakeholders feel informed, or surprised?
   - Were sign-offs obtained on time?
   - What landed well in playback, what didn't?

For each phase, capture:
- 1-2 things that worked
- 1-2 things that didn't
- 1 specific change for next initiative

## Tasks

1. **Identify the retro type** — phase retro / mid-initiative / closure. (Renamed from "mode" to "type" to avoid confusion with workstreams — same three retrospective shapes as before.)
2. **Run the conversation** — follow the structure for the type, but adapt
   based on what surfaces. Don't fire all questions; follow the thread.
3. **Distinguish symptoms from causes** — "the BRs were unclear" is a symptom.
   "We didn't interrogate them before designing" is the cause.
4. **Identify patterns** — not single events. "We hit this kind of problem
   three times" is more valuable than "this one thing went wrong."
5. **Define concrete actions** — what changes, who owns it, by when.
6. **Update other skills** — which skills need their watchlist or behaviour
   updated based on this retro?
7. **Produce the output** — appropriate to the retro type.
8. **Save the retro to a file** — ALWAYS write the retro output to a markdown file in the initiative's blueprints folder. File name: `retro-<type>-<date>.md` (e.g. `retro-mid-initiative-23jun.md`, `retro-phase2-15jul.md`, `retro-closure-01aug.md`). Location: `blueprints/<slug>/` alongside the initiative tracker. These files are valuable as a record of what was learned and when — don't just present in chat and lose it.

## Output formats

### Type 1 — Phase / workstream-completion retro

```
[Phase name] retro — [date]

Worked:
- [Specific thing that worked]

Didn't:
- [Specific thing that didn't]

Next phase, we will:
- [Specific change]
```

### Type 2 — Mid-initiative retro

```
Mid-initiative retro — [date]

Symptom: [what prompted this]
Root cause: [genuine cause, not surface]
When we first noticed: [date / phase]
Why we didn't act sooner: [honest reason]

Recovery:
- [Action — owner — by when]

Learnings (carry forward):
- [Pattern to watch for next time]

Skills to update:
- [Skill name] — [what changes]
```

### Type 3 — Closure retro

```
[Initiative name] — closure retrospective
Date: [date]
Duration: [from / to]

Outcome summary:
- Goal: [original goal]
- Delivered: [what was actually delivered]
- Met / partially met / not met: [verdict]

Per-phase reflections:
[Phase by phase summary using the structure above]

Top patterns identified:
1. [Pattern] — appeared in [phases] — root cause: [cause]
2. [Pattern] — appeared in [phases] — root cause: [cause]

Changes for the next initiative:
1. [Change] — owner — by when
2. [Change] — owner — by when

Skills to update:
- Anti-Pattern Detector: add watchlist for [pattern]
- Definition of Ready: refine criterion [name]
- Requirements Interrogator: deeper probing on [type of requirement]
- [Other skill]: [change]

Outcome metrics:
- Idea → engineering start: [time]
- Rework rate: [%]
- DoR hit rate: [%]
- Sign-off cycle time: [time]
- Risk realisation rate: [%]
- Stakeholder surprise: [count / nil]
```

## Typical questions to draw on

Pick the ones that surface real learning, not all of them.

### On process
- Where did we slow down for a reason we couldn't have predicted?
- Where did we slow down for a reason we could have predicted?
- What part of the lifecycle felt like it was working well?
- What part felt heavy or low-value?

### On decisions
- Which decisions look right in hindsight?
- Which decisions did we revisit or reverse? What did we learn the second time?
- Were there decisions we deferred that we should have made sooner?

### On stakeholders
- Were stakeholders informed at the right level of detail?
- Were there moments where someone was surprised? Why?
- Did we engage the right people at the right time?

### On information
- What information would have changed our approach if we'd had it sooner?
- What did we assume that turned out to be wrong?
- Where did "documented" turn out not to mean "understood"?

### On effort
- Where did effort estimates miss — over or under?
- Where did AI-pairing help vs not?
- Where did we do work that turned out not to be needed?

### On patterns
- Have we hit this kind of issue before, on this or another initiative?
- Is this a one-off, or is it a pattern worth watching for?

## Identifying patterns vs incidents

A single thing going wrong is an incident. A repeated pattern is worth changing
behaviour for. Be careful to distinguish:

- **Incident:** "We missed that the SNS event didn't carry the check results."
  Single thing, specific to this initiative. Note it, move on.

- **Pattern:** "We translated three different BRs into schema fields without
  interrogating any of them." Pattern across multiple instances. This needs
  to become a watchlist item for Anti-Pattern Detector and a deeper invocation
  of Requirements Interrogator in Discovery and Requirements.

Patterns earn changes to skills. Incidents go in the tracker for context.

## Skills update mechanism

When a retro identifies a pattern, name the specific skill update needed:

| Pattern | Skill update |
|---|---|
| Requirements translated to schema without interrogation | Anti-Pattern Detector: add trigger "schema field proposed, no interrogation output exists" |
| DoR criterion repeatedly missed | Definition of Ready: refine that criterion based on the failure |
| Stakeholder surprised by an outcome | Stakeholder Strategy: refine engagement plan for that stakeholder type |
| ADR reversed within 2 weeks | Solution Shaping: deeper probe before recommending |
| Risk realised that wasn't on the register | Risk and Tracker: refine risk identification questions |

Each pattern → specific skill → specific change. No abstract learnings.

## Draft the diffs (Wave 6 — explicit mechanism)

Every retro that identifies skill updates (Type 2 and Type 3) MUST produce drafted markdown patches alongside the narrative. Not "skills to update" lists — actual ready-to-apply patches.

### Why this is now explicit

Previously the retro identified what should change and the AI in the conversation often went ahead and edited the file. This worked sometimes but was emergent: dependent on AI judgement, session length, and whether the user noticed. Some retros produced narrative without follow-up edits.

Making the diff a first-class output ensures:
1. Every retro produces something the user can apply
2. The user reviews before applying (no silent edits)
3. The change is auditable later
4. Multiple retros across initiatives can be compared to see cumulative skill evolution

### Format

For each skill update identified by the retro, produce a section:

```markdown
### Skill update <N> — <skill file path>

**Type:** [add trigger / add row / refine criterion / add section / rewrite section]
**Reason:** [which pattern this addresses; link to retro line]

**Location:** [exact location in file — "in the Continuous monitoring trigger table, after the row for X" or "in the When to invoke section, before the X bullet"]

**Patch:**

[For additions: a markdown block showing what to insert]

[For modifications: a before/after pair]

Before:
> "Acceptance criteria are specific and testable"

After:
> "Acceptance criteria are specific, testable, AND include the negative case (what should NOT happen)"

**Validation:** [how to know it worked — e.g. "next initiative that hits this pattern should see Anti-Pattern Detector trigger this row"]
```

### Apply protocol

After the retro produces all drafted patches, end with an `AskQuestion`:

```
Drafted <N> skill updates. How do you want to handle them?
[Apply all] [Review each] [Defer — save for later] [Discard]
```

If "Apply all": the AI runs the edits in sequence, reporting after each.
If "Review each": present each patch in turn with [Apply this one] [Skip] [Modify first].
If "Defer": save the patches to `retro-patches-<date>.md` in the initiative's analysis folder. The Intake Reviewer reads pending patches at the start of the next session and offers to apply them.
If "Discard": log in tracker as a deliberate decision not to act on the retro, with reason.

### Pattern → trigger cross-reference (required field)

Each drafted patch for the Anti-Pattern Detector MUST include the pattern from `learnings.md` it derives from, by ID. The reverse is also enforced: every pattern row in `learnings.md` must reference its corresponding APD trigger ID (or be marked `no trigger — pattern is observational only`). The State Validator (Wave 5) cross-checks this consistency.

## Metrics integration (Wave 6)

Type 2 and Type 3 retros MUST pull and surface the four derivable metrics from `ba-project-canvas` (which now hosts the metrics computation). These give the retro evidence rather than relying solely on narrative recall.

### The four derivable metrics

| Metric | What it tells the retro |
|---|---|
| MoSCoW coverage rate (per scope, current and trend) | Whether prioritisation discipline held up |
| DoR hit rate (per scope, current and trend) | Whether stories were genuinely ready when picked up |
| Requirement interrogation rate | Whether requirements were challenged before being accepted |
| Sign-off cycle time (median + outliers) | Whether sign-offs were sought early and resolved cleanly |

### How they're used in the retro

1. **At Type 2 start:** Pull current values and trend. If a metric is below threshold or trending wrong, surface it as a starting point for the conversation: "DoR hit rate dropped from 80% to 55% in the last sprint. Worth digging into."

2. **At Type 3 (closure):** Pull final values for all four. Include in the outcome summary. Compare to the initiative's intake-time target if one was set.

3. **For pattern detection:** A metric trending badly across 2+ initiatives is a cross-initiative pattern. Add to `learnings.md` with `metric: <name>` tag so it's findable.

4. **For success analysis:** A metric performing unusually well is a success signal. "DoR hit rate of 95% — what specifically did we do differently?"

### Failure handling

If `ba-project-canvas` can't compute a metric (insufficient data, missing instrumentation), the retro proceeds without it but logs the gap. After 3 retros with the same metric uncomputable, the assistant surfaces: "we've not been able to compute <metric> for 3 retros — worth fixing instrumentation."

## Self-critique on the retro itself

After producing the retro output, ask:
- Did we identify patterns or just observations?
- Are the actions concrete enough to act on?
- Did we identify root causes or stop at symptoms?
- Will anything actually change as a result of this?

If the answer is no to any, dig deeper before signing off the retro.

## Challenge rules

- **System over blame** — focus on the system that allowed the issue, not the
  person. "We didn't have a check for X" is better than "Person Y missed X."
- **Specific over abstract** — "communication could be better" is useless.
  "Engineering wasn't told about the change in BR-04 until the story was in
  progress" is actionable.
- **Patterns over incidents** — single events matter, but the value of a retro
  is identifying the patterns across multiple events.
- **Actions over observations** — every learning must produce a specific
  change. If it can't, surface that as a gap.
- **Honest about what didn't change** — if a retro happens but nothing
  changes, the next retro should flag that explicitly.

## Integration with other skills

| Mode | Invoked by / triggered when |
|---|---|
| Phase retro | Phase transition (every phase → next phase) |
| Mid-initiative retro | Anti-Pattern Detector flags repeated issue / user invokes |
| Closure retro | Initiative end / handover / final playback |

| Updates to | When |
|---|---|
| Anti-Pattern Detector | When a pattern is identified |
| Definition of Ready | When DoR criteria proved insufficient |
| Requirements Interrogator | When interrogation was insufficient |
| Stakeholder Strategy | When stakeholder engagement missed |
| Risk and Tracker | When risk identification was incomplete |
| Critical Path | When sequencing failed |

## What this skill does NOT do

- Does not assign blame
- Does not produce generic retrospectives that don't change anything
- Does not skip the "what changes" question
- Does not run on a fixed schedule — it runs when meaningful learning is available

## Failure modes

| Failure | What it looks like | Mitigation |
|---|---|---|
| Generic observations | "Communication was tricky" | Push for specifics — when, with whom, what did it cost |
| No action | Long retro doc, nothing changes | Every learning must name a skill update or a specific change |
| Blame focus | "Person X dropped the ball" | Reframe to the system that allowed it |
| Single event ≠ pattern | One thing goes wrong, becomes a system change | Distinguish incident from pattern |
| Retro fatigue | Long retros that exhaust the team | Use phase retros (5-10 min) for most cases |
| Symptoms not causes | "The doc was unclear" | Root-cause: why was the doc unclear, what process produced that |
