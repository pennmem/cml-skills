# Locating papers by name

When the user names a specific paper (or several), this is the flow. Cascade through sources unless they specified one.

## Parsing the user's reference

Users refer to papers in varied ways:

- By first-author + year: "Cohen & Kahana 2019", "CohenKahana2019", "cohen 2019"
- By topic-ish title: "the emotional clustering paper", "our retrieved context theory paper"
- By repo name directly: "paper-CohenKahana2019"
- By GitHub URL: "https://github.com/pennmem/paper-CohenKahana2019"

Normalize to a search string by stripping: "paper-", "https://github.com/pennmem/", whitespace, `&`, `and`, `et al`.

## Searching a local directory

```python
import re
def normalize(s: str) -> str:
    return re.sub(r'[^a-z0-9]', '', s.lower())

query_norm = normalize(user_query)
candidates = []
for d in source_root.iterdir():
    if d.is_dir() and query_norm in normalize(d.name):
        candidates.append(d)
```

Rank matches by:
1. Exact match of normalized names (best)
2. Query is prefix of directory name
3. Query is substring of directory name

If multiple candidates tie, show them all to the user and let them pick.

## Searching GitHub

With `gh`:
```bash
gh repo list pennmem --limit 500 --json name \
  | jq --arg q "$QUERY_NORM" '[.[] | select(.name | ascii_downcase | gsub("[^a-z0-9]"; "") | contains($q))]'
```

Without `gh`, use the GitHub search API:
```
GET https://api.github.com/search/repositories?q=org:pennmem+paper-<query>+in:name
```

Note: GitHub's search-in-name is token-based, so searches for "CohenKahana2019" may not match `paper-CohenKahana2019` exactly. Prefer listing all `paper-*` repos and filtering client-side for fuzzy matching.

## Handling multiple matches

If more than one candidate survives ranking, stop and ask the user:

```
Found multiple matches for "cohen 2019":

  1. CohenKahana2019 (prepared local, updated 2024-03-15)
  2. CohenDaume2019 (GitHub pennmem/paper-CohenDaume2019, updated 2022-08-01)

Which one did you mean? (1 or 2, or "both" / "all")
```

Keep it terse. Always show *where* each candidate lives and *when* it was last touched — those are the tiebreakers the user needs.

## Handling zero matches

If nothing matches in the active sources:

1. **Try the next source in the cascade** before giving up. If the user didn't pin a source, a "missing" paper on rhino might be on GitHub.
2. **Suggest alternatives**: show the 3 closest-matching repo names in the source(s) searched.
3. **Only then ask the user** — with specifics: "Searched `prepared local` and `github`, no match for 'kahama2019'. Did you mean CohenKahana2019?"

## Batch mode

If the user asks for multiple papers in one call ("get me CohenKahana2019 and HealeyKahana2016"), run the search per-paper and build one bundle per paper. Don't fail the whole batch if one fails — collect errors and report at the end.
