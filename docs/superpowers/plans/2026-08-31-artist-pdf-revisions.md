# Artist PDF Revisions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement every approved catalogue correction from the artist's PDF, excluding the Instagram card, while preserving the bilingual static-site pipeline and all backup media.

**Architecture:** Treat the two ZIP archives as immutable inputs, synchronize only approved files into `/img`, then regenerate inventory, documents, manifest, published assets, and PT/ES HTML through the existing Python pipeline. Keep shared visual rules in CSS, shared carousel behavior in `js/gallery.js`, and activate exceptional behavior through explicit gallery attributes rather than forking the whole frontend.

**Tech Stack:** Python 3.14 standard library, Pillow, BeautifulSoup, HTML5, CSS3, vanilla JavaScript, `unittest`, Chromium headless, GitHub Pages.

## Global Constraints

- `drive-download-20260824T065754Z-1-001.zip` is the authoritative original archive; `Pequeñas Pipas-20260901T011313Z-1-001.zip` is authoritative only for the five approved replacements.
- Never modify the ZIPs, `/images/`, or `/img/images/` while synchronizing source media.
- Preserve `img/Peces/03-header-mark.png`; mirror it through CSS rather than rewriting its pixels.
- Keep both Vlak presentations; the independent section starts with `videos/vlak.mp4`, then the 17 ZIP images.
- Keep “Flores”; reorder only “El Nombre”.
- Translate and senior-review only the works under “Crítica”, not the entire site.
- Do not create an Instagram presentation card.
- All content changes must update PT and ES deterministically; do not patch only one rendered page.
- Run `graphify update .` after code changes because this repository maintains `graphify-out` when available.

---

### Task 1: Synchronize approved source assets without touching backups

**Files:**
- Create: `tools/acervo/sync_artist_revisions.py`
- Create: `tests/test_artist_revision_sync.py`
- Create at execution time: `img/Pequeñas Pipas/01.jpg`, `02.jpg`, `03.jpg`, `04.jpg`, `10.jpg`
- Replace from authoritative ZIP: `img/Seda/SEDA 2024/04.jpg`, `07.jpg`, `14.jpg`

**Interfaces:**
- Consumes: repository root plus the two fixed ZIP filenames.
- Produces: `SyncAction(source_archive: str, member: str, destination: Path, sha256: str)`, `build_sync_plan(root: Path) -> list[SyncAction]`, and `apply_sync_plan(actions: list[SyncAction], *, dry_run: bool) -> list[Path]`.
- Safety invariant: every destination resolves under `root / "img"` but never under `root / "img/images"`; `/images` is never a destination.

- [ ] **Step 1: Write the failing synchronization tests**

```python
class ArtistRevisionSyncTests(unittest.TestCase):
    def test_plan_contains_only_eight_approved_replacements(self):
        actions = build_sync_plan(ROOT)
        self.assertEqual(8, len(actions))
        self.assertEqual(
            {
                "img/Seda/SEDA 2024/04.jpg",
                "img/Seda/SEDA 2024/07.jpg",
                "img/Seda/SEDA 2024/14.jpg",
                "img/Pequeñas Pipas/01.jpg",
                "img/Pequeñas Pipas/02.jpg",
                "img/Pequeñas Pipas/03.jpg",
                "img/Pequeñas Pipas/04.jpg",
                "img/Pequeñas Pipas/10.jpg",
            },
            {a.destination.relative_to(ROOT).as_posix() for a in actions},
        )

    def test_plan_never_targets_backup_trees(self):
        for action in build_sync_plan(ROOT):
            relative = action.destination.relative_to(ROOT).as_posix()
            self.assertFalse(relative.startswith("images/"))
            self.assertFalse(relative.startswith("img/images/"))
```

- [ ] **Step 2: Run the focused test and confirm the red state**

Run: `python3 -m unittest -q tests.test_artist_revision_sync`

Expected: `ModuleNotFoundError: tools.acervo.sync_artist_revisions`.

- [ ] **Step 3: Implement an allowlisted ZIP synchronizer**

```python
PRIMARY_MEMBERS = {
    "Seda/SEDA 2024/04.jpg": "img/Seda/SEDA 2024/04.jpg",
    "Seda/SEDA 2024/07.jpg": "img/Seda/SEDA 2024/07.jpg",
    "Seda/SEDA 2024/14.jpg": "img/Seda/SEDA 2024/14.jpg",
}
PIPAS_MEMBERS = {
    f"Pequeñas Pipas/{name}.jpg": f"img/Pequeñas Pipas/{name}.jpg"
    for name in ("01", "02", "03", "04", "10")
}

def apply_sync_plan(actions, *, dry_run):
    written = []
    for action in actions:
        action.destination.parent.mkdir(parents=True, exist_ok=True)
        if not dry_run:
            with ZipFile(action.source_archive) as archive:
                payload = archive.read(action.member)
            if hashlib.sha256(payload).hexdigest() != action.sha256:
                raise ValueError(f"hash changed while reading {action.member}")
            action.destination.write_bytes(payload)
            written.append(action.destination)
    return written
```

The CLI must support `--root` and `--dry-run`, print all eight destinations, and refuse any destination outside the allowlist.

- [ ] **Step 4: Run dry-run, apply, and verify hashes**

Run:

```bash
python3 tools/acervo/sync_artist_revisions.py --root . --dry-run
python3 tools/acervo/sync_artist_revisions.py --root .
python3 -m unittest -q tests.test_artist_revision_sync
```

Expected: eight planned/written paths; tests pass; `git status --short -- images img/images` shows no new modifications caused by this task.

- [ ] **Step 5: Commit only source synchronization work**

```bash
git add tools/acervo/sync_artist_revisions.py tests/test_artist_revision_sync.py \
  'img/Seda/SEDA 2024/04.jpg' 'img/Seda/SEDA 2024/07.jpg' 'img/Seda/SEDA 2024/14.jpg' \
  'img/Pequeñas Pipas'
git commit -m "content: sync artist revision assets"
```

### Task 2: Curate the revised manifest and folder correspondence

**Files:**
- Modify: `tools/acervo/curate.py`
- Modify: `tools/acervo/reconcile.py`
- Modify: `tests/test_acervo_curation.py`
- Regenerate: `data/acervo/inventory.json`, `data/acervo/documents.json`, `data/acervo/manifest.json`
- Update: `docs/acervo/reconciliation-report.md`

**Interfaces:**
- Consumes: inventory and extracted documents generated from `/img`.
- Produces: `apply_artist_pdf_revisions(manifest: dict, documents: list[dict]) -> dict`.
- `tools/acervo/reconcile.py` must call that function after building the base manifest and before serializing the manifest/report, so the normal regeneration command applies the approved curation.
- The function removes `La Escultura/Verde` from publishable assets, preserves source files, normalizes joined ficha fields under `Los Niños`, and leaves both Vlak and Flores present.

- [ ] **Step 1: Add failing curation assertions**

```python
def test_artist_revisions_remove_verde_only_from_manifest(self):
    result = apply_artist_pdf_revisions(self.manifest, self.documents)
    keys = {f"{a['section']}/{a['series']}".rstrip('/') for a in result['assets']}
    self.assertNotIn("La Escultura/Verde", keys)

def test_children_details_have_boundaries(self):
    result = apply_artist_pdf_revisions(self.manifest, self.documents)
    children = [a for a in result['assets'] if a['section'] == 'Los Niños']
    for asset in children:
        details = (asset.get('caption', {}).get('source', {}).get('details') or '')
        self.assertNotRegex(details, r"\d{4}(?=[A-ZÁÉÍÓÚ])")
        self.assertNotRegex(details, r"Materiales:(?=\S)")
```

- [ ] **Step 2: Confirm failure**

Run: `python3 -m unittest -q tests.test_acervo_curation`

Expected: import/name failure for `apply_artist_pdf_revisions` or assertions failing on Verde/joined words.

- [ ] **Step 3: Implement source-level normalization**

Add `apply_artist_pdf_revisions()` after `apply_fichas()` and use `_readable_details()` plus these explicit boundaries:

```python
value = re.sub(r"(?<=\d{4})(?=[A-ZÁÉÍÓÚ])", ". ", value)
value = re.sub(r"(?i)Materiais?:(?=\S)", lambda m: f"{m.group(0)} ", value)
value = re.sub(r"(?<=[a-záéíóú])(?=(?:Algodão|Acrílico|Cerâmica|Colagem|Impressão|Papel|Tecido))", ". ", value)
```

Filter only assets whose normalized key equals `La Escultura/Verde`; do not delete files.

- [ ] **Step 4: Regenerate and audit the archive model**

```bash
python3 tools/acervo/inventory.py --source img --published img/images --html index.html --output data/acervo/inventory.json
python3 tools/acervo/extract_documents.py --source img --output data/acervo/documents.json
python3 tools/acervo/reconcile.py --inventory data/acervo/inventory.json --documents data/acervo/documents.json --html index.html es/index.html --output data/acervo/manifest.json --report docs/acervo/reconciliation-report.md
python3 -m json.tool data/acervo/manifest.json >/tmp/crisanti-manifest.valid
python3 -m unittest -q tests.test_acervo_inventory tests.test_acervo_documents tests.test_acervo_reconcile tests.test_acervo_curation
```

Expected: no missing `/img` member from the primary ZIP; no publishable Verde; both Vlak and Flores present; tests pass.

- [ ] **Step 5: Commit the reviewed archive model**

```bash
git add tools/acervo/curate.py tools/acervo/reconcile.py tests/test_acervo_curation.py data/acervo docs/acervo/reconciliation-report.md
git commit -m "content: reconcile artist revision archive"
```

### Task 3: Make rendering express the approved editorial structure

**Files:**
- Modify: `tools/acervo/render_galleries.py`
- Modify: `tests/test_acervo_render.py`
- Modify: `data/acervo/editorial-laberintos-ninos.json`
- Modify: `data/acervo/editorial-proyectos-literatura.json`
- Modify: `data/acervo/editorial-escultura-fotografia-moda.json`

**Interfaces:**
- Produces: `replace_images_after_leading_media(panel, assets, language)`, `render_master_taxi_synopsis(...)`, and `reorder_el_nombre(...)`.
- Preserves: the first video slide in `#juego-del-tren`, the Flores panel, and the downloadable Master Taxi Dinámica card.

- [ ] **Step 1: Add failing renderer tests for Vlak, Master Taxi, and El Nombre**

```python
def test_standalone_vlak_keeps_video_then_17_manifest_images(self):
    rendered = render_page(self.pt, self.manifest, "pt", self.editorial)
    section = BeautifulSoup(rendered, "html.parser").find(id="juego-del-tren")
    slides = section.select(".gallery-track > .gallery-slide")
    self.assertIsNotNone(slides[0].select_one("video.gallery-video"))
    self.assertEqual(17, len(section.select(".gallery-slide .gallery-img")))

def test_master_taxi_renders_synopsis_but_keeps_dinamica_document(self):
    soup = BeautifulSoup(render_page(self.pt, self.manifest, "pt", self.editorial), "html.parser")
    panel = soup.find(id="gallery-carousel-proyectos-especiales-master-taxi")
    self.assertIsNotNone(panel.select_one(".master-taxi-synopsis"))
    self.assertIsNotNone(panel.find(string=lambda value: value and "Dinámica" in value))
    self.assertIsNone(panel.find(string=lambda value: value and "Sinópsis" in value and "Baixar" in value))

def test_el_nombre_order_is_title_gallery_copy(self):
    rendered = render_page(self.pt, self.manifest, "pt", self.editorial)
    fiction = str(BeautifulSoup(rendered, "html.parser").find(id="ficcao"))
    title = fiction.index(">El Nombre<")
    gallery = fiction.index('id="gallery-carousel-ficcao-el-nombre"')
    copy = fiction.index('data-rendered-series-copy="ficcao-el-nombre"')
    self.assertLess(title, gallery)
    self.assertLess(gallery, copy)
    soup = BeautifulSoup(rendered, "html.parser")
    fiction = soup.find(id="ficcao")
    self.assertIsNotNone(fiction.find(id="gallery-carousel-ficcao-flores"))
```

- [ ] **Step 2: Run the renderer test and observe failures**

Run: `python3 -m unittest -q tests.test_acervo_render`

Expected: standalone Vlak still has 72 images; synopsis is a document card; El Nombre copy precedes the gallery.

- [ ] **Step 3: Implement deterministic structure helpers**

Use the manifest group `Proyectos Especiales/Vlak` for both Vlak panels. In the standalone panel, preserve the leading video node and replace every following slide:

```python
def replace_images_after_leading_media(panel, assets, language):
    track = panel.select_one(".gallery-track")
    leading = track.select_one(":scope > .gallery-slide:has(.gallery-video)")
    slides = BeautifulSoup(render_slides(assets, language, visible_captions=True), "html.parser")
    track.clear()
    track.append(leading)
    track.extend(list(slides.contents))
```

Render synopsis paragraphs from the extracted `Master Taxi Sinópsis.docx` content after the Master Taxi image. Move the rendered El Nombre copy wrapper after its gallery and tag it `data-rendered-series-copy="ficcao-el-nombre"`; leave Flores untouched.

- [ ] **Step 4: Add and localize the approved editorial copy**

Set the exact Ensayos and Laberintos PT/ES strings from the design spec. Remove “poético” from Addis Abbaba, correct `Em mi obra` to `En mi obra`, and update Seis Animales from its ficha. Do not translate unrelated site prose in this step.

- [ ] **Step 5: Run renderer and content tests**

```bash
python3 -m unittest -q tests.test_acervo_render tests.test_laberintos_hierarchy tests.test_vlak_video
python3 tools/acervo/render_galleries.py --manifest data/acervo/manifest.json --pt index.html --es es/index.html --pt-editorial data/acervo/editorial-literatura-critica.json
```

Expected: video + 17 standalone Vlak images; 17 images in Proyectos Especiales/Vlak; Master Taxi synopsis inline; El Nombre title → gallery → copy; Flores retained.

- [ ] **Step 6: Commit renderer and editorial structure**

```bash
git add tools/acervo/render_galleries.py tests/test_acervo_render.py data/acervo index.html es/index.html
git commit -m "feat: apply artist editorial structure"
```

### Task 4: Replace the five Pequeñas Pipas portada images

**Files:**
- Modify: `index.html`
- Modify: `es/index.html`
- Create: `tests/test_pequenas_pipas_replacements.py`
- Publish: `img/images/Pequeñas Pipas/01.jpg`, `02.jpg`, `03.jpg`, `04.jpg`, `10.jpg`

**Interfaces:**
- Consumes: Task 1 source files.
- Produces: six portada cards in their existing order; five use new files and the fourth legacy composition stays unchanged.

- [ ] **Step 1: Write the failing bilingual mapping test**

```python
EXPECTED = ["10.jpg", "03.jpg", "04.jpg", "pequenas-pipas-4.jpeg", "01.jpg", "02.jpg"]

def test_portada_uses_five_replacements_and_preserves_nine_studies(self):
    for page in ("index.html", "es/index.html"):
        soup = BeautifulSoup((ROOT / page).read_text(encoding="utf-8"), "html.parser")
        cards = soup.select('[data-series="pequenas-pipas"] img.obra-img')
        self.assertEqual(6, len(cards))
        self.assertEqual(EXPECTED, [Path(img["src"]).name for img in cards])
```

- [ ] **Step 2: Confirm failure**

Run: `python3 -m unittest -q tests.test_pequenas_pipas_replacements`

- [ ] **Step 3: Publish without overwriting legacy media and update both pages**

Add `publish_pipas(root: Path) -> list[Path]` to the Task 1 synchronizer. For each approved filename, compare the source and destination hashes: create a missing published file, accept an identical existing file, and raise `FileExistsError` rather than overwrite a different existing file. Run `python3 tools/acervo/sync_artist_revisions.py --root . --publish-pipas`, then update card sources to the mapping above; retain the existing `legacy/novas/7 Pequenas Pipas/pequenas-pipas-4.jpeg` reference for card four.

- [ ] **Step 4: Verify and commit**

```bash
python3 -m unittest -q tests.test_pequenas_pipas_replacements
python3 tools/acervo/audit_references.py --root . index.html es/index.html css/style.css
git add tests/test_pequenas_pipas_replacements.py index.html es/index.html 'img/images/Pequeñas Pipas'
git commit -m "content: replace five pequenas pipas photos"
```

### Task 5: Normalize the FC and fish mark across browsers

**Files:**
- Modify: `css/style.css`
- Create: `tests/css_helpers.py`
- Create: `tests/test_brand_mark.py`

**Interfaces:**
- Produces CSS custom property `--brand-mark-height: 1em` consumed by `.nav-logo-mark` and `.footer-brand-mark__fish`.
- Keeps the original PNG unchanged.
- Produces test helper `css_rule(css: str, selector: str) -> str` for narrowly checking declarations in a selector.

- [ ] **Step 1: Write failing CSS contract tests**

```python
import re

def css_rule(css, selector):
    match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]+)\}}", css)
    if match is None:
        raise AssertionError(f"missing CSS selector: {selector}")
    return match.group(1)

# tests/test_brand_mark.py
from tests.css_helpers import css_rule

def test_fish_is_mirrored_and_height_driven(self):
    css = (ROOT / "css/style.css").read_text(encoding="utf-8")
    for selector in (".nav-logo-mark", ".footer-brand-mark__fish"):
        rule = css_rule(css, selector)
        self.assertIn("height: var(--brand-mark-height);", rule)
        self.assertIn("width: auto;", rule)
        self.assertIn("flex-shrink: 0;", rule)
        self.assertIn("scaleX(-1)", rule)
```

- [ ] **Step 2: Run and confirm failure**

Run: `python3 -m unittest -q tests.test_brand_mark`

- [ ] **Step 3: Replace width-based sizing with line-box sizing**

```css
.nav-logo,
.footer-brand-mark { --brand-mark-height: 1em; align-items: center; overflow: visible; }
.nav-logo-mark,
.footer-brand-mark__fish {
  display: block;
  width: auto;
  height: var(--brand-mark-height);
  max-width: none;
  flex: 0 0 auto;
  transform: scaleX(-1);
  transform-origin: center;
}
```

Do not use an independent pixel width in open/compact header overrides. Keep the existing color filters.

- [ ] **Step 4: Test desktop/mobile CSS and commit**

```bash
python3 -m unittest -q tests.test_brand_mark
git add css/style.css tests/css_helpers.py tests/test_brand_mark.py
git commit -m "fix: normalize mirrored fish branding"
```

### Task 6: Triple artwork matting and make lightbox metadata persistent

**Files:**
- Modify: `css/style.css`
- Modify: `js/main.js`
- Modify: `tests/test_lightbox_captions.py`
- Create: `tests/test_artwork_surface.py`

**Interfaces:**
- Produces token `--artwork-mat: 3px` used only by `.obra-img`, `.gallery-img`, and `.lightbox-img`.
- Lightbox content becomes the scroll owner; caption remains below image on every viewport.

- [ ] **Step 1: Replace the obsolete mobile-hidden test with failing visibility/scroll tests**

```python
# tests/test_lightbox_captions.py and tests/test_artwork_surface.py
from tests.css_helpers import css_rule

def test_mobile_lightbox_caption_remains_visible(self):
    self.assertNotIn(".lightbox-caption {\n    display: none;", self.css)
    self.assertIn("overflow-y: auto;", css_rule(self.css, ".lightbox-content"))
    self.assertIn("flex: 0 0 auto;", css_rule(self.css, ".lightbox-caption"))

def test_every_artwork_surface_uses_three_pixel_mat(self):
    css = (ROOT / "css/style.css").read_text(encoding="utf-8")
    self.assertIn("--artwork-mat: 3px;", css)
    self.assertIn("border: var(--artwork-mat) solid var(--artwork-outline);", css)
```

- [ ] **Step 2: Confirm the old behavior fails**

Run: `python3 -m unittest -q tests.test_lightbox_captions tests.test_artwork_surface`

- [ ] **Step 3: Implement shared matting and scrollable lightbox**

Remove the one-pixel inset outline. Use a real border so the margin is visible on every image edge. Give `.lightbox-content` `max-height: calc(100dvh - 2rem)`, `overflow-y: auto`, and `overscroll-behavior: contain`; reduce image `max-height` so caption and controls remain reachable without cropping the image.

- [ ] **Step 4: Verify interactions and commit**

```bash
python3 -m unittest -q tests.test_lightbox_captions tests.test_artwork_surface
git add css/style.css js/main.js tests/test_lightbox_captions.py tests/test_artwork_surface.py
git commit -m "fix: preserve artwork mats and lightbox metadata"
```

### Task 7: Fix Cuadernos height and add Peces crossfade

**Files:**
- Modify: `js/gallery.js`
- Modify: `css/style.css`
- Modify: `tests/test_carousel_controls.py`
- Create: `tests/test_gallery_modes.py`
- Modify: `index.html`, `es/index.html`

**Interfaces:**
- Produces `measureSlideHeight(slide, availableWidth) -> number`, based on image `naturalWidth/naturalHeight` plus caption height.
- Consumes `data-transition="crossfade"` only on PT/ES Peces carousels.

- [ ] **Step 1: Add red tests for intrinsic height and scoped crossfade**

```python
def test_height_uses_intrinsic_ratio_not_clipped_figure_rect(self):
    script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
    self.assertIn("function measureSlideHeight(slide, availableWidth)", script)
    self.assertIn("img.naturalHeight / img.naturalWidth", script)
    self.assertNotIn("const height = target.getBoundingClientRect().height", script)

def test_only_peces_requests_crossfade(self):
    for page, carousel_id in (("index.html", "gallery-carousel-peixes"), ("es/index.html", "gallery-carousel-peces")):
        soup = BeautifulSoup((ROOT / page).read_text(encoding="utf-8"), "html.parser")
        self.assertEqual("crossfade", soup.find(id=carousel_id).get("data-transition"))
        self.assertEqual(1, len(soup.select('[data-transition="crossfade"]')))
```

- [ ] **Step 2: Run and see both failures**

Run: `python3 -m unittest -q tests.test_carousel_controls tests.test_gallery_modes`

- [ ] **Step 3: Make viewport height independent of clipping**

Compute rendered image height as `min(availableWidth, img.naturalWidth) * img.naturalHeight / img.naturalWidth`, add measured caption height and `captionClearance`, and update after `img.decode()`/`load`, slide changes, and ResizeObserver notifications. Change `.series-gallery` to `overflow-x: hidden; overflow-y: visible`.

- [ ] **Step 4: Implement crossfade without changing navigation APIs**

When `carouselEl.dataset.transition === 'crossfade'`, do not translate the track. Stack slides in one grid area, set only the current slide to opacity `1` and interactive, and transition opacity with the existing duration/easing. Under `prefers-reduced-motion`, transition duration becomes effectively zero. Keep current index, arrows, touch handlers, preload, and autoplay unchanged.

- [ ] **Step 5: Reproduce Cuadernos and verify both modes**

```bash
python3 -m unittest -q tests.test_carousel_controls tests.test_gallery_modes
# Terminal A (leave running during the capture):
python3 -m http.server 8766
# Terminal B; the tall viewport prevents content-visibility from skipping Cuadernos:
chromium --headless --disable-gpu --no-sandbox --window-size=1225,30000 --virtual-time-budget=5000 --screenshot=/tmp/crisanti-cuadernos-fixed.png 'http://127.0.0.1:8766/es/index.html'
```

Expected: `00.jpg` is square and fully visible; controls are not clipped; Peces fades while another sampled gallery slides laterally.

- [ ] **Step 6: Commit carousel fixes**

```bash
git add js/gallery.js css/style.css index.html es/index.html tests/test_carousel_controls.py tests/test_gallery_modes.py
git commit -m "fix: stabilize Cuadernos and crossfade Peces"
```

### Task 8: Remove Vlak player bands and collapse the trajectory

**Files:**
- Modify: `css/style.css`
- Modify: `js/main.js`
- Modify: `index.html`, `es/index.html`
- Modify: `tests/test_vlak_video.py`
- Create: `tests/test_timeline_expand.py`

**Interfaces:**
- Vlak video remains `object-fit: contain`; its figure/video backgrounds become transparent.
- Produces `initExpandableTimeline()` with button `[data-timeline-toggle]`, `aria-expanded`, and localized labels.

- [ ] **Step 1: Update Vlak expectations and add timeline red tests**

```python
# tests/test_vlak_video.py
from tests.css_helpers import css_rule

def test_video_surface_has_no_black_band_background(self):
    css = (ROOT / "css/style.css").read_text(encoding="utf-8")
    self.assertIn("background: transparent;", css_rule(css, ".gallery-figure--video"))
    self.assertIn("background: transparent;", css_rule(css, ".gallery-video"))

def test_timeline_is_accessibly_expandable_in_both_languages(self):
    expected = {"index.html": ("Ver mais", "Ver menos"), "es/index.html": ("Ver más", "Ver menos")}
    for page, labels in expected.items():
        soup = BeautifulSoup((ROOT / page).read_text(encoding="utf-8"), "html.parser")
        button = soup.select_one("[data-timeline-toggle]")
        self.assertEqual("false", button["aria-expanded"])
        self.assertEqual(labels, (button["data-label-more"], button["data-label-less"]))
```

- [ ] **Step 2: Confirm failures**

Run: `python3 -m unittest -q tests.test_vlak_video tests.test_timeline_expand`

- [ ] **Step 3: Remove only the CSS bands**

Keep `aspect-ratio: 478 / 850`, `max-height: 78vh`, and `object-fit: contain`; change only both background declarations to transparent.

- [ ] **Step 4: Add collapsed timeline markup and controller**

Wrap items after the first third in `.timeline-collapsible`, initially hidden with the `hidden` attribute. `initExpandableTimeline()` toggles `hidden`, `aria-expanded`, and localized button text; when collapsing, focus remains on the toggle and the page scrolls only if the toggle moved above the viewport.

- [ ] **Step 5: Verify and commit**

```bash
python3 -m unittest -q tests.test_vlak_video tests.test_timeline_expand
git add css/style.css js/main.js index.html es/index.html tests/test_vlak_video.py tests/test_timeline_expand.py
git commit -m "feat: refine Vlak and expandable trajectory"
```

### Task 9: Restore black Crítica cards and complete scoped PT-BR translations

**Files:**
- Modify: `data/acervo/editorial-literatura-critica.json`
- Modify: `css/style.css`
- Modify: `tests/test_critica_card_style.py`
- Modify: `tests/test_acervo_pt_br.py`
- Create: `docs/acervo/review-critica-pt-br.md`

**Interfaces:**
- Consumes: Spanish originals already rendered in `es/index.html` and PT editorial JSON.
- Produces: PT-BR texts for every Crítica article plus a reconciled review report.

- [ ] **Step 1: Add exact style and coverage failures**

```python
# tests/test_critica_card_style.py
from tests.css_helpers import css_rule

def test_critica_inherits_black_card_palette(self):
    css = (ROOT / "css/style.css").read_text(encoding="utf-8")
    self.assertNotIn("#critica .literatura-card {\n  background: #D4B38A", css)
    self.assertIn("background: #201E1C;", css_rule(css, ".literatura-card"))
    self.assertIn("color: #EAE6DF", css)

def test_every_critica_article_has_pt_editorial_copy(self):
    data = json.loads((ROOT / "data/acervo/editorial-literatura-critica.json").read_text())
    soup = BeautifulSoup((ROOT / "es/index.html").read_text(encoding="utf-8"), "html.parser")
    ids = {article.get("id") for article in soup.select("#critica article[id]")}
    self.assertEqual(ids, set(data["articles"]))
```

- [ ] **Step 2: Confirm the current earth override fails**

Run: `python3 -m unittest -q tests.test_critica_card_style tests.test_acervo_pt_br`

- [ ] **Step 3: Remove the Crítica earth override and retain accessible near-white copy**

Delete only the `#critica .literatura-card` earth-background/text overrides. Keep the base card palette `#201E1C`, heading `#FFFFFF`, body `#EAE6DF`, and existing focus/button states. Verify normal text contrast is at least 4.5:1.

- [ ] **Step 4: Complete the first-pass translations**

Translate every Spanish Crítica work into `editorial-literatura-critica.json`, preserving paragraphs, titles, citations, proper nouns, punctuation, and authorial register. Render PT again and run `audit_pt_br.py`.

- [ ] **Step 5: Dispatch two independent senior ES→PT-BR reviewers**

Reviewer A prompt: compare each Spanish Crítica article against the PT JSON for semantic fidelity, omissions, false cognates, titles, quotations, and register; report proposed changes with original, current PT, proposed PT, and rationale.

Reviewer B prompt: independently review natural Brazilian Portuguese, grammar, rhythm, terminology consistency, paragraph boundaries, and preservation of authorial voice; use the same four-column report format.

Neither reviewer edits files. Reconcile both reports into `docs/acervo/review-critica-pt-br.md`; apply only accepted changes to the JSON and record rejected disagreements with rationale.

- [ ] **Step 6: Render, validate, and commit**

```bash
python3 tools/acervo/render_galleries.py --manifest data/acervo/manifest.json --pt index.html --es es/index.html --pt-editorial data/acervo/editorial-literatura-critica.json
python3 tools/acervo/audit_pt_br.py index.html
python3 -m unittest -q tests.test_critica_card_style tests.test_acervo_pt_br
git add data/acervo/editorial-literatura-critica.json docs/acervo/review-critica-pt-br.md css/style.css index.html tests/test_critica_card_style.py tests/test_acervo_pt_br.py
git commit -m "content: review Critica translations and palette"
```

### Task 10: Full verification, visual audit, and graph refresh

**Files:**
- Modify only if verification reveals a defect: files already named in Tasks 1–9.
- Do not commit: `/tmp/crisanti-*.png` screenshots.

**Interfaces:**
- Consumes the complete implementation.
- Produces a passing repository and refreshed graph metadata when `graphify-out/graph.json` exists.

- [ ] **Step 1: Run every Python test**

Run: `python3 -m unittest discover -s tests -p 'test*.py' -q`

Expected: all tests pass; no skips for the revised surfaces.

- [ ] **Step 2: Run archive and reference audits**

```bash
python3 tools/acervo/audit_references.py --root . index.html es/index.html css/style.css js
python3 tools/acervo/audit_pt_br.py index.html
python3 -m json.tool data/acervo/manifest.json >/tmp/crisanti-manifest.valid
git diff --check
```

Expected: no missing active media, malformed JSON, unintended Spanish in scoped PT content, or whitespace errors.

- [ ] **Step 3: Run one bounded desktop/mobile visual pass**

Serve on port 8766 and capture PT/ES at desktop `1440×1000` and mobile `390×844`. Inspect together: FC/fish height and direction, all artwork mats, mobile lightbox caption/scroll, Peces crossfade, Cuadernos square/vertical/panoramic slides, Vlak video bands/order, timeline expansion, black Crítica cards, Master Taxi synopsis, Laberintos order, and El Nombre order.

- [ ] **Step 4: Run the Impeccable detector once after UI is final**

Run:

```bash
node /home/lucas/.agents/skills/impeccable/scripts/detect.mjs --json css/style.css js/main.js js/gallery.js js/gallery-tabs.js index.html es/index.html
```

Expected: no unresolved high-severity accessibility, responsive, motion, or contrast findings. Apply one consolidated correction batch if needed, then perform at most one confirmation screenshot pass.

- [ ] **Step 5: Refresh the code graph and verify scope**

```bash
test ! -f graphify-out/graph.json || graphify update .
git status -sb
git diff --stat 6747541..HEAD
```

Expected: only planned code/content/assets plus graph updates are tracked; user screenshots, PDFs, ZIPs, `.superpowers/`, and backup trees remain uncommitted and untouched.

- [ ] **Step 6: Commit any final verification-only corrections**

```bash
git add css/style.css js index.html es/index.html tests data/acervo docs/acervo
test ! -d graphify-out || git add graphify-out
git commit -m "fix: close artist revision visual audit"
```

Skip this commit when verification required no changes.
