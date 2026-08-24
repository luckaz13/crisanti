# Simplify Instagram Section Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the generated Instagram image carousel with a restrained, localized profile call-to-action featuring a linked handle and an Instagram icon button.

**Architecture:** Convert both Instagram sections to static semantic markup and remove the JavaScript paths and CSS rules used only by generated Instagram cards. Preserve the section anchor and all Instagram links elsewhere, while retaining the existing gallery/lightbox system for artwork.

**Tech Stack:** Static HTML, CSS, vanilla JavaScript, inline SVG, Python standard-library assertions, Chromium headless

## Global Constraints

- Preserve `section#instagram` in PT-BR and Spanish.
- Remove `#instagram-grid`, `.instagram-card`, and the local Instagram preview behavior.
- Link both the handle and button to `https://www.instagram.com/fabio.crisanti.artes.plasticas/`.
- Open both links in a new tab with `rel="noopener"`.
- Keep exactly one `Ver Instagram` button in each Instagram section.
- Add an inline decorative Instagram SVG to the button with `aria-hidden="true"`.
- Preserve Instagram links in the header, contact section, and footer.
- Do not delete local gallery data or image assets.
- Preserve all artwork gallery and lightbox behavior.

---

### Task 1: Replace both carousel containers with static profile CTAs

**Files:**
- Modify: `index.html` inside `section#instagram`
- Modify: `es/index.html` inside `section#instagram`

**Interfaces:**
- Consumes: existing `.instagram-feed`, `.section-header`, `.section-title`, `.section-desc`, `.instagram-actions`, and `.btn-outline` styles.
- Produces: `.instagram-handle` links and `.instagram-button` links; no `#instagram-grid` element.

- [ ] **Step 1: Run the red markup regression check**

```bash
python3 - <<'PY'
from pathlib import Path
for page in ('index.html', 'es/index.html'):
    html = Path(page).read_text()
    start = html.index('<section class="section instagram-feed" id="instagram">')
    end = html.index('</section>', start) + len('</section>')
    section = html[start:end]
    assert 'id="instagram-grid"' not in section, page
    assert 'class="instagram-handle"' in section, page
    assert 'class="instagram-button btn-outline"' in section, page
PY
```

Expected: FAIL because the grid exists and the new links do not.

- [ ] **Step 2: Implement the Portuguese static section**

Replace the title content with a link:

```html
<h2 class="section-title">
  <a class="instagram-handle" href="https://www.instagram.com/fabio.crisanti.artes.plasticas/" target="_blank" rel="noopener">@fabio.crisanti.artes.plasticas</a>
</h2>
```

Set the description to `Acompanhe novos trabalhos, processos e registros do artista no Instagram.` Remove the `#instagram-grid` element. Add `instagram-button` to the existing button and place an inline 24×24 outline SVG before `Ver Instagram`, using the standard Instagram rounded-square, circle, and corner-dot shapes, `fill="none"`, `stroke="currentColor"`, and `aria-hidden="true"`.

- [ ] **Step 3: Implement the equivalent Spanish section**

Use the same link, button, and SVG structure. Set the description to `Sigue nuevos trabajos, procesos y registros del artista en Instagram.`

- [ ] **Step 4: Run the green markup and accessibility check**

```bash
python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path

profile = 'https://www.instagram.com/fabio.crisanti.artes.plasticas/'
for page in ('index.html', 'es/index.html'):
    html = Path(page).read_text()
    start = html.index('<section class="section instagram-feed" id="instagram">')
    end = html.index('</section>', start) + len('</section>')
    section = html[start:end]
    assert 'instagram-grid' not in section
    assert section.count(profile) == 2
    assert section.count('target="_blank"') == 2
    assert section.count('rel="noopener"') == 2
    assert section.count('>Ver Instagram') == 1
    assert 'class="instagram-handle"' in section
    assert 'class="instagram-button btn-outline"' in section
    assert '<svg' in section and 'aria-hidden="true"' in section
print('static Instagram sections: PASS')
PY
git diff --check
```

Expected: `static Instagram sections: PASS` and no diff errors.

### Task 2: Remove carousel-only JavaScript and CSS

**Files:**
- Modify: `js/gallery.js:220-245`
- Modify: `js/main.js:145-152,195-205,247,257`
- Modify: `css/style.css:1057-1112,1380-1396`

**Interfaces:**
- Consumes: the absence of `#instagram-grid` and `.instagram-card` from Task 1.
- Produces: no active-code dependency on the removed carousel; artwork lightbox remains driven by `.obra-img` and `.gallery-img`.

- [ ] **Step 1: Run the red dead-code check**

```bash
python3 - <<'PY'
from pathlib import Path
active = '\n'.join(Path(p).read_text() for p in ('js/gallery.js', 'js/main.js', 'css/style.css'))
for token in ('instagram-grid', 'instagram-card', 'getInstagramItems', 'data-ig-card'):
    assert token not in active, token
PY
```

Expected: FAIL on the old carousel tokens.

- [ ] **Step 2: Remove the Instagram preview generator**

Delete the complete `Instagram preview from local exported Instagram gallery data` block from `js/gallery.js`, beginning with `const instagramGrid` and ending after `instagramGrid.appendChild(fragment)`.

- [ ] **Step 3: Remove Instagram lightbox and reveal hooks**

From `js/main.js`, delete `getInstagramItems`, the delegated `igCard` click branch, and the `.instagram-card` entries in `toReveal` and `delayMap`. Do not change the `.obra-img` or `.gallery-img` branches.

- [ ] **Step 4: Replace carousel CSS with CTA-only styles**

Remove `.instagram-grid`, `.instagram-card`, their image/caption/hover rules, their responsive grid queries, and the later responsive `.instagram-card` overrides. Retain `.instagram-feed` and `.instagram-actions`. Add:

- `.instagram-handle` with inherited color, a fine underline using `text-decoration-thickness`, and a visible `:focus-visible` outline;
- `.instagram-button svg` with fixed `1.1rem` dimensions and `flex: 0 0 auto`.

- [ ] **Step 5: Run the green dead-code and structural check**

```bash
python3 - <<'PY'
from pathlib import Path
active = '\n'.join(Path(p).read_text() for p in ('index.html', 'es/index.html', 'js/gallery.js', 'js/main.js', 'css/style.css'))
for token in ('instagram-grid', 'instagram-card', 'getInstagramItems', 'data-ig-card'):
    assert token not in active, token
css = Path('css/style.css').read_text()
assert '.instagram-handle' in css
assert '.instagram-button svg' in css
main = Path('js/main.js').read_text()
assert "const galleryImg = e.target.closest('.gallery-img')" in main
assert "const obraImg = e.target.closest('.obra-img')" in main
print('carousel code removed; gallery lightbox retained: PASS')
PY
git diff --check
```

Expected: `carousel code removed; gallery lightbox retained: PASS` and no diff errors.

### Task 3: Browser regression and commit

**Files:**
- Verify: `index.html`, `es/index.html`, `css/style.css`, `js/main.js`, `js/gallery.js`

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: verified static CTA in both locales with unaffected artwork galleries.

- [ ] **Step 1: Test PT and ES in Chromium**

Using the local server, open PT and ES and assert that each Instagram section contains one linked handle, one button, one decorative SVG, and no images or grid. Verify both links have the exact profile URL, `_blank`, and `noopener`. Click an artwork `.gallery-img` and confirm the existing lightbox opens.

- [ ] **Step 2: Test responsive layout**

At 390 px wide, assert the Instagram section has no horizontal overflow, the handle wraps within its container if necessary, and the button remains visible and centered.

- [ ] **Step 3: Commit the implementation**

```bash
git add index.html es/index.html css/style.css js/main.js js/gallery.js
git diff --cached --check
git commit -m "feat: simplify Instagram section"
```

- [ ] **Step 4: Run final verification from the committed state**

Re-run the green checks from Tasks 1 and 2, repeat the Chromium assertions, run `git diff --check HEAD`, and inspect `git status --short`.

Expected: all assertions pass; status shows only the pre-existing untracked `img/Peces/03.jpg`.

