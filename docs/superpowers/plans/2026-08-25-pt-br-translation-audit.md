# PT-BR Translation Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove unintended Spanish and mixed-language text from the PT-BR site while preserving approved original-language proper titles.

**Architecture:** A focused Python auditor extracts visible PT-BR text and reports Spanish-only lexical patterns outside an explicit proper-title allowlist. Corrections are applied to the manifest and editorial JSON sources, then the existing renderer regenerates the page. Tests cover detection, allowlisting, and zero-residual output.

**Tech Stack:** Python 3, `unittest`, BeautifulSoup, JSON, existing static-gallery renderer, Chromium.

## Global Constraints

- Preserve original titles of works, series, institutions, exhibitions, people, places, and publications.
- Translate faithfully into PT-BR without stylistic rewriting.
- Correct source editorial data before regenerating HTML.
- Do not alter Spanish copy except for renderer-required structural equivalence.

---

### Task 1: PT-BR residual-language auditor

**Files:**
- Create: `tools/acervo/audit_pt_br.py`
- Create: `tests/test_acervo_pt_br.py`

**Interfaces:**
- Produces: `audit_pt_br_html(path: Path) -> AuditReport` with contextual findings.
- Consumes: PT-BR HTML and explicit allowlisted proper titles.

- [ ] Write tests proving detection of `Vista general`, `Detalle`, `Boceto`, `Materiales`, mixed `y collage`, and full Spanish prose.
- [ ] Verify tests fail before implementation.
- [ ] Implement visible-text and relevant-attribute extraction, phrase/token rules, contextual allowlist, and nonzero CLI exit on findings.
- [ ] Verify focused tests pass and run the auditor on current `index.html` to capture the baseline.

### Task 2: Caption and metadata correction

**Files:**
- Modify: `data/acervo/manifest.json`
- Modify: `tools/acervo/curate.py` where localization rules caused the residual text
- Modify: related curator tests

**Interfaces:**
- Consumes: `caption.pt`, `alt.pt`, and source caption fields.
- Produces: fully localized PT-BR captions that survive regeneration.

- [ ] Group every flagged caption by repeated phrase/material pattern.
- [ ] Add failing localization tests for each repeated pattern.
- [ ] Correct deterministic localization rules and reapply them to manifest PT-BR fields.
- [ ] Manually correct exceptional captions while preserving proper titles.
- [ ] Run focused tests and confirm caption findings reach zero.

### Task 3: Curatorial and literary correction

**Files:**
- Modify: relevant `data/acervo/editorial-*.json`
- Modify: `data/acervo/manifest.json` series content when applicable

**Interfaces:**
- Consumes: PT-BR paragraphs and structured literary sections.
- Produces: faithful PT-BR text with original proper names/citations retained.

- [ ] Enumerate every Spanish prose block in PT-BR source data.
- [ ] Translate each block faithfully and review spelling/grammar.
- [ ] Run the auditor against a regenerated temporary page and resolve all non-allowlisted findings.

### Task 4: Regeneration and end-to-end verification

**Files:**
- Modify: `index.html`
- Preserve: `es/index.html` editorial content

**Interfaces:**
- Consumes: corrected manifest/editorial JSON through `render_galleries.py`.
- Produces: audited bilingual static pages.

- [ ] Record the Spanish page hash, render both pages, and confirm Spanish editorial content has not changed unexpectedly.
- [ ] Run renderer twice and verify idempotence.
- [ ] Run all unit tests, PT-BR audit, reference audit, and `git diff --check`.
- [ ] Inspect the PT-BR page in Chromium for residual Spanish, broken images, console errors, and layout regressions.
- [ ] Commit source corrections, auditor, generated HTML, tests, and this plan.
