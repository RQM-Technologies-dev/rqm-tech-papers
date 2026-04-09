# Notebooks — qqc-003-gate-fusion

This paper package does not currently include executable notebooks.

The benchmark numbers reported in the draft come from the shipped reference
Python harness in `artifacts/code/benchmark_gate_fusion.py`, not from a
notebook-only workflow. If future notebooks are added, they should remain
supporting material rather than the authoritative evaluation source.

Suitable future notebook topics include:

- visualizing quaternion trajectories for selected fused segments on the
  canonical hemisphere,
- replaying the shipped benchmark corpus with interactive inspection of
  reconstructed outputs, and
- comparing reconstruction categories (`named`, `axis`, `generic`) across
  segment families.

Any future notebook should state clearly whether it is pedagogical support,
benchmark inspection, or prototype development for a downstream compiler repo.
