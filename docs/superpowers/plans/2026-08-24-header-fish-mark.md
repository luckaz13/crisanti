# Header Fish Mark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a compact, transparent fish mark beside “FC” in both language versions of the responsive header.

**Architecture:** Preserve the artist's JPEG and generate one cropped PNG derivative with alpha. Both HTML entry points render that decorative asset inside the existing `.nav-logo`; CSS sizes the brand pair and switches the monochrome mark between white and dark using the header's existing scrolled state.

**Tech Stack:** Static HTML, CSS, ImageMagick, shell verification

## Global Constraints

- Preserve `img/Peces/03.jpg` without alterations.
- Preserve the irregularity of the artist's original line work; do not redraw or vectorize it.
- Keep “FC” as the primary element and the fish as a discrete secondary signature.
- The fish must remain visible in desktop and mobile layouts and in both header states.
- The decorative image must use an empty `alt` attribute because the link already has an accessible name.

---

### Task 1: Create the transparent fish asset

**Files:**
- Read: `img/Peces/03.jpg`
- Create: `img/Peces/03-header-mark.png`

**Interfaces:**
- Consumes: the 1168×1120 JPEG supplied by the artist.
- Produces: `img/Peces/03-header-mark.png`, a tightly cropped PNG with alpha for both HTML entry points.

- [ ] **Step 1: Verify the derivative does not exist yet**

Run:

```bash
test ! -e img/Peces/03-header-mark.png
```

Expected: exit status 0.

- [ ] **Step 2: Generate a transparent, cropped derivative**

Run:

```bash
magick img/Peces/03.jpg -alpha on -fuzz 10% -transparent white -trim +repage img/Peces/03-header-mark.png
```

Expected: `img/Peces/03-header-mark.png` is created while `03.jpg` remains unchanged.

- [ ] **Step 3: Verify alpha and cropping**

Run:

```bash
magick identify -format '%f %[channels] %wx%h\n' img/Peces/03-header-mark.png
```

Expected: output contains an alpha channel such as `srgba`; dimensions are smaller than `1168x1120`.

- [ ] **Step 4: Inspect the resulting mark**

Open `img/Peces/03-header-mark.png` with the local image viewer and confirm that the background is transparent, the full fish remains present, and no conspicuous white halo surrounds the line.

- [ ] **Step 5: Commit the derived asset**

```bash
git add img/Peces/03-header-mark.png
git commit -m "feat: adiciona marca transparente do peixe"
```

### Task 2: Add the mark to both headers and style its states

**Files:**
- Modify: `index.html:37`
- Modify: `es/index.html:35`
- Modify: `css/style.css:205-220`
- Modify: `css/style.css:323-337`

**Interfaces:**
- Consumes: `img/Peces/03-header-mark.png` from Task 1 and the existing `.site-header.scrolled` state toggled by `js/main.js`.
- Produces: `.nav-logo-text` and `.nav-logo-mark` elements styled as one responsive brand link.

- [ ] **Step 1: Record failing structural checks**

Run:

```bash
rg -n 'nav-logo-mark' index.html es/index.html css/style.css
```

Expected: no matches and exit status 1.

- [ ] **Step 2: Update the Portuguese header markup**

Replace the existing `.nav-logo` link in `index.html` with:

```html
<a href="#hero" class="nav-logo" aria-label="Fabio Crisanti — início">
  <span class="nav-logo-text">FC</span>
  <img class="nav-logo-mark" src="img/Peces/03-header-mark.png" alt="" />
</a>
```

- [ ] **Step 3: Update the Spanish header markup**

Replace the existing `.nav-logo` link in `es/index.html` with:

```html
<a href="#hero" class="nav-logo" aria-label="Fabio Crisanti — inicio">
  <span class="nav-logo-text">FC</span>
  <img class="nav-logo-mark" src="../img/Peces/03-header-mark.png" alt="" />
</a>
```

- [ ] **Step 4: Add the brand-pair styles**

Extend the `.nav-logo` block in `css/style.css` and add the image rules immediately after it:

```css
.nav-logo {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--f-serif);
  font-size: 1.35rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  color: var(--c-ink);
  transition: color var(--dur) var(--ease);
}

.nav-logo-text {
  line-height: 1;
}

.nav-logo-mark {
  display: block;
  width: 1.8rem;
  height: auto;
  filter: none;
  transition: filter var(--dur) var(--ease);
}

.site-header:not(.scrolled) .nav-logo-mark {
  width: 2.45rem;
  filter: invert(1);
}
```

The `2.45rem` open-state width is approximately 39 px at the root font size; the compact state remains subordinate to the 1.35 rem “FC”.

- [ ] **Step 5: Add the mobile constraint**

Inside the existing `@media (max-width: 768px)` block, immediately after the open-state `.nav-logo` rule, add:

```css
  .site-header:not(.scrolled) .nav-logo-mark {
    width: clamp(2rem, 10vw, 2.45rem);
  }
```

- [ ] **Step 6: Run static checks**

Run:

```bash
rg -n 'nav-logo-mark' index.html es/index.html css/style.css
git diff --check -- index.html es/index.html css/style.css
```

Expected: two HTML image references and three CSS rule matches; `git diff --check` exits 0.

- [ ] **Step 7: Verify both responsive states manually**

Serve the repository root locally, open `index.html` and `es/index.html`, and check widths above and below 768 px. In each page confirm: the mark is white over the hero, dark after scrolling, aligned with “FC”, does not collide with navigation or the menu toggle, and the full brand link still returns to `#hero`.

- [ ] **Step 8: Commit the header integration**

```bash
git add index.html es/index.html css/style.css
git commit -m "feat: integra peixe ao monograma do cabecalho"
```
