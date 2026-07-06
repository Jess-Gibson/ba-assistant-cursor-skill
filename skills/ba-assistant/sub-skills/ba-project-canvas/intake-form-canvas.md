# Intake Form Canvas (Wave 4 variant)
<!-- Wave 10: moved verbatim from SKILL.md. Load only when offering or building the Phase 0 intake form. -->

## Intake Form Canvas (Wave 4 — NEW)

Some BAs prefer a **form-style UI** for capturing initiative intake rather than answering questions sequentially in chat. The Intake Form Canvas is a **separate canvas variant** that renders all intake fields as editable inputs in a Cursor Canvas. The BA fills the form, copies the auto-generated JSON output, and pastes it back into chat — the assistant reads the JSON and populates `status-data.json`.

### When to generate the intake form canvas

At the very start of Phase 0 (before the chat-style intake conversation), the orchestrator should offer:

```
> Running: Project Canvas → offering intake form canvas option

How would you like to capture intake context?
[ ] Chat-style — I'll ask you questions one at a time (default, recommended for first-time users)
[ ] Form canvas — I'll generate an interactive form you can fill in beside the chat (faster if you already have most context handy)
[ ] Both — generate the form canvas AND start the chat conversation in parallel
```

If the user picks form canvas or both, this skill generates `intake-form.canvas.tsx` and tells the user how to use it.

### File location

```
<workspace-root>/canvases/<initiative-slug>-intake-form.canvas.tsx
```

E.g. `canvases/sample-initiative-intake-form.canvas.tsx`.

### Template structure

The intake form canvas is a single `.canvas.tsx` file. It MUST follow these rules:

1. **Imports only from `cursor/canvas`** — same as any canvas (no fetch, no network).
2. **Uses `useCanvasState<T>(key, initial)`** for every input field so values persist as the BA edits.
3. **Renders a "Copy this JSON" panel at the bottom** that shows the current form state formatted as JSON. The BA copies it and pastes back to chat.
4. **Groups fields into sections** matching the form-style intake screens (Workspace IDs, Templates and context, Problem and metrics, Stakeholders, RAID seed).
5. **Validation cues** — fields that are required for proceeding to Phase 1 show a small `required` label; the JSON output flags any missing required fields with `"_missing": [...]`.

### Sections and fields

| Section | Field | Type | Required |
|---|---|---|---|
| **1. Workspace IDs** | Jira project key | Text | Yes |
|  | Confluence space + parent page URL | Text | Yes |
|  | All-in-one / intake doc link | URL | No |
|  | Slack / Teams channel | Text | No |
| **2. Templates and context** | Jira template story key | Text (e.g. PROJ-XXXX) | No |
|  | Use most recent story as template? | Toggle | No |
|  | Repositories in scope | Multi-line text | No |
|  | Source of intake | Dropdown (verbal / all-in-one / Confluence page / BRD / Jira ticket) | Yes |
|  | Stakeholders already involved | Multi-line text | No |
| **3. Initiative basics** | Initiative name | Text | Yes |
|  | Complexity signal | Dropdown (lean / standard / full) | Yes |
|  | Stage | Dropdown (M0 Intake / M1 Kickoff / further) | Yes |
|  | PM name | Text | Yes |
|  | BA name | Text | Yes |
|  | Tech Lead name | Text | No |
|  | Charter / brief URL | URL | No |
| **4. Problem + success metrics** | Provisional problem statement | Multi-line text | Yes |
|  | Provisional success metrics | Multi-line text | Yes |
|  | Known target customers / personas | Multi-line text | No |
| **5. Scope** | In scope | Multi-line text | Yes |
|  | Out of scope | Multi-line text | No |
|  | Dependencies known so far | Multi-line text | No |
| **6. RAID seed** | Known risks | Multi-line text (one per line) | No |
|  | Known assumptions | Multi-line text | No |
|  | Known issues | Multi-line text | No |
|  | Open questions | Multi-line text | No |

### Copy JSON panel

At the bottom of the canvas, render a section that shows the form state as JSON, ready to paste back to chat:

```
## Copy this JSON and paste it back to chat

```json
{
  "initiative": {
    "name": "Sample Initiative",
    "code": "",
    "stage": "M0",
    "complexity": "standard",
    "pm": "[PM name]",
    "ba": "[BA name]",
    "techLead": "",
    "charterUrl": "https://...",
    "jiraProjectKey": "PROJ",
    "confluenceSpace": "PROJ",
    "allInOneDocUrl": "https://...",
    "slackChannel": "#sample-initiative",
    "jiraTemplate": { "sourceKey": "PROJ-1001" }
  },
  "problem": "...",
  "metrics": [ "..." ],
  "scope": { "in": [ "..." ], "out": [ "..." ] },
  "raid": { "risks": [ ... ], "assumptions": [ ... ], "issues": [], "openQuestions": [ ... ] },
  "_missing": []
}
```
```

Use the canvas `Code` component (or equivalent) so the BA can click-to-copy.

### Honest limitations (Wave 4 documentation)

Cursor canvases are **display-only**. They cannot write directly to chat or to a file the assistant reads automatically. The pattern is:

1. Assistant generates `intake-form.canvas.tsx` and tells the user where it is.
2. User opens the canvas (Command Palette → "Cursor: Open Canvas").
3. User fills the form. State persists within the canvas as they edit (`useCanvasState`).
4. User clicks the "Copy this JSON" panel and copies the JSON.
5. User pastes the JSON into chat.
6. Assistant parses the JSON, populates `status-data.json`, and confirms what was captured.

This is one extra step compared to a "magic" form that auto-syncs. The trade-off is that the BA gets a true form UI rather than 8 sequential questions. For BAs who prefer the chat flow, the default (chat-style intake) is unchanged.

### Refresh behaviour

If the BA wants to update intake info later (e.g. complexity changes from `standard` to `full`, or a Jira template story is added), they can:

- Re-open the canvas and edit fields (state persists)
- Copy the updated JSON and paste back to chat
- The assistant detects the diff and updates `status-data.json` accordingly

The orchestrator should treat intake form canvas updates as a Phase 0 refresh, not a full re-intake.

### Example canvas (skeleton — generate per-initiative)

```tsx
import { Stack, H1, H2, Text, Input, Select, Toggle, Textarea, Code, Divider, useCanvasState } from 'cursor/canvas';

export default function IntakeForm() {
  const [name, setName] = useCanvasState<string>('initiative.name', '');
  const [complexity, setComplexity] = useCanvasState<'lean' | 'standard' | 'full'>('initiative.complexity', 'standard');
  const [jiraKey, setJiraKey] = useCanvasState<string>('initiative.jiraProjectKey', '');
  const [jiraTemplate, setJiraTemplate] = useCanvasState<string>('initiative.jiraTemplate.sourceKey', '');
  // ... all other fields

  const json = {
    initiative: {
      name,
      complexity,
      jiraProjectKey: jiraKey,
      jiraTemplate: jiraTemplate ? { sourceKey: jiraTemplate } : null,
      // ... rest
    },
    _missing: [
      !name && 'initiative.name',
      !jiraKey && 'initiative.jiraProjectKey',
      // ...
    ].filter(Boolean),
  };

  return (
    <Stack gap={20}>
      <H1>Intake Form — Sample Initiative</H1>
      <Text tone="secondary">Fill in what you know. Leave blanks for unknowns — they'll be logged as gaps. When done, copy the JSON at the bottom and paste it into chat.</Text>

      <Divider />
      <H2>1. Workspace IDs</H2>
      <Input label="Jira project key" value={jiraKey} onChange={setJiraKey} required />
      {/* ... */}

      <Divider />
      <H2>3. Initiative basics</H2>
      <Input label="Initiative name" value={name} onChange={setName} required />
      <Select label="Complexity signal" value={complexity} options={['lean', 'standard', 'full']} onChange={setComplexity} required />
      {/* ... */}

      <Divider />
      <H2>Copy this JSON and paste it back to chat</H2>
      <Code language="json">{JSON.stringify(json, null, 2)}</Code>
    </Stack>
  );
}
```

(Adjust component names to actual `cursor/canvas` exports — verify against the SDK declarations in `~/.cursor/skills-cursor/canvas/sdk/index.d.ts` before generating the real file.)

### Slop check (per canvas skill rules)

- No emojis as visual labels — use `required` text instead
- No gradients, no box shadows
- One H1 (initiative name + "Intake Form"); H2s per section
- Group fields with `Stack` and `Divider`, not nested cards

---

