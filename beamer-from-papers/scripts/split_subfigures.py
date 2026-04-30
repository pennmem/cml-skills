#!/usr/bin/env python3
"""
Split composite scientific figures into their sub-panels, group the panels
by visual type, and emit Beamer frames that respect the skill's
<= 2 figures per slide rule with same-type grouping.

Workflow:

  1. Rasterize each input PDF page to PNG at 300 DPI via ghostscript.
  2. Detect whitespace gutters (rows / columns with high mean brightness)
     and recursively split the page into sub-panels. Handles 2x2, 2x3,
     3x3, 1xN, Nx1, and asymmetric grids.
  3. Label panels row-major (A, B, C, ...) and write each as an
     individual PNG alongside a panels.json metadata file.
  4. Compute a feature vector per panel (aspect ratio, mean brightness,
     edge density, color-fullness, dominant-color triple).
  5. Cluster panels across ALL input PDFs into groups via agglomerative
     clustering with a distance threshold (or k-means if --k given).
  6. Emit a LaTeX snippet with one frame per group, up to --max-per-slide
     panels per frame (default 2), centered and height-bounded.

Dependencies: Pillow, numpy, scikit-learn, ghostscript. On rhino2 activate
the `workshop_311_rhino2b` conda env before running this script.

Usage:

    python scripts/split_subfigures.py INPUT.pdf [INPUT2.pdf ...] \\
        --out-dir panels/ \\
        --emit-latex frames.tex \\
        [--k 2] [--distance-threshold 2.5] \\
        [--max-per-slide 2] [--dpi 300] \\
        [--gutter-min-frac 0.05] [--gutter-brightness 0.96] \\
        [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict, field
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError as e:
    print(
        f"ERROR: required dependency missing: {e}.\n"
        "On rhino2 activate the workshop_311_rhino2b conda env:\n"
        "    conda activate workshop_311_rhino2b",
        file=sys.stderr,
    )
    sys.exit(127)

try:
    from sklearn.cluster import AgglomerativeClustering, KMeans
    HAVE_SKLEARN = True
except ImportError:
    HAVE_SKLEARN = False


# -----------------------------------------------------------------------
# Rasterization
# -----------------------------------------------------------------------

def rasterize_page(pdf: Path, page: int, dpi: int, out_png: Path) -> None:
    """Render one page of a PDF to PNG via ghostscript."""
    cmd = [
        "gs", "-dNOPAUSE", "-dBATCH", "-dSAFER",
        "-sDEVICE=png16m",
        f"-r{dpi}",
        f"-dFirstPage={page}", f"-dLastPage={page}",
        f"-sOutputFile={out_png}",
        str(pdf),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not out_png.exists():
        raise RuntimeError(
            f"ghostscript failed on {pdf} page {page}:\n{result.stderr}"
        )


def page_count(pdf: Path) -> int:
    """How many pages in this PDF. Uses gs -c 'showpage' trick."""
    cmd = [
        "gs", "-q", "-dNODISPLAY", "-dNOSAFER",
        "-c", f"({pdf}) (r) file runpdfbegin pdfpagecount = quit",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return int(result.stdout.strip())
    except Exception:
        return 1  # fall back to assume single page


# -----------------------------------------------------------------------
# Whitespace gutter detection
# -----------------------------------------------------------------------

@dataclass
class BBox:
    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def w(self) -> int: return self.x1 - self.x0
    @property
    def h(self) -> int: return self.y1 - self.y0


def find_gutters(profile: np.ndarray, threshold: float, min_run: int
                 ) -> list[tuple[int, int]]:
    """Given a 1D brightness profile in [0, 1], return runs of
    consecutive indices where profile > threshold, each longer than
    min_run. These are whitespace gutters.
    """
    mask = profile > threshold
    runs: list[tuple[int, int]] = []
    i = 0
    n = len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]:
                j += 1
            if j - i >= min_run:
                runs.append((i, j))
            i = j
        else:
            i += 1
    return runs


def split_axis(has_content: np.ndarray, min_run_frac: float,
               min_strip_frac: float) -> list[tuple[int, int]]:
    """Split a 1D boolean content-mask into strips of consecutive True
    rows (content). Runs of consecutive False rows longer than
    min_run_frac * N are gutters; everything else is a strip.

    Returns (start, end) tuples in pixel coordinates.
    """
    n = len(has_content)
    min_run = max(int(n * min_run_frac), 6)
    min_strip = max(int(n * min_strip_frac), 20)

    strips: list[tuple[int, int]] = []
    i = 0
    # Skip leading empty rows (outer margin)
    while i < n and not has_content[i]:
        i += 1
    while i < n:
        start = i
        # Walk through content rows, allowing short interior gaps
        while i < n:
            if has_content[i]:
                i += 1
                continue
            # Count the empty run that starts here
            j = i
            while j < n and not has_content[j]:
                j += 1
            gap = j - i
            if gap >= min_run:
                # Real gutter: end this strip
                break
            # Short gap interior to a panel; absorb and continue
            i = j
        end = i
        if end - start >= min_strip:
            strips.append((start, end))
        # Skip past the gutter
        while i < n and not has_content[i]:
            i += 1
    return strips


def detect_subpanels(img: np.ndarray, dark_threshold: float,
                     min_gap_frac: float, min_strip_frac: float = 0.08
                     ) -> list[BBox]:
    """Detect sub-panel bounding boxes in a page image.

    Strategy: build a binary content mask (True where any pixel in a
    row or column is darker than dark_threshold). Find horizontal
    strips of content rows (separated by wide empty-row gutters), then
    within each strip find vertical strips of content columns.

    dark_threshold: pixel brightness below this counts as "content"
        (ink, data points, axis lines). 0.70 works for most figures.
    min_gap_frac: a gutter must span at least this fraction of the
        axis length to count as a real panel separator.
    min_strip_frac: a panel strip must span at least this fraction of
        the axis length. Prevents micro-strips of stray marks.
    """
    if img.ndim == 3:
        gray = img.mean(axis=2) / 255.0
    else:
        gray = img / 255.0
    dark = gray < dark_threshold  # True where there's ink

    # A row has content if any pixel in it is dark.
    row_has = dark.any(axis=1)
    h_strips = split_axis(row_has, min_gap_frac, min_strip_frac)

    panels: list[BBox] = []
    for (y0, y1) in h_strips:
        band = dark[y0:y1]
        col_has = band.any(axis=0)
        v_strips = split_axis(col_has, min_gap_frac, min_strip_frac)
        for (x0, x1) in v_strips:
            panels.append(BBox(x0=x0, y0=y0, x1=x1, y1=y1))
    return panels


# -----------------------------------------------------------------------
# Panel data + feature extraction
# -----------------------------------------------------------------------

@dataclass
class Panel:
    source_pdf: str
    page: int
    label: str                # "A", "B", ...
    bbox: BBox
    png_path: str             # relative path to the saved PNG
    features: list[float] = field(default_factory=list)
    group: int | None = None


def label_for(index: int) -> str:
    """0 -> 'A', 1 -> 'B', ..., 25 -> 'Z', 26 -> 'AA', 27 -> 'AB'."""
    s = ""
    i = index
    while True:
        s = chr(ord('A') + i % 26) + s
        i = i // 26 - 1
        if i < 0:
            break
    return s


def extract_features(img: np.ndarray, bbox: BBox) -> list[float]:
    """Compact visual feature vector for grouping."""
    crop = img[bbox.y0:bbox.y1, bbox.x0:bbox.x1]
    if crop.ndim == 2:
        crop = np.stack([crop] * 3, axis=-1)
    rgb = crop.astype(np.float32) / 255.0

    aspect = bbox.w / max(bbox.h, 1)
    mean_brightness = rgb.mean()
    # color-fullness: how much do the three channel means deviate
    ch = rgb.reshape(-1, 3).mean(axis=0)
    color_spread = float(ch.std())
    # edge density: mean absolute difference between neighbors
    gray = rgb.mean(axis=2)
    dx = np.abs(np.diff(gray, axis=1)).mean()
    dy = np.abs(np.diff(gray, axis=0)).mean()
    edge_density = float((dx + dy) / 2)
    # dark-pixel fraction (proxy for ink density)
    dark_frac = float((gray < 0.6).mean())
    return [
        float(aspect),
        float(mean_brightness),
        color_spread,
        edge_density,
        dark_frac,
        float(ch[0]), float(ch[1]), float(ch[2]),
    ]


# -----------------------------------------------------------------------
# Grouping / clustering
# -----------------------------------------------------------------------

def group_panels(panels: list[Panel], k: int | None,
                 distance_threshold: float | None) -> None:
    """Assign Panel.group labels in place."""
    if not panels:
        return
    if len(panels) == 1:
        panels[0].group = 0
        return
    if not HAVE_SKLEARN:
        # Fallback: single group
        for p in panels:
            p.group = 0
        return
    X = np.array([p.features for p in panels])
    # Per-feature scaling by inter-quartile range so a single noisy feature
    # (e.g., aspect ratio on a panel that includes a row label) doesn't
    # dominate. Adding a small epsilon keeps near-constant features stable.
    q75 = np.quantile(X, 0.75, axis=0)
    q25 = np.quantile(X, 0.25, axis=0)
    iqr = q75 - q25
    iqr = np.where(iqr < 1e-3, 1.0, iqr)
    Xs = (X - X.mean(axis=0)) / iqr

    if k is not None:
        labels = KMeans(n_clusters=min(k, len(panels)),
                        n_init=10, random_state=0).fit_predict(Xs)
    else:
        thr = distance_threshold if distance_threshold is not None else 4.0
        labels = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=thr,
            linkage="average",
        ).fit_predict(Xs)
    # Relabel so group ids are contiguous starting at 0, ordered by
    # appearance.
    remap: dict[int, int] = {}
    for lbl in labels:
        if lbl not in remap:
            remap[lbl] = len(remap)
    for p, lbl in zip(panels, labels):
        p.group = remap[int(lbl)]


# -----------------------------------------------------------------------
# LaTeX emission
# -----------------------------------------------------------------------

LATEX_HEAD = r"""% Auto-generated by split_subfigures.py. Frames respect the
% beamer-from-papers rule of <= 2 figures per slide with same-type grouping.
% Drop into a deck that defines \novelbadge (optional) and the standard
% graphicx + setspace packages. Include panels/ next to this file.
"""


def _title_for_group(panels: list[Panel]) -> str:
    """Heuristic group title from source pdf stems + labels."""
    by_src: dict[str, list[str]] = {}
    for p in panels:
        key = Path(p.source_pdf).stem
        by_src.setdefault(key, []).append(p.label)
    parts = []
    for src, lbls in by_src.items():
        parts.append(f"{src} ({', '.join(lbls)})")
    return "Group: " + "; ".join(parts)


def _figure_include(p: Panel, n_on_slide: int) -> str:
    if n_on_slide == 1:
        opts = r"width=0.80\textwidth, height=0.65\textheight, keepaspectratio"
    else:
        opts = r"width=\linewidth, height=0.58\textheight, keepaspectratio"
    return rf"\includegraphics[{opts}]{{{p.png_path}}}"


def emit_frames(panels: list[Panel], out_tex: Path, max_per_slide: int) -> None:
    """Write Beamer frames grouped by panel.group, with <= max_per_slide
    panels per slide."""
    groups: dict[int, list[Panel]] = {}
    for p in panels:
        if p.group is None:
            continue
        groups.setdefault(p.group, []).append(p)

    lines: list[str] = [LATEX_HEAD]
    for gid in sorted(groups):
        gpanels = groups[gid]
        # Chunk into groups of <= max_per_slide
        for start in range(0, len(gpanels), max_per_slide):
            chunk = gpanels[start:start + max_per_slide]
            # Title: first slide shows the group; continuation slides get "(cont.)"
            title = _title_for_group(chunk)
            if start > 0:
                title += " (cont.)"
            if len(chunk) == 1:
                body = rf"""\begin{{frame}}{{{title}}}
  \centering
  {_figure_include(chunk[0], 1)}
  \begin{{itemize}}
    \setlength\itemsep{{2pt}}
    \item Panel {chunk[0].label} from {Path(chunk[0].source_pdf).stem}
    \item Takeaway: fill in
  \end{{itemize}}
\end{{frame}}"""
            else:
                cols = []
                for p in chunk:
                    cols.append(
                        rf"""    \column{{{1.0 / len(chunk):.2f}\textwidth}}
      \centering
      {_figure_include(p, len(chunk))}\\
      {{\footnotesize Panel {p.label} ({Path(p.source_pdf).stem})}}"""
                    )
                body = rf"""\begin{{frame}}{{{title}}}
  \begin{{columns}}[T]
{chr(10).join(cols)}
  \end{{columns}}
  \vspace{{4pt}}
  \begin{{itemize}}
    \setlength\itemsep{{2pt}}
    \item Same-type panels shown together
    \item Takeaway: fill in
  \end{{itemize}}
\end{{frame}}"""
            lines.append(body)
            lines.append("")
    out_tex.write_text("\n".join(lines))


# -----------------------------------------------------------------------
# Driver
# -----------------------------------------------------------------------

def process_pdf(pdf: Path, out_dir: Path, dpi: int,
                dark_threshold: float, gutter_min_frac: float,
                strip_min_frac: float) -> list[Panel]:
    """Split a single PDF into panels, write PNGs, return Panel objects."""
    panels: list[Panel] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_p = Path(tmp)
        for page in range(1, page_count(pdf) + 1):
            png = tmp_p / f"page{page:02d}.png"
            rasterize_page(pdf, page, dpi, png)
            img = np.asarray(Image.open(png).convert("RGB"))
            bboxes = detect_subpanels(img, dark_threshold,
                                      gutter_min_frac, strip_min_frac)
            if not bboxes:
                bboxes = [BBox(0, 0, img.shape[1], img.shape[0])]
            # Order row-major by (y_mid, x_mid), rounded to group rows
            bboxes_sorted = sorted(
                bboxes,
                key=lambda b: ((b.y0 + b.y1) // (img.shape[0] // 8 + 1),
                               (b.x0 + b.x1) // 2),
            )
            stem = pdf.stem
            for i, bb in enumerate(bboxes_sorted):
                label = label_for(i)
                out_png = out_dir / f"{stem}_page{page:02d}_{label}.png"
                Image.fromarray(img[bb.y0:bb.y1, bb.x0:bb.x1]).save(out_png)
                feats = extract_features(img, bb)
                panels.append(Panel(
                    source_pdf=str(pdf),
                    page=page,
                    label=label,
                    bbox=bb,
                    png_path=f"panels/{out_png.name}",
                    features=feats,
                ))
    return panels


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdfs", nargs="+", type=Path,
                    help="one or more composite-figure PDFs to split")
    ap.add_argument("--out-dir", type=Path, default=Path("panels"),
                    help="directory for output PNG panels")
    ap.add_argument("--emit-latex", type=Path, default=None,
                    help="also write a Beamer frames snippet here")
    ap.add_argument("--max-per-slide", type=int, default=2,
                    help="max panels per emitted slide (default 2)")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--dark-threshold", type=float, default=0.70,
                    help="pixel brightness below this counts as ink")
    ap.add_argument("--gutter-min-frac", type=float, default=0.03,
                    help="a gutter must span at least this fraction of the axis")
    ap.add_argument("--strip-min-frac", type=float, default=0.08,
                    help="a panel strip must span at least this fraction of the axis")
    ap.add_argument("--k", type=int, default=None,
                    help="force k-means with K groups; default = agglomerative")
    ap.add_argument("--distance-threshold", type=float, default=4.0,
                    help="agglomerative distance cutoff (default 4.0; "
                         "raise to merge more aggressively, lower to split more)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would happen without writing files")
    args = ap.parse_args()

    if not shutil.which("gs"):
        print("ERROR: ghostscript (gs) not found in PATH", file=sys.stderr)
        return 127

    for p in args.pdfs:
        if not p.exists():
            print(f"ERROR: {p} not found", file=sys.stderr)
            return 1

    if not args.dry_run:
        args.out_dir.mkdir(parents=True, exist_ok=True)

    all_panels: list[Panel] = []
    for pdf in args.pdfs:
        if args.dry_run:
            print(f"[dry-run] would process {pdf}")
            continue
        pdf_panels = process_pdf(
            pdf, args.out_dir, args.dpi,
            args.dark_threshold, args.gutter_min_frac,
            args.strip_min_frac,
        )
        print(f"{pdf.name}: {len(pdf_panels)} panel(s)")
        for p in pdf_panels:
            print(f"  {p.label}  bbox=({p.bbox.x0},{p.bbox.y0},"
                  f"{p.bbox.x1},{p.bbox.y1})  -> {p.png_path}")
        all_panels.extend(pdf_panels)

    if args.dry_run or not all_panels:
        return 0

    group_panels(all_panels, k=args.k,
                 distance_threshold=args.distance_threshold)

    n_groups = len({p.group for p in all_panels})
    print(f"\nGrouped {len(all_panels)} panel(s) into {n_groups} group(s):")
    for gid in sorted({p.group for p in all_panels}):
        members = [p for p in all_panels if p.group == gid]
        sig = ", ".join(f"{Path(p.source_pdf).stem}:{p.label}" for p in members)
        print(f"  group {gid}: {sig}")

    # Metadata
    meta_path = args.out_dir / "panels.json"
    meta = [
        {**asdict(p), "bbox": asdict(p.bbox)}
        for p in all_panels
    ]
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"\nWrote metadata: {meta_path}")

    if args.emit_latex:
        emit_frames(all_panels, args.emit_latex, args.max_per_slide)
        print(f"Wrote Beamer frames: {args.emit_latex}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
