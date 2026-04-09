# Code — qqc-004-verification-equivalence

This directory contains the reference verification artifact for
**Verification, Canonicalization, and Equivalence in Quaternionic Quantum Compilation**.

## Included files

| File | Purpose |
|------|---------|
| `verify_canonical_equivalence.py` | Pure-Python verifier comparing segment pairs by canonical quaternion equality and matrix-based diagnostics |
| `verification_results.json` | Measured output produced by the verifier on the shipped positive and negative verification corpus |

## Scope

The verifier is intentionally small and local:

- it checks single-qubit segment equivalence only,
- it uses the fixed quaternion--`SU(2)` convention established in papers 1--3,
- it exposes both the authoritative canonical-quaternion check and interoperable matrix diagnostics, and
- it is meant as a trust-layer reference artifact rather than a production compiler service.

The script does **not**:

- optimize circuits,
- model entangling gates,
- define a full external API,
- or replace matrix-based toolchains.

It is included so that the paper's trust claims are backed by a concrete, reviewable
procedure.
