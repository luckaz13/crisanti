# Add Peixes and Peces Section Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a localized 34-work Peixes/Peces section after Seda Bahia with an accessible two-second autoplay carousel and retained manual controls.

**Architecture:** Publish the exact numbered JPEG set, insert one reversed series section per locale, and extend the shared carousel with opt-in `data-autoplay` behavior. Keep autoplay isolated to configured carousels and integrate pause/restart rules with existing next/previous/swipe behavior.

**Tech Stack:** Static HTML, vanilla JavaScript, existing CSS carousel/lightbox, Git-tracked JPEGs, Python assertions, Chromium DevTools Protocol

## Global Constraints

- Publish exactly `01.jpg` through `34.jpg` from `/img/Peces` under `images/galerias/Peces/`.
- Do not publish `Texto para Peces.docx`.
- Insert after `seda-bahia` and before `juego-del-tren`.
- Use reversed grid for Peixes/Peces; do not change neighboring grid classes.
- Use labels `Peixe 01`–`Peixe 34` in PT and `Pez 01`–`Pez 34` in ES.
- Configure only these carousels with `data-autoplay="2000"`.
- Advance one slide per interval and wrap automatically from last to first.
- Pause for hover, focus-within, hidden document, and reduced motion.
- Manual previous/next/swipe restarts a complete two-second interval.
- Preserve manual button limits and all existing carousel/lightbox behavior.

---

### Task 1: Publish the 34 JPEG assets

**Files:**
- Read: `/home/lucas/Projetos/crisanti/img/Peces/{01..34}.jpg`
- Create: `images/galerias/Peces/{01..34}.jpg`

- [ ] **Step 1: Run a red exact-set assertion** expecting 34 filenames.
- [ ] **Step 2: Copy only filenames generated from integers 1–34; do not glob the intake folder.**
- [ ] **Step 3: Assert exact destination set, byte identity for all pairs, and absence of DOCX.**
- [ ] **Step 4: Commit with `assets: add Peces works`.**

### Task 2: Add localized section markup

**Files:**
- Modify: `index.html` between Seda Bahia and Juego del Tren
- Modify: `es/index.html` at the equivalent boundary

- [ ] **Step 1: Run a red test for missing `section#peixes` and `section#peces`.**
- [ ] **Step 2: Add a reversed PT section with title `Peixes`, the approved PT paragraph, localized WhatsApp CTA, and carousel `gallery-carousel-peixes` carrying `data-autoplay="2000"`.**
- [ ] **Step 3: Emit 34 PT slides in exact order. Each uses `Peixe NN` as `.gallery-title`, `Peixe NN — Fabio Crisanti` as alt text, and no invented metadata.**
- [ ] **Step 4: Add the equivalent ES section with title `Peces`, approved Spanish paragraph, localized CTA, carousel `gallery-carousel-peces`, and labels `Pez NN`. Paths begin `../images/`.**
- [ ] **Step 5: Assert section order, reversed class, exact 34 paths/labels, autoplay attribute, neighboring normal grids, and existing files. Run `git diff --check`.**

### Task 3: Implement opt-in accessible autoplay test-first

**Files:**
- Modify: `js/gallery.js` inside `setupCarousel`

**Interfaces:**
- Consumes: optional positive integer from `carouselEl.dataset.autoplay`.
- Produces: one managed timeout per configured carousel; no timer for unconfigured carousels.

- [ ] **Step 1: Run a red static contract test** asserting the script reads `dataset.autoplay`, checks `prefers-reduced-motion`, listens for visibility/focus/hover, and clears a timer.
- [ ] **Step 2: Add state:** parsed `autoplayDelay`, `autoplayTimer`, `pointerPaused`, `focusPaused`, and a `MediaQueryList` for reduced motion.
- [ ] **Step 3: Add `canAutoplay()`, `stopAutoplay()`, and `scheduleAutoplay()`.** `scheduleAutoplay` clears the existing timeout, returns for missing/invalid delay or any pause condition, and otherwise sets one timeout that increments the index or wraps to zero, updates the carousel, then schedules again.
- [ ] **Step 4: Extend manual navigation.** After successful previous, next, or swipe navigation, call `scheduleAutoplay()` so a fresh interval begins.
- [ ] **Step 5: Add pause/resume listeners:** pointer enter/leave, focusin/focusout with deferred containment check, `visibilitychange`, and reduced-motion `change`. Start scheduling after initial setup.
- [ ] **Step 6: Run `node --check`, the static contract test, and `git diff --check`.**

### Task 4: Browser behavior, commit, and final verification

**Files:**
- Verify: `index.html`, `es/index.html`, `js/gallery.js`, `images/galerias/Peces/**`

- [ ] **Step 1: Request all 34 JPEG URLs and expect HTTP 200/image content.**
- [ ] **Step 2: In PT and ES at desktop width, assert section order and visual normal → reversed → normal positioning.**
- [ ] **Step 3: Assert autoplay advances from slide 1 to 2 after approximately two seconds and advances only one slide per tick.**
- [ ] **Step 4: Navigate manually and assert the next automatic move occurs only after a fresh interval. Assert wrap from slide 34 to 1.**
- [ ] **Step 5: Assert no movement during hover and focus; emulate reduced motion and assert no movement. Assert an unconfigured carousel remains stationary.**
- [ ] **Step 6: Open the first image in the lightbox and assert counter `1 / 34`, then navigate to `2 / 34`. At 390 px, assert no overflow.**
- [ ] **Step 7: Commit HTML and JavaScript with `feat: add autoplay Peixes gallery`.**
- [ ] **Step 8: Re-run exact asset, markup, syntax, browser, and status checks from committed state.** Expected status: only pre-existing `img/Peces/03.jpg`.

