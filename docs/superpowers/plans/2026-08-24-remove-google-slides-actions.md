# Remove Google Slides Actions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove online Google Slides viewing from the two La Fuente y los Simios presentation cards while retaining their downloads and all Master Taxi Google Docs actions.

**Architecture:** Make a narrowly scoped static-HTML change in the La Fuente y los Simios panels in both localized pages. Verify the action counts per panel, the absence of Slides viewer URLs, the continued presence of Docs viewer URLs, and the two PowerPoint download targets.

**Tech Stack:** Static HTML, Python standard-library HTML parser, Chromium headless

## Global Constraints

- Remove only Google Slides actions from La Fuente y los Simios.
- Keep exactly two PowerPoint download actions per language.
- Keep all Google Docs and DOCX download actions in Master Taxi unchanged.
- Keep all four published Office files unchanged.
- Apply equivalent copy and behavior in PT-BR and Spanish.

---

### Task 1: Remove Google Slides links without affecting Google Docs

**Files:**
- Modify: `index.html` inside `gallery-carousel-proyectos-especiales-la-fuente-y-los-simios`
- Modify: `es/index.html` inside the same panel ID

**Interfaces:**
- Consumes: the existing `.project-document__view` and `.project-document__download` action markup.
- Produces: two La Fuente cards with one download action each; Master Taxi retains two view and two download actions.

- [ ] **Step 1: Run the red regression check**

```bash
python3 - <<'PY'
from pathlib import Path

for page in ('index.html', 'es/index.html'):
    html = Path(page).read_text()
    start = html.index('id="gallery-carousel-proyectos-especiales-la-fuente-y-los-simios"')
    end = html.index('id="gallery-carousel-proyectos-especiales-master-taxi"', start)
    panel = html[start:end]
    assert 'Google Slides' not in panel, page
    assert panel.count('project-document__download') == 2, page
PY
```

Expected: FAIL because each page still contains two Google Slides links.

- [ ] **Step 2: Remove the four localized Slides anchors**

Delete only the complete `<a class="project-document__view btn-outline" ...>Ver no Google Slides</a>` elements from the two Portuguese cards and the equivalent `Ver en Google Slides` elements from the two Spanish cards. Do not modify the neighboring download anchors or any Master Taxi markup.

- [ ] **Step 3: Run the scoped green regression check**

```bash
python3 - <<'PY'
from pathlib import Path

for page in ('index.html', 'es/index.html'):
    html = Path(page).read_text()
    lf_start = html.index('id="gallery-carousel-proyectos-especiales-la-fuente-y-los-simios"')
    mt_start = html.index('id="gallery-carousel-proyectos-especiales-master-taxi"', lf_start)
    vlak_start = html.index('id="gallery-carousel-proyectos-especiales-vlak"', mt_start)
    la_fuente = html[lf_start:mt_start]
    master_taxi = html[mt_start:vlak_start]
    assert 'Google Slides' not in la_fuente, page
    assert la_fuente.count('class="project-document"') == 2, page
    assert la_fuente.count('project-document__view') == 0, page
    assert la_fuente.count('project-document__download') == 2, page
    assert master_taxi.count('Google Docs') == 2, page
    assert master_taxi.count('project-document__view') == 2, page
    assert master_taxi.count('project-document__download') == 2, page
print('Slides removed; Docs preserved: PASS')
PY
git diff --check
```

Expected: `Slides removed; Docs preserved: PASS` and no diff errors.

- [ ] **Step 4: Test downloads, tabs, and responsive layout**

Using the local server and Chromium headless, verify in PT and ES that La Fuente shows two cards with one download button each, Master Taxi still shows two cards with two actions each, Vlak shows no cards, and switching tabs remains functional. At 390 px wide, verify the cards remain a single-column grid without horizontal overflow. Request both `.pptx` URLs and expect HTTP 200.

- [ ] **Step 5: Commit the localized change**

```bash
git add index.html es/index.html
git diff --cached --check
git commit -m "content: remove Google Slides actions"
```

### Task 2: Final verification

**Files:**
- Verify: `index.html`
- Verify: `es/index.html`
- Verify: `documents/proyectos-especiales/**`

**Interfaces:**
- Consumes: the Task 1 committed state.
- Produces: evidence that the requested action was removed without broadening scope.

- [ ] **Step 1: Re-run the Task 1 green check from the committed tree**

Expected: all assertions pass and `git diff --check HEAD` emits no output.

- [ ] **Step 2: Inspect repository status**

```bash
git status --short
```

Expected: only the pre-existing untracked `img/Peces/03.jpg`.

