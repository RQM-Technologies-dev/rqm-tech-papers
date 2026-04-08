# PROJECT_RULES.md

Rules and guidelines for all contributors and AI coding agents working in this repository.

---

## Purpose

This repository is a **technical paper publishing platform** for RQM Technologies' series on quaternionic quantum computing. It is **not** a blog, wiki, or general documentation repo.

Every action taken in this repo must serve one of three purposes:

1. Publishing a new technical paper with full companion files
2. Maintaining or correcting an existing paper
3. Improving the publishing infrastructure (templates, schemas, scripts)

If your change does not serve one of these purposes, do not make it.

---

## Absolute Rules

These rules are non-negotiable and must never be broken by any contributor or AI agent:

### 1. Never invent scholarly metadata

Do not fabricate, approximate, or infer:

- Author names or affiliations
- Publication dates
- DOIs, ISBNs, or identifiers
- Journal names, volume numbers, or page numbers
- Abstract text
- Keywords
- Citation data for referenced works

If a metadata field is not known, leave it as `null` or an empty string. Do not fill it with plausible-sounding guesses.

### 2. Never rename or move paper folders after publication

Paper IDs and folder paths are **permanent** once a paper reaches `preprint` or `published` status. Renaming a folder breaks canonical URLs and invalidates citations.

If a paper must be retracted or replaced, add a `retracted` or `superseded` status to `metadata.json` and publish a correction notice. Do not delete or rename the folder.

### 3. Never auto-fill claims, notation, glossary, or references

The files `claims.json`, `notation.json`, `glossary.json`, and `references.bib` must be authored by a human expert or derived directly from the paper text. Do not generate their content by inference or language model completion without explicit human review and sign-off.

### 4. Never make PDFs optional

Every paper folder must have a `paper.pdf` file. If the final PDF is not yet available, include a clearly marked placeholder stub. The placeholder must state the paper ID and the word "PLACEHOLDER" in its content. The PDF must be replaced with a real publication-ready PDF before the paper reaches `published` status.

### 5. Validation must pass before merge

Every PR that adds or modifies a paper folder must pass the validation script:

```bash
python scripts/validate_papers.py
```

PRs that fail validation must not be merged.

### 6. Never break the index without regenerating it

After any change to paper content or companion files, regenerate the site-wide indexes:

```bash
python scripts/generate_index.py
```

Commit the updated `index/` files as part of the same PR.

---

## File Requirements

### Required files per paper folder

All of the following are mandatory. Validation fails if any are missing:

| File | Description |
|------|-------------|
| `paper.html` | Primary human-readable paper |
| `paper.pdf` | Final PDF or placeholder stub |
| `metadata.json` | Structured metadata, validated against `schemas/metadata.schema.json` |
| `paper.jats.xml` | JATS XML export for journal submission |
| `claims.json` | Structured claims, validated against `schemas/claims.schema.json` |
| `notation.json` | Symbol table, validated against `schemas/notation.schema.json` |
| `glossary.json` | Term definitions, validated against `schemas/glossary.schema.json` |
| `references.bib` | BibTeX references |
| `CITATION.cff` | Citation File Format metadata |
| `artifacts/` | Directory (may be empty but must exist) |

### Recommended artifact structure

```
artifacts/
├── figures/        # All figures referenced in the paper
├── notebooks/      # Jupyter or other computational notebooks
├── code/           # Source code for reproduced results
└── data/           # Datasets if applicable
```

---

## Naming Conventions

### Paper IDs

Format: `{series}-{number}-{slug}`

- `series` — lowercase alphabetic prefix (e.g., `qqc` for Quaternionic Quantum Computing)
- `number` — zero-padded three-digit integer (e.g., `001`, `002`)
- `slug` — short kebab-case descriptor, max 32 characters, no spaces or special characters

Examples: `qqc-001-foundations`, `qqc-002-gate-algebras`, `qqc-003-error-correction`

### File names

- Use lowercase only
- Use hyphens, not underscores, for multi-word names (exception: `CITATION.cff` is standard)
- Never include version numbers in file names (versioning lives in `metadata.json`)

### JSON fields

- Use `snake_case` for all JSON field names
- Never use camelCase in JSON metadata or schema files

---

## HTML as First-Class Output

`paper.html` is the primary output of the publishing system. It must:

- Be a complete, self-contained HTML document
- Include all figures inline or as relative references to `artifacts/figures/`
- Render correctly in a browser without a build step
- Include all metadata in `<meta>` tags for SEO and AI parsing
- Reference the paper's canonical URL in a `<link rel="canonical">` tag

---

## Machine-Readable Files Are Mandatory

The companion files (`metadata.json`, `claims.json`, `notation.json`, `glossary.json`, `paper.jats.xml`) are **not optional extras**. They are first-class outputs required for:

- AI agent parsing of the paper series
- Journal and indexing submission (JATS XML)
- Citation tooling (CITATION.cff)
- Site-wide index generation

Do not skip, stub out, or leave these files incomplete in a paper that reaches `published` status.

---

## Versioning

- Papers use semantic versioning: `{major}.{minor}.{patch}` (e.g., `1.0.0`)
- The version in `metadata.json` must match the version stated in `paper.html` and `paper.jats.xml`
- Patch versions (`1.0.x`) are for typo corrections and minor fixes
- Minor versions (`1.x.0`) are for content additions that do not change conclusions
- Major versions (`x.0.0`) are for substantive revisions that change results or claims
- A new major version should be reviewed as carefully as a new paper

---

## Status Lifecycle

Papers move through these statuses:

```
draft → preprint → submitted → published
                             ↘ retracted (from any status)
                             ↘ superseded (from any status)
```

- `draft` — internal only, not publicly indexed
- `preprint` — publicly available but not peer-reviewed
- `submitted` — submitted to a journal, pending review
- `published` — peer-reviewed and published
- `retracted` — removed from the record; folder preserved, status updated
- `superseded` — replaced by a later paper in the series

---

## What AI Agents Must Not Do

The following actions are explicitly prohibited for AI coding agents working in this repo:

1. Do not generate or modify `paper.html` or `paper.pdf` content without a human-authored source
2. Do not invent claims, theorems, or mathematical results
3. Do not add authors, affiliations, or institutional data that were not provided
4. Do not change a paper's status from `draft` to `preprint` or higher without explicit human instruction
5. Do not delete paper folders or any files within them
6. Do not modify `metadata.json` fields that encode publication facts (DOI, journal, dates) without explicit instruction
7. Do not reorder or renumber existing papers in the series
8. Do not generate `references.bib` entries for works not cited in the paper

AI agents **may**:

- Update template files
- Improve schema definitions
- Fix validation scripts
- Add issue or PR templates
- Regenerate index files from existing paper data
- Fix typos in non-metadata text (e.g., README, PROJECT_RULES)
- Add artifact READMEs in paper folders

---

## PR and Review Standards

Every PR must:

1. Include a completed PR checklist (see `.github/PULL_REQUEST_TEMPLATE.md`)
2. Pass `python scripts/validate_papers.py` with no errors
3. Include updated `index/` files if paper content changed
4. Not modify existing published paper content without a documented reason
5. Be reviewed by at least one human before merge for any paper reaching `preprint` or higher

---

## Questions and Disputes

If these rules conflict with each other or with a legitimate need, open a GitHub issue using the appropriate template before making changes. Do not resolve ambiguity by guessing.
