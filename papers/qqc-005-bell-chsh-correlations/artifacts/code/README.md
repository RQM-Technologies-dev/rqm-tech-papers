# Code - qqc-005-bell-chsh-correlations

This package includes a small executable reference script:

- `bell_chsh_demo.py` - computes quaternionic analyzer products, singlet joint probabilities, Bell correlations, and one optimal CHSH configuration
- `chsh_reference_results.json` - stored outputs produced by the script

## Scope

The code is intentionally modest. It is a reproducibility companion for the formulas in the paper, not a general Bell-scenario simulator or a full quantum SDK integration.

## Usage

```bash
python3 bell_chsh_demo.py
```

The script writes `chsh_reference_results.json` in the same directory.
