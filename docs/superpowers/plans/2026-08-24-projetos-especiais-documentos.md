# Special Project Documents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish two PowerPoint presentations for La Fuente y los Simios and two DOCX files for Master Taxi, each with separate online-view and download actions in Portuguese and Spanish.

**Architecture:** Copy the four source documents into a tracked public `documents/proyectos-especiales` tree, preserving the originals. Add a reusable static document-card pattern to the two relevant tab panels, with direct relative download links and Google Viewer links built from URL-encoded absolute GitHub Pages URLs; style the pattern in the shared stylesheet.

**Tech Stack:** Static HTML, CSS, GitHub Pages assets, Google Docs Viewer, Python standard-library regression checks, Chromium headless interaction checks

## Global Constraints

- Publish exactly two `.pptx` files for La Fuente y los Simios and exactly two `.docx` files for Master Taxi.
- Do not publish the two Vlak `.docx` files.
- Preserve all source files under `/img` unchanged.
- Provide two distinct actions for every file: online viewing and original-file download.
- Use `https://luckaz13.github.io/crisanti/` as the public URL base passed to Google Viewer.
- PT download paths start with `documents/`; ES download paths start with `../documents/`.
- Open online viewers in a new tab with `target="_blank"` and `rel="noopener"`.
- Retain the original `.pptx` and `.docx` formats; do not convert files to PDF.
- Keep the document layout responsive, keyboard accessible, and consistent with the existing editorial interface.

---

### Task 1: Publish and verify the four document assets

**Files:**
- Read: `/home/lucas/Projetos/crisanti/img/Proyectos Especiales/La Fuente y los Simios/*.pptx`
- Read: `/home/lucas/Projetos/crisanti/img/Proyectos Especiales/Master Taxi/*.docx`
- Create: `documents/proyectos-especiales/la-fuente-y-los-simios/*.pptx`
- Create: `documents/proyectos-especiales/master-taxi/*.docx`

**Interfaces:**
- Consumes: the four original Office files in the intake tree.
- Produces: stable public asset paths consumed verbatim by both HTML pages and by the Google Viewer URLs.

- [ ] **Step 1: Run the red asset-boundary check**

```bash
python3 - <<'PY'
from pathlib import Path

root = Path('documents/proyectos-especiales')
expected = {
    root / 'la-fuente-y-los-simios' / 'Apresentação Captação 2024-12-13.pptx',
    root / 'la-fuente-y-los-simios' / 'Maquete La Fuente y los Simios.pptx',
    root / 'master-taxi' / 'Master Taxi Dinámica.docx',
    root / 'master-taxi' / 'Master Taxi Sinópsis.docx',
}
assert all(path.is_file() for path in expected)
PY
```

Expected: FAIL because the public copies do not exist.

- [ ] **Step 2: Copy only the approved source files**

Use `mkdir -p` for the two exact destination directories and `cp` each of the four explicitly named source files. Do not use a wildcard that could include Vlak or future documents.

- [ ] **Step 3: Verify exact filenames, extensions, and byte identity**

```bash
python3 - <<'PY'
from pathlib import Path

source = Path('/home/lucas/Projetos/crisanti/img/Proyectos Especiales')
dest = Path('documents/proyectos-especiales')
pairs = {
    source / 'La Fuente y los Simios' / 'Apresentação Captação 2024-12-13.pptx': dest / 'la-fuente-y-los-simios' / 'Apresentação Captação 2024-12-13.pptx',
    source / 'La Fuente y los Simios' / 'Maquete La Fuente y los Simios.pptx': dest / 'la-fuente-y-los-simios' / 'Maquete La Fuente y los Simios.pptx',
    source / 'Master Taxi' / 'Master Taxi Dinámica.docx': dest / 'master-taxi' / 'Master Taxi Dinámica.docx',
    source / 'Master Taxi' / 'Master Taxi Sinópsis.docx': dest / 'master-taxi' / 'Master Taxi Sinópsis.docx',
}
actual = {p for p in dest.rglob('*') if p.is_file()}
assert actual == set(pairs.values()), actual
for original, public in pairs.items():
    assert original.read_bytes() == public.read_bytes(), public
assert not any('vlak' in str(path).lower() for path in actual)
print('document assets: PASS')
PY
```

Expected: `document assets: PASS`.

- [ ] **Step 4: Commit the assets**

```bash
git add documents/proyectos-especiales
git commit -m "assets: publish special project documents"
```

### Task 2: Add the shared document-card presentation

**Files:**
- Modify: `css/style.css` near `.tabbed-series-intro` and `.gallery-empty`

**Interfaces:**
- Consumes: semantic `.project-documents`, `.project-document`, `.project-document__meta`, and `.project-document__actions` markup.
- Produces: a responsive two-column card grid with visible focus states and button treatments shared by PT and ES.

- [ ] **Step 1: Add the CSS contract check**

```bash
python3 - <<'PY'
from pathlib import Path
css = Path('css/style.css').read_text()
for selector in ('.project-documents', '.project-document', '.project-document__meta', '.project-document__actions'):
    assert selector in css, selector
PY
```

Expected: FAIL because the selectors do not exist.

- [ ] **Step 2: Implement the shared styles**

Add styles that:

- place `.project-documents__list` in a two-column CSS grid with a restrained gap;
- give `.project-document` a thin translucent border, subtle background, and editorial spacing without a heavy shadow;
- render the title and file type in `.project-document__meta` with the existing font variables/colors;
- render `.project-document__actions` as wrapping inline actions;
- reuse the visual language of `.btn-outline`, while adding only sizing/layout rules scoped under `.project-document__actions`;
- collapse the grid to one column in the existing narrow-screen media query;
- preserve a clearly visible `:focus-visible` outline.

- [ ] **Step 3: Re-run the CSS contract and syntax checks**

```bash
python3 - <<'PY'
from pathlib import Path
css = Path('css/style.css').read_text()
for selector in ('.project-documents', '.project-documents__list', '.project-document', '.project-document__meta', '.project-document__actions'):
    assert selector in css, selector
assert css.count('{') == css.count('}')
print('document styles: PASS')
PY
git diff --check
```

Expected: `document styles: PASS` and no diff errors.

### Task 3: Add localized document cards and links

**Files:**
- Modify: `index.html` inside `gallery-carousel-proyectos-especiales-la-fuente-y-los-simios`
- Modify: `index.html` inside `gallery-carousel-proyectos-especiales-master-taxi`
- Modify: `es/index.html` inside the same two panel IDs

**Interfaces:**
- Consumes: the four public files from Task 1 and CSS classes from Task 2.
- Produces: two `.project-document` cards per selected panel, each with one `.project-document__view` and one `.project-document__download` link.

- [ ] **Step 1: Run the red localized-markup check**

```bash
python3 - <<'PY'
from pathlib import Path

for page in ('index.html', 'es/index.html'):
    html = Path(page).read_text()
    assert html.count('class="project-document"') == 4, page
    assert html.count('class="project-document__view') == 4, page
    assert html.count('class="project-document__download') == 4, page
PY
```

Expected: FAIL because no cards exist.

- [ ] **Step 2: Add the La Fuente y los Simios cards in both languages**

Inside that tab panel, after the gallery viewport, add a `<section class="project-documents">` with a localized heading and two cards. Use the visible titles `Apresentação Captação 2024-12-13` and `Maquete La Fuente y los Simios`, with type label `PowerPoint (.pptx)`.

Each download link points to its relative public asset and includes `download`. Each viewer link uses this exact pattern, with the complete public document URL percent-encoded as the `url` value:

```text
https://docs.google.com/gview?embedded=1&url=https%3A%2F%2Fluckaz13.github.io%2Fcrisanti%2Fdocuments%2Fproyectos-especiales%2Fla-fuente-y-los-simios%2F<encoded-filename>
```

Use `Ver no Google Slides` / `Baixar PowerPoint` in PT and `Ver en Google Slides` / `Descargar PowerPoint` in ES.

- [ ] **Step 3: Add the Master Taxi cards in both languages**

Inside the Master Taxi tab panel, after its gallery viewport, add the same section with visible titles `Master Taxi Dinámica` and `Master Taxi Sinópsis`, type label `Word (.docx)`, and this viewer pattern:

```text
https://docs.google.com/gview?embedded=1&url=https%3A%2F%2Fluckaz13.github.io%2Fcrisanti%2Fdocuments%2Fproyectos-especiales%2Fmaster-taxi%2F<encoded-filename>
```

Use `Ver no Google Docs` / `Baixar DOCX` in PT and `Ver en Google Docs` / `Descargar DOCX` in ES. Add document-specific `aria-label` values to every action.

- [ ] **Step 4: Validate exact panel scope, files, URLs, and localization**

```bash
python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

root = Path('.')
expected = {
    'la-fuente-y-los-simios': {'.pptx', 2},
    'master-taxi': {'.docx', 2},
}

for page in ('index.html', 'es/index.html'):
    html = Path(page).read_text()
    assert html.count('class="project-document"') == 4, page
    assert html.count('class="project-document__view') == 4, page
    assert html.count('class="project-document__download') == 4, page
    assert 'gallery-carousel-proyectos-especiales-vlak' in html
    assert 'project-documents-vlak' not in html
    assert html.count('https://docs.google.com/gview?') == 4, page
    assert html.count('download') >= 4, page
    if page.startswith('es/'):
        assert html.count('Ver en Google') == 4
        assert html.count('Descargar ') == 4
    else:
        assert html.count('Ver no Google') == 4
        assert html.count('Baixar ') == 4
print('localized document markup: PASS')
PY
git diff --check
```

Expected: `localized document markup: PASS` and no diff errors.

- [ ] **Step 5: Test serving and browser interaction**

With the existing local server, verify by HTTP that all four relative download URLs return 200 and the Office MIME type or an octet-stream fallback. In Chromium headless, open PT and ES, switch among La Fuente, Master Taxi, and Vlak, and assert that:

- the first two panels each expose two cards and four actions;
- Vlak exposes no document card;
- every download link resolves to the local server path;
- every viewer link opens a new-tab target and contains the matching encoded public GitHub Pages URL;
- the existing gallery controls and lightbox still operate after switching tabs.

Expected: all assertions pass in both languages. Do not require Google to fetch a localhost document; validate the external viewer after deployment.

- [ ] **Step 6: Commit markup and styles**

```bash
git add index.html es/index.html css/style.css
git diff --cached --check
git commit -m "feat: add document access to special projects"
```

### Task 4: Run final regression checks

**Files:**
- Verify: `documents/proyectos-especiales/**`
- Verify: `index.html`
- Verify: `es/index.html`
- Verify: `css/style.css`

**Interfaces:**
- Consumes: all prior deliverables.
- Produces: evidence that assets, localized links, tab navigation, download serving, and existing gallery behavior remain valid.

- [ ] **Step 1: Run all Task 1–3 checks from a clean committed tree**

Expected: all Python assertions pass and `git diff --check HEAD` emits no output.

- [ ] **Step 2: Inspect repository status**

```bash
git status --short
```

Expected: only the pre-existing untracked `img/Peces/03.jpg`; no implementation file remains uncommitted.

