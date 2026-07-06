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
    # Allowlist: references owned by OTHER skills (pm-data-analyst), cited from routing/maps.
    external = {"warehouse-and-sql.md", "narrative-synthesis.md"}
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
