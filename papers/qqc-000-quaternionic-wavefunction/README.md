# qqc-000-quaternionic-wavefunction

This folder is a semantic paper package for:

**The Quaternionic Wavefunction: Spin-1/2 Particles, S^3, and SU(2)**

## Source of truth

- `main.tex` is the Overleaf-friendly source of truth for the paper text.
- `index.html` is the clean package landing page for `/papers/qqc-000-quaternionic-wavefunction/`.
- `paper.html` is the full browsable paper page and should mirror the authored source.

## Role in the series

- This package is intended as a **conceptual prequel** to the rest of the quaternionic quantum computing papers.
- It introduces the quaternionic wavefunction as the grouping of a two-component complex spinor into one quaternion.
- Its job is pedagogical: to make spin-1/2 structure, the appearance of `S^3`, and the natural role of `SU(2)` visible before later papers narrow into compiler or gate-level topics.

## Local build

If a LaTeX toolchain is available locally, build with:

```bash
latexmk -pdf main.tex
```

Copy or rename the generated PDF to `paper.pdf` for the publication package.
This cloud environment does not currently provide `latexmk`, so the intended
build path for this draft is standard Overleaf / TeX Live using `main.tex` as
the authoritative source of truth.

## Metadata safety

- Never invent DOI, canonical URL, ORCID, journal, volume, issue, page-range, or acceptance metadata.
- If a metadata field is not yet known, leave it absent or `null`.
- Keep `metadata.json`, `paper.html`, `paper.jats.xml`, and `CITATION.cff` synchronized with the same real facts.

## Notes

- The paper is intentionally conservative and does not claim a new physical theory.
- It does not claim quaternionic Hilbert-space quantum mechanics in the Adler sense.
- It introduces the term **quaternionic wavefunction** as an expository bridge from spinors in `C^2` to quaternionic geometry, while keeping standard distinctions clear.
