# Remove Ensaios Escritura and Acupuntura Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the “La Escritura” and “Manos en la Acupuntura” subgalleries and their 11 source images from both language versions of the site.

**Architecture:** Delete the two tab buttons and their complete carousel panels from both static HTML entry points. Then remove the two versioned asset directories; the generic gallery JavaScript remains unchanged because the surviving tab/panel contract is preserved.

**Tech Stack:** Static HTML, Git, Python standard library structural check, shell assertions

## Global Constraints

- Remove both subgalleries from `index.html` and `es/index.html`.
- Delete all 11 versioned images under the two named directories.
- Keep “Crema” as the first active Ensaios tab and panel.
- Preserve every other Ensaios tab, panel, and asset.
- Do not modify `js/gallery-tabs.js`.
- Deleted assets remain recoverable through Git history.

---

### Task 1: Remove both subgalleries from Portuguese and Spanish markup

**Files:**
- Modify: `index.html:1997-2274`
- Modify: `es/index.html:2003-2280`

**Interfaces:**
- Consumes: `data-target` values resolved by `js/gallery-tabs.js` as `gallery-carousel-${target}`.
- Produces: six surviving Ensaios tab buttons with six matching carousel panels in each language page.

- [ ] **Step 1: Record the present references**

Run:

```bash
test "$(rg -o 'ensayos-la-escritura' index.html es/index.html | wc -l)" -eq 4
test "$(rg -o 'ensayos-manos-en-la-acupuntura' index.html es/index.html | wc -l)" -eq 4
```

Expected: both assertions exit 0, proving each identifier appears once as a tab and once as a panel in each page.

- [ ] **Step 2: Remove the two tab buttons from `index.html`**

Delete exactly these lines from the Ensaios `.gallery-tabs` element:

```html
<button class="gallery-tab" role="tab" aria-selected="false" data-target="ensayos-la-escritura">La Escritura</button>
<button class="gallery-tab" role="tab" aria-selected="false" data-target="ensayos-manos-en-la-acupuntura">Manos en la Acupuntura</button>
```

- [ ] **Step 3: Remove the two Portuguese carousel panels**

In `index.html`, delete the complete sibling blocks beginning with:

```html
<div class="gallery-carousel" id="gallery-carousel-ensayos-la-escritura" role="tabpanel" data-gallery-group="ensayos" hidden>
```

and:

```html
<div class="gallery-carousel" id="gallery-carousel-ensayos-manos-en-la-acupuntura" role="tabpanel" data-gallery-group="ensayos" hidden>
```

Delete through each block's matching closing `</div>`. The next surviving sibling must begin:

```html
<div class="gallery-carousel" id="gallery-carousel-ensayos-perspectiva" role="tabpanel" data-gallery-group="ensayos" hidden>
```

- [ ] **Step 4: Apply the equivalent removal to `es/index.html`**

Delete the same two tab buttons and the complete Spanish carousel blocks with the same IDs. Preserve their neighboring `ensayos-la-cocina` and `ensayos-perspectiva` panels unchanged.

- [ ] **Step 5: Verify tab/panel correspondence**

Run:

```bash
python3 - <<'PY'
import re
from pathlib import Path

for name in ("index.html", "es/index.html"):
    html = Path(name).read_text()
    start = html.index('aria-label="Sub-galerias de Ensayos"')
    end = html.index('</section>', start)
    section = html[start:end]
    tabs = set(re.findall(r'data-target="(ensayos-[^"]+)"', section))
    panels = set(re.findall(r'id="gallery-carousel-(ensayos-[^"]+)"', section))
    assert tabs == panels, (name, sorted(tabs - panels), sorted(panels - tabs))
    assert len(tabs) == 6, (name, len(tabs))
    assert 'class="gallery-tab active" role="tab" aria-selected="true" data-target="ensayos-crema"' in section
print("ensaios tab/panel contract: PASS")
PY
```

Expected: `ensaios tab/panel contract: PASS`.

### Task 2: Delete the original image assets and verify absence

**Files:**
- Delete: `images/galerias/Ensayos/La Escritura/01.jpg` through `07.jpg`
- Delete: `images/galerias/Ensayos/Manos en la Acupuntura/01.jpg` through `04.jpg`

**Interfaces:**
- Consumes: the 11 versioned images whose HTML references were removed in Task 1.
- Produces: no runtime interface; both asset directories disappear from the checkout while history remains in Git.

- [ ] **Step 1: Confirm the exact destructive target count**

Run:

```bash
test "$(git ls-files 'images/galerias/Ensayos/La Escritura/**' 'images/galerias/Ensayos/Manos en la Acupuntura/**' | wc -l)" -eq 11
```

Expected: exit status 0.

- [ ] **Step 2: Remove the two versioned directories**

Run:

```bash
git rm -r -- "images/galerias/Ensayos/La Escritura" "images/galerias/Ensayos/Manos en la Acupuntura"
```

Expected: Git stages deletion of exactly 11 image files.

- [ ] **Step 3: Verify complete absence and preserve unrelated code**

Run:

```bash
test ! -e "images/galerias/Ensayos/La Escritura"
test ! -e "images/galerias/Ensayos/Manos en la Acupuntura"
test "$(git diff --cached --name-only --diff-filter=D | wc -l)" -eq 11
! rg -n 'La Escritura|Manos en la Acupuntura|ensayos-la-escritura|ensayos-manos-en-la-acupuntura' index.html es/index.html
git diff --quiet HEAD -- js/gallery-tabs.js
git diff --check HEAD
```

Expected: every command exits 0 and no removed identifier remains.

- [ ] **Step 4: Verify both pages in the local server**

Open the Ensaios section in Portuguese and Spanish. Confirm six tabs remain, “Crema” opens by default, each surviving tab reveals its matching carousel, and no broken image requests refer to either removed directory.

- [ ] **Step 5: Commit the complete removal**

```bash
git add index.html es/index.html
git commit -m "content: remove escritura e acupuntura de ensaios"
```
