# Add Cadernos and Cuadernos Section Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a localized 21-work Cadernos/Cuadernos section immediately after Ensaios and preserve the alternating left/right layout of every following series section.

**Architecture:** Copy the approved sequential JPEG set into the tracked public gallery tree, excluding the unmatched duplicate and DOCX sources. Insert one standard `series-grid` section with a 21-slide captioned carousel into each static page, then flip the explicit `series-grid--reverse` classes of all subsequent series groups.

**Tech Stack:** Static HTML, existing CSS series grid, existing vanilla-JavaScript carousel/lightbox, Git-tracked JPEGs, Python standard-library assertions, Chromium headless

## Global Constraints

- Publish exactly `00.jpg` through `20.jpg` from `/img/Cuadernos`.
- Exclude `11(1).jpg`, `Ficha Cuadernos.docx`, and `Texto para Cuadernos.docx`.
- Preserve every source file under `/img` unchanged.
- Track public copies under `images/galerias/Cuadernos/`.
- Insert the section immediately after Ensaios and before Escultura.
- Use title `Cadernos` and ID `cadernos` in PT-BR; title `Cuadernos` and ID `cuadernos` in Spanish.
- Keep artwork titles `Cuaderno N` in Spanish in both locales.
- Use one carousel with exactly 21 numerically ordered slides.
- Reuse existing caption, carousel, outline, shadow, lightbox, and CTA patterns.
- Change only the explicit grid-direction class of subsequent series sections.

## Canonical captions

| File | Title | Year | PT-BR support | Spanish support |
|---|---|---:|---|---|
| `00.jpg` | Cuaderno 9 | 2025 | Acrílico sobre papel de seda | Acrílico sobre papel de seda |
| `01.jpg` | Cuaderno 7 | 2024 | Acrílico sobre papel de seda e colagem | Acrílico sobre papel de seda y collage |
| `02.jpg` | Cuaderno 4 | 2023 | Colagem, papéis de seda, acrílicos e papel kraft | Collage, papeles de seda, acrílicos y papel kraft |
| `03.jpg` | Cuaderno 4 | 2023 | Colagem, papéis de seda, acrílicos e papel kraft | Collage, papeles de seda, acrílicos y papel kraft |
| `04.jpg` | Cuaderno 4 | 2023 | Papel fotográfico e acrílicos | Papel fotográfico y acrílicos |
| `05.jpg` | Cuaderno 6 | 2024 | Colagem e papel fotográfico | Collage y papel fotográfico |
| `06.jpg` | Cuaderno 9 | 2025 | Storyboard para “Der Elefant” | Storyboard para “Der Elefant” |
| `07.jpg` | Cuaderno 10 | 2026 | Colagem | Collage |
| `08.jpg` | Cuaderno 3 | 2022 | Colagem, papel de seda, acrílicos, cortiça e juta | Collage, papel de seda, acrílicos, corcho y yute |
| `09.jpg` | Cuaderno 2 | 2021 | Vestígio orgânico | Vestigio orgánico |
| `10.jpg` | Cuaderno 5 | 2024 | Acrílicos sobre papel de seda | Acrílicos sobre papel de seda |
| `11.jpg` | Cuaderno 2 | 2021 | Acrílico sobre papel de seda | Acrílico sobre papel de seda |
| `12.jpg` | Cuaderno 2 | 2021 | Esboço | Boceto |
| `13.jpg` | Cuaderno 3 | 2022 | Esboço e amostras têxteis | Boceto y muestras textiles |
| `14.jpg` | Cuaderno 6 | 2024 | Estudo de cor, kraft e acrílicos | Estudio de color, kraft y acrílicos |
| `15.jpg` | Cuaderno 5 | 2024 | Esboço para peixe. Tecido sintético e acrílicos | Boceto para pez. Tela sintética y acrílicos |
| `16.jpg` | Cuaderno 5 | 2024 | Esboço para peixe. Acrílicos, linha de costura e vestígios orgânicos | Boceto para pez. Acrílicos, hilo de coser y vestigios orgánicos |
| `17.jpg` | Cuaderno 2 | 2021 | Esboços para pipas | Bocetos para cometas |
| `18.jpg` | Cuaderno 5 | 2024 | Esboço para peixe. Tecido sintético e acrílicos | Boceto para pez. Tela sintética y acrílicos |
| `19.jpg` | Cuaderno 3 | 2022 | Estudo de texturas com nanquim | Estudio de texturas con tinta china |
| `20.jpg` | Cuaderno 7 | 2024 | Estudo. Papel kraft, tinta e têxteis | Estudio. Papel kraft, tinta y textiles |

---

### Task 1: Publish the canonical 21-image asset set

**Files:**
- Read: `/home/lucas/Projetos/crisanti/img/Cuadernos/{00..20}.jpg`
- Create: `images/galerias/Cuadernos/{00..20}.jpg`

**Interfaces:**
- Consumes: exactly 21 approved source JPEGs.
- Produces: stable public filenames consumed identically by both localized carousels.

- [ ] **Step 1: Run the red asset test**

```bash
python3 - <<'PY'
from pathlib import Path
expected = {f'{i:02}.jpg' for i in range(21)}
actual = {p.name for p in Path('images/galerias/Cuadernos').glob('*.jpg')}
assert actual == expected, (actual - expected, expected - actual)
PY
```

Expected: FAIL because the public set does not exist.

- [ ] **Step 2: Copy only the numeric range**

Create `images/galerias/Cuadernos/` and copy each explicitly generated filename from `00.jpg` through `20.jpg`. The copy routine must derive names from `range(21)` and must not glob the intake directory, preventing `11(1).jpg` and DOCX files from entering the destination.

- [ ] **Step 3: Verify exact set and byte identity**

```bash
python3 - <<'PY'
from pathlib import Path
source = Path('/home/lucas/Projetos/crisanti/img/Cuadernos')
dest = Path('images/galerias/Cuadernos')
expected = {f'{i:02}.jpg' for i in range(21)}
actual = {p.name for p in dest.iterdir() if p.is_file()}
assert actual == expected, (actual - expected, expected - actual)
for name in expected:
    assert (source / name).read_bytes() == (dest / name).read_bytes(), name
assert (source / '11(1).jpg').is_file()
assert not (dest / '11(1).jpg').exists()
assert not list(dest.glob('*.docx'))
print('Cuadernos assets: PASS (21 exact copies)')
PY
```

Expected: `Cuadernos assets: PASS (21 exact copies)`.

- [ ] **Step 4: Commit the assets**

```bash
git add images/galerias/Cuadernos
git commit -m "assets: add Cuadernos works"
```

### Task 2: Add the localized sections and 21-slide carousels

**Files:**
- Modify: `index.html` between Ensaios and Escultura
- Modify: `es/index.html` between Ensayos and Escultura

**Interfaces:**
- Consumes: Task 1 public JPEG set and the existing series/carousel HTML contract.
- Produces: `section#cadernos` and `section#cuadernos`, each with one visible 21-slide `gallery-carousel`.

- [ ] **Step 1: Run the red section test**

```bash
python3 - <<'PY'
from pathlib import Path
assert 'id="cadernos"' in Path('index.html').read_text()
assert 'id="cuadernos"' in Path('es/index.html').read_text()
PY
```

Expected: FAIL because neither section exists.

- [ ] **Step 2: Add the Portuguese section shell and text**

Immediately after Ensaios and before Escultura, add `section class="section series series-group" id="cadernos"` with `div class="container series-grid"`. The text column contains title `Cadernos`, these four separate paragraphs, and the existing localized WhatsApp CTA pattern:

1. `Este acervo, composto por aproximadamente doze cadernos de esboços, registra a faceta mais íntima da relação de FC com o Brasil como território de enraizamento pictórico.`
2. `Podemos apreciar neles algumas descobertas que mais tarde dariam origem a séries plenamente realizadas e já expostas.`
3. `Ao mesmo tempo, contêm um amplíssimo corpo de notas, exercícios e estudos para o desenvolvimento de novos ensaios.`
4. `Em todo caso, são diários visuais e obras em si mesmas, por meio dos quais se pode acessar a dimensão mais pessoal do universo profissional do artista.`

- [ ] **Step 3: Add the Portuguese carousel**

In the gallery column, add a visible carousel `id="gallery-carousel-cadernos"` with the standard controls. Emit 21 slides with `data-index` 0–20. Each figure contains:

```html
<img src="images/galerias/Cuadernos/00.jpg" alt="Cuaderno 9 — 2025 — Acrílico sobre papel de seda — Fabio Crisanti" class="gallery-img" loading="lazy" />
<figcaption class="gallery-caption">
  <h3 class="gallery-title">Cuaderno 9</h3>
  <p class="gallery-meta">2025 · Acrílico sobre papel de seda</p>
</figcaption>
```

Generate every later row from the canonical caption table without changing order or punctuation.

- [ ] **Step 4: Add the Spanish section and carousel**

Use `id="cuadernos"`, title `Cuadernos`, a non-reversed `series-grid`, and these four paragraphs:

1. `Este acervo, compuesto por aproximadamente doce cuadernos de bocetos, registra la faceta más íntima de la relación de FC con Brasil como territorio de arraigo pictórico.`
2. `Podemos apreciar en ellos algunos hallazgos que luego darían origen a series completamente consumadas y ya expuestas.`
3. `Al mismo tiempo, contienen un amplísimo cuerpo de notas, ejercicios y estudios para el desarrollo de nuevos ensayos.`
4. `En todo caso, son diarios visuales y obras en sí mismas, que permiten acceder a la dimensión más personal del universo profesional del artista.`

Add carousel `gallery-carousel-cuadernos` using Spanish control labels, `../images/` paths, and the Spanish support column from the canonical table. Add the localized WhatsApp CTA.

- [ ] **Step 5: Verify section order, slide order, text, and captions**

Run a Python HTML parser/assertion script that, for each locale:

- asserts the new section occurs after the closing Ensaios/Ensayos section and before Escultura;
- extracts the new carousel and finds exactly 21 `.gallery-slide` elements;
- extracts filenames and compares them exactly to `[f'{i:02}.jpg' for i in range(21)]`;
- asserts every canonical title, year, localized support, and `data-index` occurs in its corresponding slide;
- asserts the four exact localized paragraphs occur once;
- resolves every relative image path to an existing public file.

Expected: all assertions pass and `git diff --check` emits no output.

### Task 3: Shift all subsequent series directions

**Files:**
- Modify: `index.html` grid classes for Escultura through Projetos Especiais
- Modify: `es/index.html` equivalent grid classes

**Interfaces:**
- Consumes: Task 2 insertion with a normal grid.
- Produces: strict alternating `reverse, normal, reverse, normal, reverse, normal` directions for the six subsequent series.

- [ ] **Step 1: Run the red alternation test**

```bash
python3 - <<'PY'
from pathlib import Path
checks = {
    'index.html': [
        ('la-escultura', True), ('la-fotografia', False), ('la-moda', True),
        ('los-laberintos', False), ('los-ninos', True), ('proyectos-especiales', False),
    ],
    'es/index.html': [
        ('la-escultura', True), ('la-fotografia', False), ('la-moda', True),
        ('los-laberintos', False), ('los-ninos', True), ('proyectos-especiales', False),
    ],
}
for page, rows in checks.items():
    html = Path(page).read_text()
    for section_id, reverse in rows:
        start = html.index(f'id="{section_id}"')
        grid = html[html.index('<div class="container series-grid', start):html.index('>', html.index('<div class="container series-grid', start))]
        assert ('series-grid--reverse' in grid) is reverse, (page, section_id, grid)
PY
```

Expected: FAIL because directions still reflect the old sequence.

- [ ] **Step 2: Flip the six grid classes in both pages**

Apply this exact sequence after the new normal-grid Cadernos/Cuadernos section:

- `la-escultura`: add `series-grid--reverse`;
- `la-fotografia`: remove `series-grid--reverse`;
- `la-moda`: add `series-grid--reverse`;
- `los-laberintos`: remove `series-grid--reverse`;
- `los-ninos`: add `series-grid--reverse`;
- `proyectos-especiales`: remove `series-grid--reverse`.

- [ ] **Step 3: Run the green alternation test**

Re-run Step 1. Expected: PASS for all 12 locale/section pairs.

- [ ] **Step 4: Commit HTML content and layout**

```bash
git add index.html es/index.html
git diff --cached --check
git commit -m "content: add Cadernos and Cuadernos section"
```

### Task 4: Browser and final regression verification

**Files:**
- Verify: `images/galerias/Cuadernos/**`, `index.html`, `es/index.html`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: evidence that the new section, navigation, lightbox, asset serving, and shifted layouts work as specified.

- [ ] **Step 1: Verify all asset URLs**

Request the 21 public JPEG paths from the local server and assert HTTP 200 with image content types.

- [ ] **Step 2: Verify PT and ES in Chromium**

For each locale, assert the new section sits between Ensaios and Escultura, has 21 slides, begins at `00.jpg`, advances to `01.jpg`, and opens the lightbox with counter `1 / 21`; navigate once and expect `2 / 21`. Assert Ensaios tab switching and the next Escultura carousel still work.

- [ ] **Step 3: Verify actual grid positioning**

At desktop width, read bounding rectangles for `.series-text` and `.series-gallery` in the new section and all six subsequent sections. Assert text/gallery horizontal order alternates at every boundary according to the canonical sequence, not merely that class names exist.

- [ ] **Step 4: Verify mobile layout**

At 390 px, assert no horizontal page overflow and that the new carousel, caption, CTA, and all section text fit within the viewport.

- [ ] **Step 5: Run final committed-state checks**

Re-run the exact asset, HTML, caption, ordering, and alternation assertions; run `git diff --check HEAD`; inspect `git status --short`.

Expected: all assertions pass; status shows only the pre-existing untracked `img/Peces/03.jpg`.

