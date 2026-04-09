# PROJECT_RULES.md

Repository governance for `rqm-tech-papers`. These rules apply to all human contributors and all AI coding agents.

---

## 1) Repository identity and scope

This repository is a **structured technical publishing system** for RQM Technologies' quaternionic quantum computing paper series.

It exists to publish **semantic technical paper packages** that support:

- human-readable presentation
- machine-readable metadata
- long-term stable organization
- static-site deployment
- future scholarly distribution

This is **not** a generic docs repository, not a blog platform, and not a marketing site.  
Changes must serve paper publication, paper maintenance, or publishing infrastructure.

---

## 2) Required per-paper artifacts (mandatory)

Each paper folder must contain all of the following:

- `paper.html`
- `paper.pdf`
- `metadata.json`
- `paper.jats.xml`
- `claims.json`
- `notation.json`
- `references.bib`
- `glossary.json`
- `CITATION.cff`
- `artifacts/`

Inside `artifacts/`, strongly prefer:

- `figures/`
- `notebooks/`
- `code/`
- `data/` (when relevant)

These files are required publication companions, not optional extras.

---

## 3) Canonical structure rules

1. **One paper per folder.**
2. Folder names must be stable and durable: use a paper ID plus slug (for example: `qqc-001-foundations`).
3. Existing paper paths are canonical and must remain stable.
4. Do not move or rename existing paper folders without an explicit migration plan, redirects strategy, and index updates.
5. Paper folders must be self-contained publication packages.
6. Keep concerns separated:
   - paper content in `papers/<paper-id-slug>/`
   - schemas in `schemas/`
   - generation/validation logic in `scripts/`
   - generated indexes in `index/`

---

## 4) Metadata integrity rules (strict)

Contributors and agents must preserve factual integrity:

- Never invent bibliographic facts.
- Never guess publication dates, DOI values, journal names, author lists, or publication status.
- Never auto-fill claims, glossary terms, notation, or references unless grounded in source material.
- Keep metadata synchronized with actual paper content.
- Treat `metadata.json` as the authoritative structured record **only for confirmed facts**.

Required quality constraints:

- Claim entries in `claims.json` must include explicit claim-type labeling.
- `notation.json` must clearly distinguish standard notation from project-specific notation.
- `glossary.json` entries must be precise and non-promotional; avoid vague or inflated wording.
- `references.bib` must contain real, properly formatted references only.

If a field cannot be verified, leave it unset or explicitly marked unknown per schema and workflow conventions. Do not fabricate completeness.

---

## 5) Content governance rules

- `paper.html` is first-class output, not a derivative afterthought.
- `paper.pdf` is required for publication readiness.
- `paper.jats.xml` is required for archival and scholarly distribution workflows.
- Machine-readable companions (`metadata.json`, `claims.json`, `notation.json`, `glossary.json`, `CITATION.cff`) are mandatory.
- Prefer explicit front matter and structured metadata over buried prose.
- Papers should separate:
  - definitions
  - formal results
  - empirical claims
  - conjectures
  - interpretive claims

Repository default preferences:

- explicit structure
- stable paths
- minimal ambiguity
- reproducible companion artifacts

---

## 6) AI agent behavior rules

All AI agents must:

- Preserve repository structure unless change is explicitly justified.
- Avoid introducing heavy frameworks or infrastructure without a clear need.
- Avoid replacing explicit versioned files with hidden automation.
- Fail loudly when required files are missing.
- Prefer validation and schema enforcement over silent assumptions.
- Avoid "smart" inference that fabricates metadata or scholarly structure.
- Keep generated or transformed output reviewable and auditable in git.
- Avoid altering canonical URLs or canonical paths lightly.
- Avoid mixing marketing copy into technical paper assets.

Agents must explicitly distinguish work across these layers:

- repository-level infrastructure
- per-paper content packages
- generated indexes
- deployment configuration

---

## 7) Validation and quality gates

Before merge, every modified paper package must pass quality gates:

1. Required files exist in each affected paper folder.
2. JSON companion files validate against repository schemas.
3. Site-wide indexes are regenerated whenever paper metadata changes.
4. Broken links or missing required artifacts are treated as failures.
5. `paper.html` and structured metadata remain synchronized.

Adopt a checklist-driven PR process; incomplete validation is a merge blocker.

---

## 8) Deployment and publishing assumptions

This repository must remain compatible with static deployment (including Vercel) and scholarly discovery workflows.

Deployment decisions must preserve:

- stable public URLs
- direct paper-level accessibility
- machine discoverability by scholarly tools and AI systems
- clean indexability of each paper package

No deployment optimization should undermine path stability or paper-level access.

---

## 9) Prohibited changes (do not do this)

- Do not convert this repository into a blog or general CMS-driven content platform.
- Do not hide canonical paper data behind a database or opaque service layer.
- Do not make `paper.pdf` optional.
- Do not delete required companion files.
- Do not invent metadata for convenience.
- Do not scatter paper assets outside their paper folder without a documented reason.
- Do not introduce fragile or opaque path structures.
- Do not mix unfinished speculative claims into formal claim files without explicit labeling.

---

## 10) Contributor workflow (required)

For new papers and substantive updates:

1. Start from repository templates.
2. Fill metadata using verified, source-grounded facts only.
3. Add or update all required companion artifacts.
4. Run repository validation.
5. Regenerate indexes when metadata/content changes affect discovery.
6. Review path stability, link integrity, and publication completeness before opening or merging a PR.

When uncertain, stop and request clarification rather than inferring scholarly facts.
