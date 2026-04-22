# Accessing pennmem paper repos on GitHub

CML's paper repos all live under `https://github.com/pennmem/` with the prefix `paper-`. Public repos can be read without auth; private repos need either `gh` CLI auth or a personal access token.

## Quick check at skill startup

```bash
if gh auth status >/dev/null 2>&1; then
  echo "gh_authenticated"
elif command -v gh >/dev/null 2>&1; then
  echo "gh_installed_not_authed"
else
  echo "gh_missing"
fi
```

Three states → three strategies below.

## Strategy A: `gh` authenticated (preferred)

Full access to public and private repos. Use it for everything.

**List all `paper-*` repos:**
```bash
gh repo list pennmem --limit 500 --json name,description,pushedAt,visibility \
  | jq '[.[] | select(.name | startswith("paper-"))]'
```

**Fetch a specific file without cloning:**
```bash
gh api repos/pennmem/paper-CohenKahana2019/contents/CLAUDE.md --jq '.content' | base64 -d
```

**Clone if needed for figures or full source:**
```bash
gh repo clone pennmem/paper-CohenKahana2019 <target_dir>
```

## Strategy B: `gh` installed but not authenticated

Walk the user through auth. This is a one-time setup:

```
To fetch CML papers from GitHub, you need to authenticate gh with your
GitHub account. Run this in your terminal:

    gh auth login

- Choose: GitHub.com
- Preferred protocol: HTTPS
- Authenticate with your GitHub credentials: Login with a web browser

Once the browser flow completes, rerun your original request.
```

If they can't interactively auth (e.g., in a non-interactive script), suggest a PAT:

```
Alternatively, create a personal access token at
https://github.com/settings/tokens with `repo` scope, then:

    echo "<YOUR_TOKEN>" | gh auth login --with-token
```

## Strategy C: `gh` not installed (public repos only)

Use `web_fetch` against GitHub's raw content URLs. Works for public repos without any credentials.

**List paper repos via the public API:**
```
GET https://api.github.com/orgs/pennmem/repos?per_page=100&page=1
```

Paginate (follow `Link: <...>; rel="next"` headers). Filter client-side for `name.startswith("paper-")`.

**Fetch a specific file:**
```
https://raw.githubusercontent.com/pennmem/paper-CohenKahana2019/main/CLAUDE.md
```

If `main` 404s, retry with `master`. Some older repos still default to `master`.

**For private repos without `gh`**: stop and ask the user to install `gh`. Don't try to fake it with a PAT embedded in the skill — that leaks secrets.

## Downloading full repos without `gh`

Two options:

1. **Zip download (public only)**:
   ```
   https://github.com/pennmem/paper-CohenKahana2019/archive/refs/heads/main.zip
   ```
   `web_fetch` can retrieve this and it expands to the full repo.

2. **Tell the user to clone locally and upload the zip** (if they need a private repo and can't set up `gh` remotely).

## Setup helper

For new users getting started, point them at `scripts/setup_github_auth.sh` (a small wrapper around `gh auth login` with CML-specific guidance). Don't run it automatically — make them opt in.

## API rate limits

- Unauthenticated requests: 60/hour per IP
- Authenticated: 5000/hour

For a single paper this doesn't matter. For topic-based searches that enumerate all `paper-*` repos and fetch their CLAUDE.md files, it can matter. Cache repo listings in `<workspace>/.pennmem_repos.json` with a TTL of 1 day.
