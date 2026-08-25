# Contact Kite Image Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Contact section’s legacy image with the selected complete Addis Abbaba kite in both languages and preserve the whole artwork at every viewport.

**Architecture:** Both static pages will reference the existing canonical asset `img/images/La Escultura/Addis Abbaba/02.jpg`, using the correct relative prefix for each locale. The shared `.contato-img` rule will switch from `cover` to `contain`, while a focused source test protects the bilingual references, decorative semantics, and uncropped rendering contract.

**Tech Stack:** Static HTML, CSS, Python `unittest`, BeautifulSoup, Chrome DevTools Protocol.

## Global Constraints

- Reuse `img/images/La Escultura/Addis Abbaba/02.jpg` directly; do not duplicate or modify the media file.
- Apply the replacement to PT-BR and Spanish.
- Display the complete artwork with `object-fit: contain` on desktop and mobile.
- Preserve the current vertical frame, empty `alt`, decorative semantics, and absence of a caption.
- Do not change the Addis Abbaba galleries, Contact text, or other images.
- Keep `img/Peces/03.jpg` untracked and untouched.

---

### Task 1: Replace the bilingual Contact image without cropping

**Files:**
- Create: `tests/test_contact_kite_image.py`
- Modify: `index.html:2252-2254`
- Modify: `es/index.html:2294-2296`
- Modify: `css/style.css:1156-1162`

**Interfaces:**
- Consumes: the existing `#contato .contato-img` element and canonical Addis Abbaba asset.
- Produces: bilingual Contact image sources ending in `img/images/La Escultura/Addis Abbaba/02.jpg` and shared `object-fit: contain` behavior.

- [ ] **Step 1: Write the failing source regression tests**

Create `tests/test_contact_kite_image.py`:

```python
import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
ASSET_SUFFIX = "img/images/La Escultura/Addis Abbaba/02.jpg"


class ContactKiteImageTests(unittest.TestCase):
    def test_bilingual_contact_sections_use_selected_kite(self):
        for relative in ("index.html", "es/index.html"):
            with self.subTest(relative=relative):
                soup = BeautifulSoup(
                    (ROOT / relative).read_text(encoding="utf-8"), "html.parser"
                )
                contact = soup.find(id="contato")
                image = contact.select_one(".contato-img")
                self.assertTrue(image["src"].endswith(ASSET_SUFFIX))
                self.assertEqual("", image.get("alt"))
                self.assertEqual("true", image.parent.get("aria-hidden"))

    def test_contact_image_preserves_the_complete_artwork(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        rule = re.search(r"\.contato-img\s*\{([^}]+)\}", css)
        self.assertIsNotNone(rule)
        self.assertIn("aspect-ratio: 3/4;", rule.group(1))
        self.assertIn("object-fit: contain;", rule.group(1))

    def test_selected_asset_exists_in_canonical_collection(self):
        self.assertTrue((ROOT / ASSET_SUFFIX).is_file())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused test and confirm the intended failures**

Run:

```bash
python3 -m unittest -q tests.test_contact_kite_image
```

Expected: the asset existence test passes; the bilingual source and `object-fit` tests fail because Contact still uses `lalibela.jpg` and `cover`.

- [ ] **Step 3: Replace the image sources in both pages**

In `index.html`, replace:

```html
<img alt="" class="contato-img" loading="lazy" src="img/images/legacy/lalibela.jpg"/>
```

with:

```html
<img alt="" class="contato-img" loading="lazy" src="img/images/La Escultura/Addis Abbaba/02.jpg"/>
```

In `es/index.html`, replace:

```html
<img alt="" class="contato-img" loading="lazy" src="../img/images/legacy/lalibela.jpg"/>
```

with:

```html
<img alt="" class="contato-img" loading="lazy" src="../img/images/La Escultura/Addis Abbaba/02.jpg"/>
```

- [ ] **Step 4: Preserve the full artwork in the shared desktop rule**

In the main `.contato-img` rule in `css/style.css`, change only:

```css
  object-fit: cover;
```

to:

```css
  object-fit: contain;
```

Keep the existing mobile `object-fit: contain` declaration unchanged.

- [ ] **Step 5: Run focused and adjacent rendering tests**

Run:

```bash
python3 -m unittest -q tests.test_contact_kite_image tests.test_acervo_render
```

Expected: all tests report `OK`.

- [ ] **Step 6: Commit the isolated image replacement**

```bash
git add index.html es/index.html css/style.css tests/test_contact_kite_image.py
git commit -m "feat: show complete kite in Contact"
```

Expected: only the two pages, shared stylesheet, and focused test are committed; the media asset is reused in place and `img/Peces/03.jpg` remains untracked.

---

### Task 2: Verify bilingual responsive rendering

**Files:**
- Verify only; no production file should change.

**Interfaces:**
- Consumes: the Contact image replacement from Task 1 and the local server at `http://localhost:8772`.
- Produces: evidence that the selected kite loads completely and the Contact layout remains stable.

- [ ] **Step 1: Run the complete automated suite and source checks**

Run:

```bash
python3 -m unittest discover -s tests -p 'test*.py' -q
python3 tools/acervo/audit_pt_br.py index.html
git diff --check HEAD
```

Expected: the suite reports `OK`, the PT-BR audit prints `"findings": []`, and the diff check emits no errors.

- [ ] **Step 2: Verify Contact at desktop and mobile widths**

At `http://localhost:8772/#contato` and `http://localhost:8772/es/#contato`, test widths `1440` and `390` pixels and assert:

```text
- .contato-img.currentSrc ends in /img/images/La%20Escultura/Addis%20Abbaba/02.jpg;
- the image is complete and has natural dimensions 849 × 1182;
- computed object-fit equals contain;
- the rendered image box has positive width and height;
- .contato-inner has two grid columns at 1440 px and one grid column at 390 px;
- the page has no horizontal overflow;
- the image remains decorative with alt="" and its parent has aria-hidden="true".
```

Expected: every assertion holds in PT-BR and Spanish at both widths.

- [ ] **Step 3: Confirm final repository state**

Run:

```bash
git status --short
git log -3 --oneline
```

Expected: no task-related modifications remain; the Contact image commit is present; `?? img/Peces/03.jpg` remains untracked. The visual-companion `.superpowers/` directory may remain untracked and must not be staged.
