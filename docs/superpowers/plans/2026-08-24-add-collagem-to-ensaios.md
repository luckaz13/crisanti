# Add Collagem to Ensaios Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the three Collagem works as the first and initially active carousel in Ensaios, with artist-provided captions in Portuguese and Spanish.

**Architecture:** Copy the three approved JPEGs from the untracked intake tree into the tracked gallery asset tree. Add one standard carousel panel and one first-position tab to each localized static page, reusing existing carousel, caption, lightbox, outline, and shadow behavior.

**Tech Stack:** Static HTML, existing vanilla-JavaScript tabs/carousel/lightbox, Git-tracked JPEGs, Python standard-library assertions, Chromium headless

## Global Constraints

- Publish exactly `01.jpg`, `02.jpg`, and `03.jpg` from `/img/Ensayos/Collagem`.
- Do not publish or link `Ficha Ensayos Collage.docx`.
- Preserve all source files under `/img` unchanged.
- Track public copies under `images/galerias/Ensayos/Collagem/`.
- Place `Collagem` before `Crema` and make it the sole initially active Ensaios tab/panel.
- Use titles `Collage I`, `Collage II`, and `Collage III`.
- Use years `1998`, `1998`, and `1999`, respectively.
- Use support `Papel fotográfico` for all three works in both languages.
- Use PT paths beginning `images/` and ES paths beginning `../images/`.
- Reuse existing `.gallery-caption`, `.gallery-title`, and `.gallery-meta` styles.

---

### Task 1: Publish the three Collagem JPEGs

**Files:**
- Read: `/home/lucas/Projetos/crisanti/img/Ensayos/Collagem/{01,02,03}.jpg`
- Create: `images/galerias/Ensayos/Collagem/{01,02,03}.jpg`

**Interfaces:**
- Consumes: three explicit source JPEGs.
- Produces: stable public paths consumed by both localized pages.

- [ ] **Step 1: Run the red asset test**

```bash
python3 - <<'PY'
from pathlib import Path
dest = Path('images/galerias/Ensayos/Collagem')
assert {p.name for p in dest.glob('*.jpg')} == {'01.jpg', '02.jpg', '03.jpg'}
PY
```

Expected: FAIL because the public folder does not exist.

- [ ] **Step 2: Copy the three explicitly named JPEGs**

Create the destination directory and copy `01.jpg`, `02.jpg`, and `03.jpg` individually. Do not use a wildcard that could include the DOCX or future assets.

- [ ] **Step 3: Verify the public boundary and byte identity**

```bash
python3 - <<'PY'
from pathlib import Path
source = Path('/home/lucas/Projetos/crisanti/img/Ensayos/Collagem')
dest = Path('images/galerias/Ensayos/Collagem')
actual = {p.name for p in dest.iterdir() if p.is_file()}
assert actual == {'01.jpg', '02.jpg', '03.jpg'}, actual
for name in actual:
    assert (source / name).read_bytes() == (dest / name).read_bytes(), name
assert (source / 'Ficha Ensayos Collage.docx').is_file()
print('Collagem assets: PASS')
PY
```

Expected: `Collagem assets: PASS`.

- [ ] **Step 4: Commit the assets**

```bash
git add images/galerias/Ensayos/Collagem
git commit -m "assets: add Collagem works"
```

### Task 2: Add the first-position localized Collagem carousel

**Files:**
- Modify: `index.html` in the Ensaios tablist and before `gallery-carousel-ensayos-crema`
- Modify: `es/index.html` in the equivalent locations

**Interfaces:**
- Consumes: Task 1 JPEG paths and the existing `data-target`/panel ID convention.
- Produces: active tab `data-target="ensayos-collagem"` and panel `id="gallery-carousel-ensayos-collagem"` with three ordered slides.

- [ ] **Step 1: Run the red localized markup test**

```bash
python3 - <<'PY'
from pathlib import Path
for page in ('index.html', 'es/index.html'):
    html = Path(page).read_text()
    assert html.count('data-target="ensayos-collagem"') == 1, page
    assert html.count('id="gallery-carousel-ensayos-collagem"') == 1, page
PY
```

Expected: FAIL because the new tab and panel do not exist.

- [ ] **Step 2: Update the tablists**

Insert before Crema:

```html
<button class="gallery-tab active" role="tab" aria-selected="true" data-target="ensayos-collagem">Collagem</button>
```

Change the existing Crema button in each language from `class="gallery-tab active" aria-selected="true"` to `class="gallery-tab" aria-selected="false"`. Leave all later tabs unchanged.

- [ ] **Step 3: Add the Portuguese panel**

Insert before the Crema panel a visible standard carousel with previous/next labels `Imagem anterior` and `Próxima imagem`. Add three slides with `data-index` 0–2. Each figure uses:

```html
<img src="images/galerias/Ensayos/Collagem/01.jpg" alt="Collage I — 1998 — Papel fotográfico — Fabio Crisanti" class="gallery-img" loading="lazy" />
<figcaption class="gallery-caption">
  <h3 class="gallery-title">Collage I</h3>
  <p class="gallery-meta">1998 · Papel fotográfico</p>
</figcaption>
```

Repeat with `02.jpg` / `Collage II` / `1998` and `03.jpg` / `Collage III` / `1999`. Add `hidden` to the existing Crema panel.

- [ ] **Step 4: Add the Spanish panel**

Use the same markup and metadata with paths prefixed `../images/` and controls labeled `Imagen anterior` and `Siguiente imagen`. Add `hidden` to the existing Spanish Crema panel.

- [ ] **Step 5: Verify exact order, state, captions, and paths**

```bash
python3 - <<'PY'
from pathlib import Path
expected = [
    ('01.jpg', 'Collage I', '1998'),
    ('02.jpg', 'Collage II', '1998'),
    ('03.jpg', 'Collage III', '1999'),
]
for page in ('index.html', 'es/index.html'):
    html = Path(page).read_text()
    tablist = html[html.index('<div class="gallery-tabs"', html.index('id="ensaios"')):]
    assert tablist.index('data-target="ensayos-collagem"') < tablist.index('data-target="ensayos-crema"')
    assert 'class="gallery-tab active" role="tab" aria-selected="true" data-target="ensayos-collagem"' in tablist
    start = html.index('id="gallery-carousel-ensayos-collagem"')
    end = html.index('id="gallery-carousel-ensayos-crema"', start)
    panel = html[start:end]
    assert panel.count('class="gallery-slide"') == 3
    assert panel.count('Papel fotográfico') == 6
    for filename, title, year in expected:
        assert filename in panel and title in panel and year in panel
    crema = html[html.index('id="gallery-carousel-ensayos-crema"'):]
    assert crema.split('>', 1)[0].endswith(' hidden')
print('Collagem markup: PASS')
PY
git diff --check
```

Expected: `Collagem markup: PASS` and no diff errors.

- [ ] **Step 6: Test browser behavior and assets**

With the local server and Chromium headless, verify PT and ES initially show Collagem with three slides, switch to Crema and back, advance to Collage II, and open the lightbox. Confirm the lightbox counter is `1 / 3` on the first image and navigation remains within the three Collagem works. Request all three JPEG paths and expect HTTP 200. At 390 px, assert no horizontal page overflow.

- [ ] **Step 7: Commit and re-verify**

```bash
git add index.html es/index.html
git diff --cached --check
git commit -m "content: add Collagem to Ensaios"
```

Re-run the green asset, markup, HTTP, browser, and responsive checks from the committed state. Expected repository status: only the pre-existing untracked `img/Peces/03.jpg`.

