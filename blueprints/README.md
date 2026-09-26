# Blueprints

This folder is retained for compatibility with older installs. New initiatives
use the configured `BA_INITIATIVES_ROOT`, which defaults to
`~/.cursor/initiatives`.

When you say "create a new initiative called X", `ba-setup` Step 3 determines
the root and `ba-new-initiative` creates:

```
~/.cursor/initiatives/
  your-initiative/
    SESSION-CONTEXT.md
    initiative-tracker.md
    Project-hub.md
    confluence-pages.json
```

Each project folder contains the state files that track your initiative's progress, RAID items, decisions, and session context.

## Folder convention

The default convention is `$BA_INITIATIVES_ROOT/<slug>`, with
`BA_INITIATIVES_ROOT=~/.cursor/initiatives`. The assistant creates the folder
and scaffolds the starter state files.

## Alternative conventions

If you prefer a different folder structure, you can:
1. Create your preferred root folder
2. Configure it in `ba-setup` Step 3
3. Set `BA_INITIATIVES_ROOT` to that root
4. Use `SKILL.md` Step 2 for resume lookup

The BA Assistant will detect and follow whatever convention it finds in your workspace.
