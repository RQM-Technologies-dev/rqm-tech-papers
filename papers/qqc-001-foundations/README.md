## qqc-001-foundations

This folder is a semantic paper package for:

**Foundations of Quaternionic Quantum Computing: Qubits, Spinors, and SU(2) Geometry**

### Source of truth

- `main.tex` is the Overleaf-friendly source of truth for the paper text.

### Local build

If a LaTeX toolchain is available locally, build with:

```bash
latexmk -pdf main.tex
```

The generated PDF should be copied or renamed to `paper.pdf` for the publication package.

### Notes

- This draft is intentionally limited to standard single-qubit mathematics plus an explicit section separating RQM Technologies framing from standard results.
- Multi-qubit quaternionic state evolution is outside the scope of this paper.
