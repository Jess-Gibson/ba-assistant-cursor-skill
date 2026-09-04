# Markdown readability (stakeholder artefacts)

**Last updated:** 4 Sep 2026  
**Trigger:** Enablement handovers, comms, debrief exports, Confluence draft mirrors, playback packs, any `.md` read by Support, Ops, GTM, or stakeholders in Cursor.

**Rule stub (auto-loads on matching paths):** `rules/markdown-readability.mdc`  
**Pairs with:** `no-em-dashes.mdc` (voice and punctuation), stakeholder voice rules if installed

---

## 1. Design for the reader first

| Reader | They need |
|--------|-----------|
| Support / Ops | What changed, for whom, what to say on a call, edge cases |
| Enablement | Scannable pack to turn into chat posts, hub pages, training |
| PM / leadership | At-a-glance who / what / when / why, then detail |

**Put the call-ready answer at the top.** Background and reference go below.

---

## 2. Dark mode safe formatting

Many readers open `.md` in **Cursor dark mode**.

| Use | Avoid |
|-----|-------|
| `---` horizontal rules between major blocks | HTML `<div>` with light background colours |
| `### ALL-CAPS LABEL` for section identity | Pastel callout boxes (`#E8F4FC`, `#FFF8E6`, etc.) |
| Markdown tables | `<br>` for vertical spacing |
| Blockquotes for short narrative or scripts | Inline `style="..."` for layout |
| Blank lines between sections | Same heading level repeated with no visual break |

Blockquotes and tables inherit theme colours and stay readable in light and dark mode.

---

## 3. Section hierarchy (enablement pattern)

Use this shape for "what's changing" packs (defaults, policy, process):

```
## Support quick answer (use this on a call)
> Who / What / Edge case / Date

---

### TODAY (before [date])
[table]

---

### WHO (from [date])
[in scope | out of scope table or two lines]

---

### WHAT CHANGES (from [date])
[numbered table, max 3-5 rows in summary]

---

### WHY
> One short blockquote

---

### KEY DATES
[table]

---

## Detail sections (edge cases, script, ops notes, FAQ)
```

**Rules:**

- Each `---`-delimited block is one idea. Reader must see where a block ends before the next label.
- Summary layer: do not bury process detail in the summary. Say "differs by cohort, see below" or move to ops notes.
- Do not duplicate the same facts in summary and detail unless the summary is truly one line.

---

## 4. Tables vs bullets

| Situation | Format |
|-----------|--------|
| Today vs tomorrow, cohort A vs cohort B, FAQ | Table |
| Peer list of changes (3+) | Table with `#` column or one bullet each |
| Call script steps | Numbered list under a **bold label** |
| "If they ask..." | Two-column table (question / answer) |

One item per bullet. No semicolon walls.

---

## 5. Support script block (when applicable)

After factual tables, add:

1. **Opening line** (blockquote)
2. **The three things** (numbered, plain language)
3. **From [hard date]** (one line, blockquote)

Write what Support can read aloud. Not internal jargon.

---

## 6. Anti-patterns

| Problem | Fix |
|---------|-----|
| WHO / WHAT / WHY all look the same weight | `---` between each; tables for WHO in/out |
| Historical detail mixed into summary | Historical only in summary when needed; move process detail to ops note |
| Coloured HTML boxes | Removed; use rules + blockquotes |
| "See section 2" in summary | "See table below" or link by heading name |
| Long prose under `###` with no break | Split into table + one blockquote |

---

## 7. Where this applies

| Path pattern | Examples |
|--------------|----------|
| `blueprints/{slug}/comms/` | Enablement handovers, Teams drafts |
| `blueprints/{slug}/debriefs/` | Meeting summaries for stakeholders |
| `blueprints/{slug}/outputs/` | Confluence draft mirrors, gap lists |
| `blueprints/**/requirements/` | Only when drafting stakeholder-facing summaries (not raw registers) |

Technical registers, tracker rows, and `SESSION-CONTEXT.md` captures are exempt unless the BA asks for a readable export.

---

## 8. Skills that load this

| Skill / rule | When |
|--------------|------|
| `ba-playback-and-enablement` | Enablement packs, Support/Ops briefings |
| `publish-docs-to-confluence` | Before publishing local `.md` to wiki |
| `markdown-readability.mdc` | Auto when editing `comms/`, `debriefs/`, `outputs/` `.md` |

---

## 9. Checklist before send

- [ ] Top section answers "who / what / when" for the primary reader
- [ ] Major blocks separated by `---`
- [ ] No HTML colour backgrounds or `<br>`
- [ ] Previewed mentally in dark mode
- [ ] No em dashes (`no-em-dashes.mdc`)
- [ ] Support script present if audience includes Ops/Support
