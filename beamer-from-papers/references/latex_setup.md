# LaTeX setup

`compile_beamer.py` needs `pdflatex` and `bibtex`. If either is missing, the script emits a pointer to this file.

## Check what you have

```bash
which pdflatex bibtex
pdflatex --version
```

If both resolve to paths, you're set. If not, install below.

## Linux (rhino2 or similar)

On rhino2 it's usually already installed globally. If not:

```bash
# Debian / Ubuntu
sudo apt-get install texlive-latex-recommended texlive-latex-extra \
    texlive-fonts-recommended texlive-bibtex-extra

# For a fuller install (includes extra packages the template might pull in)
sudo apt-get install texlive-full
```

`texlive-latex-extra` is the minimum that gets you the `beamer` class. If you skip it, pdflatex will fail with `File 'beamer.cls' not found`.

## macOS

```bash
brew install --cask mactex-no-gui
```

Or download the full MacTeX distribution from https://tug.org/mactex/ if you want the GUI tools.

## Windows / WSL

Use MiKTeX (https://miktex.org/) or install TeX Live through WSL.

## Why natbib + bibtex, not biblatex + biber

The CML Beamer template ships with `natbib` + `bibtex` instead of the more modern `biblatex` + `biber`. Reasons:

- `natbib` + `bibtex` are in every TeX Live base install going back over a decade
- `biblatex.sty` and `biber` are often missing on minimal installs (including some HPC / sandbox environments)
- The output quality is indistinguishable for the citation styles CML uses (`apalike`)

If you want to switch to biblatex anyway, the template has a commented block showing how.

## Common errors

### `File 'beamer.cls' not found`
Install `texlive-latex-extra` (Linux) or the full MacTeX distribution.

### `File 'natbib.sty' not found`
Install `texlive-latex-recommended`.

### `Package inputenc Error: Unicode character`
A source paper has an unescaped Unicode character that pdflatex with T1 can't handle. Options:

1. Preprocess the source to replace the offending character
2. Switch to `xelatex` (handles Unicode natively):
   ```bash
   xelatex deck.tex
   ```
   Works with the current template.

### Figures don't render
Check the figure file exists at the path given in `\includegraphics`. Remember paths are relative to the `.tex` file's directory. The skill's `plan_deck.py` copies bundle figures into a local `figures/` subdirectory alongside the `.tex` — don't move the `.tex` out of that directory without also moving the figures.

### Bibliography is `[?]` everywhere
Run `bibtex deck` (without the `.tex` extension), then `pdflatex` twice more. `compile_beamer.py` already does this automatically.

### Compiler hangs
Check for `\write18` or shell-escape calls in the source. Some sandboxes block these. Running pdflatex with `-interaction=nonstopmode` (which `compile_beamer.py` does) prevents hanging on errors but won't help with shell-escape blocks. Use `--no-shell-escape` if available.

## Running on rhino2

On rhino2, LaTeX is already installed globally. Just run the skill normally and everything should work. If you hit a missing-package error, notify the CML sysadmins rather than installing to your home directory — the lab keeps a common TeX Live distribution up to date.
