# Code — qqc-002-canonical-ir

This directory is reserved for future implementation artifacts associated with
**A Canonical Quaternionic Intermediate Representation for Single-Qubit Quantum Circuits**.

The present paper is a representation and canonicalization specification rather
than a full compiler implementation paper. No production code is included in
this draft package.

If later revisions add code artifacts, they should remain tightly scoped to the
representation layer described in the paper, for example:

- a reference implementation of the `u1q` normalization and sign-canonicalization rules,
- exact and floating-point gate-to-quaternion translation utilities for single-qubit gates,
- segment extraction helpers for consecutive one-qubit runs bounded by entangling gates, and
- regression fixtures showing that composition followed by re-canonicalization preserves the intended single-qubit action modulo global phase.

Any future code should make explicit that the current paper does **not** define
entangling-gate internals, a full multi-qubit IR, or a hardware execution
backend.
