#!/usr/bin/env python3
"""
Reference benchmark harness for qqc-003-gate-fusion.

This script evaluates a small shipped reference corpus of single-qubit segments
under the local quaternionic fusion pass defined in the paper. It uses only the
Python standard library.

Run:
    python3 artifacts/code/benchmark_gate_fusion.py
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path


PI = math.pi
EPS = 1e-10
OUTPUT_PATH = Path(__file__).with_name("benchmark_results.json")


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
    """Translate a supported gate into its canonical unit quaternion."""
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


KNOWN_GATES: dict[str, tuple[float, float, float, float]] = {
    name: canonicalize(value)
    for name, value in {
        "I": (1.0, 0.0, 0.0, 0.0),
        "X": (0.0, 1.0, 0.0, 0.0),
        "Y": (0.0, 0.0, 1.0, 0.0),
        "Z": (0.0, 0.0, 0.0, 1.0),
        "H": (0.0, 1.0 / math.sqrt(2.0), 0.0, 1.0 / math.sqrt(2.0)),
        "S": (1.0 / math.sqrt(2.0), 0.0, 0.0, 1.0 / math.sqrt(2.0)),
        "Sdg": (1.0 / math.sqrt(2.0), 0.0, 0.0, -1.0 / math.sqrt(2.0)),
        "T": (math.cos(PI / 8.0), 0.0, 0.0, math.sin(PI / 8.0)),
        "Tdg": (math.cos(PI / 8.0), 0.0, 0.0, -math.sin(PI / 8.0)),
    }.items()
}


def reconstruct(q: tuple[float, float, float, float]) -> dict[str, object]:
    """Reconstruct identity, named gate, axis gate, or generic primitive."""
    q = canonicalize(q)
    for name, ref in KNOWN_GATES.items():
        if approx_q(q, ref):
            return {"kind": "named", "gate": name}

    w, x, y, z = q
    nonzero = [abs(v) > 1e-9 for v in (x, y, z)]
    if sum(nonzero) == 1:
        if nonzero[0]:
            return {"kind": "axis", "gate": "Rx", "theta": 2.0 * math.atan2(x, w)}
        if nonzero[1]:
            return {"kind": "axis", "gate": "Ry", "theta": 2.0 * math.atan2(y, w)}
        return {"kind": "axis", "gate": "Rz", "theta": 2.0 * math.atan2(z, w)}

    return {"kind": "generic", "gate": "u1q", "tuple": [round(v, 12) for v in q]}


def parse_angle(expr: str) -> float:
    return float(eval(expr, {"__builtins__": {}}, {"pi": math.pi}))


def parse_gate(token: str) -> tuple[str, float | None]:
    token = token.strip()
    if "(" in token:
        name, rest = token.split("(", 1)
        return name, parse_angle(rest[:-1])
    return token, None


def format_reconstruction(item: dict[str, object]) -> str:
    gate = str(item["gate"])
    if gate == "u1q":
        w, x, y, z = item["tuple"]  # type: ignore[index]
        return f"u1q({w:.6f}, {x:.6f}, {y:.6f}, {z:.6f})"
    if "theta" in item:
        theta = float(item["theta"])
        return f"{gate}({theta / math.pi:.6f}*pi)"
    return gate


def benchmark_corpus() -> list[dict[str, object]]:
    return [
        {
            "id": "textbook-rx-pi",
            "category": "textbook single-qubit chains",
            "segment": ["Rx(pi/2)", "Rx(pi/2)"],
            "source_note": "Two adjacent quarter-turns about x.",
        },
        {
            "id": "textbook-rz-half",
            "category": "textbook single-qubit chains",
            "segment": ["Rz(pi/4)", "Rz(pi/4)"],
            "source_note": "Two adjacent eighth-turns about z.",
        },
        {
            "id": "textbook-hzh",
            "category": "textbook single-qubit chains",
            "segment": ["H", "Z", "H"],
            "source_note": "Conjugation identity often seen in textbooks.",
        },
        {
            "id": "mixed-cancellation",
            "category": "mixed named-gate segments",
            "segment": ["S", "T", "Tdg", "Z"],
            "source_note": "Named-gate chain with explicit cancellation.",
        },
        {
            "id": "rotation-heavy-1",
            "category": "rotation-heavy segments",
            "segment": ["Rx(pi/5)", "Ry(pi/7)", "Rz(pi/9)", "Rx(pi/11)"],
            "source_note": "Generic mixed-axis rotation chain.",
        },
        {
            "id": "rotation-heavy-2",
            "category": "rotation-heavy segments",
            "segment": ["Rz(pi/3)", "Rz(pi/6)", "Rz(-pi/2)"],
            "source_note": "Axis-aligned cancellation to identity.",
        },
        {
            "id": "mixed-pipeline",
            "category": "mixed named-gate segments",
            "segment": ["H", "T", "Rz(pi/3)"],
            "source_note": "Mixed named and parametric segment carried over from paper 2.",
        },
        {
            "id": "named-cancel",
            "category": "mixed named-gate segments",
            "segment": ["T", "Tdg"],
            "source_note": "Minimal exact identity cancellation.",
        },
        {
            "id": "cnot-left-segment",
            "category": "segments from two-qubit circuits",
            "segment": ["H", "T"],
            "source_note": "Single-qubit run before an entangling boundary.",
        },
        {
            "id": "cnot-right-segment",
            "category": "segments from two-qubit circuits",
            "segment": ["Tdg", "Rx(pi/4)"],
            "source_note": "Single-qubit run after an entangling boundary.",
        },
        {
            "id": "ansatz-wire",
            "category": "ansatz-style segments",
            "segment": ["Rz(0.13)", "Ry(0.27)", "Rz(0.13)", "Ry(-0.27)", "Rz(-0.13)"],
            "source_note": "Small variational-style single-wire segment.",
        },
        {
            "id": "axis-z-recovery",
            "category": "rotation-heavy segments",
            "segment": ["Rz(pi/5)", "Rz(pi/10)"],
            "source_note": "Exact non-named z-axis recovery case.",
        },
        {
            "id": "axis-x-recovery",
            "category": "rotation-heavy segments",
            "segment": ["Rx(pi/6)", "Rx(pi/3)"],
            "source_note": "Exact non-named x-axis recovery case.",
        },
    ]


def evaluate_segment(segment: list[str]) -> tuple[tuple[float, float, float, float], dict[str, object]]:
    fused = (1.0, 0.0, 0.0, 0.0)
    for token in segment:
        name, param = parse_gate(token)
        fused = canonicalize(qmul(canonicalize(gate_quaternion(name, param)), fused))
    reconstruction = reconstruct(fused)
    return fused, reconstruction


def retranslated_quaternion(reconstruction: dict[str, object]) -> tuple[float, float, float, float]:
    kind = reconstruction["kind"]
    gate = reconstruction["gate"]
    if kind == "named":
        return KNOWN_GATES[str(gate)]
    if kind == "axis":
        return canonicalize(gate_quaternion(str(gate), float(reconstruction["theta"])))
    if kind == "generic":
        values = reconstruction["tuple"]  # type: ignore[index]
        return canonicalize(tuple(float(v) for v in values))
    raise ValueError(f"unsupported reconstruction kind: {kind}")


def main() -> None:
    corpus = benchmark_corpus()
    by_category: dict[str, dict[str, int]] = defaultdict(
        lambda: {"segments": 0, "original_gate_count": 0, "optimized_gate_count": 0}
    )
    reconstruction_kinds: Counter[str] = Counter()
    measured_segments: list[dict[str, object]] = []
    aggregate = {
        "baseline": "syntax-preserving single-qubit segments with no fusion",
        "equivalence_check": "canonical quaternion equality after normalization and sign-canonicalization",
        "segments": 0,
        "original_gate_count": 0,
        "optimized_gate_count": 0,
        "original_depth": 0,
        "optimized_depth": 0,
        "identity_outputs": 0,
        "segments_collapsed_to_one_canonical_representative": 0,
        "named_or_axis_recoveries": 0,
    }

    for item in corpus:
        segment = item["segment"]  # type: ignore[index]
        fused, reconstruction = evaluate_segment(segment)  # type: ignore[arg-type]
        optimized_gate_count = 0 if reconstruction["kind"] == "named" and reconstruction["gate"] == "I" else 1
        retrans = retranslated_quaternion(reconstruction)
        equivalent = approx_q(fused, retrans, 1e-8)

        aggregate["segments"] += 1
        aggregate["original_gate_count"] += len(segment)  # type: ignore[arg-type]
        aggregate["optimized_gate_count"] += optimized_gate_count
        aggregate["original_depth"] += len(segment)  # type: ignore[arg-type]
        aggregate["optimized_depth"] += optimized_gate_count
        aggregate["segments_collapsed_to_one_canonical_representative"] += 1

        if reconstruction["kind"] == "named" and reconstruction["gate"] == "I":
            aggregate["identity_outputs"] += 1
        if reconstruction["kind"] in {"named", "axis"}:
            aggregate["named_or_axis_recoveries"] += 1

        reconstruction_kinds[str(reconstruction["kind"])] += 1

        category = str(item["category"])
        by_category[category]["segments"] += 1
        by_category[category]["original_gate_count"] += len(segment)  # type: ignore[arg-type]
        by_category[category]["optimized_gate_count"] += optimized_gate_count

        measured_segments.append(
            {
                "id": item["id"],
                "category": category,
                "input_segment": segment,
                "source_note": item["source_note"],
                "input_gate_count": len(segment),  # type: ignore[arg-type]
                "optimized_gate_count": optimized_gate_count,
                "input_depth": len(segment),  # type: ignore[arg-type]
                "optimized_depth": optimized_gate_count,
                "fused_quaternion": [round(v, 12) for v in fused],
                "reconstruction": reconstruction,
                "reconstruction_label": format_reconstruction(reconstruction),
                "equivalent_up_to_global_phase": equivalent,
            }
        )

    aggregate["gate_count_reduction"] = aggregate["original_gate_count"] - aggregate["optimized_gate_count"]
    aggregate["depth_reduction"] = aggregate["original_depth"] - aggregate["optimized_depth"]
    aggregate["gate_count_reduction_fraction"] = round(
        aggregate["gate_count_reduction"] / aggregate["original_gate_count"], 6
    )
    aggregate["depth_reduction_fraction"] = round(
        aggregate["depth_reduction"] / aggregate["original_depth"], 6
    )
    aggregate["named_or_axis_recovery_fraction"] = round(
        aggregate["named_or_axis_recoveries"] / aggregate["segments"], 6
    )
    aggregate["reconstruction_kinds"] = dict(reconstruction_kinds)

    category_summary = []
    for category, summary in sorted(by_category.items()):
        reduction = summary["original_gate_count"] - summary["optimized_gate_count"]
        category_summary.append(
            {
                "category": category,
                "segments": summary["segments"],
                "original_gate_count": summary["original_gate_count"],
                "optimized_gate_count": summary["optimized_gate_count"],
                "gate_count_reduction": reduction,
                "compression_ratio": round(
                    summary["optimized_gate_count"] / summary["original_gate_count"], 6
                ),
            }
        )

    payload = {
        "paper_id": "qqc-003-gate-fusion",
        "method": "Quaternionic local fusion with canonicalization and layered reconstruction",
        "aggregate": aggregate,
        "category_summary": category_summary,
        "segments": measured_segments,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
