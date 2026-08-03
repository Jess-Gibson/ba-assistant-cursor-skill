---
name: ba-visual-storytelling
description: "SUPERSEDED (Wave 10)  -  content merged into references/visual-output-format.md. Kept for hook-name compatibility: any HK-*-VIS-* hook or caller invoking Visual_Storytelling routes to that reference and applies it inline."
disable-model-invocation: true
---

# Skill: Visual Storytelling  -  SUPERSEDED (Wave 10)

This skill's content now lives in **`references/visual-output-format.md`**:

- Storytelling framework (Problem → Evidence → Choice → Consequence → Ask) → §13
- The 12 visual types with when-to-use and watch-fors → §4 (expanded)
- Production workflow: quick vs deep mode, tasks, iteration loop, output block, challenge rules → §14

**For any caller (hook or user request):** read `references/visual-output-format.md`, pick the type from §4, apply §13 for narrative visuals, follow §14's workflow, and use the template per §9 (interactive HTML default, `references/templates/<type>.html`; Mermaid as fallback per §8's Confluence patterns).

Hook name preservation: callers still invoke `Visual_Storytelling` / `HK-*-VIS-*` by name. Producing the visual inline against the standard IS the fulfilment of those hooks  -  there is no separate skill body to load. Save visuals to `<initiative-folder>/visuals/<slug>.html` as before.
