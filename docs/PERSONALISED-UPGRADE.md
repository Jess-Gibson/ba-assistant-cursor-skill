# Upgrading a personalised install

Use this when you have changed your installed BA Assistant: edited skills or
rules, added your own skills or rules, a tone-of-voice rule, or your own names
for things (for example `alex-actions` instead of `ba-actions`). The plain
upgrader (`tools/upgrade-ba-assistant.py`) replaces package files with the new
version. This flow keeps your changes.

## Who does what

The script never decides for you. It does the jobs where exact and repeatable
beats clever: backup, hashing, sorting files, copying only what you approved,
and rollback. The one merge it does is git's line merge for behaviour files that
you and the new version both changed; a clean result still needs your sign-off
(`auto_merged_reviewed`) before anything is built, and an overlap is left for you
(or Cursor, with you approving) to resolve.

| Job | Who |
|---|---|
| Copy your `.cursor` folder somewhere safe by hand, first | You |
| Backup, hash manifest, zip test, restore rehearsal | Script |
| Work out your naming rules (`rules.json`) | Cursor, from your sync-to-repo skill or your install |
| Sort every file into a class | Script |
| Merge a behaviour file you and the new version both changed | Script tries git's line merge; you (or Cursor) review every result and resolve overlaps |
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
| GEN | Generated workboard canvas | deployed only with `--include-generated` |

### Only behaviour changes, when the new version ships a port manifest

`docs/port-manifest.json` in the new version says which changes are behaviour
(`behaviour-critical`, `behaviour-important`, `behaviour-minor`) and which are
wording (public tidy-ups, genericisation). With it, `classify`:

- keeps your version of every wording-only file, even ones you never edited
- three-way merges behaviour files you edited (`git merge-file`): where your edits
  and the new version's don't overlap, the result is written to `merged/` for you to
  review; where they overlap, you get a `.conflict` file and a question
- reports what the `hooks.json` merge would drop or change (for example a
  `failClosed` setting), and asks before taking it
- reports a missing `ba-assistant-config.mdc`, or initiatives in a folder no
  config points at. Set `create_config` to true to add the config from the template.

Your initiative folders are found automatically, wherever they sit inside
`.cursor`, and treated as data: backed up, staged, never deployed.

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

# 5. Build the upgraded install in staging, then test it there. Staging is a whole
#    fake home (<session>/stage-home/.cursor); "run" points HOME at it, so hooks and
#    scripts read staging's config, workstream and initiatives, not your real .cursor.
#    Initiative folders OUTSIDE .cursor are not copied: they are read live (stage warns).
python3 ba-new/tools/ba-merge-upgrade.py apply-staging --session <session>
python3 ba-new/tools/ba-merge-upgrade.py run --session <session> -- python3 <session>/stage-home/.cursor/hooks/session-init.py

# 6. See exactly what would change in your real install
python3 ba-new/tools/ba-merge-upgrade.py deploy-plan --session <session>

# 7. Deploy exactly that plan (the id comes from step 6)
python3 ba-new/tools/ba-merge-upgrade.py deploy --session <session> --plan-sha <id>

# Any time after step 1: put every backed-up file back, byte for byte
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
1. Verify the new checkout is at <RELEASE_SHA> (git rev-parse HEAD). Stop if not. Check git is installed (the automatic merges need it).
2. Run backup. Show me the summary and the session folder.
3. Run stage.
4. Build rules.json in the session folder: read my sync-to-repo skill (if I have one) and list every local-to-generic name pair it uses, plus any of my file names that are renamed package files. Show me the pairs as a table with values masked (first 3 characters, then ***) and ask me to confirm.
5. Run classify with --rules. Show me the class counts, the Findings section of report.md, and the hooks.json section.
6. Go through every "ask" in decisions.json with me, highest-risk first:
   - Auto-merged files: they are already in merged/ with decision "merged". For each, show me a two-line summary of what changed from my version. Critical ones first. Only when I say they are fine, set auto_merged_reviewed to true.
   - Conflicts (a .conflict file next to the path in merged/): resolve each into merged/<path> in MY naming, keeping my intent and the new version's behaviour fix, show me the result, then set "merged".
   - hooks.json: explain each dropped or changed registration. Recommend take_new, or merged (write the merged hooks.json yourself) if I want to keep a setting such as failClosed.
   - Other D files: read my version, the old version and the new version. Explain in plain English what I changed and what the new version changed. Recommend one of: take_new (and why my change is not needed), keep_mine (and what I miss from the new version), or merged. For merged, write the merged file in MY naming to <session>/merged/<path> and show me a short summary of the result before I approve it.
   - A-review, E (possible missing naming rule), G: explain and recommend.
   Use AskQuestion. Group low-risk ones. Update decisions.json with my answers.
7. Ask whether to patch the two old /wrap and /validate-state rows in my profile (patch_profile). Show the old and new rows.
   If a finding says there is no config file, ask whether to set create_config. After apply-staging, fill in the created <session>/stage-home/.cursor/rules/ba-assistant-config.mdc with me (name, Jira, Confluence, paths, and the optional workboard and mail keys). Lift my old hard-coded values (meeting highlights, mail noise subjects, ignored folders, repo names) from my current _workstream scripts into those keys, and show me what you are adding.
8. Run apply-staging. Then test in staging, always through `run --session <session> -- <command>` (S below is <session>/stage-home/.cursor):
   - session start: `run -- py S/hooks/session-init.py`. It must list my initiatives (not "No SESSION-CONTEXT.md found"). With several, it must ask rather than guess.
   - DoR gate: write a createJiraIssue Story payload for a story that has a recorded DoR pass to a temp file and `run --stdin <file> -- py S/hooks/jira-dor-gate.py`. It must allow.
   - end of day: `run -- py S/_workstream/generate-workboard-canvas.py --cursor-home S --canvas <temp file>` (no --eod-roll) and show me the End of Day prompt. It must point at eod-closeout-procedure.md and roll the calendar once.
   - snapshots: `run -- py S/_workstream/generate-initiative-snapshots.py`, then `--check <one of my slugs>`. Must say FRESH.
   - mail: `run -- py S/_workstream/scan-outlook-mail.py`. It must either print a triage or one "Mail: unable to check" line, never a traceback.
   - read my profile, tone rules and one of my own skills in staging and confirm they are intact.
9. Run deploy-plan. Show me the counts and any "personal" or "generated" rows. Wait for my go.
10. Run deploy with the plan id. Show me the result.
11. Tell me to open a new chat and run /ba-assistant, then /workboard. Remind me of the rollback command and where the session folder is.
```

## Your first sync back to the repo

You kept your own version of every wording-only file. A full sync would push
those back over the public clean-up. So the first time, sync only what you
changed after the upgrade:

```bash
python3 ba-new/tools/ba-merge-upgrade.py changed-since-deploy --session <session> --out allowlist.txt
```

1. Reset your public clone to the merged `main`.
2. Run your sync as a dry run, limited to the paths in `allowlist.txt`.
3. Reject any wording-only file (see `docs/V15-UPGRADE-MANIFEST.md`) unless it is on the list.
4. Check `git diff --name-status` before you push.

## If something goes wrong

- **You find a bug after deploying:** `rollback` first, then run the whole flow
  again against the fixed release with a new session. Never classify an install
  that is already half upgraded.

- **Deploy stopped with "your real install changed":** something wrote to your
  install after the backup. Nothing was deployed. Start again from backup
  with a new session.
- **Deploy failed verification:** it rolls back automatically and says so.
- **You don't like the result:** `rollback --session <session>`. It moves the
  current files aside first, so files the upgrade added don't linger.
- **The tool itself is broken:** `<session>/ROLLBACK.md` has the manual steps.
