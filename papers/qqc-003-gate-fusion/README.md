# qqc-003-gate-fusion

This folder is a semantic paper package for:

**Quaternionic Gate Fusion on S^3: Geometry-Native Optimization for Single-Qubit Circuit Segments**

## Source of truth

- `main.tex` is the Overleaf-friendly source of truth for the paper text.
- `index.html` is the clean package landing page for `/papers/qqc-003-gate-fusion/`.
- `paper.html` is the full browsable paper page and should mirror the authored source.

## Dependency on papers 1 and 2

- This draft depends explicitly on `Foundations of Quaternionic Quantum Computing: Qubits, Spinors, and SU(2) Geometry` and `A Canonical Quaternionic Intermediate Representation for Single-Qubit Quantum Circuits`.
- Paper 1 supplies the fixed quaternion--`SU(2)` convention.
- Paper 2 supplies the canonical `u1q` representation and sign-canonicalization rules.
- Paper 3 studies a local optimization pass built on top of those earlier layers.

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

## Benchmark note

- The package includes a small executable reference harness at `artifacts/code/benchmark_gate_fusion.py`.
- The measured results used in the paper are written to `artifacts/code/benchmark_results.json`.
- The benchmark scope is intentionally modest: it covers a shipped reference corpus of single-qubit segments and does not claim external compiler superiority.

## Metadata safety

- Never invent DOI, canonical URL, ORCID, journal, volume, issue, page-range, or acceptance metadata.
- If a metadata field is not yet known, leave it absent or `null`.
- Keep `metadata.json`, `paper.html`, `paper.jats.xml`, and `CITATION.cff` synchronized with the same real facts.

## Notes

- The paper is intentionally limited to local fusion of single-qubit segments.
- Entangling gates, measurements, resets, and control boundaries are only segmentation barriers.
- `artifacts/figures/` contains publication-oriented SVG schematics for the optimization pipeline, canonical hemisphere, local segment extraction, and measured benchmark summary.
