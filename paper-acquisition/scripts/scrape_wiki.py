#!/usr/bin/env python3
"""Scrape the CML wiki publications page.

Fetches https://memory.psych.upenn.edu/Publications, parses each <li>
publication entry, classifies its links (pdf / code / data / supplemental
/ poster / eeg-access), and emits one record per publication. Used by
generate_report.py to fill the "wiki" column of the paper inventory.

Usage:
    python scrape_wiki.py                    # writes wiki_publications.json
    python scrape_wiki.py --json             # also dump entries to stdout
    python scrape_wiki.py --no-cache         # force re-fetch
    python scrape_wiki.py --out /path.json   # custom cache path

Cached at ~/.cache/cml-paper-acquisition/wiki_publications.json.

Output schema (per entry):
    {
      "key":              "RaoEtal25",                   # from /files/pubs/<key>.pdf
      "year":             "2025",                        # or "Submitted", "In Press"
      "raw_text":         "Rao, A. M., DeHaan, ...",     # full citation
      "title":            "Synchronous theta networks...",
      "authors":          ["Rao", "DeHaan", "Kahana"],   # surnames
      "pdf_url":          "https://.../RaoEtal25.pdf",
      "code_url":         null,                          # .code.tgz or .code.zip
      "data_url":         null,                          # .data.tgz or .data.zip
      "supplemental_url": null,                          # .Supplemental.*
      "poster_url":       null,
      "eeg_access_url":   null,                          # Request_EEG_access?paper=...
      "wiki_url":         "https://memory.psych.upenn.edu/Publications#<key>"
    }

Exit codes:
    0 = scrape succeeded (or returned a populated cache)
    2 = network / parse failure
"""

import argparse
import json
import re
import sys
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

WIKI_URL = "https://memory.psych.upenn.edu/Publications"
WIKI_HOST = "https://memory.psych.upenn.edu"
CACHE_DIR = Path.home() / ".cache" / "cml-paper-acquisition"
CACHE_FILE = CACHE_DIR / "wiki_publications.json"
DEFAULT_CACHE_TTL = 7 * 24 * 3600  # 7 days
USER_AGENT = "paper-acquisition/1.0 (mailto:kahanalab@gmail.com)"

# Year-section header detector. Matches "2025" / "  2024 " / "Submitted" /
# "In Press" / "2007 and earlier" — the wiki TOC uses these as section names.
YEAR_HEADER_RE = re.compile(
    r"^\s*(?:(\d{4})(?:\s+and\s+earlier)?|Submitted|In\s*Press)\s*$",
    re.IGNORECASE,
)
PDF_KEY_RE = re.compile(
    r"/files/pubs/([A-Za-z][A-Za-z0-9_-]+?)\.pdf(?![A-Za-z])",
    re.IGNORECASE,
)
PUB_YEAR_PUNCT_RE = re.compile(r"\((\d{4})\)\.\s*")
SURNAME_RE = re.compile(r"^[A-Z][A-Za-z'\-]{1,}$")


def _absolutize(href: str) -> str:
    if not href:
        return ""
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return WIKI_HOST + href
    return WIKI_HOST + "/" + href


def _classify_link(href: str, text: str) -> str | None:
    """Return one of: pdf, code, data, supplemental, poster, eeg_access, or None.

    Order matters: poster.pdf and Supplemental.pdf both end in .pdf, so they
    must be tested before generic .pdf.
    """
    h = (href or "").lower()
    t = (text or "").strip().lower()
    if "request_eeg_access" in h or "ephys" in t or t == "data access":
        return "eeg_access"
    if ".poster" in h or t.startswith("poster"):
        return "poster"
    if ".supplemental" in h or "supplement" in t:
        return "supplemental"
    if ".code." in h or t.startswith("code"):
        return "code"
    if ".data." in h or t.startswith("data"):
        return "data"
    if h.endswith(".pdf"):
        return "pdf"
    return None


_AUTHOR_TITLE_BOUNDARY_RE = re.compile(
    # Two consecutive initials ("M. J.") or "et al" — both signal end of authors,
    # followed by optional period, whitespace, then a Capital letter starting the
    # title. Used for Submitted / In Press entries which lack a (YYYY) anchor.
    r"(?:[A-Z]\.\s*[A-Z]\.|\bet\s+al)\.?\s+(?=[A-Z])"
)


def _parse_citation(raw: str) -> tuple[list[str], str | None, str | None]:
    """Extract (surnames, year, title) from a citation-style string.

    Two formats handled:
      1. Published: "Lastname, F. M., ..., F. (YYYY). Title. Journal, ..."
      2. Submitted/In-Press: "Lastname, F. M., ... Title. Venue."  (no year)
    """
    if not raw:
        return [], None, None

    # Strip trailing link-label parens like "(pdf)" or "(pdf, code, data)".
    raw_clean = re.sub(r"\s*\([^()]*\)\s*$", "", raw).rstrip()

    year: str | None = None
    m = PUB_YEAR_PUNCT_RE.search(raw_clean)
    if m:
        year = m.group(1)
        authors_str = raw_clean[: m.start()].rstrip(" ,.")
        rest = raw_clean[m.end():].strip()
    else:
        # No year — find the last initials/et-al boundary that precedes a
        # capital-letter token (the start of the title).
        boundary = None
        for match in _AUTHOR_TITLE_BOUNDARY_RE.finditer(raw_clean):
            boundary = match
        if not boundary:
            return [], None, None
        authors_str = raw_clean[: boundary.end()].rstrip(" ,.")
        rest = raw_clean[boundary.end():].strip()

    # Title runs up to the first ". " before a capital letter or "(" — that's
    # typically the journal/venue name. Fall back to the first ". ".
    title_split = re.search(r"\.\s+(?=[A-Z(])", rest)
    if title_split:
        title = rest[: title_split.start()].strip()
    else:
        title = rest.split(". ")[0].strip()
    title = re.sub(r"\s+", " ", title).rstrip(".")

    # Author surnames: split on "," / " and " / "&" and keep surname-shaped
    # tokens. Splits typically yield alternating ["Lastname", "F. M."].
    parts = re.split(r",\s+|\s+and\s+|\s*&\s*", authors_str)
    surnames: list[str] = []
    for p in parts:
        p = p.strip().rstrip(".")
        if not p:
            continue
        if SURNAME_RE.match(p):
            surnames.append(p)
        elif " " in p:
            # Multi-token surname: "van Wingen", "del Rio". Reject if any token
            # is initials (ends with ".").
            tokens = p.split()
            cap = [t for t in tokens if SURNAME_RE.match(t)]
            if cap and not any(t.endswith(".") for t in tokens):
                surnames.append(" ".join(cap))
    return surnames, year, title or None


class _WikiParser(HTMLParser):
    """Walk the publications page, collecting one entry per <li> under each
    year section header."""

    def __init__(self) -> None:
        super().__init__()
        self.entries: list[dict] = []
        self.current_section: str | None = None

        self._li_depth = 0
        self._li_text: list[str] = []
        self._li_links: list[dict] = []

        self._in_header: str | None = None
        self._header_text: list[str] = []

        self._a_href: str | None = None
        self._a_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._in_header = tag
            self._header_text = []
            return
        if tag == "li":
            if self._li_depth == 0:
                self._li_text = []
                self._li_links = []
            self._li_depth += 1
            return
        if tag == "a":
            href = ""
            for k, v in attrs:
                if k == "href":
                    href = v or ""
                    break
            self._a_href = href
            self._a_text = []

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._in_header == tag:
            text = "".join(self._header_text).strip()
            text = re.sub(r"\s+", " ", text)
            m = YEAR_HEADER_RE.match(text)
            if m:
                self.current_section = m.group(1) if m.group(1) else text
            self._in_header = None
            return
        if tag == "li":
            if self._li_depth > 0:
                self._li_depth -= 1
            if self._li_depth == 0:
                text = re.sub(r"\s+", " ", "".join(self._li_text)).strip()
                if text and self._li_links:
                    self.entries.append({
                        "section": self.current_section,
                        "raw_text": text,
                        "_links": self._li_links,
                    })
            return
        if tag == "a":
            if self._a_href is not None:
                link_text = re.sub(r"\s+", " ", "".join(self._a_text)).strip()
                if self._li_depth > 0:
                    self._li_links.append({
                        "href": self._a_href,
                        "text": link_text,
                    })
            self._a_href = None
            self._a_text = []

    def handle_data(self, data):
        if self._in_header:
            self._header_text.append(data)
        if self._li_depth > 0:
            self._li_text.append(data)
        if self._a_href is not None:
            self._a_text.append(data)


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} on {url}")
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def _build_entry(rec: dict) -> dict | None:
    """Turn a raw <li> record into a structured publication entry.

    Returns None when the entry has no <pdf> link AND no recognizable citation
    — these are usually navigation list items that slipped past the year-
    section filter.
    """
    raw = rec.get("raw_text") or ""
    section = rec.get("section")
    links = rec.get("_links") or []

    classified: dict[str, str] = {}
    for link in links:
        cat = _classify_link(link["href"], link.get("text", ""))
        if cat and cat not in classified:
            classified[cat] = _absolutize(link["href"])

    pdf_url = classified.get("pdf")
    surnames, year, title = _parse_citation(raw)

    # Year fallback: section header (e.g., "Submitted", "In Press") is the
    # only signal for non-published items.
    year_out = year or section

    # Key: prefer the .pdf filename — it's the wiki's canonical citation key.
    # Fall back to a synthetic key built from first author + year.
    key = None
    if pdf_url:
        m = PDF_KEY_RE.search(pdf_url)
        if m:
            key = m.group(1)
    if not key:
        if surnames and year:
            key = surnames[0][:4] + str(year)[-2:]
        elif surnames:
            key = surnames[0][:6] + (section or "X").replace(" ", "")[:6]
        else:
            return None  # Can't form a key — skip.

    # Filter: must have either a pdf link or a parseable citation. Pure nav
    # items (TOC links, year jump targets) usually have neither.
    if not pdf_url and not (surnames and title):
        return None

    return {
        "key": key,
        "year": str(year_out) if year_out else None,
        "raw_text": raw,
        "title": title,
        "authors": surnames,
        "pdf_url": pdf_url,
        "code_url": classified.get("code"),
        "data_url": classified.get("data"),
        "supplemental_url": classified.get("supplemental"),
        "poster_url": classified.get("poster"),
        "eeg_access_url": classified.get("eeg_access"),
        "wiki_url": f"{WIKI_URL}#{key}",
    }


def scrape() -> dict:
    """Fetch + parse the wiki page. Returns the cache-payload dict."""
    html = _fetch(WIKI_URL)
    parser = _WikiParser()
    parser.feed(html)

    # Many MediaWiki/Foswiki templates wrap the page nav in <li> too. Filter
    # to entries inside an actual year section.
    entries: list[dict] = []
    seen_keys: set[str] = set()
    for rec in parser.entries:
        if rec.get("section") is None:
            continue
        built = _build_entry(rec)
        if built is None:
            continue
        # De-dupe by key — if a paper appears twice (e.g., listed in both
        # "In Press" and the year section), keep the first hit.
        if built["key"] in seen_keys:
            continue
        seen_keys.add(built["key"])
        entries.append(built)

    return {
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_url": WIKI_URL,
        "count": len(entries),
        "entries": entries,
    }


def load_cache(path: Path = CACHE_FILE) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def save_cache(payload: dict, path: Path = CACHE_FILE) -> bool:
    """Write the cache file. Returns True on success, False otherwise.

    Failures are non-fatal — the report can still be built from in-memory
    data; a cache miss next run just means re-fetching.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2))
        tmp.replace(path)
        return True
    except OSError as e:
        print(f"WARN: failed to write {path}: {e}", file=sys.stderr)
        return False


def get_entries(cache_path: Path = CACHE_FILE,
                use_cache: bool = True,
                cache_ttl: int = DEFAULT_CACHE_TTL) -> list[dict]:
    """Library entry point used by generate_report.py.

    Returns the list of wiki publication entries. Hits the disk cache when
    fresh; otherwise re-scrapes and updates the cache.
    """
    if use_cache:
        cached = load_cache(cache_path)
        if cached:
            try:
                ts = time.mktime(time.strptime(
                    cached.get("fetched_at", ""), "%Y-%m-%dT%H:%M:%SZ"
                ))
                if (time.time() - ts) < cache_ttl:
                    return cached.get("entries", []) or []
            except (ValueError, KeyError):
                pass  # treat malformed timestamp as expired

    payload = scrape()
    if use_cache:
        save_cache(payload, cache_path)
    return payload.get("entries", []) or []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=CACHE_FILE,
                    help=f"Output JSON path (default: {CACHE_FILE})")
    ap.add_argument("--no-cache", action="store_true",
                    help="Force re-fetch even if cache is fresh")
    ap.add_argument("--cache-ttl", type=int, default=DEFAULT_CACHE_TTL)
    ap.add_argument("--json", action="store_true",
                    help="Also print all entries to stdout")
    args = ap.parse_args()

    try:
        entries = get_entries(
            cache_path=args.out,
            use_cache=not args.no_cache,
            cache_ttl=args.cache_ttl,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print(f"Wrote {args.out} ({len(entries)} entries)", file=sys.stderr)
    if args.json:
        print(json.dumps(entries, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
