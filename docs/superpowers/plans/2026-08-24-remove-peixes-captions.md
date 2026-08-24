# Remove Peixes Captions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove only the visible captions from all Peixes/Peces slides while preserving localized alt text and carousel behavior.

**Architecture:** Delete the `figcaption.gallery-caption` block from the 34 slides inside each targeted carousel. Make no CSS or JavaScript change because the shared height calculation already falls back correctly to the captionless figure.

**Tech Stack:** Static HTML, Python assertions, Chromium headless

## Constraints

- Target only `gallery-carousel-peixes` and `gallery-carousel-peces`.
- Preserve 34 images, order, localized alt text, autoplay, controls, and lightbox per locale.
- Preserve all captions outside those two panels.

### Task 1: Remove the targeted captions

- [ ] Run a red assertion expecting zero captions in each target panel; observe 34.
- [ ] Remove the complete three-line `figcaption` block from every target slide in `index.html` and `es/index.html`.
- [ ] Assert 34 slides, 34 localized alt texts, and zero captions per panel.
- [ ] Assert Cadernos and Collagem still contain captions.
- [ ] Run `git diff --check`.

### Task 2: Browser regression and commit

- [ ] Verify PT/ES display no visible caption below Peixes/Peces images.
- [ ] Verify autoplay advances, controls work, and lightbox reports `1 / 34`.
- [ ] Verify no mobile overflow at 390 px.
- [ ] Commit with `content: remove Peixes gallery captions`.
- [ ] Re-run committed-state assertions and inspect repository status.
