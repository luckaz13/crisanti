# Universal Artwork Outline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every artwork image a one-pixel white inner outline and a restrained base shadow without affecting its dimensions or crop.

**Architecture:** Add one shared CSS rule for the four existing artwork-image surfaces: catalog cards, gallery carousels, Instagram artwork previews, and the lightbox. A negative outline offset keeps the line inside each image box so `overflow: hidden` containers do not clip it and layout dimensions remain unchanged.

**Tech Stack:** Static CSS, Chromium headless visual verification, shell assertions

## Global Constraints

- Use a white `1px` contour with no internal padding.
- Do not change image dimensions, aspect ratios, object fitting, or crop.
- Preserve existing hover and zoom transforms.
- Apply the treatment to `.obra-img`, `.gallery-img`, `.instagram-card img`, and `.lightbox-img` only.
- Do not affect artist portraits, editorial/literary imagery, icons, logos, backgrounds, or navigation.
- The shared stylesheet must produce the same treatment in Portuguese and Spanish pages.

---

### Task 1: Add the universal artwork treatment

**Files:**
- Modify: `css/style.css:665-670`

**Interfaces:**
- Consumes: the existing `.obra-img`, `.gallery-img`, `.instagram-card img`, and `.lightbox-img` selectors.
- Produces: a grouped artwork-surface rule using `outline`, `outline-offset`, and `box-shadow` without changing the box model.

- [ ] **Step 1: Verify the shared rule is absent**

Run:

```bash
rg -n -- '--artwork-outline|outline-offset: -1px' css/style.css
```

Expected: no matches and exit status 1.

- [ ] **Step 2: Add reusable artwork tokens and the grouped rule**

Insert immediately before `.obras { background: var(--c-bg-warm); }`:

```css
/* ── Universal artwork surface ────────────────────── */
:root {
  --artwork-outline: rgba(255, 255, 255, 0.96);
  --artwork-shadow: 0 5px 14px rgba(26, 23, 20, 0.1);
}

.obra-img,
.gallery-img,
.instagram-card img,
.lightbox-img {
  outline: 1px solid var(--artwork-outline);
  outline-offset: -1px;
  box-shadow: var(--artwork-shadow);
}
```

The negative offset is required: `.obra-img` and `.instagram-card img` fill ancestors with `overflow: hidden`, so an outside outline would be clipped.

- [ ] **Step 3: Run structural checks**

Run:

```bash
test "$(rg -c -- '--artwork-outline' css/style.css)" -eq 2
test "$(rg -c 'outline-offset: -1px' css/style.css)" -eq 1
rg -n -A12 'Universal artwork surface' css/style.css
git diff --check -- css/style.css
```

Expected: both count assertions and `git diff --check` exit 0; the displayed block contains exactly the four artwork selectors.

- [ ] **Step 4: Verify the Portuguese page visually**

Serve the worktree root and capture the sections containing the catalog grid, a series carousel, and Instagram previews at desktop and mobile widths. Open an artwork in the lightbox and check both normal and zoomed states.

Expected: the white line remains visible without changing the image crop; shadows are subtle; hover, carousel sizing, lightbox fit, and mobile containment remain unchanged.

- [ ] **Step 5: Verify the Spanish page visually**

Open `es/index.html` at desktop width and inspect at least one catalog image and one gallery image.

Expected: the same outline and shadow appear because both pages load `css/style.css`.

- [ ] **Step 6: Confirm excluded imagery is unchanged**

Compare the artist portrait, hero background, literature/modal imagery, header mark, and language/navigation controls against the page before this task.

Expected: none receives the universal outline or shadow.

- [ ] **Step 7: Commit the CSS change**

```bash
git add css/style.css
git commit -m "style: adiciona contorno sutil as obras"
```
