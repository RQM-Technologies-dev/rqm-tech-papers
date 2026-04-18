# rcf-001-coherence-framework

This folder is a semantic paper package for:

**RQM Coherence Framework v0.1: Spectral-Variational Coherence on \(S^3 \times \mathbb{R}\)**

## Source of truth

- Authoritative paper text source: `main.tex`.
- `index.html` is the clean package landing page for `/papers/rcf-001-coherence-framework/`.
- `paper.html` is the full browsable paper page and should mirror the authored source.

## Purpose

This package formalizes the first rigorous RQM Coherence Framework as an operator-theoretic and variational model on
\[
M = S^3 \times \mathbb{R}_s.
\]
It is intended to serve both as a foundational theory document and as an engineering-facing technical paper for coherence metrics, residual minimization, and spectral mode tracking across RQM Technologies workflows.

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

## Notes

- The paper is a draft formal framework (v0.1), not a completed empirical validation claim.
- The package keeps all required companion files aligned with the same mathematical model.
