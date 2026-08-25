# Footer Fish Mark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the existing `FC + fish` identity mark below Fabio Crisanti's name in both localized footers.

**Architecture:** Add identical semantic brand-link markup with locale-correct paths and labels to the two static footers. Style it through footer-scoped classes so the existing animated header logo remains unaffected.

**Tech Stack:** Static HTML, shared CSS, existing transparent PNG, Python assertions, Chromium headless

## Global Constraints

- Reuse `img/Peces/03-header-mark.png`; create no new image.
- Insert the mark between `.footer-name` and `.footer-sub` in PT-BR and Spanish.
- Link to `#hero` with a localized `aria-label`.
- Use decorative `alt=""` on the fish image.
- Keep header markup and styles unchanged.
- Keep the footer compact, centered, keyboard accessible, and free of mobile overflow.

---

### Task 1: Add the localized footer brand markup

**Files:**
- Modify: `index.html` inside `.footer-inner`
- Modify: `es/index.html` inside `.footer-inner`

**Interfaces:**
- Consumes: the existing fish PNG and `#hero` anchor.
- Produces: one `.footer-brand-mark` per page containing `.footer-brand-mark__text` and `.footer-brand-mark__fish`.

- [ ] **Step 1: Run the red markup test**

```bash
python3 - <<'PY'
from pathlib import Path
for page in ('index.html', 'es/index.html'):
    html = Path(page).read_text()
    assert html.count('class="footer-brand-mark"') == 1, page
PY
```

Expected: FAIL because no footer mark exists.

- [ ] **Step 2: Add the PT-BR mark**

Immediately after `<p class="footer-name">Fabio Crisanti</p>`, add:

```html
<a class="footer-brand-mark" href="#hero" aria-label="Fabio Crisanti — voltar ao início">
  <span class="footer-brand-mark__text">FC</span>
  <img class="footer-brand-mark__fish" src="img/Peces/03-header-mark.png" alt="" />
</a>
```

- [ ] **Step 3: Add the Spanish mark**

Use the same structure with `aria-label="Fabio Crisanti — volver al inicio"` and image path `../img/Peces/03-header-mark.png`.

- [ ] **Step 4: Verify order, paths, and accessibility**

```bash
python3 - <<'PY'
from pathlib import Path
for page, src, label in (
    ('index.html', 'img/Peces/03-header-mark.png', 'Fabio Crisanti — voltar ao início'),
    ('es/index.html', '../img/Peces/03-header-mark.png', 'Fabio Crisanti — volver al inicio'),
):
    html = Path(page).read_text()
    footer = html[html.index('<footer class="site-footer">'):html.index('</footer>', html.index('<footer class="site-footer">'))]
    assert footer.count('class="footer-brand-mark"') == 1
    assert footer.index('footer-name') < footer.index('footer-brand-mark') < footer.index('footer-sub')
    assert f'src="{src}"' in footer and 'alt=""' in footer
    assert 'href="#hero"' in footer and f'aria-label="{label}"' in footer
print('footer markup: PASS')
PY
```

Expected: `footer markup: PASS`.

### Task 2: Add footer-scoped presentation and verify

**Files:**
- Modify: `css/style.css` in the footer section

**Interfaces:**
- Consumes: Task 1 footer classes.
- Produces: a compact white horizontal signature with hover/focus behavior.

- [ ] **Step 1: Run the red style test**

```bash
python3 - <<'PY'
from pathlib import Path
css = Path('css/style.css').read_text()
for selector in ('.footer-brand-mark', '.footer-brand-mark__text', '.footer-brand-mark__fish'):
    assert selector in css, selector
PY
```

Expected: FAIL because the footer classes have no styles.

- [ ] **Step 2: Add minimal footer styles**

Define `.footer-brand-mark` as a centered inline flex link with compact gap, white color, and opacity transition. Size the text with the serif font and the fish at approximately `2.2rem` wide, applying `filter: brightness(0) invert(1)`. Add subtle hover opacity and a two-pixel `:focus-visible` outline with offset. Keep all selectors footer-specific.

- [ ] **Step 3: Run structural and diff checks**

Run the Task 1 green test, the style selector test, `git diff --check`, and verify the existing `.nav-logo-mark` rules are unchanged in the diff.

- [ ] **Step 4: Test in Chromium**

In PT and ES, assert one footer mark, correct text/image/path/link, a successfully loaded image, and white fish filter. Click the mark and confirm the URL hash becomes `#hero`. At 390 px, assert the mark fits inside the viewport without horizontal overflow.

- [ ] **Step 5: Commit and re-verify**

```bash
git add index.html es/index.html css/style.css
git diff --cached --check
git commit -m "feat: add fish mark to footer"
```

Re-run all green checks from the committed state. Expected repository status: only the pre-existing untracked `img/Peces/03.jpg`.

