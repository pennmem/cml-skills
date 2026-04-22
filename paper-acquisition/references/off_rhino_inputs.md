# Handling off-rhino inputs

When the skill runs outside rhino2 (Claude.ai, Claude Desktop, etc.), the local paper directories aren't accessible. Three fallback paths, in order of convenience for the user.

## Option 1: GitHub URL (preferred)

If the paper is on pennmem GitHub, the user just gives the URL or repo name:

```
"Can you pull paper-CohenKahana2019?"
"https://github.com/pennmem/paper-CohenKahana2019"
```

The skill uses `web_fetch` against `raw.githubusercontent.com` for public repos, or `gh` CLI if authenticated. This is identical to the on-rhino GitHub path — no special handling needed.

## Option 2: Repo zip upload

For private repos where the user can't set up `gh` auth in the off-rhino environment:

```
Since this repo isn't public and gh isn't authenticated here, you'll
need to upload a zip of the repo:

  1. On a machine with access: cd <repo>; zip -r repo.zip .
  2. Upload the zip in this chat

I'll unpack it and proceed as if it came from GitHub.
```

When they upload, the file lands at `/mnt/user-data/uploads/<filename>.zip`. Unpack into a workspace directory and treat it like any other repo with a CLAUDE.md.

## Option 3: PDF-only upload

For quick one-offs when the user just wants to work with the finished paper and doesn't need figures, bib, or source:

```
If you just have the PDF, upload it and I'll build a minimal bundle —
the drafts/selected.pdf will be set but figures/ will be empty and
CLAUDE.md fields won't be populated. Some downstream skills (like
figure-heavy presentations) won't work as well without the source.
```

In this case, the manifest's `source.kind` is `user_upload` and a warning goes in noting the limitations.

## Detection logic

At skill startup, after environment detection, decide the prompt:

```python
if on_rhino:
    # all sources available, no user prompt needed unless ambiguous
    pass
elif gh_authenticated and user_query_looks_like_pennmem_repo:
    # github is fine, proceed
    pass
else:
    # ask the user what they can provide
    prompt_for_off_rhino_input()
```

Don't ask if you don't have to. If the user said "get me paper-CohenKahana2019" and GitHub is reachable, just do it.

## What goes in the manifest

For option 2 (zip upload):
```json
"source": {
  "kind": "user_upload",
  "path": "/mnt/user-data/uploads/repo.zip",
  "github_url": null,
  "mtime_iso": "<zip upload time>"
}
```

For option 3 (PDF only):
```json
"source": {
  "kind": "user_upload",
  "path": "/mnt/user-data/uploads/paper.pdf",
  "github_url": null,
  "mtime_iso": "<upload time>"
},
"warnings": [
  "Only PDF available — no LaTeX source, figures directory is empty, and no CLAUDE.md fields populated."
]
```
