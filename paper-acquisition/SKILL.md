---
name: paper-acquisition
description: Use this skill whenever the user wants to find, retrieve, or assemble materials from Computational Memory Lab (CML) papers — whether to make a presentation, replicate analyses, compare findings across papers, or just pull together a reading list. Triggers include requests like "grab our paper on emotional clustering", "pull together the three CML papers on retrieved context theory", "find our paper-* repos on GitHub about free recall", or any mention of CML paper paths (`/home1/zrentala/github_migration/work/papers/`, `/data/git_from_svn/papers/`) or the `pennmem` GitHub org. Also use whenever another CML skill (like `beamer-from-papers` or `analysis-replication`) requests a paper bundle. Do NOT use this for papers outside the CML ecosystem (arXiv, Google Scholar, third-party journals) — it relies on CML-specific repository conventions.
---

# paper-acquisition

Locate CML papers across three sources (prepared local, unprepared local, pennmem GitHub), choose the right draft, and stage everything into a standardized **paper bundle** so downstream skills don't re-discover anything.

## The three sources

| Source | Path / URL | Has CLAUDE.md? | Notes |
|---|---|---|---|
| Prepared local | `/home1/zrentala/github_migration/work/papers/` | Yes | rhino2 only |
| Unprepared local | `/data/git_from_svn/papers/` | No | rhino2 only; messier layout |
| GitHub | `https://github.com/pennmem/paper-*` | Yes | All prepared |

Default search order when the user doesn't specify: **prepared local → unprepared local → GitHub**. On non-rhino machines (e.g., Claude.ai), the local paths don't exist, so it falls through to GitHub automatically.

## High-level workflow

1. **Detect environment** — are the rhino paths reachable? Sets what sources are available.
2. **Parse the user's request** — specific paper name(s), or a topic?
3. **Ask clarifying questions only if necessary** — source preference if ambiguous, or "how many papers" if topic search returns many.
4. **Locate** — for name queries, search; for topic queries, collect candidates then filter by abstract.
5. **Select the draft** — CLAUDE.md hints first, then most recent mtime among `.tex` files, then `.pdf` fallback.
6. **Build the bundle** — standardized directory described below.
7. **Report back** — tell the user what was found, where the bundle lives, and what's inside.

Each of these has a reference file; read them as you go. The SKILL.md is intentionally short — specifics live alongside.

## Optional integration with `memory-publications`

If the `memory-publications` skill is installed alongside this one, it provides richer context that makes paper-acquisition smarter without being required. Check for it at skill startup:

```bash
# On Claude.ai skills typically sit as siblings in ~/.claude/skills or similar.
# Probe the usual spots:
for d in ./skills/memory-publications /mnt/skills/user/memory-publications \
         ~/.claude/skills/memory-publications ../memory-publications; do
  [ -f "$d/SKILL.md" ] && echo "FOUND: $d" && break
done
```

When present, prefer its data over rediscovering things:

- **`references/research-index.json`** — authoritative topic classification for 206 Overleaf projects plus filename patterns for KahanaPubs PDFs. Use this as the **primary** lookup for topic-based searches (see `references/locate_by_topic.md`). It replaces the "enumerate candidates + extract every abstract" walk when the user's query maps cleanly onto one of the five research threads.
- **`references/current-projects.md`** — priority-ranked list of 12 active manuscripts with Box folder IDs, lead authors, short names, and status. Use it to resolve short-name queries like "my PTSD paper" or "the observational stim paper" to concrete Box folders + `.tex` file IDs (see `references/locate_by_name.md`).
- **`references/domain-knowledge.md`** — CMR-family model details, TAG framework, oscillations vocabulary. Useful when the user says "our sCMR paper" and you need to know sCMR is the spatial extension (Herweg & Kahana) vs. CMR-IA (Jin et al.).

**When `memory-publications` is absent**, fall back to the behaviors already documented in `references/locate_by_topic.md` and `references/locate_by_name.md` — filesystem walks, abstract extraction, pennmem GitHub enumeration. The skill is fully functional without it; the integration just avoids reinventing work that's already indexed.

**Do not duplicate** memory-publications content into this skill's references. If a user asks for something covered by its files and the skill isn't installed, report the gap rather than partially replicating it.


## Environment detection

```bash
if [ -d /home1/zrentala/github_migration/work/papers ]; then echo "on_rhino"; else echo "off_rhino"; fi
```

On-rhino: all three sources available. Off-rhino (Claude.ai, Claude Desktop, etc.): only GitHub is directly searchable. The user can still supply papers manually via upload or zip — see `references/off_rhino_inputs.md`.

## The paper bundle (output format)

Every run produces one bundle per paper at `<workspace>/bundles/<paper_slug>/`:

```
<paper_slug>/
├── manifest.json      # title, authors, year, source, paths to other files
├── abstract.txt       # extracted from .tex or first-page PDF
├── claude_md.md       # copy of original CLAUDE.md if present, else absent
├── drafts/
│   ├── selected.tex   # or selected.pdf if no .tex available
│   └── <other drafts> # other .tex/.pdf files seen, for reference
├── figures/           # all figure files copied here with original names
├── references.bib     # if found, else absent
└── source/            # symlink or copy of the full original repo/dir
```

Downstream skills should read `manifest.json` first and only fall back to `source/` for anything custom.

See `references/bundle_format.md` for the exact manifest schema.

## Workflow details

### Step 1: Parse the user's request

Extract from their message:

- **Mode**: name-based (one or more specific papers) or topic-based (find relevant)
- **Source preference** (if stated): prepared-only, unprepared-only, github-only, or default cascade
- **N**: how many papers they want (only relevant for topic mode)

Don't over-interrogate. If they said "get me the Cohen & Kahana 2019 paper," just start looking. If they said "find our papers about emotional memory," ask only "how many should I pull?"

### Step 2: Locate

For **name-based** lookups, see `references/locate_by_name.md`. The short version:

- Fuzzy-match the requested name against directory names in the active sources
- On GitHub, search `pennmem` repos with prefix `paper-` (use `gh` CLI if available, else `web_fetch` against the GitHub API)
- If multiple matches, show the user the candidates and let them pick

For **topic-based** lookups, see `references/locate_by_topic.md`:

- Enumerate candidates from the selected sources
- Extract just the abstract from each (fast — first paragraph of main `.tex` or page 1 of PDF)
- Present abstracts with short titles to the user
- They pick N

### Step 3: Pick the draft

See `references/draft_detection.md`. Summary:

1. If CLAUDE.md has a `Main document:` field that's not `N/A`, use that.
2. Else, list all `.tex` files in the repo, pick the one with most recent mtime (excluding common non-draft files: supplementary, response, cover letter).
3. If no `.tex` exists, fall back to the most recent `.pdf`.
4. Record all candidates in `manifest.json` so the user can override.

### Step 4: Build the bundle

Use `scripts/build_bundle.py`. It takes a source directory and writes the standardized bundle. See the script's `--help` for options.

### Step 5: Report

When done, tell the user:

- Which paper(s) were found and from which source
- Which draft was chosen and why (mtime? CLAUDE.md hint?)
- What's in the bundle (figure count, has-bib, etc.)
- The bundle path

Keep it terse — no need to narrate the process unless something went wrong.

## GitHub access

The skill needs to read from `pennmem` repos. Three tiers of access:

1. **`gh` CLI authenticated** (preferred): fastest, works for private repos if the user has access.
2. **`web_fetch` on raw GitHub URLs** (fallback): works for public repos only, no auth needed.
3. **User doesn't have access configured**: stop and walk them through setup. See `references/github_pennmem.md` for the setup script.

Check for `gh auth status` at the start of any GitHub-touching call. If it fails, fall through to `web_fetch` for public repos or prompt the user to set up `gh` for private ones.

## Off-rhino inputs

If the skill is running on Claude.ai or similar and the user wants a paper that only exists locally on rhino, see `references/off_rhino_inputs.md` — it covers asking them to upload a zip, paste the GitHub URL, or transfer files.

## Reference files

- `references/bundle_format.md` — manifest schema and bundle layout
- `references/locate_by_name.md` — name-matching heuristics across sources
- `references/locate_by_topic.md` — abstract-based filtering workflow
- `references/draft_detection.md` — picking the right draft
- `references/claude_md_format.md` — parsing the CLAUDE.md format CML uses
- `references/github_pennmem.md` — GitHub auth setup + API calls
- `references/off_rhino_inputs.md` — how to handle users who can't reach rhino

## Scripts

- `scripts/parse_claude_md.py` — parse a CLAUDE.md into structured fields
- `scripts/list_pennmem_papers.py` — enumerate `paper-*` repos in pennmem
- `scripts/build_bundle.py` — construct the standardized bundle from a source dir
- `scripts/extract_abstract.py` — pull abstract from .tex or PDF
- `scripts/extract_figures.py` — gather all figure files from a repo

Each script has a `--help` flag. Read the script itself before modifying.
