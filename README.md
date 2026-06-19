# PraktikumsBericht

LaTeX project for the internship report and related presentation material.

## Project Contents

- `Bericht.tex`: Main report source
- `literatur.bib`: Bibliography database
- `Bericht_Präsentation.tex`: Full presentation
- `Bericht_Präsentation_kurz.tex`: Short presentation
- `images/`: Figures used in report/presentation
- `data/`: Analysis input data (harmonics, weekly/range summaries)
- `scripts/`: Helper scripts for generating charts

## Build

### Report PDF

```bash
latexmk -pdf -g Bericht.tex
```

### Alternative incremental build

```bash
latexmk -pdf Bericht.tex
```

## Requirements

- TeX distribution with `pdflatex` (e.g. TeX Live)
- `latexmk`
- `biber` (bibliography backend used by `biblatex`)

## Clean generated files

```bash
latexmk -C
```

## Notes

- Main language is German (`ngerman` in LaTeX).
- Bibliography is managed via `biblatex` + `biber`.
- If bibliography errors occur, run a full rebuild:

```bash
latexmk -pdf -g Bericht.tex
```
