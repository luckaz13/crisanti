# Incorporate La Fuente y los Simios Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the 25 existing La Fuente y los Simios JPEGs as a complete carousel in Portuguese and Spanish.

**Architecture:** Copy the JPEG source set from the untracked `/img` intake tree into the tracked gallery asset tree. Replace each language's empty panel with the existing carousel markup pattern, using identical ordered filenames and language-appropriate relative paths/ARIA labels.

**Tech Stack:** Static HTML, Git-tracked JPEG assets, existing vanilla-JavaScript carousel/lightbox, Python standard-library assertions

## Global Constraints

- Incorporate exactly 25 `.jpg` files; exclude `.pptx` and `.docx`.
- Preserve every source file under `/img` unchanged.
- Track copies under `images/galerias/Proyectos Especiales/La Fuente y los Simios/`.
- Keep La Fuente y los Simios as the default active project tab.
- Use `loading="lazy"` and `.gallery-img` on every image.
- PT paths start with `images/`; ES paths start with `../images/`.
- Reuse existing controls, carousel, outline/shadow, and lightbox behavior.

## Canonical slide order

| Index | Filename |
|---:|---|
| 0 | `01.jpg` |
| 1 | `11 (1).jpg` |
| 2 | `16 (3).jpg` |
| 3 | `17 (1).jpg` |
| 4 | `22.jpg` |
| 5 | `20260808_182618.jpg` |
| 6 | `20260808_182647.jpg` |
| 7 | `20260808_182734.jpg` |
| 8 | `20260808_182800.jpg` |
| 9 | `20260808_182836.jpg` |
| 10 | `20260808_182902.jpg` |
| 11 | `20260808_182922.jpg` |
| 12 | `20260808_182942.jpg` |
| 13 | `20260808_183012.jpg` |
| 14 | `20260808_183038.jpg` |
| 15 | `20260808_183102.jpg` |
| 16 | `20260808_183125.jpg` |
| 17 | `20260808_183146.jpg` |
| 18 | `20260808_183209.jpg` |
| 19 | `20260808_183228.jpg` |
| 20 | `20260808_183343.jpg` |
| 21 | `20260808_183409.jpg` |
| 22 | `20260808_183439.jpg` |
| 23 | `20260808_183506.jpg` |
| 24 | `20260808_183601.jpg` |

---

### Task 1: Copy and verify the publishable assets

**Files:**
- Read: `/home/lucas/Projetos/crisanti/img/Proyectos Especiales/La Fuente y los Simios/Exposición Virtual (La Fuente...)/*.jpg`
- Create: `images/galerias/Proyectos Especiales/La Fuente y los Simios/*.jpg`

**Interfaces:**
- Consumes: exactly 25 source JPEGs from the intake tree.
- Produces: a tracked gallery directory whose filenames are consumed verbatim by both HTML pages.

- [ ] **Step 1: Run the red regression check**

Run:

```bash
python3 - <<'PY'
import re
from pathlib import Path

for name in ('index.html', 'es/index.html'):
    html = Path(name).read_text()
    start = html.index('id="gallery-carousel-proyectos-especiales-la-fuente-y-los-simios"')
    end = html.index('<div class="gallery-carousel"', start + 1)
    panel = html[start:end]
    count = len(re.findall(r'class="gallery-img"', panel))
    print(f'{name}: {count} incorporated gallery images')
    assert count == 25
PY
```

Expected: FAIL because the current panel contains 0 images.

- [ ] **Step 2: Validate the source boundary**

Run:

```bash
source_dir="/home/lucas/Projetos/crisanti/img/Proyectos Especiales/La Fuente y los Simios/Exposición Virtual (La Fuente...)"
test "$(find "$source_dir" -maxdepth 1 -type f -iname '*.jpg' | wc -l)" -eq 25
```

Expected: exit status 0.

- [ ] **Step 3: Copy only JPEG assets**

Run:

```bash
source_dir="/home/lucas/Projetos/crisanti/img/Proyectos Especiales/La Fuente y los Simios/Exposición Virtual (La Fuente...)"
mkdir -p "images/galerias/Proyectos Especiales/La Fuente y los Simios"
find "$source_dir" -maxdepth 1 -type f -iname '*.jpg' -exec cp -t "images/galerias/Proyectos Especiales/La Fuente y los Simios" -- {} +
```

Expected: 25 copied JPEGs; source files remain present.

- [ ] **Step 4: Verify exact destination filenames and source preservation**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

source = Path('/home/lucas/Projetos/crisanti/img/Proyectos Especiales/La Fuente y los Simios/Exposición Virtual (La Fuente...)')
dest = Path('images/galerias/Proyectos Especiales/La Fuente y los Simios')
expected = {
    '01.jpg', '11 (1).jpg', '16 (3).jpg', '17 (1).jpg', '22.jpg',
    '20260808_182618.jpg', '20260808_182647.jpg', '20260808_182734.jpg',
    '20260808_182800.jpg', '20260808_182836.jpg', '20260808_182902.jpg',
    '20260808_182922.jpg', '20260808_182942.jpg', '20260808_183012.jpg',
    '20260808_183038.jpg', '20260808_183102.jpg', '20260808_183125.jpg',
    '20260808_183146.jpg', '20260808_183209.jpg', '20260808_183228.jpg',
    '20260808_183343.jpg', '20260808_183409.jpg', '20260808_183439.jpg',
    '20260808_183506.jpg', '20260808_183601.jpg',
}
actual = {p.name for p in dest.glob('*.jpg')}
assert actual == expected, (actual - expected, expected - actual)
for name in expected:
    assert (source / name).read_bytes() == (dest / name).read_bytes(), name
print('asset copies: PASS')
PY
```

Expected: 25 exact filename matches and 25 identical file pairs.

- [ ] **Step 5: Commit the assets**

```bash
git add "images/galerias/Proyectos Especiales/La Fuente y los Simios"
git commit -m "assets: add la fuente y los simios gallery"
```

### Task 2: Replace both placeholders with 25-slide carousels

**Files:**
- Modify: `index.html:3728-3730`
- Modify: `es/index.html:3739-3741`

**Interfaces:**
- Consumes: the canonical ordered filename list and tracked asset directory from Task 1.
- Produces: 25 `.gallery-slide` elements inside each existing `gallery-carousel-proyectos-especiales-la-fuente-y-los-simios` panel.

- [ ] **Step 1: Replace the Portuguese placeholder**

Inside the existing panel, replace:

```html
<p class="gallery-empty">Galeria em preparação.</p>
```

with the standard structure:

```html
<div class="gallery-controls">
  <button class="gallery-btn gallery-btn--prev" aria-label="Imagem anterior">
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
  </button>
  <button class="gallery-btn gallery-btn--next" aria-label="Próxima imagem">
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
  </button>
</div>
<div class="gallery-viewport">
  <div class="gallery-track">
  </div>
</div>
```

For each canonical row, emit exactly:

```html
<div class="gallery-slide" data-index="0">
  <figure class="gallery-figure">
    <img src="images/galerias/Proyectos Especiales/La Fuente y los Simios/01.jpg" alt="Proyectos Especiales — La Fuente y los Simios — Fabio Crisanti" class="gallery-img" loading="lazy" />
  </figure>
</div>
```

Increment `data-index` from 0 through 24 and substitute the exact filename from the corresponding canonical row. Do not URL-encode spaces in static HTML paths.

- [ ] **Step 2: Replace the Spanish placeholder**

Use the same 25 rows and structure, changing only:

- previous label to `Imagen anterior`;
- next label to `Siguiente imagen`;
- each image path prefix to `../images/`;
- placeholder text removed is `Galería en preparación.`.

- [ ] **Step 3: Run the green regression and path checks**

Run:

```bash
python3 - <<'PY'
import re
from pathlib import Path

root = Path('.')
for name, prefix in (('index.html', ''), ('es/index.html', '../')):
    html = Path(name).read_text()
    start = html.index('id="gallery-carousel-proyectos-especiales-la-fuente-y-los-simios"')
    end = html.index('<div class="gallery-carousel"', start + 1)
    panel = html[start:end]
    paths = re.findall(r'<img src="([^"]+)"[^>]+class="gallery-img"', panel)
    assert len(paths) == 25, (name, len(paths))
    for src in paths:
        disk_path = root / (src[3:] if src.startswith('../') else src)
        assert disk_path.is_file(), (name, src)
    assert 'gallery-empty' not in panel
    assert '.pptx' not in panel and '.docx' not in panel
print('la fuente panels: PASS')
PY
git diff --check HEAD
```

Expected: `la fuente panels: PASS` and no whitespace errors.

- [ ] **Step 4: Verify browser behavior**

In both languages, confirm 25 slides, next/previous navigation, lazy-loaded images, and lightbox opening. Confirm Master Taxi and Vlak tabs still switch normally.

- [ ] **Step 5: Commit the HTML integration**

```bash
git add index.html es/index.html
git commit -m "content: publish la fuente y los simios gallery"
```
