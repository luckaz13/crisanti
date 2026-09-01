# Task 2 — curated archive manifest

## RED

- Added `ArtistPdfRevisionTests` for removing only `La Escultura/Verde`, preserving `Vlak` and `Flores`, and restoring explicit boundaries in `Los Niños` ficha details.
- Ran `python3 -m unittest -q tests.test_acervo_curation`.
- Result: expected `ImportError` because `apply_artist_pdf_revisions` did not exist.

## GREEN

- Added `apply_artist_pdf_revisions(manifest, documents)` after `apply_fichas()`.
- The function applies fichas, excludes only the normalized gallery key `La Escultura/Verde`, and normalizes the approved `Los Niños` detail boundaries without touching source files.
- Wired `reconcile()` to apply this curation before the manifest is serialized and reported.
- Re-ran `python3 -m unittest -q tests.test_acervo_curation`: 18 tests passed.

## Regenerated artifacts

- `data/acervo/inventory.json`
- `data/acervo/documents.json`
- `data/acervo/manifest.json`
- `docs/acervo/reconciliation-report.md`

Commands run:

```bash
python3 tools/acervo/inventory.py --source img --published img/images --html index.html --output data/acervo/inventory.json
python3 tools/acervo/extract_documents.py --source img --output data/acervo/documents.json
python3 tools/acervo/reconcile.py --inventory data/acervo/inventory.json --documents data/acervo/documents.json --html index.html es/index.html --output data/acervo/manifest.json --report docs/acervo/reconciliation-report.md
python3 -m json.tool data/acervo/manifest.json >/tmp/crisanti-manifest.valid
```

Archive audit result: 1,237 publishable assets; `La Escultura/Verde` absent; `Proyectos Especiales/Vlak` and `Literatura/Ficción/Flores` present; 51 `Los Niños` assets checked for the required boundaries.

## Verification

- Focused: `python3 -m unittest -q tests.test_acervo_inventory tests.test_acervo_documents tests.test_acervo_reconcile tests.test_acervo_curation` — 30 passed.
- Full suite: `python3 -m unittest discover -s tests -p 'test_*.py' -q` — 91 passed.
- `git diff --check` passed for all task files.

## Self-review

- Confirmed filtering removes only manifest records keyed `La Escultura/Verde`; no filesystem deletion logic was introduced.
- Confirmed the curation preserves Vlak and Flores and does not alter ZIPs, `/images`, or `img/images`.
- The additional Spanish `Materiales:` boundary complements the required `Materiais?` expression because the source fichas use the Spanish spelling.
