# Task 8 report — Vlak surface and expandable trajectory

## RED → GREEN

- RED: `python3 -m unittest -q tests.test_vlak_video tests.test_timeline_expand` initially ran 16 tests and failed 8 for the expected missing transparent video surface, localized controls, semantic collapsed region, and controller behavior. A responsive-alignment test then failed before its compact rule was added.
- GREEN: the final focused suite passed all 17 tests after the minimal CSS, HTML, and JavaScript changes.
- Regression suite: `python3 -m unittest discover -s tests -p 'test_*.py' -q` passed all 134 tests.
- Static gates: `node --check js/main.js` and `git diff --check` passed.

## Implementation and accessibility

- The Vlak figure and video backgrounds are transparent; `aspect-ratio: 478 / 850`, `max-height: 78vh`, and `object-fit: contain` are unchanged, so no video crop or recoding is introduced.
- Each locale presents two of six timeline entries initially. The remaining four live in a native `hidden` region, preserving a meaningful collapsed no-JavaScript view.
- A native button supports click, touch, and keyboard activation. It keeps `aria-expanded`, `aria-controls`, and its PT/ES labels in sync (`Ver mais`/`Ver menos`, `Ver más`/`Ver menos`).
- Collapse leaves focus on the clicked button. Scroll correction is only attempted while collapsing when the toggle was above the viewport.
- The control follows the incumbent editorial system with an accessible focus ring, intrinsic-sized label for both translations, and compact-width alignment with the timeline content.

## Audit

- `node /home/lucas/.agents/skills/impeccable/scripts/detect.mjs --json css/style.css js/main.js index.html es/index.html` returned `[]`.
- Desktop and mobile Chromium captures confirmed the incumbent page still renders at 1440px and 390px widths. The timeline remains semantically verified by the focused tests; hash-route headless capture was blank because offscreen `content-visibility` was not painted by Chromium's one-shot screenshot path.
- `graphify update .` rebuilt the local graph (1118 nodes, 1380 edges).

## Concerns

No known functional concern. Chromium emitted unrelated Google Cloud Messaging authentication noise during standalone screenshots.
