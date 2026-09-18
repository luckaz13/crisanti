# Crítica Reading Modal Light Surface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adapt the Literature/Crítica reading modal so its reading surface is white with high-contrast text, while preserving dark chrome and gold accents on dark surfaces.

**Architecture:** Keep the existing modal DOM and JavaScript behavior. Update the shared modal CSS in `css/style.css`; the root and Spanish pages already consume the same stylesheet. Add focused CSS assertions to the existing modal-style test coverage.

**Tech Stack:** Static HTML, shared CSS, vanilla JavaScript, Python `unittest`/`pytest` checks.

## Global Constraints

- Apply white only to `.lit-modal-body`, not the backdrop, header, or footer.
- Preserve gold on dark modal chrome; replace gold only where it appears over white.
- Do not change editorial copy or modal behavior.
- Keep the reading controls usable on desktop and mobile.

---

### Task 1: Implement and verify the light reading surface

**Files:**
- Modify: `css/style.css:2313-2550` — modal surface, typography, divider, scrollbar, and responsive states.
- Modify: `tests/test_critica_card_style.py` — focused assertions for the reading modal palette.

**Interfaces:**
- Consumes: existing `.lit-modal-*` selectors and shared design tokens.
- Produces: a white `.lit-modal-body` with dark reading copy and neutral accents, while `.lit-modal-header` and `.lit-modal-footer` retain dark backgrounds and gold-compatible chrome.

- [ ] **Step 1: Add focused CSS assertions**

Assert that `.lit-modal-body` is white, `.lit-modal-text` and `.lit-modal-title` use dark foregrounds, the body divider/cap still use neutral colors, and the header/footer retain dark surfaces.

- [ ] **Step 2: Run the focused test and confirm the new assertions fail**

Run: `python3 -m pytest -q tests/test_critica_card_style.py`
Expected: FAIL against the current dark reading surface.

- [ ] **Step 3: Update the modal CSS**

Set the reading body to `#FFFFFF`, use `#1E1B18` for title/body text, use neutral gray for the divider, capitular, scrollbar track/thumb, and keep gold values in header/footer selectors unchanged.

- [ ] **Step 4: Run focused and full relevant tests**

Run: `python3 -m pytest -q tests/test_critica_card_style.py tests/test_gallery_rendered_layout.py`
Expected: all tests pass.

- [ ] **Step 5: Run the Impeccable detector and inspect the final diff**

Run: `node /home/lucas/.agents/skills/impeccable/scripts/detect.mjs --json css/style.css`
Then run: `git diff --check`.
Expected: no blocking detector finding and no whitespace errors.

- [ ] **Step 6: Commit the implementation**

```bash
git add css/style.css tests/test_critica_card_style.py
git commit -m "Adapta leitura crítica para superfície clara"
```
