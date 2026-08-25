# Acervo Editorial Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile the published bilingual catalog with the artist's authoritative `/img/` archive, publish current and still-used legacy media under `/img/images/`, and enrich every gallery with ordered images, localized texts, captions, and accessible behavior.

**Architecture:** A tested Python audit pipeline reads the external editorial archive, extracts Office metadata, matches media by hash and visual identity, and produces a versioned JSON manifest. A deterministic renderer uses reviewed manifest content to update the static PT/ES pages; published media lives only in `/img/images/`. The old `/images/` tree remains untouched until browser approval, then becomes an ignored local backup in the final gated task.

**Tech Stack:** Python 3 standard library, Pillow when available for dimensions/perceptual review, static HTML5, CSS, vanilla JavaScript, GitHub Pages, Chromium headless/CDP.

## Global Constraints

- `/home/lucas/Projetos/crisanti/img/` is the authoritative editorial source; do not rename or edit artist-delivered originals.
- Natural filename order (`00`, `01`, `02`...) overrides DOCX numbering.
- Preserve site-only legacy works; never remove them based solely on absence from `/img/`.
- Publish shared media under `/img/images/`; PT and ES share files but localize prose, captions, and `alt` text.
- Correct Spanish spelling and grammar without stylistic rewriting; translate faithfully to PT-BR.
- Keep Peixes/Peces free of visible captions.
- Never invent missing metadata or silently resolve conflicts.
- Do not rewrite Git history in this plan; use the separate history-cleanup plan only after visual approval.
- Preserve the untracked `img/Peces/03.jpg` already present in the worktree unless the manifest migration explicitly supersedes it with the authoritative source.

---

### Task 1: Build the deterministic archive inventory

**Files:**
- Create: `tools/acervo/inventory.py`
- Create: `tests/test_acervo_inventory.py`
- Create: `data/acervo/.gitkeep`

**Interfaces:**
- Produces: `natural_key(name: str) -> tuple`, `sha256_file(path: Path) -> str`, `scan_media(root: Path) -> list[MediaRecord]`, and `MediaRecord(path, section, series, filename, order, sha256, width, height)`.
- Consumes: an explicit `--source` path; never assumes that the worktree's `/img/` contains the local master archive.

- [ ] **Step 1: Write failing unit tests**

Test that `natural_key("10.jpg")` sorts after `natural_key("02.jpg")`, duplicate bytes share a hash, and section/series are derived from relative paths without losing accents.

- [ ] **Step 2: Run the focused tests and confirm failure**

Run: `python3 -m unittest -q tests.test_acervo_inventory`

Expected: import failure because `tools.acervo.inventory` does not exist.

- [ ] **Step 3: Implement the inventory module and CLI**

The CLI must accept:

```text
python3 tools/acervo/inventory.py \
  --source /home/lucas/Projetos/crisanti/img \
  --published images \
  --html index.html \
  --output data/acervo/inventory.json
```

Write stable UTF-8 JSON with sorted keys and relative logical source paths beginning with `img/`.

- [ ] **Step 4: Run tests and generate the baseline inventory**

Expected baseline: 453 source images, 448 unique source hashes, and no mutation under the source directory.

- [ ] **Step 5: Commit the inventory foundation**

```bash
git add tools/acervo/inventory.py tests/test_acervo_inventory.py data/acervo/.gitkeep data/acervo/inventory.json
git commit -m "feat: inventory authoritative art archive"
```

### Task 2: Extract and normalize editorial documents

**Files:**
- Create: `tools/acervo/extract_documents.py`
- Create: `tests/test_acervo_documents.py`
- Create: `data/acervo/documents.json`

**Interfaces:**
- Produces: `extract_docx(path) -> DocumentText`, `extract_pptx(path) -> DocumentText`, `extract_pdf(path) -> DocumentText`, and normalized paragraph/table records retaining original order.
- Consumes: inventory source root and DOCX/PPTX/PDF files beneath it.

- [ ] **Step 1: Add fixture-driven extraction tests**

Cover paragraphs, tables used by fichas, accented text, empty cells, slide order, and duplicate PDF/DOCX material. Assert that table cell boundaries are retained rather than flattened ambiguously.

- [ ] **Step 2: Run tests and confirm they fail**

Run: `python3 -m unittest -q tests.test_acervo_documents`

- [ ] **Step 3: Implement extraction with ZIP/XML parsing and a bounded PDF fallback**

DOCX and PPTX extraction must use their XML structures. PDF extraction may call `pdftotext` only when available; otherwise record `extraction_status: unavailable` instead of failing silently.

- [ ] **Step 4: Generate `documents.json` and compare totals**

Expected: 73 DOCX, 2 PPTX, and 3 PDF records, each carrying its source path, type, extracted content, and extraction status.

- [ ] **Step 5: Commit document extraction**

```bash
git add tools/acervo/extract_documents.py tests/test_acervo_documents.py data/acervo/documents.json
git commit -m "feat: extract archive editorial documents"
```

### Task 3: Produce the reconciliation manifest and conflict report

**Files:**
- Create: `tools/acervo/reconcile.py`
- Create: `tests/test_acervo_reconcile.py`
- Create: `data/acervo/manifest.json`
- Create: `docs/acervo/reconciliation-report.md`

**Interfaces:**
- Produces: classifications `atual`, `novo`, `legado-em-uso`, `substituído`, and `conflito`; `reconcile(source, published, references, documents) -> Manifest`.
- Consumes: `inventory.json`, `documents.json`, PT/ES HTML references, and current media hashes.

- [ ] **Step 1: Write tests for exact match, renamed match, missing source, legacy reference, duplicate, and ambiguous match**

The ambiguous case must result in `conflito`, never an arbitrary choice. A source filename order mismatch must produce an explicit order change.

- [ ] **Step 2: Confirm the reconciliation tests fail**

Run: `python3 -m unittest -q tests.test_acervo_reconcile`

- [ ] **Step 3: Implement deterministic reconciliation**

Use exact SHA-256 first, then dimensions and bounded perceptual comparison only as suggestions requiring `visual_status: pending`. Record current HTML usage separately from physical presence.

- [ ] **Step 4: Generate and manually inspect the report**

The report must enumerate every source gallery, source count, current referenced count, desired order, new items, legacy-in-use items, conflicts, and associated documents. Confirm the known new galleries Gatos, La Papa, and Flores appear.

- [ ] **Step 5: Commit the manifest and report**

```bash
git add tools/acervo/reconcile.py tests/test_acervo_reconcile.py data/acervo/manifest.json docs/acervo/reconciliation-report.md
git commit -m "feat: reconcile editorial and published archives"
```

### Task 4: Review Seda and Ensaios editorial data

**Files:**
- Modify: `data/acervo/manifest.json`
- Create: `docs/acervo/review-seda-ensaios.md`

**Interfaces:**
- Produces reviewed `text.es`, `text.pt`, `caption.es`, `caption.pt`, `alt.es`, `alt.pt`, and `visual_status` fields.
- Covers: Seda, Seda 2024, Seda Bahia, Collagem, Crema/Emulsión, El Teléfono, Gatos, La Cocina, Perspectiva, Siluetas, and Urubús.

- [ ] **Step 1: Match each numbered image to its ficha row and record discrepancies**
- [ ] **Step 2: Visually inspect every source image in filename order**
- [ ] **Step 3: Correct Spanish grammar and spelling without changing voice**
- [ ] **Step 4: Add faithful PT-BR translations and meaningful localized alt text**
- [ ] **Step 5: Validate JSON and commit the reviewed group**

Run: `python3 -m json.tool data/acervo/manifest.json >/tmp/crisanti-manifest.valid`

```bash
git add data/acervo/manifest.json docs/acervo/review-seda-ensaios.md
git commit -m "content: review Seda and Ensaios archive"
```

### Task 5: Review Escultura, Fotografía, and Moda editorial data

**Files:**
- Modify: `data/acervo/manifest.json`
- Create: `docs/acervo/review-escultura-fotografia-moda.md`

**Interfaces:**
- Covers: Addis Abbaba, Invierno II, Invierno III, Pez III, Pez IV, Soies Sauvages, retained Verde legacy, Cotidiano, Exilio, Luz Líquida, and Moda.

- [ ] **Step 1: Resolve gallery boundaries, especially the current combined Invierno presentation**
- [ ] **Step 2: Match and visually inspect all numbered images**
- [ ] **Step 3: Add reviewed ES metadata and faithful PT-BR translations**
- [ ] **Step 4: Record credits, dimensions, materials, and missing-data cases without invention**
- [ ] **Step 5: Validate and commit**

```bash
git add data/acervo/manifest.json docs/acervo/review-escultura-fotografia-moda.md
git commit -m "content: review sculpture photography and fashion archive"
```

### Task 6: Review Laberintos, Niños, Proyectos Especiales, and Literatura

**Files:**
- Modify: `data/acervo/manifest.json`
- Create: `docs/acervo/review-laberintos-ninos-proyectos-literatura.md`

**Interfaces:**
- Covers all current and new subseries, including La Papa, Gatos only in its Ensaios group, Flores fiction, completed El Nombre fiction, La Fuente y los Simios, Master Taxi document links, and Vlak.

- [ ] **Step 1: Match ficha rows and inspect images in authoritative filename order**
- [ ] **Step 2: Incorporate each associated prose document in ES and PT-BR**
- [ ] **Step 3: Preserve all eight existing Crítica articles and mark duplicate literary excerpts intentionally reused**
- [ ] **Step 4: Verify project download files and classify Master Taxi's single image**
- [ ] **Step 5: Validate and commit**

```bash
git add data/acervo/manifest.json docs/acervo/review-laberintos-ninos-proyectos-literatura.md
git commit -m "content: review remaining editorial archive"
```

### Task 7: Materialize the consolidated published asset tree

**Files:**
- Create: `tools/acervo/publish_assets.py`
- Create: `tests/test_acervo_publish.py`
- Create: `img/images/**`

**Interfaces:**
- Produces: `publish_manifest(manifest, source_root, legacy_root, output_root, dry_run=True) -> PublishReport`.
- Consumes only reviewed manifest entries classified `atual`, `novo`, or `legado-em-uso`.

- [ ] **Step 1: Test dry-run, collision refusal, checksum verification, and idempotence**
- [ ] **Step 2: Confirm tests fail before implementation**
- [ ] **Step 3: Implement copy-only publishing with explicit roots**

Never delete source or legacy files. Refuse an output collision unless bytes are identical. After copying, verify every output hash against the manifest.

- [ ] **Step 4: Run a dry-run and review counts before copying**

```bash
python3 tools/acervo/publish_assets.py --manifest data/acervo/manifest.json --source /home/lucas/Projetos/crisanti/img --legacy images --output img/images --dry-run
```

- [ ] **Step 5: Materialize, verify, and commit the active assets**

```bash
git add tools/acervo/publish_assets.py tests/test_acervo_publish.py img/images
git commit -m "assets: consolidate active catalog media"
```

### Task 8: Render synchronized gallery content from the manifest

**Files:**
- Create: `tools/acervo/render_galleries.py`
- Create: `tests/test_acervo_render.py`
- Modify: `index.html`
- Modify: `es/index.html`
- Modify: `js/gallery-tabs.js`
- Modify: `css/style.css`

**Interfaces:**
- Produces deterministic PT/ES gallery markup and synchronized tab panels.
- Consumes reviewed manifest records and `/img/images/` URLs.

- [ ] **Step 1: Add rendering tests for order, localized text, optional metadata, caption omission for Peixes, and tab-panel linkage**
- [ ] **Step 2: Run tests and confirm failure**
- [ ] **Step 3: Implement deterministic section rendering with explicit generated-region markers**

Use stable markers such as `<!-- acervo:ensayos:start -->` and `<!-- acervo:ensayos:end -->`; refuse to render if either marker is missing or duplicated.

- [ ] **Step 4: Update tab behavior so text and gallery switch as one panel**

Keep keyboard tab semantics, `aria-selected`, `hidden`, focus behavior, and the existing carousel initialization guard.

- [ ] **Step 5: Render both pages, inspect the diff, run tests, and commit**

```bash
python3 tools/acervo/render_galleries.py --manifest data/acervo/manifest.json --pt index.html --es es/index.html
python3 -m unittest -q tests.test_acervo_render
git add tools/acervo/render_galleries.py tests/test_acervo_render.py index.html es/index.html js/gallery-tabs.js css/style.css
git commit -m "feat: render reconciled bilingual galleries"
```

### Task 9: Migrate every remaining active media reference

**Files:**
- Modify: `index.html`
- Modify: `es/index.html`
- Modify: `css/style.css`
- Modify: `README.md`
- Create: `tools/acervo/audit_references.py`
- Create: `tests/test_acervo_references.py`

**Interfaces:**
- Produces a zero-exit reference audit that checks HTML, CSS, JS, download links, and file existence.

- [ ] **Step 1: Write a failing audit test that rejects active `/images/` URLs and missing local targets**
- [ ] **Step 2: Implement the bounded static reference auditor**
- [ ] **Step 3: Move non-gallery active media into `/img/images/site/` or classify it as legacy-in-use**
- [ ] **Step 4: Update all PT/ES/CSS references and README structure documentation**
- [ ] **Step 5: Run the audit and commit**

Expected: `0 active references to /images/; 0 missing local assets`.

### Task 10: Perform full functional, accessibility, and visual verification

**Files:**
- Create: `tests/browser/acervo-smoke.js`
- Modify: `data/acervo/manifest.json`
- Create: `docs/acervo/verification-report.md`

**Interfaces:**
- Browser suite covers PT, ES, desktop, 390px mobile, all tabs, all carousels, lightbox, autoplay, controls, downloads, and broken-resource collection.

- [ ] **Step 1: Start the static server and run the asset audit**
- [ ] **Step 2: Run browser smoke tests in PT and ES**
- [ ] **Step 3: Compare each gallery's DOM order with the manifest**
- [ ] **Step 4: Perform visual sampling and then full sequence review, recording `visual_status: approved` or a concrete conflict**
- [ ] **Step 5: Run `git diff --check`, verify only expected untracked local source files remain, and commit the report**

Do not proceed to Task 11 until the user explicitly approves the local preview.

### Task 11: Retire `/images/` from version control while preserving the local backup

**Files:**
- Modify: `.gitignore`
- Delete from Git index after backup: `images/**`
- Preserve locally: `images/**`
- Modify: `docs/acervo/verification-report.md`

**Interfaces:**
- Consumes an explicit user approval of Task 10.
- Produces a site that loads exclusively from `/img/images/` while the old tree remains on local disk and ignored.

- [ ] **Step 1: Verify zero active references and create a checksum inventory of the local legacy tree**
- [ ] **Step 2: Copy the legacy tree to an explicit temporary safety location before changing the index**
- [ ] **Step 3: Add `/images/` to `.gitignore` and remove it from the Git index without deleting the preserved local copy**
- [ ] **Step 4: Re-run static and browser verification from a clean checkout simulation**
- [ ] **Step 5: Commit the retirement and hand off to the separate history-cleanup plan**

```bash
git add .gitignore docs/acervo/verification-report.md
git commit -m "chore: retire legacy images tree"
```

The actual index-removal command must be chosen during execution after the explicit backup path and target list are verified. It must not use a broad unresolved variable or delete the local directory.

