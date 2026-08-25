# Vlak Train Video Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `vlak.mp4` as the first slide of the Train Game carousel, rename the section bilingually, and autoplay the muted video only while its slide is active and visible.

**Architecture:** The video is a fixed editorial slide prepended directly to the existing bilingual static carousel, while the 72 manifest-independent legacy image slides remain untouched. The generic carousel controller gains opt-in media synchronization by detecting `.gallery-video`; `IntersectionObserver` supplies viewport state and every carousel index update synchronizes play/pause without resetting playback.

**Tech Stack:** Static HTML, CSS, MP4/H.264/AAC, vanilla JavaScript, Python `unittest`, BeautifulSoup, Chrome DevTools Protocol.

## Global Constraints

- Incorporate `/home/lucas/Projetos/crisanti/videos/vlak.mp4` as tracked `videos/vlak.mp4` without transcoding or modifying it.
- Title PT-BR: `Vlak: O jogo do trem`.
- Title Spanish: `Vlak: El juego del tren`.
- Preserve `juego-del-tren` IDs, all 72 current images, their order, arrows, indicators, and manual navigation.
- Use `muted`, `playsinline`, `preload="metadata"`, and native `controls`; do not use static `autoplay` or `loop` attributes.
- Play only while the video slide is active, its carousel is visible, and the document is visible.
- Pause without resetting `currentTime`; resume from that time when eligible again.
- Do not autoplay again after the video reaches its end; native controls must still permit manual replay.
- Do not expose the video through the image lightbox.
- Keep `img/Peces/03.jpg` untracked and untouched.
- Preserve the backup worktree after completion.

---

### Task 1: Add the bilingual Vlak slide and responsive video surface

**Files:**
- Create: `videos/vlak.mp4` by copying the provided binary without modification
- Create: `tests/test_vlak_video.py`
- Modify: `index.html:549-595`
- Modify: `es/index.html:548-594`
- Modify: `css/style.css` after the general `.gallery-img` rules

**Interfaces:**
- Consumes: `/home/lucas/Projetos/crisanti/videos/vlak.mp4`, `#gallery-carousel-juego-del-tren`, and the existing `.gallery-slide > .gallery-figure` contract.
- Produces: a first `.gallery-slide--video` containing `.gallery-video`, followed by the unchanged 72 image slides in each locale.

- [ ] **Step 1: Write the failing content and media tests**

Create `tests/test_vlak_video.py`:

```python
import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]


class VlakVideoTests(unittest.TestCase):
    def _section(self, relative):
        soup = BeautifulSoup(
            (ROOT / relative).read_text(encoding="utf-8"), "html.parser"
        )
        return soup.find(id="juego-del-tren")

    def test_video_asset_is_the_provided_mp4(self):
        video = ROOT / "videos/vlak.mp4"
        self.assertTrue(video.is_file())
        self.assertEqual(24_103_420, video.stat().st_size)

    def test_bilingual_titles_are_reviewed(self):
        expected = {
            "index.html": "Vlak: O jogo do trem",
            "es/index.html": "Vlak: El juego del tren",
        }
        for relative, title in expected.items():
            with self.subTest(relative=relative):
                self.assertEqual(
                    title, self._section(relative).select_one(".section-title").get_text(strip=True)
                )

    def test_video_is_first_slide_and_images_keep_their_order(self):
        expected_first_image = {
            "index.html": "img/images/legacy/highres/Juego del Tren/1.jpg",
            "es/index.html": "../img/images/legacy/highres/Juego del Tren/1.jpg",
        }
        for relative, first_image in expected_first_image.items():
            with self.subTest(relative=relative):
                section = self._section(relative)
                slides = section.select(".gallery-track > .gallery-slide")
                video = slides[0].select_one("video.gallery-video")
                self.assertIsNotNone(video)
                self.assertEqual(73, len(slides))
                self.assertEqual(72, len(section.select(".gallery-slide .gallery-img")))
                self.assertEqual(first_image, slides[1].select_one(".gallery-img")["src"])

    def test_video_has_manual_controls_and_no_static_autoplay_or_loop(self):
        expected_source = {
            "index.html": "videos/vlak.mp4",
            "es/index.html": "../videos/vlak.mp4",
        }
        for relative, source in expected_source.items():
            with self.subTest(relative=relative):
                video = self._section(relative).select_one("video.gallery-video")
                self.assertEqual("", video.get("controls"))
                self.assertEqual("", video.get("muted"))
                self.assertEqual("", video.get("playsinline"))
                self.assertEqual("metadata", video.get("preload"))
                self.assertIsNone(video.get("autoplay"))
                self.assertIsNone(video.get("loop"))
                self.assertEqual(source, video.select_one("source")["src"])

    def test_video_surface_is_scoped_and_uncropped(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        rule = re.search(r"\.gallery-video\s*\{([^}]+)\}", css)
        self.assertIsNotNone(rule)
        self.assertIn("aspect-ratio: 478 / 850;", rule.group(1))
        self.assertIn("object-fit: contain;", rule.group(1))
        self.assertIn("max-height: 78vh;", rule.group(1))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused test and confirm the intended failures**

Run:

```bash
python3 -m unittest -q tests.test_vlak_video
```

Expected: all five tests fail because the worktree lacks the video, reviewed titles, first video slide, required attributes, and scoped CSS.

- [ ] **Step 3: Copy the provided video without transcoding**

Run:

```bash
mkdir -p videos
cp /home/lucas/Projetos/crisanti/videos/vlak.mp4 videos/vlak.mp4
sha256sum /home/lucas/Projetos/crisanti/videos/vlak.mp4 videos/vlak.mp4
```

Expected: both SHA-256 hashes are identical.

- [ ] **Step 4: Rename the section and prepend the PT-BR video slide**

In `index.html`, replace only the section title text with:

```html
<h2 class="section-title">Vlak: O jogo do trem</h2>
```

Immediately inside `.gallery-track`, before the current first image slide, insert:

```html
<div class="gallery-slide gallery-slide--video" data-index="vlak-video">
<figure class="gallery-figure gallery-figure--video">
<video aria-label="Vlak: O jogo do trem" class="gallery-video" controls="" muted="" playsinline="" preload="metadata">
<source src="videos/vlak.mp4" type="video/mp4"/>
</video>
</figure>
</div>
```

- [ ] **Step 5: Rename the section and prepend the Spanish video slide**

In `es/index.html`, replace only the section title text with:

```html
<h2 class="section-title">Vlak: El juego del tren</h2>
```

Immediately inside `.gallery-track`, before the current first image slide, insert:

```html
<div class="gallery-slide gallery-slide--video" data-index="vlak-video">
<figure class="gallery-figure gallery-figure--video">
<video aria-label="Vlak: El juego del tren" class="gallery-video" controls="" muted="" playsinline="" preload="metadata">
<source src="../videos/vlak.mp4" type="video/mp4"/>
</video>
</figure>
</div>
```

- [ ] **Step 6: Add the scoped responsive video surface**

Add to `css/style.css` after the general gallery image rules:

```css
.gallery-figure--video {
  background: var(--c-bg-dark);
}

.gallery-video {
  display: block;
  width: 100%;
  aspect-ratio: 478 / 850;
  max-height: 78vh;
  object-fit: contain;
  background: var(--c-bg-dark);
}
```

- [ ] **Step 7: Run focused and adjacent rendering tests**

Run:

```bash
python3 -m unittest -q tests.test_vlak_video tests.test_acervo_render tests.test_carousel_controls
```

Expected: all tests report `OK`; the renderer test confirms unrelated generated galleries remain stable.

- [ ] **Step 8: Commit the media and static presentation**

```bash
git add videos/vlak.mp4 index.html es/index.html css/style.css tests/test_vlak_video.py
git commit -m "feat: add Vlak video to train carousel"
```

Expected: the binary, bilingual pages, CSS, and focused test are committed; `img/Peces/03.jpg` remains untracked.

---

### Task 2: Synchronize video playback with slide and viewport visibility

**Files:**
- Modify: `tests/test_vlak_video.py`
- Modify: `js/gallery.js:9-225`

**Interfaces:**
- Consumes: `.gallery-video`, the carousel’s private `currentIndex`, the existing `updateCarousel()` call path, document visibility, and `IntersectionObserver`.
- Produces: private `syncVideoPlayback(): void`, which plays eligible video slides and pauses all ineligible video slides without touching `currentTime`.

- [ ] **Step 1: Add failing controller-contract tests**

Append to `VlakVideoTests` in `tests/test_vlak_video.py`:

```python
    def test_controller_requires_active_slide_and_visible_carousel(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
        self.assertIn("function syncVideoPlayback()", script)
        self.assertIn("slideIndex === currentIndex", script)
        self.assertIn("carouselVisible", script)
        self.assertIn("document.visibilityState === 'visible'", script)
        self.assertIn("!video.ended", script)

    def test_controller_plays_safely_and_pauses_without_resetting(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
        self.assertIn("video.play()", script)
        self.assertIn("playPromise.catch(() => {})", script)
        self.assertIn("video.pause()", script)
        self.assertNotIn("video.currentTime = 0", script)

    def test_controller_observes_viewport_and_syncs_after_navigation(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
        self.assertIn("new IntersectionObserver", script)
        self.assertIn("visibilityObserver.observe(viewport)", script)
        self.assertIn("syncVideoPlayback();", script)
```

- [ ] **Step 2: Run the controller tests and confirm the intended failures**

Run:

```bash
python3 -m unittest -q tests.test_vlak_video
```

Expected: the five static-content tests pass; the three controller tests fail because synchronization is not implemented.

- [ ] **Step 3: Track carousel visibility and video elements**

Inside `setupCarousel()`, after the current pause-state variables, add:

```js
        const videos = [...carouselEl.querySelectorAll('.gallery-video')];
        let carouselVisible = false;
```

- [ ] **Step 4: Implement the isolated playback synchronizer**

Before `updateCarousel()`, add:

```js
        function syncVideoPlayback() {
            videos.forEach(video => {
                const slide = video.closest('.gallery-slide');
                const slideIndex = [...slides].indexOf(slide);
                const shouldPlay = slideIndex === currentIndex && carouselVisible &&
                    document.visibilityState === 'visible' && !video.ended;
                if (shouldPlay && video.paused) {
                    const playPromise = video.play();
                    if (playPromise && typeof playPromise.catch === 'function') {
                        playPromise.catch(() => {});
                    }
                } else if (!shouldPlay && !video.paused) {
                    video.pause();
                }
            });
        }
```

Do not write to `video.currentTime` anywhere.

- [ ] **Step 5: Synchronize after every carousel update**

At the end of `updateCarousel()`, after ARIA button state updates, add:

```js
            syncVideoPlayback();
```

This automatically covers arrows, swipe, carousel autoplay, lazy tab initialization, and resize updates because all paths already call `updateCarousel()`.

- [ ] **Step 6: Observe carousel and document visibility**

After initial carousel setup and before pointer/focus handlers, add:

```js
        if ('IntersectionObserver' in window) {
            const visibilityObserver = new IntersectionObserver(entries => {
                carouselVisible = entries.some(entry => entry.isIntersecting);
                syncVideoPlayback();
            }, { threshold: 0.25 });
            visibilityObserver.observe(viewport);
        } else {
            carouselVisible = true;
            syncVideoPlayback();
        }
```

Replace the existing document visibility listener:

```js
        document.addEventListener('visibilitychange', scheduleAutoplay);
```

with:

```js
        document.addEventListener('visibilitychange', () => {
            scheduleAutoplay();
            syncVideoPlayback();
        });
```

- [ ] **Step 7: Recalculate carousel geometry when video metadata loads**

After the existing image load-listener loop, add:

```js
        videos.forEach(video => {
            video.addEventListener('loadedmetadata', updateCarousel, { once: true });
        });
```

- [ ] **Step 8: Run focused and carousel regression tests**

Run:

```bash
python3 -m unittest -q tests.test_vlak_video tests.test_carousel_controls tests.test_lightbox_captions
```

Expected: all tests report `OK`; the lightbox tests confirm video slides remain excluded because `getCarouselItems()` filters entries without `.gallery-img` sources.

- [ ] **Step 9: Commit the visibility-aware playback behavior**

```bash
git add js/gallery.js tests/test_vlak_video.py
git commit -m "feat: autoplay visible Vlak slide"
```

Expected: only the controller and its focused tests are committed.

---

### Task 3: Verify generation stability and real browser behavior

**Files:**
- Verify only; no production files should change.

**Interfaces:**
- Consumes: the complete bilingual pages, tracked video, controller, and local server.
- Produces: evidence that generation preserves the fixed video slide and playback obeys all approved states.

- [ ] **Step 1: Verify gallery regeneration does not remove the fixed slide**

Run:

```bash
sha256sum index.html es/index.html > /tmp/vlak-before.sha256
python3 tools/acervo/render_galleries.py --manifest data/acervo/manifest.json --pt index.html --es es/index.html
sha256sum index.html es/index.html > /tmp/vlak-after.sha256
diff -u /tmp/vlak-before.sha256 /tmp/vlak-after.sha256
```

Expected: the diff emits no differences because Juego del Tren is not a generated `GALLERY_TARGETS` entry.

- [ ] **Step 2: Run the complete automated suite and audits**

Run:

```bash
python3 -m unittest discover -s tests -p 'test*.py' -q
python3 tools/acervo/audit_pt_br.py index.html
python3 tools/acervo/audit_references.py index.html es/index.html css/style.css
git diff --check HEAD
```

Expected: tests report `OK`, PT-BR findings are empty, reference audit reports no legacy or missing references, and the diff check is clean.

- [ ] **Step 3: Validate PT-BR and Spanish at 1440 px and 390 px**

For `http://localhost:8772/#juego-del-tren` and `http://localhost:8772/es/#juego-del-tren`, assert at each width:

```text
- the localized title is exact;
- the first slide contains the 478 × 850 video and the second contains the former first image;
- video.muted is true, controls are visible, loop and autoplay attributes are absent;
- the whole video is contained without horizontal overflow;
- when the first slide and carousel are visible, currentTime advances while muted;
- navigating to the second slide pauses and preserves currentTime;
- returning to the first slide resumes from the preserved time;
- scrolling the carousel out of view pauses and preserves currentTime;
- returning it to view resumes;
- after forcing the ended state, visibility changes do not restart playback;
- clicking an image slide still opens the image lightbox, while clicking video controls does not.
```

Expected: every assertion holds in both languages and widths.

- [ ] **Step 4: Confirm final repository state**

Run:

```bash
git status --short
git log -4 --oneline
git worktree list
```

Expected: only `?? img/Peces/03.jpg` remains in the feature worktree, the three Vlak commits are visible, and the backup worktree remains registered.
