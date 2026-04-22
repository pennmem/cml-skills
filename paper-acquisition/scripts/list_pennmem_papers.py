#!/usr/bin/env python3
"""List paper repos in the pennmem GitHub org.

Usage:
    python list_pennmem_papers.py                  # list all paper-* repos
    python list_pennmem_papers.py --query cohen    # filter name by substring
    python list_pennmem_papers.py --json           # JSON output
    python list_pennmem_papers.py --cache-ttl 3600 # use cache if < 1hr old

Tries `gh` CLI first (for auth + private repos); falls back to public
GitHub API via urllib. Caches results to <cache_dir>/pennmem_repos.json.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


CACHE_DIR = Path.home() / ".cache" / "cml-paper-acquisition"
CACHE_FILE = CACHE_DIR / "pennmem_repos.json"
API_PAGE_SIZE = 100


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def list_via_gh() -> list[dict] | None:
    """Try listing repos via gh CLI. Returns None if gh unavailable or not auth'd."""
    if not shutil.which("gh"):
        return None
    check = subprocess.run(
        ["gh", "auth", "status"], capture_output=True, text=True
    )
    if check.returncode != 0:
        return None

    try:
        result = subprocess.run(
            [
                "gh", "repo", "list", "pennmem",
                "--limit", "500",
                "--json", "name,description,pushedAt,visibility,url",
            ],
            capture_output=True, text=True, timeout=60, check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"WARN: gh call failed: {e}", file=sys.stderr)
        return None

    repos = json.loads(result.stdout)
    return [r for r in repos if r["name"].startswith("paper-")]


def list_via_public_api() -> list[dict]:
    """Fall back to the public GitHub API. Public repos only, rate-limited."""
    repos: list[dict] = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/pennmem/repos?per_page={API_PAGE_SIZE}&page={page}"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status != 200:
                    print(f"WARN: API returned {resp.status}", file=sys.stderr)
                    break
                page_data = json.loads(resp.read())
        except Exception as e:
            print(f"WARN: API call failed on page {page}: {e}", file=sys.stderr)
            break

        if not page_data:
            break
        repos.extend(page_data)
        if len(page_data) < API_PAGE_SIZE:
            break
        page += 1
        if page > 20:  # safety brake (2000 repos cap)
            break

    # Normalize to match gh's output shape
    out = []
    for r in repos:
        if not r["name"].startswith("paper-"):
            continue
        out.append({
            "name": r["name"],
            "description": r.get("description") or "",
            "pushedAt": r.get("pushed_at"),
            "visibility": "public" if not r.get("private") else "private",
            "url": r.get("html_url"),
        })
    return out


def load_cache(ttl_seconds: int) -> list[dict] | None:
    if not CACHE_FILE.exists():
        return None
    age = time.time() - CACHE_FILE.stat().st_mtime
    if age > ttl_seconds:
        return None
    try:
        return json.loads(CACHE_FILE.read_text())
    except Exception:
        return None


def save_cache(repos: list[dict]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(repos, indent=2))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--query", default=None, help="Filter repos by name substring (case/punctuation-insensitive)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--cache-ttl", type=int, default=86400, help="Cache TTL in seconds (default: 1 day)")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--force-public", action="store_true", help="Skip gh CLI even if available")
    args = ap.parse_args()

    repos = None if args.no_cache else load_cache(args.cache_ttl)
    if repos is None:
        if not args.force_public:
            repos = list_via_gh()
        if repos is None:
            repos = list_via_public_api()
        save_cache(repos)

    if args.query:
        q = _normalize(args.query)
        repos = [r for r in repos if q in _normalize(r["name"])]

    repos.sort(key=lambda r: r["name"].lower())

    if args.json:
        print(json.dumps(repos, indent=2))
    else:
        if not repos:
            print("No matching repos.")
            return 1
        for r in repos:
            desc = (r.get("description") or "").strip()
            if len(desc) > 60:
                desc = desc[:57] + "..."
            print(f"  {r['name']:50s}  {r.get('pushedAt', '')[:10]}  {desc}")
        print(f"\nTotal: {len(repos)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
