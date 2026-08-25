# Stable Carousel Controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep desktop carousel arrows at the vertical position established by the first measurable slide while artwork heights change.

**Architecture:** JavaScript measures the first slide and stores its center in a carousel-scoped `--gallery-controls-top` CSS custom property. CSS uses that value only on desktop; existing mobile flow remains unchanged. Width changes invalidate the measurement, while slide changes do not.

**Tech Stack:** Vanilla JavaScript, CSS custom properties, Python `unittest`, Chromium DevTools Protocol.

## Global Constraints

- Do not change gallery markup, captions, autoplay, swipe, lightbox, or navigation semantics.
- Defer measurement for hidden tab panels until visible.
- Recalculate only when carousel width changes.
- Preserve the existing mobile controls layout at widths up to 768px.

---

### Task 1: Stable desktop anchor

**Files:**
- Create: `tests/test_carousel_controls.py`
- Modify: `js/gallery.js`
- Modify: `css/style.css`

**Interfaces:**
- Consumes: existing `setupCarousel(carouselEl)` and `updateCarousel()` lifecycle.
- Produces: carousel CSS property `--gallery-controls-top` containing a pixel length.

- [ ] **Step 1: Write the failing source-contract test**

Assert that JavaScript records a width-sensitive anchor from the first slide, does not update it merely because the active slide changes, and that desktop CSS consumes the property while mobile CSS remains static.

- [ ] **Step 2: Run the test and verify RED**

Run: `python3 -m unittest -q tests.test_carousel_controls`

Expected: failure because `--gallery-controls-top` is absent.

- [ ] **Step 3: Implement the minimal stable-anchor behavior**

Add a measurement helper inside `setupCarousel` that:

```javascript
const width = carouselEl.getBoundingClientRect().width;
const firstHeight = slides[0].querySelector('.gallery-figure').getBoundingClientRect().height;
carouselEl.style.setProperty('--gallery-controls-top', `${Math.ceil(firstHeight / 2)}px`);
```

Guard zero-size hidden panels, retain the previous value across slide changes, and invalidate it only when width changes.

Update desktop controls to:

```css
top: var(--gallery-controls-top, 50%);
```

Keep the mobile rule `position: static; transform: none` unchanged.

- [ ] **Step 4: Verify GREEN and regressions**

Run:

```bash
python3 -m unittest discover -s tests -p 'test*.py' -q
python3 tools/acervo/audit_references.py --root . index.html es/index.html css/style.css
git diff --check
```

Expected: all tests pass, no legacy or missing references, no whitespace errors.

- [ ] **Step 5: Browser-coordinate verification**

Open a carousel containing slides of different heights in Chromium. Record the previous/next button `getBoundingClientRect().top`, navigate twice, and confirm both top coordinates remain unchanged. Repeat at 390px and confirm the controls remain in normal mobile flow with no horizontal overflow.

- [ ] **Step 6: Commit**

```bash
git add tests/test_carousel_controls.py js/gallery.js css/style.css docs/superpowers/plans/2026-08-25-stable-carousel-controls.md
git commit -m "fix: keep carousel controls vertically stable"
```
