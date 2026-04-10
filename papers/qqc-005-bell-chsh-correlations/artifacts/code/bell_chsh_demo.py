#!/usr/bin/env python3
"""
bell_chsh_demo.py

Reference calculations for qqc-005-bell-chsh-correlations.

This script computes:

1. quaternionic analyzer products for pure unit quaternions u_a, u_b in Im(H),
2. singlet joint probabilities P(s,t|a,b) = 1/4 (1 - s t a·b),
3. correlation values E(a,b) = - a·b,
4. one optimal CHSH configuration with |S| = 2 sqrt(2).

The script uses only the Python standard library.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List

Vector = List[float]


def dot(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))


def cross(a: Vector, b: Vector) -> Vector:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def pure_quaternion_product(a: Vector, b: Vector) -> Dict[str, object]:
    """
    For pure unit quaternions u_a and u_b corresponding to vectors a and b,
    return the scalar and vector parts of u_a u_b = -a·b + u_{a×b}.
    """
    return {
        "scalar_part": -dot(a, b),
        "vector_part": cross(a, b),
    }


def joint_probability(s: int, t: int, a: Vector, b: Vector) -> float:
    return 0.25 * (1.0 - s * t * dot(a, b))


def joint_distribution(a: Vector, b: Vector) -> Dict[str, float]:
    probs: Dict[str, float] = {}
    for s in (+1, -1):
        for t in (+1, -1):
            key = f"{s:+d}{t:+d}"
            probs[key] = joint_probability(s, t, a, b)
    return probs


def correlation(a: Vector, b: Vector) -> float:
    probs = joint_distribution(a, b)
    total = 0.0
    for key, prob in probs.items():
        s = 1 if key[0] == "+" else -1
        t = 1 if key[2] == "+" else -1
        total += s * t * prob
    return total


def pair_report(a: Vector, b: Vector) -> Dict[str, object]:
    return {
        "dot_product": dot(a, b),
        "pure_quaternion_product": pure_quaternion_product(a, b),
        "joint_probabilities": joint_distribution(a, b),
        "correlation": correlation(a, b),
    }


def main() -> None:
    a = [0.0, 0.0, 1.0]
    a_prime = [1.0, 0.0, 0.0]
    b = [1.0 / math.sqrt(2.0), 0.0, 1.0 / math.sqrt(2.0)]
    b_prime = [-1.0 / math.sqrt(2.0), 0.0, 1.0 / math.sqrt(2.0)]

    result = {
        "paper_id": "qqc-005-bell-chsh-correlations",
        "description": (
            "Reference Bell/CHSH values computed from quaternionic analyzer "
            "geometry and singlet probabilities."
        ),
        "settings": {
            "a": a,
            "a_prime": a_prime,
            "b": b,
            "b_prime": b_prime,
        },
        "pairs": {
            "E(a,b)": pair_report(a, b),
            "E(a,b_prime)": pair_report(a, b_prime),
            "E(a_prime,b)": pair_report(a_prime, b),
            "E(a_prime,b_prime)": pair_report(a_prime, b_prime),
        },
    }

    s_value = (
        result["pairs"]["E(a,b)"]["correlation"]
        + result["pairs"]["E(a,b_prime)"]["correlation"]
        + result["pairs"]["E(a_prime,b)"]["correlation"]
        - result["pairs"]["E(a_prime,b_prime)"]["correlation"]
    )
    result["chsh"] = {
        "value": s_value,
        "absolute_value": abs(s_value),
        "tsirelson_bound": 2.0 * math.sqrt(2.0),
        "saturates_tsirelson_bound": abs(abs(s_value) - 2.0 * math.sqrt(2.0)) < 1e-12,
    }

    out_path = Path(__file__).with_name("chsh_reference_results.json")
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
