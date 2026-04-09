# qqc-004-verification-equivalence

This folder is a semantic paper package for:

**Verification, Canonicalization, and Equivalence in Quaternionic Quantum Compilation**

## Source of truth

- `main.tex` is the Overleaf-friendly source of truth for the paper text.
- `index.html` is the clean package landing page for `/papers/qqc-004-verification-equivalence/`.
- `paper.html` is the full browsable paper page and should mirror the authored source.

## Dependencies on earlier papers

- This draft depends explicitly on `qqc-001-foundations`, `qqc-002-canonical-ir`, and `qqc-003-gate-fusion`.
- It reuses the same quaternion--`SU(2)` convention `Phi`, canonical `u1q` representation, and local fusion semantics.
- Its contribution is the trust layer: canonical equivalence, invariants, validation procedures, and matrix-based interoperability diagnostics.

## Local build

If a LaTeX toolchain is available locally, build with:

```bash
latexmk -pdf main.tex
```

Copy or rename the generated PDF to `paper.pdf` for the publication package.
This cloud environment does not currently provide `latexmk`, so the intended
build path for this draft is standard Overleaf / TeX Live using `main.tex` as
the authoritative source of truth.
This cloud environment does not currently provide `latexmk`, so the intended
build path for this draft is standard Overleaf / TeX Live using `main.tex` as
the authoritative source of truth.

## Verification artifacts

- The package includes a small executable verifier at `artifacts/code/verify_canonical_equivalence.py`.
- Measured outputs from the shipped verification corpus are written to `artifacts/code/verification_results.json`.
- The verifier exercises both positive and negative cases so the package demonstrates acceptance and rejection behavior, not only successful matches.

## Metadata safety

- Never invent DOI, canonical URL, ORCID, journal, volume, issue, page-range, or acceptance metadata.
- If a metadata field is not yet known, leave it absent or `null`.
- Keep `metadata.json`, `paper.html`, `paper.jats.xml`, and `CITATION.cff` synchronized with the same real facts.

## Notes

- The paper is intentionally focused on verification and trust for single-qubit compilation layers.
- Entangling gates are mentioned only as boundaries or interoperability context, not as optimization targets.
- `artifacts/figures/` contains publication-oriented SVG schematics for equivalence checks, canonicalization, and validation workflow.
