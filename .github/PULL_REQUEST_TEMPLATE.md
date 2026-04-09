# Pull Request — Adding or Updating a Paper

## Summary

<!-- One or two sentences describing what this PR does. -->

## Paper ID(s) affected

<!-- List the paper IDs this PR adds or modifies, e.g. qqc-001-foundations -->

## Type of change

- [ ] New paper (full paper folder added)
- [ ] Content update (paper text or companion files revised)
- [ ] Metadata correction
- [ ] Infrastructure change (templates, schemas, scripts, GitHub config)

---

## Paper checklist

For each paper folder added or modified, confirm the following:

### Required files
- [ ] `index.html` — package landing page present and complete
- [ ] `paper.html` — present and complete
- [ ] `paper.pdf` — present (real PDF or clearly marked placeholder stub)
- [ ] `metadata.json` — complete and validated
- [ ] `paper.jats.xml` — present
- [ ] `claims.json` — all theorems, definitions, propositions, and results listed
- [ ] `notation.json` — all symbols defined
- [ ] `glossary.json` — all domain-specific terms defined
- [ ] `references.bib` — all cited works included
- [ ] `CITATION.cff` — present and accurate
- [ ] `artifacts/` — directory exists (even if empty)

### Metadata quality
- [ ] `paper_id` matches folder name exactly
- [ ] `status` field is correct for the current publication state
- [ ] No metadata fields are invented or approximated
- [ ] `authors` reflects the actual authors with accurate affiliations
- [ ] `abstract` is the verbatim authored abstract

### Validation
- [ ] `python3 scripts/validate_papers.py` passes with no errors
- [ ] `python3 scripts/generate_index.py` has been run
- [ ] Updated `index/` files are committed in this PR

### Canonical URLs and IDs
- [ ] Paper folder name is stable and will not change after merging
- [ ] `paper_id` in `metadata.json` matches folder name
- [ ] No existing paper folder has been renamed or moved

---

## Notes for reviewers

<!-- Any context, decisions, or open questions the reviewer should know about. -->
