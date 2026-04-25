# nav-001-quaternionic-pnt-confidence-navigation

This folder is a semantic paper package for:

**Quaternionic Frame Residuals and Coherence Metrics for Lunar and Cislunar Navigation Software Confidence Scoring**

## Source of truth

- Authoritative paper text source: `main.tex`
- `index.html` is the clean package landing page for `/papers/nav-001-quaternionic-pnt-confidence-navigation/`.
- `paper.html` is the full browsable paper page and mirrors the authored source.

## Package status

- Current status: **draft**
- This is a first technical draft intended for iterative refinement and simulation-backed validation.

## Local build

If a LaTeX toolchain is available locally, build with:

```bash
latexmk -pdf main.tex
```

Copy or rename the generated PDF to `paper.pdf` for the publication package.

## Metadata safety

- Do not invent DOI, journal, venue, canonical URL, or publication identifiers.
- If a metadata field is unknown, leave it absent or `null`.
- Keep `metadata.json`, `paper.html`, `paper.jats.xml`, and `CITATION.cff` synchronized.
