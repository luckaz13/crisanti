# Critica Card Colors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recolor only the “Crítica” text cards with the site's light gold `#D4B38A`, dark readable typography, and a subtle edge shadow.

**Architecture:** Keep the shared `.literatura-card` component unchanged and add narrowly scoped overrides below its general rules using the existing bilingual `#critica` section ID. A focused source-level regression test protects selector scope and the approved palette, followed by browser verification in both languages and responsive widths.

**Tech Stack:** Static HTML, CSS, Python `unittest`, BeautifulSoup, Chrome DevTools Protocol.

## Global Constraints

- Apply the treatment only to `.literatura-card` descendants of `#critica`.
- Use `#D4B38A` as the card background.
- Preserve the existing HTML, copy, reading modal, and cards outside `#critica`.
- Preserve the current light button treatment.
- Apply identically to PT-BR and Spanish through the shared stylesheet.
- Keep `img/Peces/03.jpg` untracked and untouched.

---

### Task 1: Add the scoped Crítica card treatment

**Files:**
- Create: `tests/test_critica_card_style.py`
- Modify: `css/style.css` after the general `.literatura-card:hover` rule

**Interfaces:**
- Consumes: the existing bilingual `#critica` container and shared `.literatura-card` markup.
- Produces: CSS overrides qualified by `#critica` without changing the generic Literature card component.

- [ ] **Step 1: Write the failing regression tests**

Create `tests/test_critica_card_style.py`:

```python
import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]


class CriticaCardStyleTests(unittest.TestCase):
    def test_bilingual_pages_share_the_critica_scope(self):
        for relative in ("index.html", "es/index.html"):
            with self.subTest(relative=relative):
                soup = BeautifulSoup(
                    (ROOT / relative).read_text(encoding="utf-8"), "html.parser"
                )
                critica = soup.find(id="critica")
                self.assertIsNotNone(critica)
                self.assertTrue(critica.select(".literatura-card"))

    def test_critica_cards_use_scoped_gold_surface_and_subtle_shadow(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        card_rule = re.search(r"#critica \.literatura-card\s*\{([^}]+)\}", css)
        self.assertIsNotNone(card_rule)
        declarations = card_rule.group(1)
        self.assertIn("background: #D4B38A;", declarations)
        self.assertIn("border: 1px solid rgba(26, 23, 20, 0.14);", declarations)
        self.assertIn("box-shadow: 0 6px 18px rgba(26, 23, 20, 0.14);", declarations)

    def test_critica_card_copy_uses_dark_palette(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        self.assertIn("#critica .literatura-card h4", css)
        self.assertIn("#critica .literatura-card p", css)
        self.assertIn("color: #1A1714 !important;", css)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused tests and confirm the intended failure**

Run:

```bash
python3 -m unittest -q tests.test_critica_card_style
```

Expected: the bilingual structure test passes, while the CSS tests fail because the scoped `#critica` rules do not yet exist.

- [ ] **Step 3: Add the minimal scoped CSS overrides**

Insert after `.literatura-card:hover` in `css/style.css`:

```css
#critica .literatura-card {
  background: #D4B38A;
  border: 1px solid rgba(26, 23, 20, 0.14);
  box-shadow: 0 6px 18px rgba(26, 23, 20, 0.14);
}

#critica .literatura-card:hover {
  border-color: rgba(26, 23, 20, 0.2);
  box-shadow: 0 10px 24px rgba(26, 23, 20, 0.18);
}

#critica .literatura-card h4,
#critica .literatura-card h3,
#critica .literatura-card p,
#critica .literatura-card .literatura-excerpt,
#critica .literatura-card .literatura-full p {
  color: #1A1714 !important;
}
```

Do not add a `#critica .literatura-expand` override: the generic light-button rule must continue to apply.

- [ ] **Step 4: Run focused and adjacent Literature tests**

Run:

```bash
python3 -m unittest -q tests.test_critica_card_style tests.test_acervo_render
```

Expected: all tests report `OK`.

- [ ] **Step 5: Commit the isolated visual change**

```bash
git add css/style.css tests/test_critica_card_style.py
git commit -m "style: lighten Critica text cards"
```

Expected: only the stylesheet and focused test are committed; `img/Peces/03.jpg` remains untracked.

---

### Task 2: Verify responsive and cross-section behavior

**Files:**
- Verify only; no production file should change.

**Interfaces:**
- Consumes: the scoped styles from Task 1 and the local server at `http://localhost:8772`.
- Produces: evidence that the treatment is bilingual, responsive, and isolated from other Literature cards.

- [ ] **Step 1: Run the complete automated suite and source checks**

Run:

```bash
python3 -m unittest discover -s tests -p 'test*.py' -q
python3 tools/acervo/audit_pt_br.py index.html
git diff --check HEAD
```

Expected: the suite reports `OK`, the PT-BR audit prints `"findings": []`, and the diff check emits no errors.

- [ ] **Step 2: Verify the computed styles in PT-BR and Spanish**

At `http://localhost:8772/#critica` and `http://localhost:8772/es/#critica`, test widths `1440` and `390` pixels and assert:

```text
- every #critica .literatura-card has computed background rgb(212, 179, 138);
- its visible h4 and excerpt text are dark rgb(26, 23, 20);
- its box-shadow is present and uses a low-opacity dark color;
- its reading button remains light;
- a .literatura-card outside #critica retains computed background rgb(32, 30, 28);
- no horizontal overflow appears at either width.
```

Expected: all assertions hold for both languages and widths.

- [ ] **Step 3: Confirm final repository state**

Run:

```bash
git status --short
git log -3 --oneline
```

Expected: no task-related modifications remain, the style commit is present, and `?? img/Peces/03.jpg` remains untracked.
