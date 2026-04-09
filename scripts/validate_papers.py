#!/usr/bin/env python3
"""
validate_papers.py — Validation script for the rqm-tech-papers repository.

Checks that every paper folder under papers/ contains all required files,
and validates JSON companion files against their schemas.

Usage:
    python3 scripts/validate_papers.py [--paper PAPER_ID]

Exit codes:
    0 — all validations passed
    1 — one or more validations failed
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
PAPERS_DIR = REPO_ROOT / "papers"
SCHEMAS_DIR = REPO_ROOT / "schemas"

REQUIRED_FILES = [
    "paper.html",
    "paper.pdf",
    "metadata.json",
    "paper.jats.xml",
    "claims.json",
    "notation.json",
    "glossary.json",
    "references.bib",
    "CITATION.cff",
    "artifacts",
]

SCHEMA_MAP = {
    "metadata.json": "metadata.schema.json",
    "claims.json": "claims.schema.json",
    "notation.json": "notation.schema.json",
    "glossary.json": "glossary.schema.json",
}

PAPER_ID_PATTERN = re.compile(r"^[a-z]+-\d{3}-[a-z0-9-]+$")

# ── Helpers ───────────────────────────────────────────────────────────────────


def print_ok(msg: str) -> None:
    print(f"  \033[32m✓\033[0m {msg}")


def print_fail(msg: str) -> None:
    print(f"  \033[31m✗\033[0m {msg}")


def print_warn(msg: str) -> None:
    print(f"  \033[33m⚠\033[0m {msg}")


def print_header(msg: str) -> None:
    print(f"\n\033[1m{msg}\033[0m")


# ── JSON Schema validation ────────────────────────────────────────────────────


def validate_json_against_schema(json_path: Path, schema_path: Path) -> list[str]:
    """
    Validate a JSON file against a JSON Schema.
    Returns a list of error messages (empty if valid).
    """
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return ["jsonschema not installed; run: pip install jsonschema"]

    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"JSON parse error: {e}"]

    try:
        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Schema parse error: {e}"]

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    return [f"{'.'.join(str(p) for p in e.path) or '(root)'}: {e.message}" for e in errors]


# ── Per-paper validation ───────────────────────────────────────────────────────


def validate_paper(paper_dir: Path) -> list[str]:
    """
    Validate a single paper directory.
    Returns a list of error strings (empty if valid).
    """
    errors: list[str] = []
    paper_id = paper_dir.name

    # 1. Validate folder name matches paper ID pattern
    if not PAPER_ID_PATTERN.match(paper_id):
        errors.append(
            f"Folder name '{paper_id}' does not match required pattern "
            f"{{series}}-{{NNN}}-{{slug}} (e.g. qqc-001-foundations)"
        )

    # 2. Check all required files/directories exist
    for required in REQUIRED_FILES:
        path = paper_dir / required
        if not path.exists():
            errors.append(f"Missing required file/directory: {required}")

    # 3. Validate JSON files are parseable
    for json_file in ["metadata.json", "claims.json", "notation.json", "glossary.json"]:
        json_path = paper_dir / json_file
        if not json_path.exists():
            continue  # already reported above
        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"{json_file}: JSON parse error — {e}")
            continue

        # 4. Validate JSON against schema
        schema_name = SCHEMA_MAP.get(json_file)
        if schema_name:
            schema_path = SCHEMAS_DIR / schema_name
            if schema_path.exists():
                schema_errors = validate_json_against_schema(json_path, schema_path)
                for se in schema_errors:
                    errors.append(f"{json_file}: schema violation — {se}")
            else:
                errors.append(f"Schema file not found: schemas/{schema_name}")

        # 5. Check paper_id field matches folder name (for files that have it)
        if isinstance(data, dict) and "paper_id" in data:
            if data["paper_id"] != paper_id:
                errors.append(
                    f"{json_file}: paper_id field '{data['paper_id']}' "
                    f"does not match folder name '{paper_id}'"
                )

    # 6. Check metadata.json status-specific rules
    metadata_path = paper_dir / "metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path, encoding="utf-8") as f:
                metadata = json.load(f)
            status = metadata.get("status", "")
            # Published papers must have a canonical_url
            if status == "published" and not metadata.get("canonical_url"):
                errors.append("metadata.json: published paper must have a canonical_url")
            # Published papers must have a real publication_date
            if status == "published" and not metadata.get("publication_date"):
                errors.append("metadata.json: published paper must have a publication_date")
        except (json.JSONDecodeError, KeyError):
            pass  # already reported

    # 7. Check paper.pdf is not empty (basic check)
    pdf_path = paper_dir / "paper.pdf"
    if pdf_path.exists() and pdf_path.stat().st_size == 0:
        errors.append("paper.pdf exists but is empty (0 bytes); use a placeholder stub")

    return errors


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate all paper folders in the rqm-tech-papers repository."
    )
    parser.add_argument(
        "--paper",
        metavar="PAPER_ID",
        help="Validate a single paper by ID (e.g. qqc-001-foundations)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    args = parser.parse_args()

    if not PAPERS_DIR.exists():
        print(f"Error: papers directory not found at {PAPERS_DIR}")
        return 1

    # Collect paper directories
    if args.paper:
        paper_dirs = [PAPERS_DIR / args.paper]
        if not paper_dirs[0].exists():
            print(f"Error: paper directory not found: {paper_dirs[0]}")
            return 1
    else:
        paper_dirs = sorted(
            [d for d in PAPERS_DIR.iterdir() if d.is_dir()],
            key=lambda d: d.name,
        )

    if not paper_dirs:
        print("No paper directories found.")
        return 0

    total_errors = 0
    total_papers = 0

    for paper_dir in paper_dirs:
        total_papers += 1
        print_header(f"Validating: {paper_dir.name}")
        errors = validate_paper(paper_dir)

        if errors:
            total_errors += len(errors)
            for error in errors:
                print_fail(error)
        else:
            print_ok("All checks passed")

    # Summary
    print_header("Summary")
    print(f"  Papers checked: {total_papers}")

    if total_errors == 0:
        print_ok(f"All {total_papers} paper(s) passed validation.")
        return 0
    else:
        print_fail(f"{total_errors} error(s) found across {total_papers} paper(s). Fix before merging.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
