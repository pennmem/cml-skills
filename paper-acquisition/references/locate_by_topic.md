# Locating papers by topic

When the user gives a topic ("find our papers on emotional memory", "what have we written about PTSD intrusions?"), enumerate candidates, filter by abstract, and let the user pick how many to include.

## Workflow

### 1. Enumerate candidates

List all papers in the selected source(s). For:

- **Prepared local**: `ls /home1/zrentala/github_migration/work/papers/`
- **Unprepared local**: `ls /data/git_from_svn/papers/` — this set is messier, some items aren't papers. See `unprepared` notes below.
- **GitHub**: all `paper-*` repos in pennmem (cached; see `github_pennmem.md`)

### 2. Extract abstracts

For each candidate, pull just the abstract. Cheap options in order:

1. `.tex` source: find `\begin{abstract}...\end{abstract}` (or the first paragraph after `\maketitle` for some templates). Use `scripts/extract_abstract.py`.
2. PDF fallback: extract text from page 1, look for the first paragraph after "Abstract" keyword.
3. CLAUDE.md fallback: sometimes the repo description or first prose paragraph gives the gist.

Skip candidates where all three fail — log as "no abstract available" but don't crash.

### 3. Filter by relevance

Two ways to match topic to abstract:

**Keyword match (fast, works fine for specific topics)**:
```python
keywords = topic.lower().split()
scored = []
for paper, abstract in candidates:
    score = sum(1 for k in keywords if k in abstract.lower())
    if score > 0:
        scored.append((score, paper, abstract))
scored.sort(reverse=True)
```

**Semantic match (for vaguer topics)**: have Claude read each abstract and rank relevance. Good for topics like "papers where we challenged the SAM model" where keywords would miss it. More expensive but better.

Default to keyword matching; escalate to semantic matching when the user's topic is abstract or keyword search returns nothing.

### 4. Present candidates to the user

Show titles + one-sentence abstracts + relevance rank. **Ask how many they want before building bundles** — building bundles is expensive.

```
Found 8 candidate papers on "emotional clustering":

  1. CohenKahana2019 — Retrieved-context theory of emotional memory...
  2. LongKahana2017 — Emotional arousal and memory retrieval dynamics...
  3. Talmi2019 — ...
  ...

How many should I bundle? (top N, or comma-separated indices, or "all")
```

### 5. Build bundles for selected papers

Once the user picks, run the normal single-paper workflow per selection.

## Unprepared-local special handling

`/data/git_from_svn/papers/` is messier — it contains things that aren't finished papers (exploratory drafts, shared documents, etc.). Heuristics to filter:

- Must contain at least one `.tex` or `.pdf` file
- Name doesn't start with an underscore or contain "tmp", "scratch", "old"
- Directory hasn't been touched in > 10 years (probably abandoned)

When in doubt, include and warn. Don't silently drop.

## Caching

Topic searches can touch many papers. Cache the extracted abstracts per-repo keyed on the CLAUDE.md (or .tex) mtime so repeat topic searches are fast:

```
<workspace>/.abstract_cache/<paper_slug>.json
```

Invalidate when the source file's mtime changes.
