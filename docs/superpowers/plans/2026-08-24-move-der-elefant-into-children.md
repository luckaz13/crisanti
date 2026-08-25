# Move Der Elefant Into Children Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the “Der Elefant” tab inside As Crianças / Los Niños reveal the complete 66-image gallery and curatorial text, then remove the old standalone section.

**Architecture:** Reuse the existing Los Niños tab-panel contract and the existing Der Elefant carousel markup. The destination panel itself remains the `.gallery-carousel`; it receives a compact curatorial intro followed by the existing controls, viewport, track, and 66 slides, avoiding nested carousels and duplicate IDs.

**Tech Stack:** Static HTML, CSS, existing vanilla-JavaScript gallery tabs/carousel/lightbox, Python standard-library structural assertions

## Global Constraints

- Portuguese section title is “As Crianças”; Spanish remains “Los Niños”.
- The tab label is exactly “Der Elefant”, without `↗`.
- Keep Cósimo as the default active tab.
- Preserve all 66 Der Elefant images, their order, paths, lazy loading, and lightbox behavior.
- Do not move, duplicate, rename, or delete image files.
- Remove the standalone `<section id="der-elefant">` from both pages.
- Preserve one `id="der-elefant"` anchor inside the new panel.
- Keep the existing consultation action at the parent As Crianças / Los Niños level; do not duplicate it inside the tab.

---

### Task 1: Move the Portuguese Der Elefant gallery into As Crianças

**Files:**
- Modify: `index.html:1212-1571`
- Modify: `index.html:3537-3580`

**Interfaces:**
- Consumes: the standalone `#der-elefant` section and the placeholder panel `#gallery-carousel-los-ninos-der-elefant`.
- Produces: one tab panel with `data-gallery-group="los-ninos"`, one nested anchor `#der-elefant`, curatorial copy, controls, viewport, and 66 slides.

- [ ] **Step 1: Record the Portuguese pre-move contract**

Run:

```bash
test "$(rg -o 'id="der-elefant"' index.html | wc -l)" -eq 1
test "$(rg -o 'images/highres/Der Elefant/' index.html | wc -l)" -eq 66
rg -n 'data-target="los-ninos-der-elefant">Der Elefant ↗|Ver galeria completa de Der Elefant' index.html
```

Expected: one standalone anchor, 66 image references, and both placeholder-link matches.

- [ ] **Step 2: Remove the standalone Portuguese section wrapper and duplicate presentation**

Delete the complete block beginning with:

```html
<section class="section series" id="der-elefant">
```

and ending at its matching `</section>`. Preserve the curatorial paragraphs and the complete inner carousel markup for insertion in Step 4; do not alter any slide or image path.

- [ ] **Step 3: Normalize the Portuguese tab label**

Replace:

```html
<button class="gallery-tab" role="tab" aria-selected="false" data-target="los-ninos-der-elefant">Der Elefant ↗</button>
```

with:

```html
<button class="gallery-tab" role="tab" aria-selected="false" data-target="los-ninos-der-elefant">Der Elefant</button>
```

- [ ] **Step 4: Replace the Portuguese placeholder panel with the full gallery**

Keep the destination opening tag exactly:

```html
<div class="gallery-carousel" id="gallery-carousel-los-ninos-der-elefant" role="tabpanel" data-gallery-group="los-ninos" hidden>
```

Replace `.existing-gallery-link` with:

```html
<div class="tabbed-series-intro" id="der-elefant">
  <h3>Der Elefant</h3>
  <p>Na série <em lang="de">Der Elefant</em>, o artista explora a relação entre memória e figuração, trabalhando com técnicas mistas sobre papel de seda e superfícies industriais.</p>
  <p>Todas as imagens são apresentadas em alta resolução, permitindo apreciar os detalhes e as texturas características da técnica do artista.</p>
</div>
```

Immediately after the intro, insert the existing Der Elefant `.gallery-controls`, `.gallery-viewport`, `.gallery-track`, and all 66 `.gallery-slide` elements. Remove the obsolete standalone control IDs `gallery-prev-der-elefant` and `gallery-next-der-elefant`; carousel initialization uses classes and the destination panel identity.

- [ ] **Step 5: Verify Portuguese structure and image preservation**

Run:

```bash
test "$(rg -o 'id="der-elefant"' index.html | wc -l)" -eq 1
test "$(rg -o 'images/highres/Der Elefant/' index.html | wc -l)" -eq 66
test "$(rg -o 'id="gallery-carousel-los-ninos-der-elefant"' index.html | wc -l)" -eq 1
! rg -n '<section class="section series" id="der-elefant"|Der Elefant ↗|existing-gallery-link' index.html
```

Expected: every assertion exits 0 and the negative search returns no match.

### Task 2: Apply the equivalent move to Spanish

**Files:**
- Modify: `es/index.html:1215-1575`
- Modify: `es/index.html:3547-3591`

**Interfaces:**
- Consumes: Spanish standalone `#der-elefant` section and its Los Niños placeholder panel.
- Produces: the same 66-slide panel contract with Spanish curatorial copy.

- [ ] **Step 1: Record the Spanish pre-move contract**

Run:

```bash
test "$(rg -o 'id="der-elefant"' es/index.html | wc -l)" -eq 1
test "$(rg -o '../images/highres/Der Elefant/' es/index.html | wc -l)" -eq 66
```

Expected: both assertions exit 0.

- [ ] **Step 2: Remove the standalone Spanish section and normalize the tab**

Delete the complete `<section class="section series" id="der-elefant">…</section>` block. Change the Los Niños tab label from `Der Elefant ↗` to `Der Elefant`.

- [ ] **Step 3: Replace the Spanish placeholder with the full gallery**

Use the same destination panel contract as Portuguese. Its intro must be:

```html
<div class="tabbed-series-intro" id="der-elefant">
  <h3>Der Elefant</h3>
  <p>En la serie <em lang="de">Der Elefant</em>, el artista explora la relación entre memoria y figuración, trabajando con técnicas mixtas sobre papel de seda y superficies industriales.</p>
  <p>Todas las imágenes se presentan en alta resolución, permitiendo apreciar los detalles y texturas características de la técnica del artista.</p>
</div>
```

Insert the existing Spanish controls, viewport, track, and all 66 slides after the intro. Preserve every `../images/highres/Der Elefant/` path and remove obsolete standalone control IDs.

- [ ] **Step 4: Verify Spanish structure and image preservation**

Run:

```bash
test "$(rg -o 'id="der-elefant"' es/index.html | wc -l)" -eq 1
test "$(rg -o '../images/highres/Der Elefant/' es/index.html | wc -l)" -eq 66
test "$(rg -o 'id="gallery-carousel-los-ninos-der-elefant"' es/index.html | wc -l)" -eq 1
! rg -n '<section class="section series" id="der-elefant"|Der Elefant ↗|existing-gallery-link' es/index.html
```

Expected: every assertion exits 0 and the negative search returns no match.

### Task 3: Style and verify the integrated gallery

**Files:**
- Modify: `css/style.css:1960-1985`
- Test: `index.html`
- Test: `es/index.html`

**Interfaces:**
- Consumes: `.tabbed-series-intro` added in Tasks 1 and 2.
- Produces: a compact intro that fits inside a tab panel without changing carousel dimensions.

- [ ] **Step 1: Verify the intro style is absent**

Run:

```bash
rg -n 'tabbed-series-intro' css/style.css
```

Expected: no matches and exit status 1.

- [ ] **Step 2: Add compact intro styling**

Add immediately after `.existing-gallery-link p`:

```css
.tabbed-series-intro {
  max-width: 68ch;
  margin: 0 auto var(--sp-md);
  text-align: center;
}

.tabbed-series-intro h3 {
  margin-bottom: var(--sp-xs);
  font-family: var(--f-serif);
  font-size: clamp(1.35rem, 3vw, 2rem);
  font-weight: 400;
}

.tabbed-series-intro p {
  margin-bottom: var(--sp-xs);
  color: var(--c-ink-mid);
}
```

- [ ] **Step 3: Verify all tab/panel contracts**

Run:

```bash
python3 - <<'PY'
import re
from pathlib import Path

for name in ('index.html', 'es/index.html'):
    html = Path(name).read_text()
    anchor = html.index('data-target="los-ninos-cosimo"')
    start = html.rfind('<section', 0, anchor)
    end = html.index('</section>', start)
    section = html[start:end]
    tabs = set(re.findall(r'data-target="(los-ninos-[^"]+)"', section))
    panels = set(re.findall(r'id="gallery-carousel-(los-ninos-[^"]+)"', section))
    assert tabs == panels and len(tabs) == 4, (name, tabs ^ panels)
    assert section.count('images/highres/Der Elefant/') == 66
print('children tab/panel contract: PASS')
PY
git diff --check HEAD
```

Expected: `children tab/panel contract: PASS` and no whitespace errors.

- [ ] **Step 4: Verify interaction in the local server**

In PT and ES, open As Crianças / Los Niños, click “Der Elefant”, and confirm: intro and gallery appear inline; previous/next controls work; images open in the lightbox; Cósimo remains the default after reload; mobile layout contains the intro and controls; direct `#der-elefant` navigation reaches the integrated panel area.

- [ ] **Step 5: Confirm assets are untouched and commit**

Run:

```bash
git diff --name-only HEAD -- images/highres/Der\ Elefant
```

Expected: no output.

Then:

```bash
git add index.html es/index.html css/style.css
git commit -m "content: move der elefant into children gallery"
```
