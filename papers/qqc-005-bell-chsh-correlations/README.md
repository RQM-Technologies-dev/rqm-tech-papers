# qqc-005-bell-chsh-correlations

This folder is a semantic paper package for:

**Bell and CHSH Correlations from Quaternionic Spin Geometry: A Direct Derivation on S^3**

## Source of truth

- `main.tex` is the Overleaf-friendly source of truth for the paper text.
- `index.html` is the clean package landing page for `/papers/qqc-005-bell-chsh-correlations/`.
- `paper.html` is the full browsable paper page and should mirror the authored source.

## Dependency on earlier papers

- This draft depends explicitly on `qqc-001-foundations`.
- Paper 1 supplies the fixed quaternion--`SU(2)` convention `Phi`.
- The present paper is the first paper in the series focused on Bell/CHSH correlations and singlet-sector entanglement geometry.

## Local build

If a LaTeX toolchain is available locally, build with:

```bash
latexmk -pdf main.tex
```

Copy or rename the generated PDF to `paper.pdf` for the publication package.
This cloud environment does not currently provide `latexmk`, so the intended
build path for this draft is standard Overleaf / TeX Live using `main.tex` as
the authoritative source of truth.

## Code artifact

- The package includes a small executable reference script at `artifacts/code/bell_chsh_demo.py`.
- The measured outputs used in the package are written to `artifacts/code/chsh_reference_results.json`.
- The script computes quaternionic analyzer products, singlet joint probabilities, the Bell correlation law, and one optimal CHSH configuration.

## Metadata safety

- Never invent DOI, canonical URL, ORCID, journal, volume, issue, page-range, or acceptance metadata.
- If a metadata field is not yet known, leave it absent or `null`.
- Keep `metadata.json`, `paper.html`, `paper.jats.xml`, and `CITATION.cff` synchronized with the same real facts.

## Notes

- The paper is intentionally conservative and does not claim a new physical theory.
- It does not claim a local hidden-variable completion.
- It does not define a full general quaternionic tensor-product formalism beyond the singlet-sector derivations used here.
