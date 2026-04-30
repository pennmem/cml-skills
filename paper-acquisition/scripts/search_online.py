#!/usr/bin/env python3
"""Resolve a publication URL/DOI for a paper given its title and authors.

Usage:
    python search_online.py --title "Title of paper" --authors "Smith, Jones"
    python search_online.py --title "..." --authors "..." --year 2019 --json
    python search_online.py --title "..." --authors "..." --no-cache

Primary backend: CrossRef REST API (https://api.crossref.org/works). Free,
no auth, returns DOI + URL. Fallback: arXiv Atom feed for preprints that
aren't indexed in CrossRef.

Matching: title token-overlap score + first-author last-name agreement.
Exits 1 ("no confident match") rather than guessing when the score is low.

Exit codes:
    0 = confident match found
    1 = no confident match
    2 = network / hard error

Results cached at ~/.cache/cml-paper-acquisition/online_lookups.json
keyed by sha1(title|authors|year).
"""

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path  # noqa: F401  (used by fetch_publisher_pdf)

CACHE_DIR = Path.home() / ".cache" / "cml-paper-acquisition"
CACHE_FILE = CACHE_DIR / "online_lookups.json"
USER_AGENT = "paper-acquisition/1.0 (mailto:kahanalab@gmail.com)"
DEFAULT_CACHE_TTL = 7 * 24 * 3600  # 7 days
MATCH_THRESHOLD = 0.40  # combined score needed to accept
CROSSREF_ROWS = 10
ARXIV_ROWS = 5

_STOPWORDS = {
    "a", "an", "and", "as", "at", "be", "but", "by", "for", "from", "in", "is",
    "it", "of", "on", "or", "that", "the", "to", "via", "with", "without",
}


def _tokens(s: str) -> set[str]:
    s = re.sub(r"[^a-z0-9\s]", " ", s.lower())
    return {w for w in s.split() if w and w not in _STOPWORDS and len(w) > 1}


def _last_names(authors_str: str) -> list[str]:
    """Best-effort last-name extraction from an author string."""
    if not authors_str:
        return []
    # Split on common separators
    parts = re.split(r",|;|\sand\s|&", authors_str, flags=re.IGNORECASE)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # If "First Last" take last token; if "Last, First" would have been split above
        # but might still see initials/dots; pick the longest alphabetic token.
        tokens = [re.sub(r"[^A-Za-z-]", "", t) for t in p.split()]
        tokens = [t for t in tokens if len(t) > 1]
        if not tokens:
            continue
        tokens.sort(key=len, reverse=True)
        out.append(tokens[0].lower())
    return out


def _score(query_title: str, query_authors: str,
           cand_title: str, cand_authors: list[str],
           query_year: int | None, cand_year: int | None) -> float:
    """Combined match score in [0, 1]."""
    qtok = _tokens(query_title)
    ctok = _tokens(cand_title or "")
    if not qtok or not ctok:
        title_score = 0.0
    else:
        overlap = len(qtok & ctok) / max(1, len(qtok))
        title_score = overlap

    q_last = _last_names(query_authors)
    c_last = [a.lower() for a in cand_authors if a]
    author_score = 0.0
    if q_last and c_last:
        # Require first query author to appear somewhere in candidate authors.
        if q_last[0] in c_last:
            author_score = 1.0
        elif any(q in c_last for q in q_last):
            author_score = 0.6

    year_penalty = 0.0
    if query_year and cand_year:
        diff = abs(int(query_year) - int(cand_year))
        if diff == 0:
            year_penalty = 0.0
        elif diff == 1:
            year_penalty = 0.05
        else:
            year_penalty = 0.15

    # Title carries 70%, author 30%.
    return max(0.0, 0.7 * title_score + 0.3 * author_score - year_penalty)


def _http_get_json(url: str, timeout: int = 20) -> dict | None:
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                print(f"WARN: HTTP {resp.status} on {url}", file=sys.stderr)
                return None
            return json.loads(resp.read())
    except Exception as e:
        print(f"WARN: request failed: {e}", file=sys.stderr)
        return None


def _http_get_text(url: str, timeout: int = 20) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                print(f"WARN: HTTP {resp.status} on {url}", file=sys.stderr)
                return None
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"WARN: request failed: {e}", file=sys.stderr)
        return None


def _score_crossref_items(title: str, authors: str, year: int | None,
                          items: list[dict]) -> tuple[dict | None, float]:
    """Score a batch of CrossRef items, return (best_result, best_score)."""
    best = None
    best_score = 0.0
    for item in items:
        cand_title = ""
        if item.get("title"):
            cand_title = item["title"][0]
        cand_authors = []
        for a in item.get("author", []) or []:
            fam = a.get("family") or a.get("name") or ""
            if fam:
                cand_authors.append(fam)
        issued = item.get("issued", {}).get("date-parts", [[None]])
        cand_year = None
        if issued and issued[0] and issued[0][0]:
            cand_year = int(issued[0][0])

        s = _score(title, authors, cand_title, cand_authors, year, cand_year)
        if s > best_score:
            doi = item.get("DOI")
            best = {
                "title": cand_title,
                "authors": cand_authors,
                "year": cand_year,
                "doi": doi,
                "url": item.get("URL") or (f"https://doi.org/{doi}" if doi else None),
                "source": "crossref",
                "score": round(s, 3),
            }
            best_score = s
    return best, best_score


def _crossref_query(params: dict) -> list[dict]:
    params = {k: v for k, v in params.items() if v}
    params["rows"] = str(CROSSREF_ROWS)
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    data = _http_get_json(url)
    if not data or "message" not in data:
        return []
    return data["message"].get("items", []) or []


def search_crossref(title: str, authors: str, year: int | None) -> dict | None:
    """Try several CrossRef query shapes and return the best match.

    Strategies, in order (we consider candidates from each one and keep the
    highest-scoring across all of them):
      1. query.title=title & query.author=authors
      2. query.bibliographic="title authors" (free-form bibliographic search)
      3. query.title=title only (no author constraint)
      4. query.bibliographic=first-3-title-tokens (handles truncated titles)

    The multi-query approach handles cases where the local title is partial,
    messy, or differs from the canonical published title in word order.
    """
    first_author = (_last_names(authors) or [""])[0]
    title_tokens = [t for t in re.sub(r"[^a-z0-9\s]", " ", title.lower()).split()
                    if len(t) > 2]

    strategies = [
        {"query.title": title, "query.author": authors},
        {"query.bibliographic": f"{title} {first_author}".strip()},
        {"query.title": title},
    ]
    if len(title_tokens) >= 3:
        strategies.append({"query.bibliographic": " ".join(title_tokens[:6])})

    best = None
    best_score = 0.0
    seen_dois = set()
    for strat in strategies:
        items = _crossref_query(strat)
        # Dedupe by DOI so scoring isn't dominated by repeats
        fresh = []
        for it in items:
            doi = (it.get("DOI") or "").lower()
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)
            fresh.append(it)
        cand, score = _score_crossref_items(title, authors, year, fresh)
        if score > best_score:
            best, best_score = cand, score
        if best_score >= 0.85:
            break  # already a strong hit — skip remaining queries

    if best and best_score >= MATCH_THRESHOLD:
        return best
    return None


def search_arxiv(title: str, authors: str, year: int | None) -> dict | None:
    # arXiv API: space-separated terms, ti: for title, au: for author
    q_parts = []
    for t in _tokens(title):
        q_parts.append(f"ti:{t}")
    first_last = (_last_names(authors) or [""])[0]
    if first_last:
        q_parts.append(f"au:{first_last}")
    if not q_parts:
        return None
    search_query = "+AND+".join(q_parts)
    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query={search_query}&start=0&max_results={ARXIV_ROWS}"
    )
    xml = _http_get_text(url)
    if not xml:
        return None

    # Minimal Atom parsing without lxml.
    entries = re.findall(r"<entry>(.*?)</entry>", xml, re.DOTALL)
    best = None
    best_score = 0.0
    for e in entries:
        m_title = re.search(r"<title>(.*?)</title>", e, re.DOTALL)
        m_link = re.search(r'<id>(.*?)</id>', e, re.DOTALL)
        m_published = re.search(r"<published>(\d{4})", e)
        m_doi = re.search(r"<arxiv:doi[^>]*>(.*?)</arxiv:doi>", e, re.DOTALL)
        cand_title = (m_title.group(1) if m_title else "").strip().replace("\n", " ")
        cand_title = re.sub(r"\s+", " ", cand_title)
        cand_authors = re.findall(r"<name>(.*?)</name>", e, re.DOTALL)
        cand_authors = [a.strip().split()[-1] for a in cand_authors if a.strip()]
        cand_year = int(m_published.group(1)) if m_published else None
        cand_url = (m_link.group(1) if m_link else "").strip() or None
        cand_doi = (m_doi.group(1) if m_doi else "").strip() or None

        s = _score(title, authors, cand_title, cand_authors, year, cand_year)
        if s > best_score:
            best = {
                "title": cand_title,
                "authors": cand_authors,
                "year": cand_year,
                "doi": cand_doi,
                "url": cand_url,
                "source": "arxiv",
                "score": round(s, 3),
            }
            best_score = s

    if best and best_score >= MATCH_THRESHOLD:
        return best
    return None


def fetch_publisher_pdf(doi_or_url: str, dest: Path,
                        timeout: int = 60) -> str | None:
    """Try to download the publisher's PDF for a DOI or DOI URL.

    CrossRef's /works/{DOI} endpoint returns a `link` array describing
    full-text resources. Open-access publishers (eLife, biorxiv, PNAS OA, JoN
    OA, etc.) expose `content-type: application/pdf` entries that are
    directly downloadable. Paywalled publishers either omit such entries or
    return HTML / 403 — we detect that by checking the first 4 bytes for
    %PDF and bail.

    On success: writes the PDF to `dest` and returns the URL we fetched
    from. On failure: returns None.
    """
    # Normalize input: accept "10.1234/foo", "https://doi.org/10.1234/foo",
    # or any DOI-bearing URL.
    m = re.search(r"10\.\d{4,9}/[^\s]+", doi_or_url)
    if not m:
        return None
    doi = m.group(0).rstrip(".,;)")  # strip common trailing punctuation

    api = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='/')}"
    data = _http_get_json(api, timeout=timeout)
    if not data or "message" not in data:
        return None

    links = data["message"].get("link") or []
    pdf_candidates = [
        L["URL"] for L in links
        if L.get("content-type", "").lower() == "application/pdf" and L.get("URL")
    ]
    # Some entries lack content-type but URL ends in .pdf — give them a chance.
    pdf_candidates.extend(
        L["URL"] for L in links
        if not L.get("content-type") and (L.get("URL") or "").lower().endswith(".pdf")
    )

    for url in pdf_candidates:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status != 200:
                    continue
                ctype = (resp.headers.get("Content-Type") or "").lower()
                # First chunk: verify magic bytes; many paywall responses
                # come through as HTML with 200 OK.
                first = resp.read(4)
                if first[:4] != b"%PDF":
                    continue
                if "html" in ctype:
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_suffix(dest.suffix + ".tmp")
                with tmp.open("wb") as f:
                    f.write(first)
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
                tmp.replace(dest)
                return url
        except Exception:
            continue
    return None


def _cache_key(title: str, authors: str, year: int | None) -> str:
    raw = f"{title.strip().lower()}|{authors.strip().lower()}|{year or ''}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text())
    except Exception:
        return {}


def save_cache(cache: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cache, indent=2))
    tmp.replace(CACHE_FILE)


def lookup(title: str, authors: str, year: int | None = None,
           cache_ttl: int = DEFAULT_CACHE_TTL,
           use_cache: bool = True) -> tuple[dict | None, bool]:
    """Return (result_dict_or_None, cache_hit_bool)."""
    key = _cache_key(title, authors, year)
    cache = load_cache() if use_cache else {}
    entry = cache.get(key) if use_cache else None
    if entry and (time.time() - entry.get("ts", 0) < cache_ttl):
        return entry.get("result"), True

    result = search_crossref(title, authors, year)
    if result is None:
        result = search_arxiv(title, authors, year)

    if use_cache:
        cache[key] = {"ts": time.time(), "result": result}
        save_cache(cache)
    return result, False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--title", required=True)
    ap.add_argument("--authors", required=True,
                    help="Author names separated by commas/semicolons/'and'")
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--cache-ttl", type=int, default=DEFAULT_CACHE_TTL)
    args = ap.parse_args()

    try:
        result, cache_hit = lookup(
            args.title, args.authors, args.year,
            cache_ttl=args.cache_ttl, use_cache=not args.no_cache,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if result is None:
        if args.json:
            print(json.dumps({"result": None, "cache_hit": cache_hit}))
        else:
            print("No confident match.", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"result": result, "cache_hit": cache_hit}, indent=2))
    else:
        print(f"URL\t{result.get('url') or ''}")
        print(f"DOI\t{result.get('doi') or ''}")
        print(f"Source\t{result['source']}\tScore\t{result['score']}")
        if cache_hit:
            print("(cache hit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
