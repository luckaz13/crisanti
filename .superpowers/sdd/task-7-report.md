# Task 7 report — Cuadernos height and Peces crossfade

## Root cause

`updateViewportHeight()` measured the active `figure` with `getBoundingClientRect()` after that figure had already been placed inside a height-constrained, clipped carousel. It then wrote the clipped measurement back to the viewport, creating a self-reinforcing height collapse. `.series-gallery { overflow: hidden; }` made the missing image and controls more severe. The source image `Cuadernos/00.jpg` is intrinsically square (3024×3024).

## RED → GREEN

- RED: `python3 -m unittest -q tests.test_carousel_controls tests.test_gallery_modes` ran 8 tests and failed 6 for the expected missing behaviors: intrinsic measurement/decode, scoped PT/ES opt-in, crossfade stacking, and reduced-motion duration.
- GREEN: the same focused command passed all 8 tests after implementing `measureSlideHeight(slide, availableWidth)`, image load/decode remeasurement, carousel/resize remeasurement, and the opt-in transition.
- Regression suite: `python3 -m unittest discover -s tests -p 'test*.py' -q` passed all 123 tests.
- Static gates: `node --check js/gallery.js` and `git diff --check` passed.

### Follow-up hardening

- RED: the expanded focused suite ran 12 tests and failed 5 (no test errors), proving the axis-coercion bug, ungated crossfade layout, missing source deferral/restoration, incorrect initialization order, and the reduced-motion selector contract.
- GREEN: `python3 -m unittest -q tests.test_gallery_modes tests.test_carousel_controls` passed all 12 tests after the follow-up implementation.
- Follow-up regression suite: `python3 -m unittest discover -s tests -p 'test*.py' -q` passed all 127 tests; JavaScript syntax, diff whitespace, scoped audit, and the Impeccable detector also passed.
- The resource test executes the real JavaScript helper functions under Node with fake image elements; it verifies that indices 0–4 retain `src`, later images move to `data-src`, and `preloadImage()` restores the requested source and probe.

## Implementation and scope

- Image height now comes from `min(availableWidth, naturalWidth) × naturalHeight / naturalWidth`; measured caption height and 8 px clearance are added independently of clipping.
- Recalculation occurs on initial setup, every slide change, loaded/decoded image readiness, and `ResizeObserver` updates. Video slides retain their media-height fallback.
- Only `gallery-carousel-peixes` (PT) and `gallery-carousel-peces` (ES) opt into `data-transition="crossfade"`. Navigation index, arrows, swipe, preload, autoplay, pause behavior, and video synchronization remain on the existing code paths.
- Crossfade slides share one grid area; exactly one is active and interactive. Other galleries keep their lateral `translateX` behavior. Reduced motion computes to 0.01 ms.
- `.series-gallery` now uses `overflow-x: clip` with `overflow-y: visible`; Chromium confirms both computed values without the `hidden/visible` axis coercion.
- Crossfade stacking is gated by `data-carousel-initialized="true"`. Before enabling it, images outside the initial radius are moved from `src` to `data-src`; the existing preloader restores sources only as navigation reaches their window. Without JavaScript the track stays flex and the first slide remains visible.
- Impeccable was applied as a narrow refinement of the incumbent visual system: no visual-world or content changes were introduced.

## Runtime and visual evidence

Chromium headless at 1225 px verified real artwork profiles: square Cuadernos 3024×3024 rendered 480×480 with a 628 px viewport including caption; vertical Seda 1080×1368 rendered 480×606; panoramic Fotografía 400×265 rendered at intrinsic scale with a 413 px viewport including caption. Runtime inspection found one active/interactive Peces slide with track `transform: none`, while Cuadernos remained `translateX(0%)`; emulated reduced motion reported `1e-05s`.

- Full tall capture: `/tmp/crisanti-cuadernos-fixed.png`
- Useful Cuadernos crop: `/tmp/crisanti-cuadernos-fixed-crop.png` — square artwork, caption, and both controls are fully visible.
- Impeccable detector: `node /home/lucas/.agents/skills/impeccable/scripts/detect.mjs --json index.html es/index.html css/style.css js/gallery.js` returned `[]`.
- Audit confirmed exactly one `data-transition="crossfade"` per locale page and no remaining clipped-figure height assignment.

The follow-up Chromium fixture confirmed initial crossfade state with 5 `src` / 2 `data-src`, then 7 `src` / 0 `data-src` after navigating to slide 6. The active slide was the only interactive one; a regular carousel retained `translateX(0%)`. With script execution disabled, `data-carousel-initialized` remained absent, the track computed to `flex`, and the first image remained visible and sourced.

## Concerns

No known functional concern. Chromium emitted unrelated Google Cloud Messaging authentication noise during the standalone screenshot, but the capture completed successfully.
