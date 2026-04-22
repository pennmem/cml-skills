# Draft detection

A CML paper repo typically contains many draft files accumulated over the paper's history — `paper_v1.tex`, `paper_v7_submitted.tex`, `response_to_reviewers.tex`, `supplement.tex`, etc. This skill has to pick *one* to hand downstream as "the current paper."

## Priority ladder

Try each rule in order. Stop at the first one that returns a unique, valid result.

### 1. CLAUDE.md `Main document` hint

If CLAUDE.md has `Main document: <path>` and the value is **not** `N/A` / empty / missing, resolve that path and use it.

```python
hint = claude_md_fields.get("main_document")
if hint and hint.upper() != "N/A" and (repo_root / hint).exists():
    return repo_root / hint, "claude_md_hint"
```

### 2. Most recent `.tex` file, excluding non-draft patterns

List all `.tex` files in the repo. Drop anything matching these patterns (case-insensitive, substring match):

- `supplement`, `supplementary`, `si.tex`
- `response`, `reviewer`, `rebuttal`
- `cover_letter`, `coverletter`
- `readme`
- `slides`, `presentation`, `talk`

Of what remains, take the one with the most recent mtime.

```python
candidates = [p for p in repo_root.rglob("*.tex") if not matches_exclusion(p.name)]
if candidates:
    return max(candidates, key=lambda p: p.stat().st_mtime), "most_recent_mtime"
```

### 3. PDF fallback

If no `.tex` remains, repeat the same logic with `.pdf` files.

```python
candidates = [p for p in repo_root.rglob("*.pdf") if not matches_exclusion(p.name)]
if candidates:
    return max(candidates, key=lambda p: p.stat().st_mtime), "pdf_fallback"
```

### 4. Nothing found

Return `None` and record an error in the manifest warnings. Don't crash — the user might want to continue with just figures or raw source.

## Edge cases

**Repo has only one `.tex`**: Easy, use it — no exclusion filtering needed.

**Multiple .tex files with identical mtimes** (e.g., fresh clone where git sets all to clone time): Fall back to alphabetical order of filenames, and record this in the manifest as a warning. The user should correct.

**Draft is in a subdirectory like `writing/`, `manuscript/`, or `paper/`**: `rglob("*.tex")` picks these up fine. No special handling needed.

**Compiled `.pdf` sitting next to `.tex`**: Both pass exclusion filters. Prefer `.tex` when it exists — it's the source of truth. The compiled PDF can still be stored as `drafts/selected.pdf` alongside if present.

**File named `main.tex` or `paper.tex`**: Don't give these extra priority. The mtime rule is deliberate — the most recently edited file is almost always what the author is working on.

## Recording the choice

Always write to `manifest.json`:

```json
{
  "selected_draft": {
    "path": "drafts/selected.tex",
    "original_name": "CohenKahana2019_v7.tex",
    "selection_reason": "most_recent_mtime",
    "mtime_iso": "2024-03-15T10:22:00Z"
  },
  "alternate_drafts": [
    {"path": "drafts/alternate_v6.tex", "original_name": "CohenKahana2019_v6.tex"},
    {"path": "drafts/alternate_submission.tex", "original_name": "submission_copy.tex"}
  ]
}
```

All other `.tex` files go into `alternate_drafts` so the user can override easily with `--override-draft drafts/alternate_submission.tex` on a later call.

## User override

Always honor an explicit `--draft <path>` override from the user, skipping the ladder entirely. Record `selection_reason: "user_override"`.
