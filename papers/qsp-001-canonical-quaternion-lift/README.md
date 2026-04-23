# qsp-001-canonical-quaternion-lift

This folder is a semantic paper package for:

**Canonical Quaternion Lifting for Multichannel RF and Sensing Signals**

## Source of truth

- Authoritative paper text source: `main.tex`
- `index.html` is the clean package landing page for `/papers/qsp-001-canonical-quaternion-lift/`.
- `paper.html` is the full browsable paper page and should mirror the authored source.

## Package status

- Current status: **draft scaffold**
- This package intentionally includes placeholder publication surfaces only.
- Full technical sections and validated results will be added in a later revision.

## Local build

If a LaTeX toolchain is available locally, build with:

```bash
latexmk -pdf main.tex
```

Copy or rename the generated PDF to `paper.pdf` for the publication package.

## Metadata safety

- Never invent DOI, canonical URL, ORCID, journal, volume, issue, or page-range metadata.
- If a metadata field is not yet known, leave it absent or `null`.
- Keep `metadata.json`, `paper.html`, `paper.jats.xml`, and `CITATION.cff` synchronized with the same facts.
