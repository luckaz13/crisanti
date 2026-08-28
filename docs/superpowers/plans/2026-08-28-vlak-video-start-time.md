# Vlak Video Start Time Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Vlak gallery video begin at 00:10 once and resume from its paused position on later visits to the slide.

**Architecture:** The PT-BR and Spanish video elements opt in through `data-start-time="10"`. The shared gallery controller applies the configured seek once after metadata is available, then leaves the existing play/pause synchronization unchanged.

**Tech Stack:** Static HTML, vanilla JavaScript, Python `unittest`, BeautifulSoup.

## Global Constraints

- Apply the start time to both PT-BR and Spanish versions.
- Seek to 10 seconds only once per page load.
- Returning to the video slide must resume from the paused position.
- Videos without a valid `data-start-time` must retain their existing behavior.

---

### Task 1: Declarative one-time video start position

**Files:**
- Modify: `index.html:593`
- Modify: `es/index.html:597`
- Modify: `js/gallery.js:187-189`
- Test: `tests/test_vlak_video.py`

**Interfaces:**
- Consumes: `video.dataset.startTime`, `video.readyState`, `video.duration`, and the media `loadedmetadata` event.
- Produces: one-time initialization marked by `video.dataset.startTimeApplied = 'true'`.

- [ ] **Step 1: Write failing markup and controller tests**

Add tests that require both language versions to declare the start time and require the controller to guard a one-time seek:

```python
def test_video_declares_ten_second_start_time_in_both_languages(self):
    for relative in ("index.html", "es/index.html"):
        with self.subTest(relative=relative):
            video = self._section(relative).select_one("video.gallery-video")
            self.assertEqual("10", video.get("data-start-time"))

def test_controller_applies_configured_start_time_only_once(self):
    script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
    self.assertIn("function applyInitialVideoTime(video)", script)
    self.assertIn("video.dataset.startTimeApplied === 'true'", script)
    self.assertIn("video.currentTime = startTime;", script)
    self.assertIn("video.dataset.startTimeApplied = 'true';", script)
    self.assertIn("video.addEventListener('loadedmetadata', initializeVideo, { once: true });", script)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
python3 -m unittest -q tests.test_vlak_video
```

Expected: failures because neither `data-start-time="10"` nor `applyInitialVideoTime` exists.

- [ ] **Step 3: Declare the start time in both HTML documents**

Add the same attribute to the PT-BR and Spanish video tags:

```html
<video class="gallery-video" data-start-time="10" ...>
```

- [ ] **Step 4: Implement the one-time metadata initialization**

Inside `setupCarousel`, add:

```javascript
function applyInitialVideoTime(video) {
    if (video.dataset.startTimeApplied === 'true') return;
    const startTime = Number.parseFloat(video.dataset.startTime || '');
    if (!Number.isFinite(startTime) || startTime < 0 ||
        !Number.isFinite(video.duration) || startTime >= video.duration) return;
    video.currentTime = startTime;
    video.dataset.startTimeApplied = 'true';
}
```

Replace the video metadata listener with initialization that seeks before recalculating the carousel:

```javascript
videos.forEach(video => {
    const initializeVideo = () => {
        applyInitialVideoTime(video);
        updateCarousel();
    };
    if (video.readyState >= 1) {
        initializeVideo();
    } else {
        video.addEventListener('loadedmetadata', initializeVideo, { once: true });
    }
});
```

- [ ] **Step 5: Run the focused tests and verify GREEN**

Run:

```bash
python3 -m unittest -q tests.test_vlak_video
```

Expected: all Vlak video tests pass.

- [ ] **Step 6: Run the complete regression suite**

Run:

```bash
python3 -m unittest discover -s tests -p 'test*.py' -q
```

Expected: all tests pass.

- [ ] **Step 7: Validate browser behavior**

Open the PT-BR and Spanish galleries, bring the Vlak video fully into view, and verify:

1. The first playback begins at approximately 10 seconds.
2. Navigate to the next slide after playback advances.
3. Return to the video slide.
4. Playback resumes from the paused position rather than returning to 10 seconds.

- [ ] **Step 8: Update the code graph and commit**

```bash
graphify update .
git add index.html es/index.html js/gallery.js tests/test_vlak_video.py
git commit -m "feat: start Vlak video at ten seconds"
```
