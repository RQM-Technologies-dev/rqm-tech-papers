# SERIES-NNN-slug

This folder is a semantic paper package for:

**REPLACE WITH PAPER TITLE**

## Source of truth

- Authoritative paper text source: `main.tex`
- `index.html` is the clean package landing page for `/papers/SERIES-NNN-slug/`.
- `paper.html` is the full browsable paper page and should mirror the authored source.
- If you choose a different authored source, update this README explicitly before publishing.

## Local build

If a LaTeX toolchain is available locally, build with:

```bash
latexmk -pdf main.tex
```

Copy or rename the generated PDF to `paper.pdf` for the publication package.

## Metadata safety

- Never invent DOI, canonical URL, ORCID, journal, volume, issue, or page-range metadata.
- If a metadata field is not yet known, leave it absent or `null` instead of publishing a plausible placeholder.
- Keep `metadata.json`, `paper.html`, `paper.jats.xml`, and `CITATION.cff` synchronized with the same real facts.

## Notes

- Keep the companion files aligned with the actual text of the paper.
- Keep `index.html` and `paper.html` visually and semantically aligned.
- Use `artifacts/figures/`, `artifacts/notebooks/`, and `artifacts/code/` for supporting materials.
