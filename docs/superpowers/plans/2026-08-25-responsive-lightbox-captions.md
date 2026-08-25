# Responsive Lightbox Captions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show each gallery's complete existing caption in the desktop lightbox while keeping lightbox captions hidden at widths up to 768 px and keeping Peixes captionless everywhere.

**Architecture:** Keep the single existing lightbox. Extend its carousel-item adapter to collect the title, metadata, and optional description already rendered in each slide; compose only non-empty fields when an item opens. Use the existing CSS breakpoint to hide the caption visually on mobile, so resizing and rotation need no JavaScript state synchronization.

**Tech Stack:** Static HTML, vanilla JavaScript, responsive CSS, Python `unittest`, BeautifulSoup-generated gallery markup, Chrome DevTools Protocol for browser validation.

## Global Constraints

- Desktop means a viewport wider than 768 px.
- Mobile means a viewport width of 768 px or less.
- Peixes must remain without a lightbox caption at every viewport width.
- Use only metadata already rendered in `.gallery-title`, `.gallery-meta`, and `.gallery-desc`.
- Do not change navigation, zoom, counter, close behavior, consultation button, image `alt`, or editorial caption content.
- Do not add another lightbox, user-agent detection, dependencies, or additional breakpoints.
- Preserve the untracked user file `img/Peces/03.jpg`; do not stage, modify, or delete it.

## File Structure

- Modify `js/main.js`: collect all available slide caption fields and compose the lightbox caption.
- Modify `css/style.css`: hide the existing lightbox caption at the approved mobile breakpoint.
- Create `tests/test_lightbox_captions.py`: source-level regression coverage for metadata collection, empty-field filtering, Peixes behavior, and responsive CSS.

---

### Task 1: Carry complete gallery captions into the lightbox

**Files:**
- Create: `tests/test_lightbox_captions.py`
- Modify: `js/main.js:103-145`
- Read for fixture contract: `tools/acervo/render_galleries.py:55-88`

**Interfaces:**
- Consumes: `.gallery-title`, `.gallery-meta`, and `.gallery-desc` descendants of each `.gallery-slide`.
- Produces: lightbox item properties `title: string`, `meta: string`, and `desc: string`; `open(index)` renders their non-empty values into `#lightbox-caption`.

- [ ] **Step 1: Write failing JavaScript-adapter regression tests**

Create `tests/test_lightbox_captions.py` with:

```python
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LightboxCaptionTests(unittest.TestCase):
    def setUp(self):
        self.script = (ROOT / "js/main.js").read_text(encoding="utf-8")
        self.css = (ROOT / "css/style.css").read_text(encoding="utf-8")

    def test_carousel_items_collect_all_rendered_caption_fields(self):
        self.assertIn(
            "meta:  slide.querySelector('.gallery-meta')?.textContent?.trim() || ''",
            self.script,
        )
        self.assertIn(
            "desc:  slide.querySelector('.gallery-desc')?.textContent?.trim() || ''",
            self.script,
        )

    def test_lightbox_caption_filters_missing_fields(self):
        self.assertIn(
            "[item.title, item.serie, item.dims, item.meta, item.desc].filter(Boolean).join(' · ')",
            self.script,
        )

    def test_mobile_lightbox_caption_is_hidden(self):
        self.assertIn(
            "@media (max-width: 768px) {\n"
            "  .lightbox-caption {\n"
            "    display: none;\n"
            "  }\n"
            "}",
            self.css,
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused tests and verify the JavaScript expectations fail**

Run:

```bash
python3 -m unittest -q tests.test_lightbox_captions
```

Expected: two failures for the absent `meta`/`desc` adapter lines and the incomplete caption-composition expression. The mobile test may also fail until Task 2.

- [ ] **Step 3: Extend the carousel-item adapter**

In `getCarouselItems` within `js/main.js`, replace the returned object with:

```javascript
({
  src:   slide.querySelector('.gallery-img')?.src || '',
  alt:   slide.querySelector('.gallery-img')?.alt || '',
  title: slide.querySelector('.gallery-title')?.textContent?.trim() || '',
  serie: '',
  dims:  '',
  meta:  slide.querySelector('.gallery-meta')?.textContent?.trim() || '',
  desc:  slide.querySelector('.gallery-desc')?.textContent?.trim() || '',
})
```

Do not synthesize data from `alt`: slides without visible caption markup, including Peixes, must keep `title`, `meta`, and `desc` empty.

- [ ] **Step 4: Compose all available caption fields**

In `open(index)` within `js/main.js`, replace the current caption assignment with:

```javascript
lbCaption.textContent = [
  item.title,
  item.serie,
  item.dims,
  item.meta,
  item.desc,
].filter(Boolean).join(' · ');
```

This retains the existing artwork-card fields while adding gallery metadata and prevents empty separators.

- [ ] **Step 5: Run the focused suite**

Run:

```bash
python3 -m unittest -q tests.test_lightbox_captions
```

Expected: only `test_mobile_lightbox_caption_is_hidden` remains failing.

- [ ] **Step 6: Commit the caption data-flow change**

```bash
git add js/main.js tests/test_lightbox_captions.py
git commit -m "fix: show complete gallery captions in lightbox"
```

Expected: the commit includes only `js/main.js` and `tests/test_lightbox_captions.py`; `img/Peces/03.jpg` remains untracked.

---

### Task 2: Hide lightbox captions on mobile and verify the complete behavior

**Files:**
- Modify: `css/style.css:1289-1300`
- Test: `tests/test_lightbox_captions.py`

**Interfaces:**
- Consumes: the existing `#lightbox-caption.lightbox-caption` populated by Task 1.
- Produces: desktop-visible captions and `display: none` at viewport widths up to 768 px.

- [ ] **Step 1: Add the mobile presentation rule**

Immediately after the base `.lightbox-caption` rule in `css/style.css`, add:

```css
@media (max-width: 768px) {
  .lightbox-caption {
    display: none;
  }
}
```

Keep the base desktop rule unchanged so the caption remains visible above 768 px.

- [ ] **Step 2: Run the focused tests**

Run:

```bash
python3 -m unittest -q tests.test_lightbox_captions
```

Expected: all three tests pass.

- [ ] **Step 3: Run the complete automated verification**

Run:

```bash
python3 -m unittest discover -s tests -p 'test*.py' -q
python3 tools/acervo/audit_pt_br.py index.html
git diff --check
```

Expected: the complete test suite reports `OK`, the PT-BR audit prints `"findings": []`, and `git diff --check` emits no errors.

- [ ] **Step 4: Validate desktop, mobile, navigation, and Peixes in the browser**

With the local server available at `http://localhost:8772`, use the already running Chrome DevTools endpoint at port 9223 or an equivalent browser. Verify these exact assertions:

```text
Desktop 1440 px, Addis Abbaba slide 1:
- #lightbox-caption is visible.
- Caption contains "ADDIS ABABA" and "Materiais".

Desktop 1440 px, navigate to Addis Abbaba slide 4:
- Caption changes to "LALIBELA · (Detalhe)".

Mobile 390 px, the same Addis Abbaba image:
- computed display of #lightbox-caption is "none".
- #lightbox-img has a non-empty alt attribute.

Desktop 1440 px, Peixes:
- #lightbox-caption.textContent is empty.
```

Expected: all assertions hold without changing the lightbox counter, navigation, zoom, close button, or consultation button.

- [ ] **Step 5: Commit the responsive presentation rule**

```bash
git add css/style.css
git commit -m "fix: hide lightbox captions on mobile"
```

Expected: the commit includes only `css/style.css`; `git status --short` shows no task-related changes and continues to preserve `?? img/Peces/03.jpg`.
