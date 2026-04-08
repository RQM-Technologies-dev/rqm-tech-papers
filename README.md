# rqm-tech-papers

**AI-friendly semantic publishing system for quaternionic quantum computing research by RQM Technologies.**

This repository is not a generic documentation repo. It is a structured, machine-readable publishing platform for a series of journal-ready technical papers. Every paper ships with both human-readable formats (HTML, PDF) and a full suite of machine-readable companion files, making the series scannable by AI agents, citable by researchers, and deployable as a static site.

---

## Table of Contents

- [What This Repo Is](#what-this-repo-is)
- [Why It Exists](#why-it-exists)
- [Repo Structure](#repo-structure)
- [Paper Organization](#paper-organization)
- [Required Files Per Paper](#required-files-per-paper)
- [How to Add a New Paper](#how-to-add-a-new-paper)
- [Validation](#validation)
- [Index Files for AI Agents](#index-files-for-ai-agents)
- [Static Deployment (Vercel)](#static-deployment-vercel)
- [Human Readers vs AI Agents](#human-readers-vs-ai-agents)
- [License](#license)

---

## What This Repo Is

`rqm-tech-papers` is the canonical publishing home for RQM Technologies' series of peer-reviewed technical papers in **quaternionic quantum computing**. Topics include:

- Quaternionic qubit models and SU(2) geometry
- Spinor representations and their computational implications
- Quaternionic quantum gates and circuits
- Error correction and decoherence in quaternionic frameworks
- Applications to quantum simulation and optimization

Each paper in the series lives in its own self-contained folder under `papers/` and is published with a stable paper ID, a full set of machine-readable companion files, and a canonical URL.

## Why It Exists

Standard code repositories handle source files well but are poorly suited for academic publishing. This repo provides:

1. **Human-readable output** — polished HTML and PDF for each paper
2. **Machine-readable companions** — structured metadata, claims, notation, glossary, references, and JATS XML per paper
3. **AI agent accessibility** — site-wide index files so agents can scan the full series without reading PDFs
4. **Citability** — stable paper IDs, CITATION.cff files, and DOI-ready metadata
5. **Static deployment** — clean path structure that deploys to Vercel without a database or build server

## Repo Structure

```
rqm-tech-papers/
├── README.md                         # This file
├── PROJECT_RULES.md                  # Rules for contributors and AI agents
├── LICENSE
├── .editorconfig
├── .gitignore
│
├── papers/                           # One folder per paper
│   └── qqc-001-foundations/          # Example paper
│       ├── paper.html
│       ├── paper.pdf                 # Drop real PDF here; placeholder included
│       ├── metadata.json
│       ├── paper.jats.xml
│       ├── claims.json
│       ├── notation.json
│       ├── references.bib
│       ├── glossary.json
│       ├── CITATION.cff
│       └── artifacts/
│           ├── figures/
│           ├── notebooks/
│           └── code/
│
├── templates/                        # Reusable starter templates
│   ├── metadata.json
│   ├── claims.json
│   ├── notation.json
│   ├── glossary.json
│   ├── references.bib
│   ├── CITATION.cff
│   ├── paper.jats.xml
│   └── paper.html
│
├── schemas/                          # JSON schemas for validation
│   ├── metadata.schema.json
│   ├── claims.schema.json
│   ├── notation.schema.json
│   └── glossary.schema.json
│
├── scripts/                          # Validation and index generation
│   ├── validate_papers.py
│   └── generate_index.py
│
├── index/                            # Generated site-wide machine-readable indexes
│   ├── papers.json
│   ├── claims.json
│   ├── notation.json
│   └── glossary.json
│
└── .github/
    ├── PULL_REQUEST_TEMPLATE.md
    └── ISSUE_TEMPLATE/
        ├── new-paper.md
        └── paper-correction.md
```

## Paper Organization

Each paper has a **stable paper ID** using the format `{series}-{number}-{slug}`:

| Component | Example | Notes |
|-----------|---------|-------|
| Series prefix | `qqc` | Quaternionic Quantum Computing series |
| Number | `001` | Zero-padded, sequential |
| Slug | `foundations` | Short kebab-case descriptor |
| Full ID | `qqc-001-foundations` | Permanent, never renamed |

Paper IDs and folder names are **permanent** once published. Renaming a folder breaks canonical URLs.

## Required Files Per Paper

Every paper folder **must** contain all of the following:

| File | Purpose |
|------|---------|
| `paper.html` | Primary human-readable version |
| `paper.pdf` | Required; use placeholder stub until final PDF is ready |
| `metadata.json` | Structured metadata (validated against schema) |
| `paper.jats.xml` | JATS XML for journal submission and indexing |
| `claims.json` | Structured list of theorems, definitions, results |
| `notation.json` | Symbol/notation table for AI parsing |
| `glossary.json` | Term definitions |
| `references.bib` | BibTeX references |
| `CITATION.cff` | Citation File Format for software/artifact citation |
| `artifacts/` | Directory for figures, notebooks, code, data |

Validation will fail if any required file is missing. See `scripts/validate_papers.py`.

## How to Add a New Paper

1. **Copy the template folder:**
   ```bash
   cp -r templates/ papers/qqc-002-your-slug/
   ```

2. **Edit `metadata.json`** — fill in all required fields using real data. Never invent or approximate metadata.

3. **Write `paper.html`** — the primary authored version of the paper.

4. **Add `paper.pdf`** — either the final PDF or a placeholder stub (see `papers/qqc-001-foundations/paper.pdf`).

5. **Populate companion files:**
   - `claims.json` — list every theorem, definition, proposition, and empirical result
   - `notation.json` — list every symbol used, with domain and meaning
   - `glossary.json` — define all domain-specific terms
   - `references.bib` — BibTeX entries for all cited works
   - `paper.jats.xml` — JATS XML export
   - `CITATION.cff` — citation metadata

6. **Validate:**
   ```bash
   python scripts/validate_papers.py
   ```

7. **Regenerate indexes:**
   ```bash
   python scripts/generate_index.py
   ```

8. **Open a PR** using the paper PR template (`.github/PULL_REQUEST_TEMPLATE.md`).

## Validation

Run the validation script to check all paper folders:

```bash
python scripts/validate_papers.py
```

This checks:
- All required files are present
- JSON files are valid and conform to their schemas
- No required fields are empty
- Paper IDs match folder names

Run index generation after adding or updating papers:

```bash
python scripts/generate_index.py
```

This regenerates `index/papers.json`, `index/claims.json`, `index/notation.json`, and `index/glossary.json`.

## Index Files for AI Agents

The `index/` directory contains generated site-wide machine-readable indexes:

| File | Contents |
|------|---------|
| `index/papers.json` | All paper metadata in one file |
| `index/claims.json` | All claims across all papers |
| `index/notation.json` | All notation entries across all papers |
| `index/glossary.json` | All glossary terms across all papers |

An AI agent can scan the entire series by fetching `index/papers.json` without needing to parse individual paper folders.

## Static Deployment (Vercel)

The repo is designed for deployment to Vercel as a static site:

- All paper files live at predictable paths: `/papers/{paper-id}/paper.html`
- No build step is required for basic deployment
- Add a `vercel.json` at the root to configure rewrites if needed
- The `index/` directory serves as the API layer for agents

Example `vercel.json` (not included, add when deploying):
```json
{
  "cleanUrls": true,
  "trailingSlash": false
}
```

## Human Readers vs AI Agents

| Audience | Entry point |
|----------|-------------|
| Human readers | `papers/{id}/paper.html` or `papers/{id}/paper.pdf` |
| AI agents (full series scan) | `index/papers.json` |
| AI agents (specific paper) | `papers/{id}/metadata.json` |
| Citation tools | `papers/{id}/CITATION.cff` |
| Journal submission | `papers/{id}/paper.jats.xml` |
| Symbolic reasoning | `papers/{id}/notation.json` |
| Claim verification | `papers/{id}/claims.json` |
| Reference lookup | `papers/{id}/references.bib` |

## License

See [LICENSE](./LICENSE). All paper content is copyright RQM Technologies unless otherwise noted.
