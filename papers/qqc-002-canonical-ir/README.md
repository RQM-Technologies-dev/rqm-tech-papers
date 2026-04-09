# qqc-002-canonical-ir

This folder is a semantic paper package for:

**A Canonical Quaternionic Intermediate Representation for Single-Qubit Quantum Circuits**

## Source of truth

- `main.tex` is the Overleaf-friendly source of truth for the paper text.
- `index.html` is the clean package landing page for `/papers/qqc-002-canonical-ir/`.
- `paper.html` is the full browsable paper page and should mirror the authored source.

## Dependency on paper 1

- This draft depends explicitly on `qqc-001-foundations`.
- It reuses the same quaternion--`SU(2)` convention `Phi` fixed there.
- Its contribution is representational: a canonical single-qubit IR layer, not a new physical model.

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

- The paper is intentionally limited to single-qubit gate action modulo global phase.
- Entangling gates appear only as segment boundaries.
- `artifacts/figures/` contains publication-oriented SVG schematics for the IR pipeline, canonical hemisphere, gate table, and segment extraction concept.
