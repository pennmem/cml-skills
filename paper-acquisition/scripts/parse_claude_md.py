#!/usr/bin/env python3
"""Parse a CLAUDE.md file from a CML paper repo into structured fields.

Usage:
    python parse_claude_md.py <path/to/CLAUDE.md>
    python parse_claude_md.py <path/to/CLAUDE.md> --json

The format is loose Markdown — see references/claude_md_format.md for details.
This parser uses lenient heuristics and never raises on malformed input;
unrecognized content goes into an `extra` dict.
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Known bullet prefixes under "## Key Files"
KNOWN_FIELDS = {
    "Main document:": "main_document",
    "Analysis scripts:": "analysis_scripts",
    "Data files:": "data_files",
    "Figures:": "figure_files",
    "Bibliography:": "bib_file",
}


def parse_claude_md(text: str) -> dict:
    """Parse a CLAUDE.md string. Returns a dict with known fields populated."""
    result = {
        "repo_name": None,
        "directory_structure": None,
        "main_document": None,
        "analysis_scripts": [],
        "data_files": [],
        "figure_files": [],
        "bib_file": None,
        "build": None,
        "extra": {},
        "parse_warnings": [],
    }

    # 1. Repo name = first `# ` heading
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if m:
        result["repo_name"] = m.group(1).strip()

    # 2. Directory structure = first fenced code block after "## Directory Structure"
    ds = re.search(
        r"##\s+Directory Structure\s*\n+```[^\n]*\n(.*?)\n```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if ds:
        result["directory_structure"] = ds.group(1)

    # 3. Key Files bullets
    kf_section = re.search(
        r"##\s+Key Files\s*\n(.*?)(?=\n##\s|\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if kf_section:
        for raw_line in kf_section.group(1).splitlines():
            line = raw_line.strip()
            if not line.startswith("-"):
                continue
            # Strip leading "- " and whitespace
            body = line[1:].strip()
            matched = False
            for prefix, field in KNOWN_FIELDS.items():
                if body.startswith(prefix):
                    value = body[len(prefix):].strip()
                    # Strip backticks around values
                    value = value.strip("`")
                    if field in ("analysis_scripts", "data_files", "figure_files"):
                        # Comma-separated paths, each possibly in backticks
                        paths = [p.strip().strip("`") for p in value.split(",")]
                        paths = [p for p in paths if p and not p.startswith("...")]
                        result[field] = paths
                    else:
                        result[field] = value if value.upper() != "N/A" else None
                    matched = True
                    break
            if not matched and body:
                # Keep unrecognized bullets in extra for debugging
                result["extra"].setdefault("unknown_key_file_bullets", []).append(body)

    # 4. Build section
    build = re.search(
        r"##\s+Build\s*\n+(.*?)(?=\n##\s|\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if build:
        val = build.group(1).strip()
        result["build"] = val if val and val.lower() != "unknown" else None

    # Sanity warnings
    if not result["repo_name"]:
        result["parse_warnings"].append("Could not find top-level '# ' heading")
    if not result["directory_structure"]:
        result["parse_warnings"].append("No directory structure section found")

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", type=Path, help="Path to CLAUDE.md")
    ap.add_argument("--json", action="store_true", help="Emit JSON (default: pretty)")
    args = ap.parse_args()

    if not args.path.exists():
        print(f"ERROR: {args.path} does not exist", file=sys.stderr)
        return 1

    try:
        text = args.path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"ERROR reading {args.path}: {e}", file=sys.stderr)
        return 1

    parsed = parse_claude_md(text)

    if args.json:
        print(json.dumps(parsed, indent=2))
    else:
        print(f"Repo name:          {parsed['repo_name']}")
        print(f"Main document:      {parsed['main_document'] or '(none)'}")
        print(f"Analysis scripts:   {len(parsed['analysis_scripts'])} files")
        print(f"Data files:         {len(parsed['data_files'])} files")
        print(f"Build:              {parsed['build'] or '(unknown)'}")
        if parsed["parse_warnings"]:
            print("\nWarnings:")
            for w in parsed["parse_warnings"]:
                print(f"  - {w}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
