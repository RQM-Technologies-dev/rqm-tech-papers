#!/usr/bin/env python3
"""
Reference verifier for qqc-004-verification-equivalence.

This script compares pairs of single-qubit segments using both the authoritative
canonical-quaternion criterion and interoperable matrix-based diagnostics.

Run:
    python3 artifacts/code/verify_canonical_equivalence.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path


PI = math.pi
EPS = 1e-10
OUTPUT_PATH = Path(__file__).with_name("verification_results.json")


def qmul(q2: tuple[float, float, float, float], q1: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    """Return the quaternion product q2 * q1."""
    w2, x2, y2, z2 = q2
    w1, x1, y1, z1 = q1
    return (
        w2 * w1 - x2 * x1 - y2 * y1 - z2 * z1,
        w2 * x1 + x2 * w1 + y2 * z1 - z2 * y1,
        w2 * y1 - x2 * z1 + y2 * w1 + z2 * x1,
        w2 * z1 + x2 * y1 - y2 * x1 + z2 * w1,
    )


def qnorm(q: tuple[float, float, float, float]) -> float:
    return math.sqrt(sum(v * v for v in q))


def normalize(q: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    n = qnorm(q)
    if n < EPS:
        raise ValueError("zero quaternion cannot be normalized")
    return tuple(v / n for v in q)


def canonicalize(q: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    """Normalize and choose the canonical sign representative."""
    q = normalize(q)
    w, x, y, z = q
    if w > EPS:
        return q
    if w < -EPS:
        return tuple(-v for v in q)
    for component in (x, y, z):
        if component > EPS:
            return q
        if component < -EPS:
            return tuple(-v for v in q)
    return (1.0, 0.0, 0.0, 0.0)


def approx_q(q1: tuple[float, float, float, float], q2: tuple[float, float, float, float], eps: float = 1e-9) -> bool:
    return all(abs(a - b) <= eps for a, b in zip(q1, q2))


def gate_quaternion(name: str, param: float | None = None) -> tuple[float, float, float, float]:
    """Translate a supported gate into a canonical unit quaternion."""
    c = math.cos
    s = math.sin
    root_half = 1.0 / math.sqrt(2.0)
    table: dict[str, tuple[float, float, float, float]] = {
        "I": (1.0, 0.0, 0.0, 0.0),
        "X": (0.0, 1.0, 0.0, 0.0),
        "Y": (0.0, 0.0, 1.0, 0.0),
        "Z": (0.0, 0.0, 0.0, 1.0),
        "H": (0.0, root_half, 0.0, root_half),
        "S": (root_half, 0.0, 0.0, root_half),
        "Sdg": (root_half, 0.0, 0.0, -root_half),
        "T": (c(PI / 8.0), 0.0, 0.0, s(PI / 8.0)),
        "Tdg": (c(PI / 8.0), 0.0, 0.0, -s(PI / 8.0)),
    }
    if name in table:
        return table[name]
    if name == "Rx" and param is not None:
        return (c(param / 2.0), s(param / 2.0), 0.0, 0.0)
    if name == "Ry" and param is not None:
        return (c(param / 2.0), 0.0, s(param / 2.0), 0.0)
    if name == "Rz" and param is not None:
        return (c(param / 2.0), 0.0, 0.0, s(param / 2.0))
    raise KeyError(f"unsupported gate: {name}")


def parse_angle(expr: str) -> float:
    return float(eval(expr, {"__builtins__": {}}, {"pi": math.pi}))


def parse_gate(token: str) -> tuple[str, float | tuple[float, float, float, float] | None]:
    token = token.strip()
    if token.startswith("u1q("):
        values = token[token.index("(") + 1 : -1].split(",")
        return "u1q", tuple(float(v.strip()) for v in values)
    if "(" in token:
        name, rest = token.split("(", 1)
        return name, parse_angle(rest[:-1])
    return token, None


def segment_quaternion(segment: list[str]) -> tuple[float, float, float, float]:
    """Return the canonical fused quaternion for a segment."""
    fused = (1.0, 0.0, 0.0, 0.0)
    for token in segment:
        name, param = parse_gate(token)
        if name == "u1q":
            q = canonicalize(param)  # type: ignore[arg-type]
        else:
            q = canonicalize(gate_quaternion(name, param))  # type: ignore[arg-type]
        fused = canonicalize(qmul(q, fused))
    return fused


def phi(q: tuple[float, float, float, float]) -> tuple[tuple[complex, complex], tuple[complex, complex]]:
    """Map a quaternion to the fixed SU(2) matrix convention."""
    w, x, y, z = q
    return (
        (complex(w, -z), complex(-y, -x)),
        (complex(y, -x), complex(w, z)),
    )


def matmul(
    a: tuple[tuple[complex, complex], tuple[complex, complex]],
    b: tuple[tuple[complex, complex], tuple[complex, complex]],
) -> tuple[tuple[complex, complex], tuple[complex, complex]]:
    return (
        (
            a[0][0] * b[0][0] + a[0][1] * b[1][0],
            a[0][0] * b[0][1] + a[0][1] * b[1][1],
        ),
        (
            a[1][0] * b[0][0] + a[1][1] * b[1][0],
            a[1][0] * b[0][1] + a[1][1] * b[1][1],
        ),
    )


def dagger(
    a: tuple[tuple[complex, complex], tuple[complex, complex]]
) -> tuple[tuple[complex, complex], tuple[complex, complex]]:
    return (
        (a[0][0].conjugate(), a[1][0].conjugate()),
        (a[0][1].conjugate(), a[1][1].conjugate()),
    )


def trace(a: tuple[tuple[complex, complex], tuple[complex, complex]]) -> complex:
    return a[0][0] + a[1][1]


def process_fidelity(
    u: tuple[tuple[complex, complex], tuple[complex, complex]],
    v: tuple[tuple[complex, complex], tuple[complex, complex]],
) -> float:
    x = matmul(dagger(u), v)
    return abs(trace(x)) ** 2 / 4.0


def phase_aware_residual(
    u: tuple[tuple[complex, complex], tuple[complex, complex]],
    v: tuple[tuple[complex, complex], tuple[complex, complex]],
) -> float:
    x = matmul(dagger(u), v)
    tr = trace(x)
    phase = 1 + 0j if abs(tr) < EPS else tr / abs(tr)
    return max(
        abs(x[0][0] - phase),
        abs(x[1][1] - phase),
        abs(x[0][1]),
        abs(x[1][0]),
    )


def verification_corpus() -> list[dict[str, object]]:
    return [
        {
            "id": "positive-rx-vs-x",
            "category": "positive exact named-gate recovery",
            "original": ["Rx(pi/2)", "Rx(pi/2)"],
            "candidate": ["X"],
            "expected_equivalent": True,
        },
        {
            "id": "positive-rz-vs-s",
            "category": "positive exact named-gate recovery",
            "original": ["Rz(pi/4)", "Rz(pi/4)"],
            "candidate": ["S"],
            "expected_equivalent": True,
        },
        {
            "id": "positive-generic-u1q",
            "category": "positive generic primitive verification",
            "original": ["H", "T", "Rz(pi/3)"],
            "candidate": ["u1q(0.560985526797,-0.430459334577,-0.560985526797,-0.430459334577)"],
            "expected_equivalent": True,
        },
        {
            "id": "positive-identity",
            "category": "positive identity elimination",
            "original": ["T", "Tdg"],
            "candidate": [],
            "expected_equivalent": True,
        },
        {
            "id": "negative-x-vs-y",
            "category": "negative distinct named gates",
            "original": ["X"],
            "candidate": ["Y"],
            "expected_equivalent": False,
        },
        {
            "id": "negative-rz-vs-rx",
            "category": "negative wrong axis recovery",
            "original": ["Rz(pi/3)"],
            "candidate": ["Rx(pi/3)"],
            "expected_equivalent": False,
        },
        {
            "id": "negative-generic-perturbed",
            "category": "negative perturbed generic primitive",
            "original": ["u1q(0.560985526797,-0.430459334577,-0.560985526797,-0.430459334577)"],
            "candidate": ["u1q(0.560985526797,-0.430459334577,-0.560985526797,-0.420459334577)"],
            "expected_equivalent": False,
        },
    ]


def main() -> None:
    corpus = verification_corpus()
    rows: list[dict[str, object]] = []
    positives_passed = 0
    negatives_rejected = 0

    for item in corpus:
        original = item["original"]  # type: ignore[index]
        candidate = item["candidate"]  # type: ignore[index]
        qa = segment_quaternion(original)  # type: ignore[arg-type]
        qb = segment_quaternion(candidate) if candidate else (1.0, 0.0, 0.0, 0.0)  # type: ignore[arg-type]
        ua = phi(qa)
        ub = phi(qb)
        canonical_match = approx_q(qa, qb, 1e-9)
        residual = phase_aware_residual(ua, ub)
        fidelity = process_fidelity(ua, ub)
        equivalent = canonical_match
        expected = bool(item["expected_equivalent"])
        if expected and equivalent:
            positives_passed += 1
        if (not expected) and (not equivalent):
            negatives_rejected += 1

        rows.append(
            {
                "id": item["id"],
                "category": item["category"],
                "expected_equivalent": expected,
                "canonical_match": equivalent,
                "phase_aware_residual": residual,
                "process_fidelity": fidelity,
                "trace_overlap_abs": abs(trace(matmul(dagger(ua), ub))),
                "original_quaternion": [round(v, 12) for v in qa],
                "candidate_quaternion": [round(v, 12) for v in qb],
            }
        )

    payload = {
        "paper_id": "qqc-004-verification-equivalence",
        "authoritative_equivalence_check": "canonical quaternion equality after normalization and sign-canonicalization",
        "matrix_interoperability_check": "phase-aware matrix residual and process fidelity under the fixed quaternion-SU(2) map",
        "aggregate": {
            "cases": len(corpus),
            "positive_cases": sum(1 for item in corpus if item["expected_equivalent"]),
            "negative_cases": sum(1 for item in corpus if not item["expected_equivalent"]),
            "positives_passed": positives_passed,
            "negatives_rejected": negatives_rejected,
            "all_cases_consistent_with_expectation": positives_passed + negatives_rejected == len(corpus),
        },
        "cases": rows,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
