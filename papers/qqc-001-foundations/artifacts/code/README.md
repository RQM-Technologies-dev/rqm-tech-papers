# Code — qqc-001-foundations

This directory contains source code supporting
**Foundations of Quaternionic Quantum Computing: Qubits, Spinors, and SU(2) Geometry**.

## Files

| File | Description | Status |
|------|-------------|--------|
| `quaternion_gates.py` | Python implementation of quaternionic single-qubit gates; validates Proposition 1 and Result 1 | Pending |

## Requirements

Python 3.9+, `numpy`.

## Usage

```python
from quaternion_gates import QuaternionGate, X, Y, Z, H, S, T

# Apply X gate to quaternionic qubit q = 1 (|0⟩)
q0 = (1.0, 0.0, 0.0, 0.0)  # a + bi + cj + dk
q1 = X(q0)
print(q1)  # Should be (0, 1, 0, 0) = i  ↔  |1⟩
```

## Testing

```bash
python -m pytest quaternion_gates.py -v
```
