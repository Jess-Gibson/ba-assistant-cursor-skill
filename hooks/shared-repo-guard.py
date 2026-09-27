# Shared-repo guard — blocks working-file leakage into the shared delivery repo.
# Wave: hook-reliability (C1b). Used by TWO hook events:
#
#   postToolUse (Write)    → mode "edit":  can't undo the edit, so it WARNS loudly
#                            (additional_context) when an edited file under the shared
#                            repo links to a git-ignored working file.
#   beforeShellExecution   → mode "shell": DENIES git commit/push run inside the shared
#                            repo while any analysis/ file contains a leak.
#
# stdin: hook JSON (edited file path, or shell command + cwd — verify field names
# against current Cursor hooks docs). stdout: {"permission": ..., messages}.
# Fail-open: guard errors must never block unrelated work.

import json, os, re, sys, glob

FORBIDDEN = re.compile(
    r'(SESSION-CONTEXT(\.team)?\.md|initiative-tracker\.md|status-data\.json'
    r'|metrics-cache\.json|/debriefs/|superseded-pages\.json)', re.I)
LINKISH = re.compile(r'\]\([^)]*(SESSION-CONTEXT|initiative-tracker|status-data|debriefs)[^)]*\)'
                     r'|(\.\./)+[^\s)]*(SESSION-CONTEXT|initiative-tracker|status-data)', re.I)

def out(permission, agent="", user=""):
    # snake_case fields; the edit-mode warning ships as additional_context, which Cursor
    # reads on postToolUse (afterFileEdit reads nothing, so it is not registered there).
    # camelCase kept for back-compat.
    o = {"permission": permission, "agent_message": agent, "user_message": user,
         "agentMessage": agent, "userMessage": user}
    if agent:
        o["additional_context"] = agent
    print(json.dumps(o))
    sys.exit(0)

def repo_root():
    # paths.sharedRepoRoot in ~/.cursor/rules/ba-assistant-config.mdc (/handover writes it
    # the first time the BA says where confirmed analysis goes). The env var may override.
    # Neither set = guard does nothing.
    env = os.environ.get("BA_SHARED_REPO_ROOT", "")
    if env:
        return env
    # Older or hand-built installs keep paths.* in ba-profile.mdc; config wins.
    text = ""
    for name in ("ba-assistant-config.mdc", "ba-profile.mdc"):
        cfg = os.path.expanduser(os.path.join("~", ".cursor", "rules", name))
        try:
            text += open(cfg, encoding="utf-8", errors="ignore").read() + "\n"
        except Exception:
            pass
    m = re.search(r'^\s*sharedRepoRoot\s*:\s*["\']?([^"\'#\n]+)', text, re.M)
    val = m.group(1).strip() if m else ""
    if not val or val.startswith("["):   # unset or still a template placeholder
        return ""
    return os.path.expanduser(val)

def is_within(path, root):
    # Containment by path parts, not string prefix: /work/repo-old is NOT inside /work/repo.
    try:
        a, b = os.path.realpath(path), os.path.realpath(root)
        return os.path.commonpath([os.path.normcase(a), os.path.normcase(b)]) == os.path.normcase(b)
    except ValueError:   # different drives on Windows
        return False

def scan_file(path):
    try:
        text = open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return []
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if LINKISH.search(line) or (FORBIDDEN.search(line) and re.search(r'\[.*\]\(|href=|file://', line, re.I)):
            hits.append(f"{os.path.basename(path)}:{i}: {line.strip()[:100]}")
    return hits

try:
    payload = json.loads(sys.stdin.read() or "{}")
except Exception:
    out("allow")

root = repo_root()
mode = "shell" if any(k in payload for k in ("command", "cmd", "shell")) else "edit"
blob = json.dumps(payload)

if mode == "edit":
    # Find the edited path in the payload
    path = ""
    sources = [payload]
    if isinstance(payload.get("tool_input"), dict):   # postToolUse nests the path
        sources.append(payload["tool_input"])
    for src in sources:
        for key in ("filePath", "file_path", "path", "uri"):
            if isinstance(src.get(key), str):
                path = src[key]; break
        if path:
            break
    if not path or not root or not is_within(path, root):
        out("allow")
    hits = scan_file(path)
    if hits:
        out("allow",
            agent=("WARNING (shared-repo-guard): the file just edited in the shared delivery repo "
                   "links to git-ignored BA working files the devs cannot see:\n- " + "\n- ".join(hits[:5]) +
                   "\nPer dev-handover-format.md, workspace content must be EMBEDDED as a summary, never linked. "
                   "Fix before this is committed — the commit gate will block it."),
            user="Handover leak warning: a shared-repo file links to a BA working file. Embed a summary instead.")
    out("allow")

# shell mode
cmd = str(payload.get("command", payload.get("cmd", "")))
cwd = str(payload.get("cwd", ""))
if not re.search(r'\bgit\b.*\b(commit|push)\b', cmd):
    out("allow")
# Folders the git command runs in: the hook's cwd, any `cd <dir>`, and any `git -C <dir>`.
# Compared as folders, so a command that merely mentions the repo path elsewhere
# (or a sibling like repo-old) does not count.
base = cwd or os.getcwd()
dirs = [base]
for m in re.finditer(r'(?:(?<![\w-])cd|\s-C)\s+("[^"]+"|\'[^\']+\'|[^\s;&|]+)', cmd):
    d = os.path.expanduser(m.group(1).strip("\"'"))
    dirs.append(d if os.path.isabs(d) else os.path.join(base, d))
in_shared = bool(root) and any(is_within(d, root) for d in dirs)
if not in_shared:
    out("allow")

all_hits = []
for f in glob.glob(os.path.join(root, "analysis", "**", "*.md"), recursive=True):
    all_hits += scan_file(f)
if all_hits:
    out("deny",
        agent=("BLOCKED (shared-repo-guard): refusing git " + ("push" if "push" in cmd else "commit") +
               " — shared-repo analysis files link to git-ignored BA working files:\n- " + "\n- ".join(all_hits[:8]) +
               "\nEmbed the content as a summary (per dev-handover-format.md) and retry."),
        user="Commit blocked: a handover file links to a BA working file the devs can't see. Fix the leak first.")
out("allow")
