# Locating papers by topic

When the user gives a topic ("find our papers on emotional memory", "what have we written about PTSD intrusions?"), there are two ways to resolve it — and which one you use depends on whether the `memory-publications` skill is installed.

## Two paths

### Fast path: `memory-publications/references/research-index.json` (when installed)

If the skill startup check found `$MEMPUB_DIR`, use its research index as the primary lookup. It pre-classifies 206 Overleaf projects and all KahanaPubs filename patterns into five research threads:

1. `memory_theory_and_models` — TCM, CMR, sCMR, CMR-IA, free recall phenomena
2. `behavioral_economics_memory_decisions` — Wachter / Ramayya / Zaghloul work
3. `eeg_oscillations` — intracranial + scalp EEG, theta/alpha/beta/gamma
4. `brain_stimulation` — DARPA RAM, Nia Therapeutics, open/closed-loop
5. `single_unit_recordings` — time cells, MTL phase locking

Workflow:

```python
import json
from pathlib import Path

index = json.loads(Path(mempub_dir, "references/research-index.json").read_text())

# 1. Map the user's topic words to one or more threads
#    Simple: check for keywords in each thread's label + description
#    Better: ask Claude which thread(s) the topic belongs to

# 2. Pull the candidate papers from those threads
candidates = []
for thread_id in selected_threads:
    thread = index["topics"][thread_id]
    candidates.extend(thread["overleaf_projects"])          # Overleaf project names
    candidates.extend(thread.get("kahana_pubs_patterns", []))  # KahanaPubs filename patterns

# 3. Present to the user
```

Present the candidates to the user with the index's metadata (project name, note if present, thread label) and ask how many to bundle. **Do not extract abstracts at this stage** — the index already did that classification work.

When the user picks specific papers, resolve each back to a source:

- Overleaf project names correspond to directory names in `/home1/zrentala/github_migration/work/papers/` (approximately — slugify and match) and to `pennmem/paper-<n>` GitHub repos.
- KahanaPubs patterns like `PolyEtal09` correspond to PDFs in `RESEARCH/References-Publications/KahanaPubs/` on Box, or to `paper-PolynEtal2009` style repos.

For mapping Overleaf project IDs → Box folder IDs when the user has Box access, consult `memory-publications/references/current-projects.md`, which has the authoritative mapping for the 12 active manuscripts.

### Slow path: abstract-walking (fallback when memory-publications is absent)

When the research index isn't available, use the original enumerate-then-filter approach:

#### 1. Enumerate candidates

List all papers in the selected source(s). For:

- **Prepared local**: `ls /home1/zrentala/github_migration/work/papers/`
- **Unprepared local**: `ls /data/git_from_svn/papers/` — messier; see handling below.
- **GitHub**: all `paper-*` repos in pennmem (cached; see `github_pennmem.md`)

#### 2. Extract abstracts

For each candidate, pull just the abstract. Cheap options in order:

1. `.tex` source: find `\begin{abstract}...\end{abstract}` (or the first paragraph after `\maketitle` for some templates). Use `scripts/extract_abstract.py`.
2. PDF fallback: extract text from page 1, look for the first paragraph after "Abstract" keyword.
3. CLAUDE.md fallback: sometimes the repo description or first prose paragraph gives the gist.

Skip candidates where all three fail — log as "no abstract available" but don't crash.

#### 3. Filter by relevance

**Keyword match (fast, specific topics)**:
```python
keywords = topic.lower().split()
scored = []
for paper, abstract in candidates:
    score = sum(1 for k in keywords if k in abstract.lower())
    if score > 0:
        scored.append((score, paper, abstract))
scored.sort(reverse=True)
```

**Semantic match (vaguer topics)**: have Claude read each abstract and rank. Good for topics like "papers where we challenged the SAM model" where keywords miss it. More expensive but better.

Default to keyword matching; escalate to semantic when the topic is abstract or keyword search returns nothing.

#### 4. Present candidates

Show titles + one-sentence abstracts + relevance rank. **Ask how many they want before building bundles** — building bundles is expensive.

```
Found 8 candidate papers on "emotional clustering":

  1. CohenKahana2019 — Retrieved-context theory of emotional memory...
  2. LongKahana2017 — Emotional arousal and memory retrieval dynamics...
  3. Talmi2019 — ...
  ...

How many should I bundle? (top N, or comma-separated indices, or "all")
```

## Common to both paths

### Confirmation before bundling

Always present the candidate list and wait for selection before running `build_bundle.py`. Users routinely correct or prune the list — running bundle construction on the full candidate set is wasteful.

### Unprepared-local special handling

`/data/git_from_svn/papers/` is messier — it contains things that aren't finished papers. Heuristics to filter:

- Must contain at least one `.tex` or `.pdf` file
- Name doesn't start with an underscore or contain "tmp", "scratch", "old"
- Directory hasn't been touched in > 10 years (probably abandoned)

When in doubt, include and warn. Don't silently drop.

### Caching

Topic searches (slow-path only) can touch many papers. Cache extracted abstracts per-repo keyed on source file mtime:

```
<workspace>/.abstract_cache/<paper_slug>.json
```

Invalidate when the source file's mtime changes.

The fast path (research-index) needs no caching — the JSON file is small and already indexed.
