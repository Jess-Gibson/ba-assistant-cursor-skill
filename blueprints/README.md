# Blueprints

This is the default project folder for BA Assistant initiatives.

When you say "create a new project called X", the BA Assistant will create a folder here following the convention:

```
blueprints/
  Project 001 - your-initiative/
    docs/blueprints/analysis/
      SESSION-CONTEXT.md
      initiative-tracker.md
      Project-hub.md
      confluence-pages.json
```

Each project folder contains the state files that track your initiative's progress, RAID items, decisions, and session context.

## Folder convention

The default convention is `Project NNN - <slug>`. The assistant will:
1. Find the next available number
2. Create the folder structure
3. Scaffold starter templates for all state files

## Alternative conventions

If you prefer a different folder structure (e.g. `initiatives/`, `projects/`, or a flat layout), you can:
1. Create your preferred root folder
2. Update the glob patterns in `SKILL.md` Step 2.5 and Step 2.75
3. Update the `session-init` hook search paths
4. Set `BA_INITIATIVES_ROOT` environment variable to point to your root

The BA Assistant will detect and follow whatever convention it finds in your workspace.
