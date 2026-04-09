# Code — qqc-003-gate-fusion

This directory contains a small reference benchmark harness for
**Quaternionic Gate Fusion on S^3: Geometry-Native Optimization for Single-Qubit Circuit Segments**.

Included artifacts:

| File | Purpose |
|------|---------|
| `benchmark_gate_fusion.py` | Pure-Python reference implementation of the local quaternionic fusion pass used for the paper's shipped benchmark corpus |
| `benchmark_results.json` | Measured output produced by the harness on the shipped reference corpus |

## Scope

The code is intentionally narrow:

- it extracts no segments from arbitrary full-circuit parsers,
- it evaluates a fixed reference corpus of single-qubit segments,
- it fuses by quaternion multiplication in circuit order,
- it applies normalization and sign-canonicalization,
- it reconstructs to identity, recognized named gates, axis-aligned rotations, or a generic `u1q` primitive, and
- it measures local gate-count and depth changes against a syntax-preserving no-fusion baseline.

## Non-claims

This artifact is **not**:

- a full compiler,
- a complete synthesis engine,
- an optimizer for entangling gates, or
- evidence of universal superiority over external compiler stacks.

It is a reproducible reference harness supporting the paper's local
single-qubit-segment evaluation.
