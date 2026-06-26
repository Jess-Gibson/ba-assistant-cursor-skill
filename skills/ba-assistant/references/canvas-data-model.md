# Canvas Data Model Standard

**Location:** `~/.cursor/skills/ba-assistant/references/canvas-data-model.md`
**Owner:** ba-project-canvas (this file is its data layer specification)
**Last reviewed:** 2026-06-01
**Status:** ACTIVE â€” content migrated from ba-project-canvas/SKILL.md (Wave 7 Patch 2a)

This file is the canonical source for the `status-data.json` schema, the canvas tab structure, and the metric computation rules. Any sub-skill writing to `status-data.json` or producing canvas output MUST conform to this standard.

---

## 1. Files this standard governs

| File | What it is | Owner |
|---|---|---|
| `status-data.json` | Structured machine-readable state for the initiative | This standard |
| `<initiative>.canvas.tsx` | Interactive React canvas, regenerated from `status-data.json` | This standard |
| `status-snapshot.html` | Static HTML export of the canvas, for sharing | This standard |
| `metrics-cache.json` | Cached metric computations (1-hour TTL) | This standard |

### File location

```
blueprints/<initiative>/status-data.json
```

### Why a structured data model exists

Without a data model, the same facts (ticket statuses, blocker states, dates, decisions, MoSCoW ratings, workstream states) are maintained independently in 4+ places:
- `SESSION-CONTEXT.md`
- `status-snapshot.html`
- `*.canvas.tsx`
- Confluence status page

This leads to drift, multi-file correction sessions, and missed updates. A structured data model eliminates this: change `status-data.json` **once**, all downstream outputs re-render from it.

---

## 2. status-data.json schema

The schema below is the canonical shape. Sub-skills that write to `status-data.json` follow it exactly. The Anti-Pattern Detector flags any write that introduces fields not defined here or omits required fields.

### Scope identifier convention

Tracker items, requirements, MoSCoW ratings, and workstreams can be tagged with a `scope` object. Scope has four levels:

```json
{
  "level": "initiative | feature | cohort | slice",
  "id": "string (e.g. 'initiative' | 'feature-b-full-t2p' | 'cohort-1-existing-oip-lt-12mo' | 'slice-quick-t2p-prefill')",
  "parentId": "string (the parent scope id; null for initiative-level)"
}
```

If a tracker item applies to the whole initiative, `scope.level = "initiative"`. If it applies to one feature, `scope.level = "feature"`. If it applies to one cohort or slice within a feature, `scope.level = "cohort"` or `"slice"` and `parentId` points to the feature.

### Top-level structure

```jsonc
{
  "version": "1.0",
  "computedAt": "2026-05-30T16:10:00+13:00",

  "initiative": {
    // identity, sponsorship, approval state, workspace config
  },

  "sourcesSearched": {
    // MCP source acknowledgement from intake
  },

  "workstreams": {
    // per-scope workstream state grid
  },

  "scopes": [
    // list of scopes within this initiative
  ],

  "features": [],
  "cohorts": [],
  "slices": [],

  "modes": {
    // initiative-level modeStates (backwards-compat alias for workstreams)
  },

  "narrative": "string â€” 2-4 sentence 'Where We Are' summary",
  "lastWeek": [],
  "thisWeek": [],

  "confidenceScores": {
    // the 6 confidence scores with history
  },

  "confidence": [
    // flat confidence array (backwards-compat alternative to confidenceScores)
  ],

  "criticalPath": [],
  "blockers": [],

  "requirements": [],

  "decisions": [],

  "raid": {
    "risks": [],
    "assumptions": [],
    "issues": [],
    "dependencies": []
  },

  "tracker": {
    // extended operational tracker (knowns, unknowns, actions, signoffs)
  },

  "openQuestions": [],

  "stories": [],
  "spikes": [],
  "tickets": [],

  "signOffs": [],
  "dorChecks": [],
  "milestones": [],

  "artefacts": [],
  "meetings": []
}
```

### `initiative` block

```jsonc
{
  "id": "[initiative-id]",
  "name": "[Initiative Name]",
  "slug": "[initiative-slug]",
  "code": "string (e.g. INI-001)",
  "stage": "string",
  "startedAt": "2026-04-15",
  "phase": "Phase 3 - Feature Slicing",
  "complexity": "lean | standard | full",
  "draftDepth": "minimal | standard | comprehensive",
  "lastUpdated": "YYYY-MM-DD",

  "sponsor": "[name]",
  "productManager": "[name]",
  "pm": "[name]",                    // alias â€” use productManager as canonical
  "techLead": "[name]",
  "businessAnalyst": "[Your Name]",
  "ba": "[Your Name]",              // alias â€” use businessAnalyst as canonical

  "charterUrl": "string | null",
  "jiraProjectKey": "string (e.g. PROJ)",
  "confluenceSpace": "string",
  "allInOneDocUrl": "string | null",
  "slackChannel": "string | null",

  "jiraTemplate": {
    "sourceKey": "string (e.g. PROJ-XXXX)",
    "descriptionSections": ["string"],
    "customFields": "object",
    "labels": ["string"],
    "linkPattern": "string"
  },

  "pmApproval": {
    "status": "pending",             // "pending" | "requested" | "approved" | "tbc" | "rejected"
    "approver": "[PM name]",
    "pm": "[PM name]",              // alias â€” use approver as canonical
    "requestedAt": "2026-05-20",
    "requestedDate": "YYYY-MM-DD | null",  // alias â€” use requestedAt as canonical
    "approvedAt": null,
    "approvedDate": "YYYY-MM-DD | null",   // alias â€” use approvedAt as canonical
    "version": "v3",
    "scope": "string[] â€” which v1 artefacts the approval covers (e.g. ['problem-statement','success-metrics','scope','raid-v1'])",
    "notes": "string | null â€” change requests, conditions, or context from PM"
  }
}
```

**Drift rule:** Sponsor, PM, Tech Lead names must match across every artefact. State Validator cross-checks this. The canonical source is `status-data.json â†’ initiative` (synced from intake or tracker on change).

### `sourcesSearched` block

Records which MCP sources were queried during intake and whether results were acknowledged.

```jsonc
{
  "sourcesSearched": {
    "confluence": { "searched": true, "resultsCount": 0, "vettedCount": 0 },
    "jira":       { "searched": true, "resultsCount": 0 },
    "gleanEnterprise": { "searched": true, "skipped": false, "skipReason": null },
    "gleanCode":  { "searched": true, "skipped": false, "skipReason": null },
    "web":        { "searched": true, "skipped": false, "skipReason": null, "regulatoryGateFired": false },
    "acknowledged": "YYYY-MM-DD | null (timestamp when user acknowledged the search/skip report at hook 2.6)"
  }
}
```

### `workstreams` block

Workstreams are the BA Assistant's primary state model. Each cell represents one (workstream Ã— scope) combination.

```jsonc
{
  "workstreams": {
    "intake": { "initiative": "complete" },
    "discovery": {
      "feature_cohort_a": "complete",
      "feature_cohort_b": "active",
      "feature_quick_t2p": "complete"
    },
    "solutionShaping": {
      "feature_cohort_a": "active",
      "feature_cohort_b": "not_started",
      "feature_quick_t2p": "complete"
    },
    "featureSlicing": {
      "feature_cohort_a": "complete",
      "feature_cohort_b": "not_started",
      "feature_quick_t2p": "complete"
    },
    "delivery": {
      "feature_cohort_a": "active",
      "feature_cohort_b": "not_started",
      "feature_quick_t2p": "delivering"
    },
    "verification": {
      "feature_cohort_a": "not_started",
      "feature_cohort_b": "not_started",
      "feature_quick_t2p": "active"
    }
  }
}
```

**Valid state values:**
- `not_started`
- `active`
- `delivering` (for delivery workstream only â€” implies stories are in flight)
- `blocked`
- `paused`
- `complete`

**Workstream order (canonical):**
1. `intake`
2. `discovery`
3. `solutionShaping`
4. `featureSlicing`
5. `delivery`
6. `verification`
7. `closure`

#### `modeStates` object (backwards-compatible representation)

The internal data-model field name may still be `modes` for backwards compatibility; all user-facing labels use "Workstreams". Each scope (initiative, each feature, each cohort, each slice) has its own `modeStates` object. Not all modes apply to all scope levels â€” e.g. M0 Intake only ever sits at initiative level. Set inapplicable ones to `not started` and never advance them.

```json
{
  "M0": "not started | active | paused | complete",
  "M1": "not started | active | paused | complete",
  "M2": "not started | active | paused | complete",
  "M3": "not started | active | paused | complete",
  "M4": "not started | active | paused | complete",
  "M5": "not started | active | paused | complete",
  "M6": "not started | active | paused | complete",
  "M7": "not started | active | paused | complete",
  "M8": "not started | active | paused | complete"
}
```

### `scopes` array

```jsonc
{
  "scopes": [
    {
      "id": "feature_cohort_a",
      "label": "Cohort A â€” High-risk merchants",
      "level": "feature",   // "initiative" | "feature" | "cohort" | "slice"
      "parentScope": null,
      "priority": "must",
      "isCustomerFacing": true
    },
    {
      "id": "feature_quick_t2p",
      "label": "Quick T2P pilot",
      "level": "feature",
      "parentScope": null,
      "priority": "should",
      "isCustomerFacing": false
    }
  ]
}
```

### `features`, `cohorts`, `slices` arrays

These collections provide granular scope detail with relationships. The `scopes` array above is the normalised view; these arrays carry operational detail.

```jsonc
{
  "features": [
    {
      "id": "string",
      "name": "string",
      "status": "done | in-progress | blocked | deferred | not-started",
      "summary": "string",
      "modes": "modeStates object (see above)",
      "cohortIds": ["string"],
      "sliceIds": ["string"]
    }
  ],
  "cohorts": [
    {
      "id": "string",
      "featureId": "string",
      "name": "string",
      "definition": "string",
      "obligation": "string",
      "approach": "string",
      "status": "done | in-progress | blocked | deferred | not-started",
      "modes": "modeStates object"
    }
  ],
  "slices": [
    {
      "id": "string",
      "featureId": "string",
      "name": "string",
      "rationale": "string",
      "status": "done | in-progress | blocked | deferred | not-started",
      "modes": "modeStates object"
    }
  ],
  "modes": {
    "initiative": "modeStates object â€” initiative-level modes (M0 Intake, M8 Change, etc)"
  }
}
```

### `narrative`, `lastWeek`, `thisWeek`

```jsonc
{
  "narrative": "string â€” 2-4 sentence 'Where We Are' summary",
  "lastWeek": [
    { "item": "string", "date": "YYYY-MM-DD (optional)", "scope": "scope object (optional)" }
  ],
  "thisWeek": [
    { "item": "string", "owner": "string", "atRisk": false, "scope": "scope object (optional)" }
  ]
}
```

### `confidenceScores` block

The 6 confidence scores per the SKILL.md ownership table. Each carries current value and history.

```jsonc
{
  "confidenceScores": {
    "problemClarity": {
      "current": "high",      // "unknown" | "low" | "medium" | "high"
      "history": [
        { "date": "2026-04-20", "value": "low", "trigger": "intake complete" },
        { "date": "2026-05-02", "value": "medium", "trigger": "interrogator confirmed" },
        { "date": "2026-05-10", "value": "high", "trigger": "sponsor agreement" }
      ]
    },
    "requirementsCompleteness": { ... },
    "dependencyAwareness": { ... },
    "complianceReadiness": { ... },
    "solutionViability": { ... },
    "definitionOfReady": { ... }
  }
}
```

Threshold rules for transitions: see Wave 5 SKILL.md addition `Confidence score thresholds`.

Flat alternative (backwards-compatible):

```jsonc
{
  "confidence": [
    { "area": "string", "score": "high | medium | low", "note": "string", "scope": "scope object (optional)" }
  ]
}
```

### `criticalPath` and `blockers`

```jsonc
{
  "criticalPath": [
    {
      "id": "number",
      "milestone": "string",
      "date": "string",
      "status": "done | in-progress | blocked | pending | overdue",
      "owner": "string",
      "scope": "scope object (optional)"
    }
  ],
  "blockers": [
    {
      "id": "string",
      "description": "string",
      "impact": "string",
      "owner": "string",
      "targetDate": "YYYY-MM-DD | null",
      "daysOverdue": "number (computed â€” never stored, recalculate on every read)",
      "scope": "scope object (optional)"
    }
  ]
}
```

### `requirements` array

```jsonc
{
  "requirements": [
    {
      "id": "string (e.g. REQ-001)",
      "description": "string",
      "type": "functional | non-functional | compliance | data | design | operational | acceptance",
      "source": "string",
      "lifecycleState": "proposed | interrogated | accepted | in-flight | delivered | evaluated | deferred | rejected",
      "interrogated": "boolean",
      "jtbdBreakdown": {
        "functional": "string | null",
        "emotional": "string | null",
        "social": "string | null",
        "dimensionsSolvingFor": "string"
      },
      "moscowMatrix": [
        { "scope": "scope object", "rating": "Must | Should | Could | Won't", "ratedBy": "string", "date": "YYYY-MM-DD" }
      ],
      "changeLog": [
        { "date": "YYYY-MM-DD", "type": "state | content", "fromValue": "string", "toValue": "string", "reason": "string", "owner": "string" }
      ]
    }
  ]
}
```

### `decisions` array

```jsonc
{
  "decisions": [
    {
      "id": "D-04",
      "title": "Use vendor X for ID verification",
      "date": "2026-05-12",
      "owner": "[Tech Lead]",
      "status": "confirmed",     // "tentative" | "confirmed" | "reversed"
      "scope": "feature_cohort_a",
      "rationale": "Cost 40% lower than vendor Y, integration time 2 weeks shorter, regulatory coverage matches",
      "alternativesConsidered": ["Vendor Y", "Build in-house"],
      "supersededBy": null,
      "linkedADR": "ADR-04",
      "sourceMeeting": "string | null"
    }
  ]
}
```

**Canonical source for decisions:** `initiative-tracker.md` (narrative). `status-data.json` derives the structured view via Project Canvas regeneration.

### `raid` block

```jsonc
{
  "raid": {
    "risks": [
      {
        "id": "R-12",
        "title": "Vendor ID verification capacity may be insufficient at launch",
        "likelihood": "medium",
        "impact": "high",
        "owner": "[Tech Lead]",
        "mitigation": "Pre-negotiated capacity uplift; load test against 3x expected volume",
        "status": "open",       // "open" | "mitigated" | "realised" | "closed"
        "source": "interrogator",   // "interrogator" | "pre-mortem" | "incident" | "manual"
        "createdAt": "2026-05-08"
      }
    ],
    "assumptions": [ ... ],
    "issues": [ ... ],
    "dependencies": [ ... ]
  }
}
```

### `tracker` block

The operational tracker extends RAID with knowns, unknowns, actions, and signoffs. Skills that write tracker entries use this shape.

```jsonc
{
  "tracker": {
    "knowns": [
      { "id": "string", "fact": "string", "scope": "scope object (optional)" }
    ],
    "unknowns": [
      { "id": "string", "description": "string", "owner": "string", "targetDate": "YYYY-MM-DD | null", "scope": "scope object (optional)", "ageDays": "number (computed â€” never stored)" }
    ],
    "assumptions": [
      { "id": "string", "assumption": "string", "scope": "scope object (optional)", "validation": "string | null" }
    ],
    "risks": [
      { "id": "string", "severity": "critical | high | medium | low", "risk": "string", "mitigation": "string", "owner": "string", "scope": "scope object (optional)" }
    ],
    "dependencies": [
      { "id": "string", "description": "string", "blocks": "string", "owner": "string", "scope": "scope object (optional)" }
    ],
    "decisions": [
      { "id": "string", "decision": "string", "owner": "string", "date": "string", "status": "string", "scope": "scope object (optional)", "sourceMeeting": "string | null" }
    ],
    "actions": [
      { "id": "string", "description": "string", "owner": "string", "due": "YYYY-MM-DD | null", "status": "open | in-progress | done | dropped", "scope": "scope object (optional)", "sourceMeeting": "string | null", "ageDays": "number (computed â€” never stored)" }
    ],
    "signoffs": [
      { "id": "string", "artefact": "string", "approver": "string", "status": "approved | pending | overdue", "date": "YYYY-MM-DD | null", "scope": "scope object (optional)" }
    ]
  }
}
```

### `signOffs` array

```jsonc
{
  "signOffs": [
    {
      "id": "SO-03",
      "artefact": "Legal sign-off on customer-facing decline messaging",
      "approver": "[Legal lead]",
      "scope": "feature_cohort_a",
      "requestedDate": "2026-05-25",
      "approvedDate": null,        // null while pending
      "status": "pending",          // "pending" | "approved" | "rejected" | "withdrawn"
      "linkedDecision": "D-07",
      "validUntilArtefactChanges": true
    }
  ]
}
```

**Sign-off cycle time computation:**
```
signOffCycleTime = approvedDate - requestedDate (in working days)
```

### `dorChecks` array

```jsonc
{
  "dorChecks": [
    {
      "storyKey": "PROJ-001",
      "scope": "feature_cohort_a",
      "checkedAt": "2026-05-28",
      "firstAttempt": "pass",     // "pass" | "partial" | "fail"
      "missingCriteria": []
    }
  ]
}
```

### `stories`, `spikes`, `tickets` arrays

```jsonc
{
  "stories": [
    {
      "key": "PROJ-001",
      "title": "...",
      "type": "story",          // see references/user-story-format.md for types
      "scope": "feature_cohort_a",
      "status": "In Progress",  // synced from Jira
      "moscow": "must",
      "storyPoints": 5,
      "linkedSlice": "SL-02",
      "linkedRequirements": ["BR-005"]
    }
  ],
  "tickets": [
    {
      "key": "string (e.g. PROJ-XXX)",
      "summary": "string",
      "status": "To Do | In Progress | Done | Blocked",
      "assignee": "string | null",
      "sprint": "string | null",
      "sprintEndDate": "YYYY-MM-DD | null",
      "scope": "scope object (optional)",
      "linkedRequirementIds": ["string"],
      "moscowFlag": "ok | missing | inconsistent (warn-and-flag)",
      "lastJiraSync": "ISO 8601 timestamp"
    }
  ]
}
```

### `milestones` array

```jsonc
{
  "milestones": [
    {
      "id": "M-03",
      "title": "Legal sign-off complete",
      "targetDate": "2026-06-06",
      "actualDate": null,
      "status": "on-track",       // "on-track" | "at-risk" | "missed" | "complete"
      "scope": "feature_cohort_a",
      "linkedSignOff": "SO-03"
    }
  ]
}
```

### `artefacts` and `meetings`

```jsonc
{
  "artefacts": [
    { "name": "string", "url": "string | null", "status": "string", "scope": "scope object (optional)" }
  ],
  "meetings": [
    {
      "id": "string",
      "name": "string",
      "date": "YYYY-MM-DD",
      "attendees": ["string"],
      "scope": "scope object (optional)",
      "debriefStatus": "pending | processed",
      "debriefReportPath": "string | null"
    }
  ]
}
```

---

## 3. Canvas tab structure

The canvas has 8 tabs. Each tab reads from specific `status-data.json` fields.

| Tab | Primary data source | Purpose |
|---|---|---|
| Workstreams | `workstreams` Ã— `scopes` | Grid view of state per cell |
| Features | `scopes` (level=feature) + their workstream states | Feature-level status |
| Timeline | `milestones`, `stories` (with dates), `signOffs` | Time-ordered work view |
| Tracker (RAID) | `raid.*`, `openQuestions`, `decisions` | RAID and decision narrative |
| MoSCoW | `stories` grouped by `moscow` per `scope` | Prioritisation matrix |
| Sign-offs | `signOffs` | Approval pipeline |
| Quality metrics | computed from above (see Section 4) | Quality measures |
| Intake form | `initiative` + intake summary | Reference for problem framing |

---

## 4. Metric computation rules

The 4 derivable metrics live here (per Wave 6). The Project Canvas computes these from existing state. They are surfaced in `/status`, `/snapshot`, and feed every retro automatically.

### MoSCoW coverage rate

```javascript
function mosCoWCoverageRate(scopeId) {
  const requirements = readRequirementsForScope(scopeId);  // from initiative-tracker.md
  const withRating = requirements.filter(r => r.moscow !== null);
  if (requirements.length === 0) return null;  // n/a
  return withRating.length / requirements.length;
}
```

**Source:** requirements register in `initiative-tracker.md` cross-referenced with the per-scope MoSCoW matrix in `status-data.json`. Compute per scope (initiative / each feature / each cohort). Track current value and trend (current vs 7 days ago, 14 days ago).

Compute per scope. Warning threshold: <80% on any scope with `delivery` workstream active. Surface in `/status` MoSCoW summary.

### DoR hit rate

```javascript
function dorHitRate(scopeId, windowDays = 30) {
  const checks = statusData.dorChecks.filter(
    c => c.scope === scopeId &&
         daysSince(c.checkedAt) <= windowDays
  );
  if (checks.length === 0) return null;
  const passes = checks.filter(c => c.firstAttempt === 'pass');
  return passes.length / checks.length;
}
```

**Source:** `dorChecks` array in `status-data.json` capturing every DoR run with `storyKey`, `firstAttempt: pass | partial | fail`, `date`, `scope`. Delivery Definition writes to this array on every DoR check.

Warning threshold: <70% on any scope with active delivery. Trend matters more than absolute value â€” a falling rate is the signal.

### Requirement interrogation rate

```javascript
function requirementInterrogationRate(scopeId) {
  const requirements = readRequirementsForScope(scopeId);
  const interrogated = requirements.filter(r => r.interrogationArtefact !== null);
  if (requirements.length === 0) return null;
  return interrogated.length / requirements.length;
}
```

**Source:** requirements register cross-referenced with the existence of an interrogation artefact (either inline in the requirement entry or in a separate `interrogations/` folder). Discovery and Requirements should already be writing these.

Warning threshold: <95% on any scope past Discovery completion. Below 95% means at least one requirement entered the register without challenge â€” which is the failure mode the Interrogator exists to prevent.

### Sign-off cycle time

```javascript
function signOffCycleTime() {
  const completed = statusData.signOffs.filter(s => s.approvedDate !== null);
  const times = completed.map(s => workingDaysBetween(s.requestedDate, s.approvedDate));
  return {
    median: median(times),
    p90: percentile(times, 90),
    openOver7Days: statusData.signOffs.filter(
      s => s.approvedDate === null && workingDaysBetween(s.requestedDate, today()) > 7
    ).length
  };
}
```

**Source:** sign-off entries in the tracker need both `requestedDate` and `approvedDate`. Add `requestedDate` field if not present.

Warning thresholds: median >5 working days OR any sign-off open >10 working days. Surface in `/status` and `/next`.

### Failure handling

Any metric that can't be computed returns `null`, displayed as `n/a`. Never fabricate `0%` for missing data â€” that looks like a real signal and triggers false alarms.

After 3 status outputs with the same metric `n/a`, surface a one-line nudge: "DoR hit rate has been n/a for 3 status runs â€” likely missing instrumentation in Delivery Definition. Want me to look?"

### Caching

Computed metrics are NOT stored in `status-data.json` as canonical (they're derived). They are cached in a sibling file `metrics-cache.json` with `computedAt` timestamp. TTL is 1 hour. Re-compute on:
- `/status` (after Jira sync, before the chat status text is generated)
- `/snapshot`
- `/metrics`
- Any retro invocation (Type 2 / Type 3 â€” the retro skill reads them)

Anything older than 1 hour is recomputed on next request.

---

## 5. State sync triggers

Other skills update `status-data.json` via these triggers:

| Source | Trigger | Updates |
|---|---|---|
| Jira Sync | Every `/status`, every resume, on demand | `stories[].status`, `tickets[].status`, derived workstream states |
| Project Canvas (Data Model section) | Before every canvas render | Re-derives structured view from `initiative-tracker.md` |
| Discovery and Requirements | New requirement entered | `confidenceScores.requirementsCompleteness.current` re-evaluated |
| Delivery Definition | DoR check performed | Appends to `dorChecks` |
| Sponsor Engagement | Touchpoint complete | Appends to RAID if outcomes warrant |
| State Validator | Detects drift | Reports only â€” does not auto-write |

---

## 6. Required-vs-optional fields

| Block | Required at all times | Optional |
|---|---|---|
| `initiative` | id, name, slug, phase, sponsor, productManager, businessAnalyst, pmApproval.status | techLead, startedAt, draftDepth, code, stage, complexity, charterUrl, jiraProjectKey, confluenceSpace |
| Each scope | id, label, level | parentScope, priority, isCustomerFacing |
| Each feature | id, name, status | summary, modes, cohortIds, sliceIds |
| Each decision | id, title, date, owner, status | rationale, alternativesConsidered, linkedADR, sourceMeeting |
| Each risk | id, title, likelihood, impact, owner, status | mitigation, source, createdAt |
| Each sign-off | id, artefact, approver, requestedDate, status | approvedDate (null until approved), linkedDecision |
| Each requirement | id, description, type, lifecycleState | source, interrogated, jtbdBreakdown, moscowMatrix, changeLog |
| Each ticket | key, summary, status | assignee, sprint, scope, linkedRequirementIds, moscowFlag, lastJiraSync |
| Each blocker | id, description, owner | impact, targetDate |

Anti-Pattern Detector flags writes that omit required fields.

---

## 7. Workstream state transition rules

Valid transitions:

```
not_started â†’ active
active â†’ blocked
active â†’ paused
active â†’ complete
active â†’ delivering   (delivery workstream only)
blocked â†’ active
blocked â†’ paused
paused â†’ active
delivering â†’ active   (back to non-delivery work)
delivering â†’ complete
complete â†’ active   (rare â€” rework triggered)
```

Invalid transitions are rejected. Reason for any transition that crosses a sensitive boundary (e.g. `active â†’ blocked`, `complete â†’ active`) is logged in `initiative-tracker.md` with a date.

---

## 8. Canvas regeneration rules

Project Canvas regenerates when:
- `/status`, `/canvas`, `/snapshot` invoked
- `status-data.json` mutated by any sub-skill
- A material change to `initiative-tracker.md` is detected (decisions, RAID, scope)
- End-of-session checkpoint accepted

Regeneration writes:
- `<initiative>.canvas.tsx`
- `status-snapshot.html`

Both always regenerate together. Never one without the other.

---

## 9. Output anti-patterns (Anti-Pattern Detector triggers)

| Watching | Trigger | Anti-pattern |
|---|---|---|
| Any skill | Writes to `status-data.json` field not defined in this schema | Off-schema write |
| Any skill | Writes to `status-data.json` and omits a required field | Required field missing |
| Any skill | Updates `confidenceScores` without an entry in `history` | Score change without provenance |
| Any skill | Writes a workstream state transition not in Section 7's valid list | Invalid state transition |
| Project Canvas | Regenerates `.tsx` or `.html` and `status-data.json` was not refreshed from `initiative-tracker.md` | Stale derived output |
| State Validator | Field disagreement between `initiative-tracker.md` and `status-data.json` for >24 hours | Tracker/data drift |
| Any skill | Updates a downstream output (canvas, HTML, Confluence) without also updating `status-data.json` | Bypassed single source of truth |
| Any skill | Adds a ticket to `status-data.json` without a Jira key | Untraceable ticket |
| Any skill | Skips the Jira sync before updating ticket statuses | Stale ticket data |
| Any skill | Stores computed fields (`daysOverdue`, `ageDays`, `moscowFlag`) as persisted values | Computed field stored as canonical |
| Any skill | Computes a metric as `0%` when the underlying data is missing | Fabricated zero â€” should be `n/a` |
| Any skill | Caches metrics longer than 1 hour without recomputation | Stale metric cache |

---

## 10. Migration history

Migration from `sub-skills/ba-project-canvas/SKILL.md` completed 2026-06-01 (Wave 7 Patch 2a).

**What was migrated:**
- Schema â€” scope identifier convention, main structure, modeStates object
- Metrics â€” four metric formulas, sources, thresholds, failure handling, caching rules
- Data anti-patterns
- Implementation notes and Wave 3 schema evolution history

**What stays in ba-project-canvas/SKILL.md:**
- Workflow: when to invoke, hooks, context-gathering pipeline, generation phases
- Data tasks: create/update `status-data.json`, feed downstream, date-aware computation, validation, migration
- Canvas UI: tab specifications, scope navigator, template structure, HTML snapshot, pre-delivery self-check
- Integration: BA Assistant, standalone, reference implementation

---

## 11. Versioning

This standard is at v1.0 (2026-05-30, shell created) â†’ v1.1 (2026-06-01, content migrated). When the schema evolves (new field, new workstream state, new metric), increment to v1.2, etc. Breaking changes (renamed field, removed field) require a major bump to v2.0 and a migration note in `initiative-tracker.md` for any in-flight initiatives.

---

## 12. Implementation notes

- The schema is deliberately flat and readable â€” it should be hand-editable if needed.
- `lastJiraSync` per ticket allows partial refreshes (only query tickets not synced recently).
- `daysOverdue` and `ageDays` fields are always computed, never stored â€” recalculate on every read.

---

## 13. Wave 3 schema changes summary

| Change | Why |
|---|---|
| Scope object added; can be attached to most items | Enables per-feature/per-cohort/per-slice filtering and views |
| `features[]` now has `modes`, `cohortIds`, `sliceIds` | Workstream grid per feature; cohort/slice relationships explicit. (Data-model field name stays `modes` for backwards compat; UI surfaces it as "workstreams".) |
| New `cohorts[]` and `slices[]` collections | Cohorts and slices are first-class scopes, not just labels |
| New top-level `modes` object | Initiative-level workstreams (M0 Intake, M8 Change, cross-cutting). Field name kept as `modes` for backwards compat. |
| New `requirements[]` collection with lifecycle state, JTBD breakdown, MoSCoW matrix, change log | From Wave 2 (lifecycle, JTBD) + Wave 3 (MoSCoW per scope) |
| New `tracker.actions[]` collection (action register) | First-class action items routed by Meeting Debrief, owned by Risk & Tracker |
| `tickets[]` gains `linkedRequirementIds`, `moscowFlag`, `scope` | Enables warn-and-flag for tickets without MoSCoW |
| `unknowns[]` and `actions[]` gain computed `ageDays` | Surface rotting OQs and stale actions in `/next` |
| `decisions[]`, `actions[]` gain `sourceMeeting` | Traceability back to the meeting where the item originated |
| New `meetings[]` collection | Meeting Debrief skill writes here; status surfaces undebriefed meetings |

