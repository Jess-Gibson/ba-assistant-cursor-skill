#!/usr/bin/env python3
"""BA Assistant conformance check.

Run after every phase of the rework (and any time you like). Read-only.
Catches the drift class that bit us before: count mismatches, dangling
references, env vars nothing sets, leftover every-reply mandates, and
hook IDs that exist on one side of the contract only.

Usage:
    python3 conformance-check.py --root ~/.cursor
    python3 conformance-check.py --root /path/to/repo-clone   (repo layout auto-detected)

Exit code 0 = no FAILs (WARNs allowed). Non-zero = at least one FAIL.
"""
import argparse, os, re, sys, glob

results = []  # (level, check, detail)

def add(level, check, detail):
    results.append((level, check, detail))

def read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.expanduser("~/.cursor"))
    args = ap.parse_args()
    root = os.path.abspath(os.path.expanduser(args.root))

    # Layout detection: ~/.cursor has skills/ + rules/ at top; repo clone has skills/ + rules/ too.
    ba = os.path.join(root, "skills", "ba-assistant")
    rules_dir = os.path.join(root, "rules")
    if not os.path.isdir(ba):
        print(f"FATAL: {ba} not found — wrong --root?"); sys.exit(2)

    skill_md = read(os.path.join(ba, "SKILL.md")) or ""
    sub_dir = os.path.join(ba, "sub-skills")
    refs_dir = os.path.join(ba, "references")

    # ---- 1. Sub-skill counts ----
    folders = sorted(d for d in os.listdir(sub_dir) if os.path.isdir(os.path.join(sub_dir, d)))
    active, superseded = [], []
    for d in folders:
        body = read(os.path.join(sub_dir, d, "SKILL.md")) or ""
        (superseded if re.search(r"SUPERSEDED", body[:600]) else active).append(d)
    n_active = len(active)

    claimed = set()
    for m in re.finditer(r"(\d+)\s+active\s+sub-?skills", skill_md, re.I):
        claimed.add(int(m.group(1)))
    for m in re.finditer(r"all\s+(\d+)\s+(?:active\s+)?skills", skill_md, re.I):
        claimed.add(int(m.group(1)))
    for m in re.finditer(r"not all (\d+)", skill_md):
        claimed.add(int(m.group(1)))
    if not claimed:
        add("WARN", "counts", "No count claims found in SKILL.md (unexpected)")
    elif claimed == {n_active}:
        add("PASS", "counts", f"All SKILL.md count claims = {n_active} actual active sub-skills ({len(superseded)} superseded markers)")
    else:
        add("FAIL", "counts", f"SKILL.md claims {sorted(claimed)} but actual active sub-skills = {n_active} (folders: {len(folders)}, superseded: {len(superseded)})")

    readme = read(os.path.join(root, "README.md"))
    if readme:
        rm = set(int(m.group(1)) for m in re.finditer(r"(\d+)\s+active\s+sub-?skills", readme, re.I))
        if rm and rm != {n_active}:
            add("WARN", "counts", f"README.md claims {sorted(rm)}, actual {n_active}")

    # ---- 2. Referenced reference-files exist ----
    missing = set()
    for path in glob.glob(os.path.join(ba, "**", "*.md"), recursive=True) + glob.glob(os.path.join(rules_dir, "*.mdc")):
        body = read(path) or ""
        for m in re.finditer(r"references/([A-Za-z0-9._\-]+\.(?:md|html))", body):
            rel = m.group(1)
            if not os.path.exists(os.path.join(refs_dir, rel)) and not os.path.exists(os.path.join(refs_dir, "templates", os.path.basename(rel))):
                missing.add(rel)
    # Allowlist: references owned by OTHER skills in this repo (their own references/
    # folder, not ba-assistant's), or by skills outside this package (pm-data-analyst).
    external = {"warehouse-and-sql.md", "narrative-synthesis.md", "confluence-workflow.md"}
    missing = {m for m in missing if not m.startswith("<") and m not in external}
    if missing:
        add("FAIL", "references", f"Referenced but missing under references/: {sorted(missing)}")
    else:
        add("PASS", "references", "Every references/<file> mentioned in skills+rules exists")

    # ---- 3. Env vars read somewhere but set nowhere ----
    hooks_text = ""
    for hp in glob.glob(os.path.join(root, "hooks", "*")):
        hooks_text += (read(hp) or "")
    md_text = ""
    for path in glob.glob(os.path.join(ba, "**", "*.md"), recursive=True):
        md_text += (read(path) or "")
    read_vars = set(re.findall(r"\b(CURSOR_[A-Z_]+|BA_[A-Z_]+)\b", md_text))
    unset = sorted(v for v in read_vars
                   if v not in hooks_text
                   and v not in ("BA_INITIATIVES_ROOT", "BA_DOWNLOADS_PATH", "BA_SHARED_REPO_ROOT"))  # user-set, not hook-set
    if unset:
        add("WARN", "env-vars", f"Env vars referenced in skills but not set by any hook script: {unset}")
    else:
        add("PASS", "env-vars", "All hook-provided env vars referenced in skills are set by a hook script")

    # ---- 4. Leftover every-reply AskQuestion mandates ----
    hits = []
    for path in glob.glob(os.path.join(ba, "**", "*.md"), recursive=True) + glob.glob(os.path.join(rules_dir, "*.mdc")):
        body = read(path) or ""
        for i, line in enumerate(body.splitlines(), 1):
            if re.search(r"(mandatory (on|every) every reply|MUST end with an `?AskQuestion`? call|still mandatory every reply|AskQuestion at every reply|Every turn:\*?\*? end with)", line):
                hits.append(f"{os.path.relpath(path, root)}:{i}")
    if hits:
        add("FAIL", "askquestion", f"Every-reply mandate still present: {hits}")
    else:
        add("PASS", "askquestion", "No unconditional every-reply AskQuestion mandates remain")

    # ---- 5. Hook ID cross-check ----
    contracts = read(os.path.join(ba, "hook-contracts.md")) or ""
    contract_ids = set(re.findall(r"\bHK-[A-Z]+-[A-Z]+-[a-z0-9\-]+\b", contracts))
    used_ids = set()
    for path in glob.glob(os.path.join(sub_dir, "**", "*.md"), recursive=True) + [os.path.join(ba, "instructions.md"), os.path.join(ba, "SKILL.md")]:
        body = read(path) or ""
        used_ids |= set(re.findall(r"\bHK-[A-Z]+-[A-Z]+-[a-z0-9\-]+\b", body))
    orphan_used = sorted(used_ids - contract_ids)
    if orphan_used:
        add("FAIL", "hooks", f"Hook IDs used in skills but absent from hook-contracts.md: {orphan_used}")
    else:
        add("PASS", "hooks", f"All {len(used_ids)} hook IDs used in skills are registered in hook-contracts.md")
    # (Hooks registered in contracts but not cited in skill prose are by-design — no warning.)

    # ---- 6. Routing rows pointing at missing local skills (info only) ----
    routing = read(os.path.join(rules_dir, "skills-routing.mdc")) or ""
    dangling = []
    for m in re.finditer(r"`ba-assistant/sub-skills/([a-z\-]+)`", routing):
        if not os.path.isdir(os.path.join(sub_dir, m.group(1))):
            dangling.append(m.group(1))
    if dangling:
        add("FAIL", "routing", f"Routing rows point at missing sub-skills: {dangling}")
    else:
        add("PASS", "routing", "All ba-assistant sub-skill routing targets exist")

    # ---- 7. HARD gates in critical-gates.mdc must name a real, registered script ----
    hooks_dir = os.path.join(root, "hooks")
    hooks_json_text = read(os.path.join(hooks_dir, "hooks.json")) or ""
    hook_files_present = set(os.listdir(hooks_dir)) if os.path.isdir(hooks_dir) else set()

    gates_text = read(os.path.join(rules_dir, "critical-gates.mdc")) or ""
    bad_gate_rows = []
    for line in gates_text.splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        gate_name, enforcement = cells[0], cells[2]
        if gate_name == "Gate" or set(gate_name) <= {"-"}:
            continue  # header / separator row
        if "**HARD" not in enforcement:
            continue  # only HARD-marked rows claim a hook-enforced script
        scripts = set()
        for backticked in re.findall(r"`([^`]*)`", enforcement):
            scripts |= set(re.findall(r"[A-Za-z0-9_\-]+\.(?:py|ps1|sh)\b", backticked))
        for script in scripts:
            present = script in hook_files_present
            registered = script in hooks_json_text
            if not (present and registered):
                reason = []
                if not present:
                    reason.append("missing under hooks/")
                if not registered:
                    reason.append("not referenced in hooks/hooks.json")
                bad_gate_rows.append(f"{gate_name!r} names `{script}` ({', '.join(reason)})")
    if bad_gate_rows:
        add("FAIL", "gate-scripts", f"HARD gate rows naming a script that isn't both present under hooks/ AND registered in hooks.json: {bad_gate_rows}")
    else:
        add("PASS", "gate-scripts", "Every HARD gate row in critical-gates.mdc names a script present under hooks/ and registered in hooks.json")

    # ---- 8. Orphan scripts under hooks/ (present but never registered) ----
    orphans = []
    if os.path.isdir(hooks_dir):
        for fname in sorted(hook_files_present):
            if fname == "hooks.json" or os.path.isdir(os.path.join(hooks_dir, fname)):
                continue
            if fname not in hooks_json_text:
                orphans.append(fname)
    if orphans:
        add("WARN", "orphan-scripts", f"Files under hooks/ never referenced in any hooks.json command string: {orphans}")
    else:
        add("PASS", "orphan-scripts", "Every file under hooks/ is referenced in hooks.json")

    # ---- 9. Referenced mail script must exist ----
    mail_script = "scan-outlook-mail.py"
    mail_exists = bool(glob.glob(os.path.join(root, "**", mail_script), recursive=True))
    mail_refs = []
    for pattern in ("**/*.md", "**/*.mdc", "**/*.py", "**/*.json"):
        for f in glob.glob(os.path.join(root, pattern), recursive=True):
            name = os.path.basename(f)
            if name in ("CHANGELOG.md", "conformance-check.py"):
                continue
            if mail_script in (read(f) or ""):
                mail_refs.append(os.path.relpath(f, root))
    if mail_refs and not mail_exists:
        add("FAIL", "mail-script", f"{mail_script} is referenced but does not exist: {sorted(mail_refs)}")
    else:
        add("PASS", "mail-script", f"{mail_script} is not referenced, or it exists")

    # ---- 10. Commands must point at the installed skill path ----
    cmd_dir = os.path.join(root, "commands")
    bad_cmd = []
    for f in sorted(glob.glob(os.path.join(cmd_dir, "*.md"))):
        for i, line in enumerate((read(f) or "").splitlines(), 1):
            if not re.search(r"(?<![~/\w.-])skills/ba-assistant/", line):
                continue
            if "~/.cursor/skills/" in line:
                continue  # the sentence also gives the installed path
            bad_cmd.append(f"{os.path.basename(f)}:{i}")
    if bad_cmd:
        add("FAIL", "command-paths", f"commands/*.md read skills/ba-assistant/ without the ~/.cursor/ prefix: {bad_cmd}")
    else:
        add("PASS", "command-paths", "commands/*.md use ~/.cursor/skills/ba-assistant/ paths")

    # ---- report ----
    width = max(len(c) for _, c, _ in results)
    fails = 0
    print(f"\nBA Assistant conformance — root: {root}\n" + "-" * 72)
    for level, check, detail in results:
        if level == "FAIL":
            fails += 1
        print(f"{level:4}  {check:<{width}}  {detail}")
    print("-" * 72)
    print(f"{fails} FAIL, {sum(1 for l, _, _ in results if l == 'WARN')} WARN, {sum(1 for l, _, _ in results if l == 'PASS')} PASS")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
