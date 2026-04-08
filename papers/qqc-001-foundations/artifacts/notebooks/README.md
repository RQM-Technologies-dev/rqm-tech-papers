# Notebooks — qqc-001-foundations

This directory contains Jupyter notebooks supporting
**Foundations of Quaternionic Quantum Computing: Qubits, Spinors, and SU(2) Geometry**.

## Notebooks

| File | Description | Status |
|------|-------------|--------|
| `bloch_sphere_visualization.ipynb` | Interactive Bloch sphere visualization using quaternion parametrization; validates Result 1 | Pending |

## Requirements

Notebooks require Python 3.9+ and the following packages:
- `numpy`
- `matplotlib`
- `scipy`

Install with:
```bash
pip install numpy matplotlib scipy
```

## Running notebooks

```bash
jupyter notebook bloch_sphere_visualization.ipynb
```

Results should reproduce the numerical validation in Section 5 (Result 1) of the paper.
