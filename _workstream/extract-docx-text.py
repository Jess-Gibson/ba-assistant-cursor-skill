#!/usr/bin/env python3
"""Extract readable text (or raw XML) from a .docx file for meeting debriefs.

A .docx is a ZIP archive; the document body lives in word/document.xml as
WordprocessingML. This uses only the standard library (zipfile + XML
parsing) so it runs identically on Windows, Mac, and Linux with whatever
Python launches it (`py` on Windows, `python3` on Mac/Linux) -- no
PowerShell, no external packages.

Default mode extracts clean readable text (one line per paragraph), matching
what a debrief needs to read. --raw-xml dumps word/document.xml unprocessed,
for cases where the agent needs to see formatting/track-changes markup that
plain text extraction discards.

Usage:
  python3 extract-docx-text.py --docx-path meeting.docx --out-path out.txt
  python3 extract-docx-text.py --docx-path meeting.docx --out-path out.xml --raw-xml
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def extract_text(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as z:
        xml_bytes = z.read("word/document.xml")
    root = ET.fromstring(xml_bytes)

    paragraphs = []
    for p in root.iter(f"{WORD_NS}p"):
        parts = []
        for node in p.iter():
            tag = node.tag
            if tag == f"{WORD_NS}t":
                parts.append(node.text or "")
            elif tag == f"{WORD_NS}tab":
                parts.append("\t")
            elif tag in (f"{WORD_NS}br", f"{WORD_NS}cr"):
                parts.append("\n")
        paragraphs.append("".join(parts))
    return "\n".join(paragraphs)


def extract_raw_xml(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as z:
        return z.read("word/document.xml").decode("utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract text or raw XML from a .docx file")
    ap.add_argument("--docx-path", required=True, type=Path)
    ap.add_argument("--out-path", required=True, type=Path)
    ap.add_argument(
        "--raw-xml",
        action="store_true",
        help="Dump word/document.xml raw instead of extracted readable text",
    )
    args = ap.parse_args()

    docx_path = args.docx_path.expanduser().resolve()
    out_path = args.out_path.expanduser().resolve()

    if not docx_path.is_file():
        print(f"ERROR: docx not found: {docx_path}", file=sys.stderr)
        return 1

    try:
        content = extract_raw_xml(docx_path) if args.raw_xml else extract_text(docx_path)
    except zipfile.BadZipFile:
        print(f"ERROR: not a valid .docx (not a zip archive): {docx_path}", file=sys.stderr)
        return 1
    except KeyError:
        print(
            f"ERROR: {docx_path} is a zip but has no word/document.xml -- "
            "not a Word document?",
            file=sys.stderr,
        )
        return 1
    except ET.ParseError as e:
        print(f"ERROR: could not parse word/document.xml as XML: {e}", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    kind = "raw XML" if args.raw_xml else "extracted text"
    print(f"Wrote {kind} ({len(content)} chars) -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
