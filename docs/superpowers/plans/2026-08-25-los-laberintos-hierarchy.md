# Los Laberintos Hierarchy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep the general Os/Los Labirintos introduction permanent while showing an explicit active-subsection heading and its optional text beside the tabs and gallery, with corrected PT-BR captions for El Calendario.

**Architecture:** Mark only the bilingual Los Laberintos sections with a reusable `data-series-copy-layout="gallery"` contract. The existing tab controller will branch on that declarative contract: gallery-layout sections render an `h3`, optional template content, and the active carousel in one column; all other tabbed sections retain their current behavior. Caption corrections remain source-driven in the PT manifest localizer and are regenerated into `index.html`.

**Tech Stack:** Static bilingual HTML, vanilla JavaScript, CSS, Python `unittest`, BeautifulSoup, JSON manifest generation, Chrome DevTools Protocol.

## Global Constraints

- Keep “Os Labirintos”/“Los Laberintos”, the general introduction, and the consultation button permanent.
- Render the active subsection name as an `h3` between the tabs and its specific text.
- Place the optional specific text before the active carousel in the gallery column.
- Cadaver Exquisito, El Calendario, El Puzzle, and La Papa have specific text.
- Las Etiquetas and Memory show their active title and gallery without reusing the general introduction as specific text.
- Preserve proper titles in Spanish in both languages.
- Correct only the two specified PT-BR El Calendario captions; do not editorially modify the Spanish page.
- Preserve carousel order, images, controls, lightbox behavior, and every unrelated tabbed section.
- Preserve the untracked user file `img/Peces/03.jpg`; never stage, modify, or delete it.

## File Structure

- Create `tests/test_laberintos_hierarchy.py`: structural and controller-contract regressions for both languages.
- Modify `index.html` and `es/index.html`: opt the Los Laberintos section into the gallery-copy layout.
- Modify `js/gallery-tabs.js`: render the active work heading and optional copy at the declared mount point while preserving legacy behavior.
- Modify `css/style.css`: style the active subsection heading and its copy block.
- Modify `tests/test_acervo_curation.py`: source-driven El Calendario caption regression.
- Modify `tests/test_acervo_pt_br.py`: ensure the newly discovered Spanish phrase is detectable.
- Modify `tools/acervo/localize_manifest_pt.py`: define exact PT caption overrides by asset path.
- Modify `tools/acervo/audit_pt_br.py`: detect the Spanish construction found in El Calendario.
- Regenerate `data/acervo/manifest.json` and `index.html`; render `es/index.html` only to verify structural preservation and editorial stability.

---

### Task 1: Establish the gallery-column copy contract

**Files:**
- Create: `tests/test_laberintos_hierarchy.py`
- Modify: `index.html:1593`
- Modify: `es/index.html` at `section#los-laberintos`
- Modify: `js/gallery-tabs.js:6-29`

**Interfaces:**
- Consumes: `section.dataset.seriesCopyLayout`, `.gallery-tabs`, active `.gallery-tab`, optional matching `template[data-series-copy]`, and `.series-lead`.
- Produces: `.series-copy-display.series-copy-display--gallery` immediately after the tab list, containing `.series-copy-title` plus optional cloned template content.

- [ ] **Step 1: Write failing structural and controller tests**

Create `tests/test_laberintos_hierarchy.py`:

```python
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]


class LaberintosHierarchyTests(unittest.TestCase):
    def test_bilingual_sections_opt_into_gallery_copy_layout(self):
        for relative in ("index.html", "es/index.html"):
            with self.subTest(relative=relative):
                soup = BeautifulSoup((ROOT / relative).read_text(encoding="utf-8"), "html.parser")
                section = soup.find(id="los-laberintos")
                self.assertEqual("gallery", section.get("data-series-copy-layout"))

    def test_controller_mounts_active_title_and_copy_after_tabs(self):
        script = (ROOT / "js/gallery-tabs.js").read_text(encoding="utf-8")

        self.assertIn("section.dataset.seriesCopyLayout === 'gallery'", script)
        self.assertIn("tablist.insertAdjacentElement('afterend', display)", script)
        self.assertIn("title.className = 'series-copy-title'", script)
        self.assertIn("title.textContent = activeTab.textContent.trim()", script)
        self.assertIn("display.appendChild(template.content.cloneNode(true))", script)

    def test_gallery_layout_keeps_general_lead_visible_without_specific_copy(self):
        script = (ROOT / "js/gallery-tabs.js").read_text(encoding="utf-8")

        self.assertIn("if (lead) lead.hidden = false", script)
        self.assertIn("if (template) display.appendChild(template.content.cloneNode(true))", script)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused test and confirm the missing contract fails**

Run:

```bash
python3 -m unittest -q tests.test_laberintos_hierarchy
```

Expected: three failures because neither HTML section has the marker and the controller has no gallery-layout branch.

- [ ] **Step 3: Opt in only the bilingual Los Laberintos sections**

In both `index.html` and `es/index.html`, change the opening tag of `section#los-laberintos` to:

```html
<section class="section series series-group" data-series-copy-layout="gallery" id="los-laberintos">
```

Do not add the attribute to any other section.

- [ ] **Step 4: Add the gallery-layout branch to `syncSeriesCopy`**

At the start of `syncSeriesCopy`, obtain the tab and layout state before the current missing-template early return:

```javascript
var tablist = section.querySelector('.gallery-tabs');
var activeTab = section.querySelector('.gallery-tab[data-target="' + targetId + '"]');
var copyInGallery = section.dataset.seriesCopyLayout === 'gallery';
```

Then insert this branch before the legacy `if (!template)` block:

```javascript
if (copyInGallery && tablist && activeTab) {
  if (!display) {
    display = document.createElement('div');
    display.className = 'series-copy-display series-copy-display--gallery';
    tablist.insertAdjacentElement('afterend', display);
  }
  display.innerHTML = '';
  var title = document.createElement('h3');
  title.className = 'series-copy-title';
  title.textContent = activeTab.textContent.trim();
  display.appendChild(title);
  if (template) display.appendChild(template.content.cloneNode(true));
  display.hidden = false;
  if (lead) lead.hidden = false;
  return;
}
```

Remove the later duplicate declaration of `activeTab`, but leave the existing `.literatura-work-title` behavior intact for non-gallery layouts.

- [ ] **Step 5: Run the focused and existing gallery-tab tests**

Run:

```bash
python3 -m unittest -q tests.test_laberintos_hierarchy tests.test_acervo_render
```

Expected: all tests pass.

- [ ] **Step 6: Commit the structural behavior**

```bash
git add index.html es/index.html js/gallery-tabs.js tests/test_laberintos_hierarchy.py
git commit -m "fix: clarify Los Laberintos content hierarchy"
```

Expected: only the four listed files are committed; `img/Peces/03.jpg` remains untracked.

---

### Task 2: Style the subsection heading without changing other tabbed sections

**Files:**
- Modify: `tests/test_laberintos_hierarchy.py`
- Modify: `css/style.css:859-865`

**Interfaces:**
- Consumes: `.series-copy-display--gallery` and `.series-copy-title` created by Task 1.
- Produces: a clear third-level editorial heading and spacing scoped to the gallery-layout copy block.

- [ ] **Step 1: Add a failing scoped-style test**

Add this method to `LaberintosHierarchyTests`:

```python
def test_gallery_copy_heading_has_scoped_editorial_style(self):
    css = (ROOT / "css/style.css").read_text(encoding="utf-8")

    self.assertIn(".series-copy-display--gallery", css)
    self.assertIn(".series-copy-title", css)
    self.assertIn("font-family: var(--f-serif);", css)
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run:

```bash
python3 -m unittest -q tests.test_laberintos_hierarchy
```

Expected: one failure because the new scoped selectors do not exist.

- [ ] **Step 3: Add the minimal scoped styles**

After the base `.series-copy-display p` rule in `css/style.css`, add:

```css
.series-copy-display--gallery {
  margin: 0 0 1.5rem;
}

.series-copy-title {
  margin: 0 0 0.75rem;
  font-family: var(--f-serif);
  font-size: clamp(1.5rem, 2.5vw, 2rem);
  font-weight: 500;
  line-height: 1.2;
  color: var(--c-ink);
}
```

Do not modify `.gallery-tab`, `.section-title`, or the layout rules of unrelated sections.

- [ ] **Step 4: Run the focused test**

Run:

```bash
python3 -m unittest -q tests.test_laberintos_hierarchy
```

Expected: all four tests pass.

- [ ] **Step 5: Commit the scoped presentation**

```bash
git add css/style.css tests/test_laberintos_hierarchy.py
git commit -m "style: distinguish active Laberintos subsection"
```

Expected: only the CSS file and hierarchy test are committed.

---

### Task 3: Correct El Calendario captions at the localization source

**Files:**
- Modify: `tests/test_acervo_curation.py`
- Modify: `tests/test_acervo_pt_br.py`
- Modify: `tools/acervo/localize_manifest_pt.py`
- Modify: `tools/acervo/audit_pt_br.py`
- Regenerate: `data/acervo/manifest.json`
- Regenerate: `index.html`
- Regenerate without Spanish editorial changes: `es/index.html`

**Interfaces:**
- Consumes: asset paths `img/Los Laberintos/El Calendario/01.jpg` and `02.jpg`.
- Produces: exact `caption.pt.title`, `caption.pt.details`, and rebuilt `alt.pt` values; the PT audit detects the original Spanish residue.

- [ ] **Step 1: Write failing path-specific localization tests**

Add to `tests/test_acervo_curation.py`:

```python
def test_localizes_el_calendario_captions_exactly(self):
    manifest = {
        "assets": [
            {
                "path": "img/Los Laberintos/El Calendario/01.jpg",
                "caption": {"pt": {"title": "Tapa del Calendario", "year": "2006", "details": "Motivo"}},
                "alt": {"pt": "legacy"},
            },
            {
                "path": "img/Los Laberintos/El Calendario/02.jpg",
                "caption": {"pt": {"title": "Imágenes del Calendario", "year": "2006", "details": "legacy"}},
                "alt": {"pt": "legacy"},
            },
        ]
    }

    localized = localize_manifest_pt(manifest)

    first, second = localized["assets"]
    self.assertEqual('Capa de “El Calendario”', first["caption"]["pt"]["title"])
    self.assertEqual(
        'Motivo: detalhe da personagem do candombe uruguaio “Mamá Vieja”.',
        first["caption"]["pt"]["details"],
    )
    self.assertEqual('Imagens de “El Calendario”', second["caption"]["pt"]["title"])
    self.assertEqual(
        'As fotografias foram feitas a partir da série do autor “Hay agua caliente”, exposta no Consulado da República Argentina em Colônia do Sacramento, Uruguai, em 2005.',
        second["caption"]["pt"]["details"],
    )
    self.assertIn('Capa de “El Calendario”', first["alt"]["pt"])
```

- [ ] **Step 2: Add a failing audit regression for the discovered residue**

Add to `tests/test_acervo_pt_br.py`:

```python
def test_detects_spanish_exhibition_caption(self):
    findings = find_spanish_residuals(
        ['Las fotografía fueron tomadas de la serie del autor, expuesta en el Consulado.']
    )

    self.assertEqual(1, len(findings))
    self.assertIn("spanish-exhibition-caption", findings[0].rules)
```

- [ ] **Step 3: Run the localization and audit tests to verify red**

Run:

```bash
python3 -m unittest -q tests.test_acervo_curation tests.test_acervo_pt_br
```

Expected: the exact override test and the new audit rule test fail.

- [ ] **Step 4: Define exact PT caption overrides**

In `tools/acervo/localize_manifest_pt.py`, add:

```python
CAPTION_OVERRIDES = {
    "img/Los Laberintos/El Calendario/01.jpg": {
        "title": 'Capa de “El Calendario”',
        "details": 'Motivo: detalhe da personagem do candombe uruguaio “Mamá Vieja”.',
    },
    "img/Los Laberintos/El Calendario/02.jpg": {
        "title": 'Imagens de “El Calendario”',
        "details": 'As fotografias foram feitas a partir da série do autor “Hay agua caliente”, exposta no Consulado da República Argentina em Colônia do Sacramento, Uruguai, em 2005.',
    },
}
```

After applying `TITLE_OVERRIDES` inside `localize_manifest_pt`, apply the matching caption override before rebuilding `alt.pt`:

```python
override = CAPTION_OVERRIDES.get(asset.get("path"))
if override:
    caption.update(override)
```

- [ ] **Step 5: Extend the PT audit rule**

Add to `PHRASE_RULES` in `tools/acervo/audit_pt_br.py`:

```python
"spanish-exhibition-caption": r"(?:las\s+fotograf[ií]a|fueron\s+tomadas|de\s+la\s+serie\s+del\s+autor|expuesta\s+en\s+el\s+consulado)",
```

- [ ] **Step 6: Run the focused tests and verify green**

Run:

```bash
python3 -m unittest -q tests.test_acervo_curation tests.test_acervo_pt_br
```

Expected: all tests pass.

- [ ] **Step 7: Regenerate the manifest and bilingual pages**

Run:

```bash
python3 tools/acervo/localize_manifest_pt.py data/acervo/manifest.json
python3 tools/acervo/render_galleries.py --manifest data/acervo/manifest.json --pt index.html --es es/index.html
```

Expected: both HTML pages retain `data-series-copy-layout="gallery"`; only PT caption fields receive the two editorial corrections.

- [ ] **Step 8: Verify source idempotence and PT audit**

Run:

```bash
sha256sum index.html es/index.html data/acervo/manifest.json > /tmp/laberintos-before.sha256
python3 tools/acervo/localize_manifest_pt.py data/acervo/manifest.json
python3 tools/acervo/render_galleries.py --manifest data/acervo/manifest.json --pt index.html --es es/index.html
sha256sum index.html es/index.html data/acervo/manifest.json > /tmp/laberintos-after.sha256
diff -u /tmp/laberintos-before.sha256 /tmp/laberintos-after.sha256
python3 tools/acervo/audit_pt_br.py index.html
```

Expected: `diff` emits no differences and the audit prints `"findings": []`.

- [ ] **Step 9: Commit the editorial correction and regenerated artifacts**

```bash
git add data/acervo/manifest.json index.html es/index.html tests/test_acervo_curation.py tests/test_acervo_pt_br.py tools/acervo/audit_pt_br.py tools/acervo/localize_manifest_pt.py
git commit -m "fix: localize El Calendario captions"
```

Expected: the listed source, tests, manifest, and rendered pages are committed; `img/Peces/03.jpg` remains untracked.

---

### Task 4: Validate all tabs, responsive layout, and regressions

**Files:**
- Verify only; no production files should change.

**Interfaces:**
- Consumes: the completed bilingual pages and local server at `http://localhost:8772`.
- Produces: evidence that all six tabs meet the approved hierarchy in desktop and mobile layouts.

- [ ] **Step 1: Run the complete automated suite**

Run:

```bash
python3 -m unittest discover -s tests -p 'test*.py' -q
python3 tools/acervo/audit_pt_br.py index.html
git diff --check HEAD
```

Expected: the complete test suite reports `OK`, the audit has zero findings, and the diff check is clean.

- [ ] **Step 2: Validate all PT-BR tabs at 1440 px and 390 px**

For each viewport, navigate through Cadaver Exquisito, El Calendario, El Puzzle, La Papa, Las Etiquetas, and Memory and verify:

```text
- “Os Labirintos” and the general introduction remain visible.
- .series-copy-title equals the active tab label.
- Cadaver Exquisito, El Calendario, El Puzzle, and La Papa show specific text.
- Las Etiquetas and Memory show no specific body text.
- Exactly one carousel is visible and it matches the active tab.
- aria-selected="true" exists only on the active tab.
```

Expected: every assertion holds at both widths; El Calendario displays the corrected PT captions.

- [ ] **Step 3: Validate all Spanish tabs at 1440 px and 390 px**

Repeat Step 2 at `http://localhost:8772/es/#los-laberintos`, replacing the permanent heading with “Los Laberintos”.

Expected: hierarchy and responsive behavior match PT-BR; Spanish editorial text remains unchanged.

- [ ] **Step 4: Confirm final repository state**

Run:

```bash
git status --short
git log -4 --oneline
```

Expected: no task-related modifications remain; `?? img/Peces/03.jpg` remains present and untracked; the three implementation commits are visible.
