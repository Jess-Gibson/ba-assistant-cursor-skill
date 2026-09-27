"""
Scan Outlook Inbox and Sent for BA workboard / EOD mail triage.

Usage:
  py _workstream/scan-outlook-mail.py
  py _workstream/scan-outlook-mail.py --since 2026-09-18 --out _workstream/mail-triage-latest.json

Requires Windows, the Outlook desktop app and pywin32 (`py -m pip install pywin32`).
Read-only: never sends, moves or marks mail.

Exit codes (end of day step 1 relies on these):
  0  scanned; triage printed (and written to --out if given)
  2  unable to check (not Windows, pywin32 missing, or Outlook not available).
     Prints one "Mail: unable to check (...)" line. The agent then tries the
     Outlook MCP connector, and failing that says "Mail: unable to check".

Optional noise filters, comma-separated, in ~/.cursor/rules/ba-assistant-config.mdc
(or ba-profile.mdc). They live in config, not here, so upgrades never wipe them:
  mail_noise_subjects: Weekly digest, Build report
  mail_ignore_folders: Newsletters, Change notices
  mail_noise_repos: my-team-repo
"""
from __future__ import annotations

import argparse
import os
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


OL_INBOX = 6
OL_SENT = 5
OL_MAIL = 43

ACTION_HINTS = re.compile(
    r"\b("
    r"please|can you|could you|need you|action required|fyi|please review|"
    r"please confirm|please advise|reply|respond|follow[- ]?up|asap|"
    r"waiting on you|for your action|approval|sign[- ]?off|question|"
    r"what do you think|thoughts\?|let me know|when you can"
    r")\b",
    re.I,
)
FYI_HINTS = re.compile(r"\b(fyi|for your information|no action|nfa|heads[- ]?up only)\b", re.I)
NOISE_HINTS = re.compile(
    r"("
    r"you have new held messages|"
    r"sent a message$|"
    r"mentioned you in a conversation|"
    r"newsletter|digest|weekly summary|learning summary|"
    r"weekly project updates|"
    r"meeting recording has expired|"
    r"invitation:|accepted:|canceled:|cancelled:|"
    r"pr build|ci build|dependabot|"
    r"your loom profile|"
    r"secure message viewed|"
    r"secure content shared|"
    r"new customer ticket created|"
    r"pushed 1 commit|"
    r"new activity: .* board needs your attention"
    r")",
    re.I,
)
UNABLE = "Mail: unable to check"


def parse_rule_value(text: str, key: str) -> str | None:
    """Same reader as the other BA Assistant scripts: `key: value`, quotes
    stripped, a trailing ` # comment` ignored, template placeholders skipped."""
    patterns = [
        rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$",
        rf"^\s*{re.escape(key)}\s*=\s*(.+?)\s*$",
    ]
    for line in text.splitlines():
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                value = match.group(1).strip()
                if value[:1] in {'"', "'"}:
                    end = value.find(value[0], 1)
                    value = value[1:end] if end > 0 else value[1:]
                else:
                    value = value.split(" #", 1)[0].strip()
                if value and value not in {"[Your Name]", "[BA name]", "TBC"} and not value.startswith("["):
                    return value
    return None


def load_rules_text(cursor_home: Path) -> str:
    text = ""
    for name in ("ba-assistant-config.mdc", "ba-profile.mdc"):
        path = cursor_home / "rules" / name
        if path.exists():
            text += path.read_text(encoding="utf-8", errors="replace") + "\n"
    return text


def config_list(rules_text: str, key: str) -> list[str]:
    raw = parse_rule_value(rules_text, key) or ""
    return [part.strip() for part in raw.split(",") if part.strip()]


def phrase_pattern(phrases: list[str]) -> re.Pattern | None:
    if not phrases:
        return None
    return re.compile("|".join(re.escape(p) for p in phrases), re.I)


class MailConfig:
    """Per-BA settings from config. Nothing organisation-specific lives in code."""

    def __init__(self, rules_text: str = ""):
        self.ba_name = parse_rule_value(rules_text, "ba_name") or parse_rule_value(rules_text, "name") or "[BA name]"
        self.noise_subjects = phrase_pattern(config_list(rules_text, "mail_noise_subjects"))
        self.ignore_folders = phrase_pattern(config_list(rules_text, "mail_ignore_folders"))
        self.noise_repos = [r.lower() for r in config_list(rules_text, "mail_noise_repos")]
        self.mention = mention_token(self.ba_name)

    def is_noise_text(self, text: str) -> bool:
        return bool(NOISE_HINTS.search(text) or (self.noise_subjects and self.noise_subjects.search(text)))


def mention_token(ba_name: str) -> str:
    first = (ba_name.split() or ["ba"])[0].lower()
    if first.startswith("["):
        return "@[ba-name]"
    return f"@{first}"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Outlook inbox/sent triage for BA workboard")
    p.add_argument(
        "--since",
        default=None,
        help="ISO date inclusive (default: last Friday before today, or today-3 weekdays)",
    )
    p.add_argument(
        "--out",
        default=None,
        help="Write JSON summary path (utf-8)",
    )
    p.add_argument("--max", type=int, default=80, help="Max items per folder")
    p.add_argument("--cursor-home", default=str(Path.home() / ".cursor"), help="Where to read config from")
    return p.parse_args()


def default_since(today: date) -> date:
    """Three calendar days back, so a Monday run still covers Friday."""
    return today - timedelta(days=3)


def local_now() -> datetime:
    return datetime.now().astimezone()


def to_naive_local(dt: datetime) -> datetime:
    """Outlook COM ReceivedTime/SentOn are usually already local wall time.

    pywin32 sometimes tags them as UTC anyway. Prefer stripping tzinfo when the
    value is naive-looking local; only convert when the instant is clearly UTC.
    """
    if not isinstance(dt, datetime):
        return dt
    if dt.tzinfo is None:
        return dt
    as_local = dt.astimezone().replace(tzinfo=None)
    stripped = dt.replace(tzinfo=None)
    now = local_now().replace(tzinfo=None)
    # Prefer stripped local when conversion lands >6h ahead of now (common false-UTC tag)
    if as_local > now + timedelta(hours=6) and stripped <= now + timedelta(hours=2):
        return stripped
    return as_local


def outlook_dt_str(d: date) -> str:
    # Outlook Jet Restrict prefers US-ish m/d/yyyy in many locales; also try ISO
    return f"{d.month}/{d.day}/{d.year}"


def item_row(mail, folder: str, cfg: MailConfig) -> dict | None:
    try:
        if int(getattr(mail, "Class", OL_MAIL) or 0) != OL_MAIL:
            return None
        subject = (mail.Subject or "").strip()
        sender = (getattr(mail, "SenderName", None) or "").strip()
        sender_addr = (getattr(mail, "SenderEmailAddress", None) or "").strip()
        to = (mail.To or "").strip()
        cc = (mail.CC or "").strip()
        unread = bool(getattr(mail, "UnRead", False))
        entry_id = str(getattr(mail, "EntryID", "") or "")
        conversation = str(getattr(mail, "ConversationTopic", "") or subject)
        received = getattr(mail, "ReceivedTime", None)
        sent_on = getattr(mail, "SentOn", None)
        when = received if folder == "inbox" else sent_on or received
        if when is None:
            return None
        when_nz = to_naive_local(when) if isinstance(when, datetime) else when
        body = (mail.Body or "")[:400]
        preview = " ".join(body.split())[:220]
        text_blob = f"{subject}\n{preview}"
        parent_name = ""
        try:
            parent = getattr(mail, "Parent", None)
            parent_name = str(getattr(parent, "Name", "") or "")
        except Exception:
            parent_name = ""
        actionish = bool(ACTION_HINTS.search(text_blob))
        fyiish = bool(FYI_HINTS.search(text_blob)) and not unread
        noise = cfg.is_noise_text(subject) or cfg.is_noise_text(preview)
        if parent_name and cfg.ignore_folders and cfg.ignore_folders.search(parent_name):
            noise = True
            actionish = False
        # Repo / pull request mail is noise unless the BA is assigned or @-mentioned
        subject_l = subject.lower()
        if any(repo in subject_l for repo in cfg.noise_repos) or "pull request" in subject_l:
            if "assigned you" not in subject_l and cfg.mention not in preview.lower():
                noise = True
        return {
            "folder": folder,
            "parent_folder": parent_name or None,
            "subject": subject,
            "from": sender,
            "from_addr": sender_addr,
            "to": to,
            "cc": cc,
            "unread": unread,
            "when": when_nz.strftime("%Y-%m-%d %H:%M") if hasattr(when_nz, "strftime") else str(when_nz),
            "when_date": when_nz.strftime("%Y-%m-%d") if hasattr(when_nz, "strftime") else "",
            "conversation": conversation,
            "preview": preview,
            "action_hint": actionish and not noise,
            "fyi_hint": fyiish or noise,
            "noise": noise,
            "entry_id": entry_id[:24],
        }
    except Exception as exc:  # noqa: BLE001
        return {"folder": folder, "error": str(exc), "subject": "(unreadable)"}


def collect_folder(ns, folder_id: int, folder_name: str, since: date, limit: int, cfg: MailConfig) -> list[dict]:
    folder = ns.GetDefaultFolder(folder_id)
    items = folder.Items
    items.Sort("[ReceivedTime]" if folder_id == OL_INBOX else "[SentOn]", True)
    since_dt = datetime.combine(since, datetime.min.time())
    out: list[dict] = []
    # Prefer Restrict; fall back to scan
    filter_s = f"[ReceivedTime] >= '{outlook_dt_str(since)}'" if folder_id == OL_INBOX else f"[SentOn] >= '{outlook_dt_str(since)}'"
    try:
        restricted = items.Restrict(filter_s)
        restricted.Sort("[ReceivedTime]" if folder_id == OL_INBOX else "[SentOn]", True)
        enumerable = restricted
    except Exception:
        enumerable = items

    count = 0
    for mail in enumerable:
        count += 1
        if count > limit * 3:
            break
        row = item_row(mail, folder_name, cfg)
        if not row or row.get("error"):
            if row and row.get("error"):
                out.append(row)
            continue
        try:
            when = datetime.strptime(row["when"], "%Y-%m-%d %H:%M")
        except Exception:
            when = since_dt
        if when.date() < since:
            # Sorted newest first; can stop once past window if Restrict worked
            if enumerable is not items:
                break
            continue
        out.append(row)
        if len(out) >= limit:
            break
    return out


def classify(inbox: list[dict], sent: list[dict]) -> dict:
    sent_topics = {(s.get("conversation") or s.get("subject") or "").strip().lower() for s in sent}
    sent_subjects = {(s.get("subject") or "").strip().lower() for s in sent}

    needs_action = []
    likely_replied = []
    fyi = []
    unread = []

    for m in inbox:
        subj = (m.get("subject") or "").strip().lower()
        topic = (m.get("conversation") or subj).strip().lower()
        # strip common Re:/Fw: for match
        norm = re.sub(r"^(re|fw|fwd):\s*", "", subj, flags=re.I).strip().lower()
        replied = topic in sent_topics or subj in sent_subjects or norm in {
            re.sub(r"^(re|fw|fwd):\s*", "", s, flags=re.I).strip().lower() for s in sent_subjects
        }
        bucket = {
            **m,
            "likely_replied": replied,
            "triage": "unread"
            if m.get("unread")
            else ("likely_replied" if replied else ("fyi" if m.get("fyi_hint") and not m.get("action_hint") else "review")),
        }
        if m.get("unread"):
            unread.append(bucket)
        if m.get("noise") and not m.get("unread"):
            fyi.append(bucket)
        elif replied and not m.get("unread"):
            likely_replied.append(bucket)
        elif m.get("fyi_hint") and not m.get("action_hint") and not m.get("unread"):
            fyi.append(bucket)
        else:
            needs_action.append(bucket)

    return {
        "needs_action_or_review": needs_action,
        "unread": unread,
        "likely_already_handled": likely_replied,
        "fyi_low": fyi,
        "sent_recent": sent,
    }


def main() -> int:
    args = parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    today = local_now().date()
    since = date.fromisoformat(args.since) if args.since else default_since(today)
    cfg = MailConfig(load_rules_text(Path(os.path.expanduser(args.cursor_home))))

    if os.name != "nt":
        print(f"{UNABLE} (Outlook desktop scan is Windows only)")
        return 2
    try:
        import win32com.client  # type: ignore
    except ImportError:
        print(f"{UNABLE} (pywin32 not installed: py -m pip install pywin32)")
        return 2
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        ns = outlook.GetNamespace("MAPI")
        inbox = collect_folder(ns, OL_INBOX, "inbox", since, args.max, cfg)
        sent = collect_folder(ns, OL_SENT, "sent", since, args.max, cfg)
    except Exception as exc:  # noqa: BLE001 - any COM failure means "unable to check"
        print(f"{UNABLE} (Outlook not available: {type(exc).__name__})")
        return 2
    classified = classify(inbox, sent)

    payload = {
        "scanned_at": local_now().isoformat(timespec="seconds"),
        "since": since.isoformat(),
        "through": today.isoformat(),
        "counts": {
            "inbox": len(inbox),
            "sent": len(sent),
            "unread": len(classified["unread"]),
            "needs_action_or_review": len(classified["needs_action_or_review"]),
            "likely_already_handled": len(classified["likely_already_handled"]),
        },
        **classified,
    }

    out_path = Path(args.out) if args.out else None
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {out_path}")

    # Compact stdout for agent
    print(f"MAIL_TRIAGE since={since} inbox={len(inbox)} sent={len(sent)} unread={len(classified['unread'])}")
    print("\n=== UNREAD ===")
    for m in classified["unread"][:25]:
        print(f"- [{m.get('when')}] {m.get('from')}: {m.get('subject')}")
    print("\n=== NEEDS ACTION / REVIEW (not clearly replied) ===")
    for m in classified["needs_action_or_review"][:30]:
        flag = "UNREAD" if m.get("unread") else "review"
        print(f"- [{flag}] [{m.get('when')}] {m.get('from')}: {m.get('subject')}")
        if m.get("preview"):
            print(f"    {m['preview'][:160]}")
    print("\n=== LIKELY ALREADY HANDLED (matching sent) ===")
    for m in classified["likely_already_handled"][:15]:
        print(f"- [{m.get('when')}] {m.get('from')}: {m.get('subject')}")
    print("\n=== YOUR RECENT SENT (commitments / follow-ups) ===")
    for m in sent[:20]:
        print(f"- [{m.get('when')}] To {m.get('to')}: {m.get('subject')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
