# Upgrading a personalised install

Use this when you have changed your installed BA Assistant: edited skills or
rules, added your own skills or rules, a tone-of-voice rule, or your own names
for things (for example `alex-actions` instead of `ba-actions`). The plain
upgrader (`tools/upgrade-ba-assistant.py`) replaces package files with the new
version. This flow keeps your changes.

## Who does what

The script never merges file content and never decides. It does the jobs where
exact and repeatable beats clever: backup, hashing, sorting files, copying only
what you approved, and rollback. Anything that needs judgement is done by you,
or by Cursor with you approving each file.

| Job | Who |
|---|---|
| Copy your `.cursor` folder somewhere safe by hand, first | You |
| Backup, hash manifest, zip test, restore rehearsal | Script |
| Work out your naming rules (`rules.json`) | Cursor, from your sync-to-repo skill or your install |
| Sort every file into a class | Script |
| Merge any file you and the new version both changed | Cursor, one file at a time, you approve |
| Your own skills, rules, profile, tone, data | Never touched |
| Deploy, verify, roll back if anything fails | Script |

## The classes

| Class | Meaning | Default |
|---|---|---|
| A | You never changed it; the new version did | take new, **written in your naming** |
| A-review | Looks untouched, but only via a very short naming rule | ask |
| B | Only you changed it | keep yours |
| C | You both made the same change | keep yours (same thing) |
| D | You both changed it differently | ask: merge it |
| E | New in the new version | add, in your naming. Asks instead if you have a similar-named file (probable missing naming rule) |
| F | Removed or renamed in the new version | keep yours (old package hook wrappers: moved aside) |
| G | In the old version, missing from your install | ask |
| H | Your own file | never touched |
| P | Profile, config, tone rules | never touched except an approved profile-row patch |
| M | `hooks.json` | merged hook by hook, your own hooks kept |
| DATA | Actions, workboard, calendar, initiatives | never touched |
| GEN | Generated workboard canvas | deployed only with `--include-canvas` |

## Your naming: `rules.json`

The public package uses generic names. If your install uses your own, list the
pairs. It's the same list your sync-to-repo skill uses when it genericises
files, just written down:

```json
{
  "rules": [
    {"local": "alex-actions", "generic": "ba-actions"},
    {"local": "sync-alex-actions", "generic": "sync-ba-actions"}
  ]
}
```

Every file taken from the new version is rewritten with these pairs, file names
included. With no rules file, new files keep the generic names. The report
never prints the values in your rules.

## Steps

Windows: use `py` for `python3`, or `.\tools\ba-merge-upgrade.ps1` with the same arguments.
Close other Cursor windows first. A chat writing to your install mid-upgrade
makes the deploy stop (drift check), which is safe but means starting again.

```bash
# 0. Get the old and new package versions side by side (pinned commits)
git clone https://github.com/<owner>/ba-assistant-cursor-skill ba-new
git -C ba-new checkout <RELEASE_SHA>
git -C ba-new worktree add ../ba-old <the commit you installed, e.g. 750a6c5 for Version 14>

# 1. Backup (prints the session folder, e.g. ~/ba-assistant-upgrade-20260927-101500)
python3 ba-new/tools/ba-merge-upgrade.py backup

# 2. Staging copy
python3 ba-new/tools/ba-merge-upgrade.py stage --session <session>

# 3. Classify
python3 ba-new/tools/ba-merge-upgrade.py classify --session <session> --base ba-old --new ba-new --rules rules.json

# 4. Decide: edit <session>/decisions.json (every "ask"). For a merge, write the merged
#    file (in your naming) to <session>/merged/<same path> and set "merged".

# 5. Build the upgraded install in staging, then test it there
python3 ba-new/tools/ba-merge-upgrade.py apply-staging --session <session>

# 6. See exactly what would change in your real install
python3 ba-new/tools/ba-merge-upgrade.py deploy-plan --session <session>

# 7. Deploy exactly that plan (the id comes from step 6)
python3 ba-new/tools/ba-merge-upgrade.py deploy --session <session> --plan-sha <id>

# Any time after step 1: put everything back exactly
python3 ba-new/tools/ba-merge-upgrade.py rollback --session <session>
```

## Cursor prompt

Paste this into a Cursor chat after cloning the new version. Fill in the three
values at the top.

```text
Upgrade my personalised BA Assistant install with tools/ba-merge-upgrade.py.
New package checkout: <path to ba-new>, pinned at <RELEASE_SHA>.
Old package: the commit I installed (<commit>), as a worktree at <path to ba-old>.

Rules:
- Before anything, ask me to confirm I have copied my .cursor folder somewhere safe by hand. Do not continue until I say yes.
- Tell me to close other Cursor windows and chats for the whole upgrade.
- Run the tool's commands. Never copy, move or edit files in my real .cursor yourself. The only files you write are in the session folder: rules.json, decisions.json, and merged/.
- Never run my sync-to-repo skill. You may read it.
- Never print secrets, internal URLs or values from my naming rules in chat.
- Never use em dashes.

Steps:
1. Verify the new checkout is at <RELEASE_SHA> (git rev-parse HEAD). Stop if not.
2. Run backup. Show me the summary and the session folder.
3. Run stage.
4. Build rules.json in the session folder: read my sync-to-repo skill (if I have one) and list every local-to-generic name pair it uses, plus any of my file names that are renamed package files. Show me the pairs as a table with values masked (first 3 characters, then ***) and ask me to confirm.
5. Run classify with --rules. Show me the class counts.
6. Go through every "ask" in decisions.json with me, highest-risk first:
   - D: read my version, the old version and the new version. Explain in plain English what I changed and what the new version changed. Recommend one of: take_new (and why my change is not needed), keep_mine (and what I miss from the new version), or merged. For merged, write the merged file in MY naming to <session>/merged/<path> and show me a short summary of the result before I approve it.
   - A-review, E (possible missing naming rule), G: explain and recommend.
   Use AskQuestion. Group low-risk ones. Update decisions.json with my answers.
7. Ask whether to patch the two old /wrap and /validate-state rows in my profile (patch_profile). Show the old and new rows.
8. Run apply-staging. Then test in staging (<session>/staging):
   - run <session>/staging/hooks/session-init.py with empty input (it only reads my real install). Confirm it runs and asks which initiative, rather than guessing. Then run it again with CURSOR_PROJECT_DIR set to one of my initiative folders and confirm it names that one.
   - run <session>/staging/_workstream/generate-workboard-canvas.py --cursor-home <session>/staging --canvas <a temp file> (no --eod-roll) and show me the End of Day prompt. It must point at eod-closeout-procedure.md and roll the calendar once.
   - read my profile, tone rules and one of my own skills in staging and confirm they are intact.
9. Run deploy-plan. Show me the counts and any "personal" or "canvas" rows. Wait for my go.
10. Run deploy with the plan id. Show me the result.
11. Tell me to open a new chat and run /ba-assistant, then /workboard. Remind me of the rollback command and where the session folder is.
```

## If something goes wrong

- **Deploy stopped with "your real install changed":** something wrote to your
  install after the backup. Nothing was deployed. Start again from backup
  with a new session.
- **Deploy failed verification:** it rolls back automatically and says so.
- **You don't like the result:** `rollback --session <session>`. It moves the
  current files aside first, so files the upgrade added don't linger.
- **The tool itself is broken:** `<session>/ROLLBACK.md` has the manual steps.
