# Parsing CLAUDE.md files

CML papers (both the prepared local set and all pennmem `paper-*` repos) ship with a `CLAUDE.md` file at the repo root that summarizes the repo's structure. This skill reads that file to inform draft selection and to populate `manifest.json`.

## Format

The format is loose Markdown with a few conventional sections. Here's a canonical example (from `CohenKahana2019`):

```markdown
# CohenKahana2019

## Directory Structure
```
CohenKahana2019/
  README.txt
  Core_Model/
    CMR3.pyx
    ...
```

## Key Files
- Main document: `N/A`
- Analysis scripts: `Core_Model/HelperFiles/__init__.py`, `Core_Model/HelperFiles/crp.py`, ...
  - ... and 41 more
- Data files: `Core_Model/HelperFiles/wordproperties_CSV.csv`, ...

## Build
Unknown
```

## Fields to extract

| Field | How to extract | Notes |
|---|---|---|
| `title` (implicit) | First `# ` heading | Usually the repo name, not the paper title. Don't use this as the paper title. |
| `directory_structure` | Contents of the first fenced code block under `## Directory Structure` | Useful for sanity checks but don't rely on it — the actual repo filesystem is authoritative. |
| `main_document` | Line starting with `- Main document:` under `## Key Files` | **Often `N/A`** — when it is, fall through to mtime-based draft detection. |
| `analysis_scripts` | Line starting with `- Analysis scripts:` — comma-separated paths | Paths relative to repo root. Ignore the "... and N more" continuation lines; just take what's listed. |
| `data_files` | Line starting with `- Data files:` — comma-separated paths | Same. |
| `build` | Text under `## Build` | Often "Unknown". Pass through as-is. |

## Parsing approach

Don't try to write a strict parser — the format is hand-written and varies across repos. The script `scripts/parse_claude_md.py` uses simple regex heuristics:

1. Extract the first `# ` heading as the repo name.
2. Find each `## Key Files` bullet starting with a known prefix (`- Main document:`, `- Analysis scripts:`, etc.).
3. For comma-separated path lists, split on `,` and strip backticks.
4. Anything that doesn't match a known field → put in a `extra` dict, don't fail.

If the file doesn't parse at all, treat it as absent rather than erroring out. Log a warning into the manifest.

## What CLAUDE.md does and doesn't tell you

**It does**:
- Give a curated list of the most important analysis/data files (useful for the `analysis-replication` skill later).
- Sometimes point to the main document explicitly.

**It doesn't**:
- Reliably tell you the paper's title, authors, or year (you need `.tex` metadata for those).
- List figure files (walk `Figs/` or `figures/` directly).
- List .bib files (walk the repo or look for common names: `refs.bib`, `references.bib`, `bib.bib`).
- Guarantee the `Main document` field is populated — treat `N/A`, empty, or missing as "no hint, fall back to mtime."

## Location across sources

| Source | CLAUDE.md location |
|---|---|
| Prepared local | `<repo_root>/CLAUDE.md` — always present |
| Unprepared local | **Not present** — skip parsing, use only filesystem heuristics |
| GitHub pennmem | `<repo_root>/CLAUDE.md` — always present; fetch via raw.githubusercontent.com |

For GitHub, the raw URL is: `https://raw.githubusercontent.com/pennmem/<repo>/main/CLAUDE.md` (try `master` as fallback).
