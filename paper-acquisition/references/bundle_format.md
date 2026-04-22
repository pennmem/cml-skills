# Paper bundle format

The paper bundle is a standardized directory layout that downstream skills (`beamer-from-papers`, `analysis-replication`, etc.) consume. Treat this as a contract — don't break it without updating downstream skills.

## Directory layout

```
<paper_slug>/
├── manifest.json       # REQUIRED - see schema below
├── abstract.txt        # REQUIRED - plain-text abstract
├── claude_md.md        # OPTIONAL - only if source had CLAUDE.md
├── drafts/
│   ├── selected.tex    # REQUIRED - or selected.pdf if no .tex
│   ├── selected.pdf    # OPTIONAL - compiled version if available
│   └── alternate_*     # OPTIONAL - other candidate drafts, named alternate_<origname>
├── figures/            # REQUIRED (may be empty) - all figure files
├── references.bib      # OPTIONAL - if a .bib was found
└── source/             # REQUIRED - symlink or copy of original
```

The `<paper_slug>` is derived from the source directory name, lowercased and with non-alphanumeric characters replaced by underscores. Example: `CohenKahana2019` → `cohenkahana2019`.

## manifest.json schema

```json
{
  "schema_version": "1.0",
  "paper_slug": "cohenkahana2019",
  "title": "Retrieved-context theory of emotional memory",
  "authors": ["Cohen, N.", "Kahana, M. J."],
  "year": 2019,
  "venue": "Journal or preprint server if known, else null",
  "source": {
    "kind": "prepared_local | unprepared_local | github | user_upload",
    "path": "/home1/zrentala/github_migration/work/papers/CohenKahana2019",
    "github_url": "https://github.com/pennmem/paper-CohenKahana2019",
    "mtime_iso": "2024-03-15T10:22:00Z"
  },
  "selected_draft": {
    "path": "drafts/selected.tex",
    "original_name": "CohenKahana2019_v7.tex",
    "selection_reason": "most_recent_mtime | claude_md_hint | pdf_fallback | user_override",
    "mtime_iso": "2024-03-15T10:22:00Z"
  },
  "alternate_drafts": [
    {"path": "drafts/alternate_v6.tex", "original_name": "CohenKahana2019_v6.tex"}
  ],
  "figures": {
    "count": 13,
    "files": ["Fig1_model_schematic.pdf", "Fig2_FitComparisons.pdf", "..."]
  },
  "bib_path": "references.bib",
  "claude_md_present": true,
  "claude_md_fields": {
    "main_document": "N/A",
    "analysis_scripts": ["Core_Model/run_CMR3.py", "..."],
    "data_files": ["..."],
    "build": "Unknown"
  },
  "warnings": [
    "Main document was listed as N/A in CLAUDE.md; fell back to mtime-based selection."
  ]
}
```

### Field notes

- `title`, `authors`, `year`, `venue`: Try to extract from the `.tex` (`\title{}`, `\author{}`, `\year{}`) or from the first page of the PDF. If any field can't be confidently extracted, set it to `null` and add a warning — never guess.
- `source.kind`: One of `prepared_local`, `unprepared_local`, `github`, or `user_upload`. Anything else → fix the code.
- `selection_reason`: Critical for debugging. If a downstream skill produces something weird, the first question is "which draft did we pick and why?"
- `claude_md_fields`: Only populated when the source had a CLAUDE.md. The fields mirror the CLAUDE.md format (see `claude_md_format.md`).
- `warnings`: Any non-fatal issues the user or a downstream skill should know about. Keep them human-readable.

## Design intent

Three things a downstream skill typically needs:

1. **The text of the paper** → read `drafts/selected.tex` (or fall back to PDF)
2. **The figures to embed in a talk** → grab files from `figures/`
3. **Metadata for citations** → read `manifest.json` and optionally `references.bib`

By standardizing these three, the downstream skill doesn't need to know anything about where the paper came from or how CML organizes its repos. That's the whole point.

## Multi-paper bundles

When the user asks for several papers at once, produce one bundle per paper under a shared parent:

```
bundles/
├── cohenkahana2019/
├── healeykahana2016/
└── zaromb2006/
```

Don't try to merge across papers at this stage — that's the downstream skill's job.
