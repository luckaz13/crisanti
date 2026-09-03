#!/usr/bin/env node

import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdir, mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { basename, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = fileURLToPath(new URL('../..', import.meta.url));
const CAPTURE_FLAG = '--capture-dir';
const captureFlagIndex = process.argv.indexOf(CAPTURE_FLAG);
const captureDir = captureFlagIndex >= 0 ? process.argv[captureFlagIndex + 1] : null;
const OUTPUT_FLAG = '--output';
const outputFlagIndex = process.argv.indexOf(OUTPUT_FLAG);
const outputPath = outputFlagIndex >= 0 ? process.argv[outputFlagIndex + 1] : null;
const chromium = process.env.CHROMIUM_BIN ||
  (existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : 'chromium');
// The Python harness imports this budget and grants Chromium startup + probe + cleanup time.
export const PROBE_TIMING = Object.freeze({
  capturedProbeMs: 105_000,
  cleanupKillWaitMs: 5_000,
  cleanupResidualWaitMs: 3_000,
  cleanupReserveMs: 11_000,
  cleanupTermWaitMs: 3_000,
  contactSheetCommandMs: 5_000,
  startupMs: 15_000,
  uncapturedProbeMs: 80_000,
});
const probeTimeoutMs = captureDir ? PROBE_TIMING.capturedProbeMs : PROBE_TIMING.uncapturedProbeMs;
const contactSheetCommandTimeoutMs = PROBE_TIMING.contactSheetCommandMs;
const captureFrames = [];
let navigationSequence = 0;

function withTimeout(promise, timeoutMs, message) {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(message)), timeoutMs);
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function connectToPage(child) {
  const input = child.stdio[3];
  const output = child.stdio[4];
  let nextId = 0;
  const pending = new Map();
  let sessionId = null;
  let buffer = Buffer.alloc(0);
  input.on('error', () => {});
  output.on('error', () => {});

  const dispatch = frame => {
    const message = JSON.parse(frame.toString('utf8'));
    if (!message.id) return;
    const waiter = pending.get(message.id);
    if (!waiter) return;
    pending.delete(message.id);
    if (message.error) waiter.reject(new Error(waiter.method + ': ' + message.error.message));
    else waiter.resolve(message.result);
  };
  output.on('data', chunk => {
    buffer = Buffer.concat([buffer, chunk]);
    let delimiter;
    while ((delimiter = buffer.indexOf(0)) >= 0) {
      const frame = buffer.subarray(0, delimiter);
      buffer = buffer.subarray(delimiter + 1);
      if (frame.length) dispatch(frame);
    }
  });

  const rawSend = (method, params = {}, targetSessionId = null) =>
    new Promise((resolve, reject) => {
      const id = ++nextId;
      pending.set(id, { method, resolve, reject });
      const message = { id, method, params };
      if (targetSessionId) message.sessionId = targetSessionId;
      input.write(JSON.stringify(message) + '\0');
    });
  const targets = await rawSend('Target.getTargets');
  const page = targets.targetInfos.find(target => target.type === 'page');
  if (!page) throw new Error('Chromium did not expose a page target');
  sessionId = (await rawSend('Target.attachToTarget', {
    flatten: true,
    targetId: page.targetId,
  })).sessionId;

  return {
    close: () => input.end(),
    send: (method, params = {}) => rawSend(method, params, sessionId),
  };
}

async function evaluate(cdp, expression) {
  const result = await cdp.send('Runtime.evaluate', {
    awaitPromise: true,
    expression,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text);
  }
  return result.result.value;
}

async function callPage(cdp, fn, ...args) {
  const serializedArgs = args.map(value => JSON.stringify(value)).join(',');
  return evaluate(cdp, '(' + fn.toString() + ')(' + serializedArgs + ')');
}

async function waitForPage(cdp) {
  await callPage(cdp, async function waitUntilReady() {
    await new Promise((resolve, reject) => {
      const deadline = performance.now() + 15000;
      const ready = () => {
        const carousels = [...document.querySelectorAll('.gallery-carousel')];
        const initialized = carousels.length > 0 && carousels.every(
          carousel => carousel.dataset.carouselInitialized === 'true'
        );
        if (document.readyState !== 'loading' && initialized) return resolve(true);
        if (performance.now() > deadline) {
          return reject(new Error('gallery initialization timeout'));
        }
        requestAnimationFrame(ready);
      };
      ready();
    });
    return true;
  });
}

async function waitForVisibleGalleryMedia(cdp) {
  await callPage(cdp, async function waitUntilVisibleMediaLoads() {
    await new Promise((resolve, reject) => {
      const deadline = performance.now() + 15000;
      const ready = () => {
        const carousels = [...document.querySelectorAll('.gallery-carousel')].filter(carousel => {
          const bounds = carousel.querySelector('.gallery-viewport')?.getBoundingClientRect();
          return bounds && bounds.width > 0 && bounds.height > 0;
        });
        const loaded = carousels.every(carousel => {
          const slide = carousel.dataset.transition === 'crossfade'
            ? carousel.querySelector('.gallery-slide.is-active')
            : carousel.querySelector('.gallery-slide');
          const media = slide?.querySelector('.gallery-img, .gallery-video');
          return media?.tagName === 'VIDEO'
            ? media.readyState >= 1
            : media?.complete && media.naturalWidth > 0;
        });
        if (carousels.length > 0 && loaded) return resolve(true);
        if (performance.now() > deadline) {
          return reject(new Error('visible gallery media timeout'));
        }
        requestAnimationFrame(ready);
      };
      ready();
    });
    return true;
  });
}

async function waitForUrl(cdp, url) {
  const deadline = Date.now() + 10_000;
  while (Date.now() <= deadline) {
    try {
      if (await evaluate(cdp, 'location.href') === url) return;
    } catch {
      // The previous execution context is destroyed while navigation commits.
    }
    await wait(25);
  }
  throw new Error('Page navigation timed out: ' + url);
}

async function navigate(cdp, url) {
  const target = new URL(url);
  target.searchParams.set('gallery-probe', String(++navigationSequence));
  const targetUrl = target.href;
  await cdp.send('Page.navigate', { url: targetUrl });
  await waitForUrl(cdp, targetUrl);
  await withTimeout(waitForPage(cdp), 20_000, 'Page initialization timed out: ' + targetUrl);
  await withTimeout(
    waitForVisibleGalleryMedia(cdp),
    20_000,
    'Gallery media timed out: ' + targetUrl
  );
}

async function waitForCarouselMedia(cdp, carouselId) {
  await callPage(cdp, async function waitForMedia(id) {
    await new Promise((resolve, reject) => {
      const deadline = performance.now() + 15000;
      const ready = () => {
        const carousel = document.getElementById(id);
        const slide = carousel?.dataset.transition === 'crossfade'
          ? carousel.querySelector('.gallery-slide.is-active')
          : carousel?.querySelector('.gallery-slide');
        const media = slide?.querySelector('.gallery-img, .gallery-video');
        if (media?.tagName === 'VIDEO' && media.readyState >= 1) return resolve(true);
        if (media?.tagName === 'IMG' && media.complete && media.naturalWidth > 0) {
          return resolve(true);
        }
        if (performance.now() > deadline) return reject(new Error('media timeout: ' + id));
        requestAnimationFrame(ready);
      };
      ready();
    });
    return true;
  }, carouselId);
}

async function waitForImage(cdp, selector) {
  await callPage(cdp, async function waitUntilImageLoads(targetSelector) {
    await new Promise((resolve, reject) => {
      const deadline = performance.now() + 15000;
      const ready = () => {
        const image = document.querySelector(targetSelector);
        if (image?.complete && image.naturalWidth > 0) return resolve(true);
        if (performance.now() > deadline) {
          return reject(new Error('image load timeout: ' + targetSelector));
        }
        requestAnimationFrame(ready);
      };
      ready();
    });
    return true;
  }, selector);
}

async function settleLayout(cdp) {
  await callPage(cdp, async function settle() {
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    return true;
  });
}

async function screenshot(cdp, name) {
  captureFrames.push(name);
  if (!captureDir) return;
  await mkdir(captureDir, { recursive: true });
  const result = await cdp.send('Page.captureScreenshot', {
    captureBeyondViewport: false,
    format: 'png',
    fromSurface: true,
  });
  await writeFile(join(captureDir, name + '.png'), Buffer.from(result.data, 'base64'));
}

async function scrollAndCapture(cdp, selector, name) {
  const found = await callPage(cdp, function scrollTarget(targetSelector) {
    const element = document.querySelector(targetSelector);
    if (!element) return false;
    element.scrollIntoView({ behavior: 'instant', block: 'center', inline: 'nearest' });
    return true;
  }, selector);
  if (!found) throw new Error('Capture target not found: ' + selector);
  await settleLayout(cdp);
  await screenshot(cdp, name);
}

async function disableHorizontalOverflowMask(cdp) {
  return callPage(cdp, function disableMask() {
    const actual = {
      body: getComputedStyle(document.body).overflowX,
      documentElement: getComputedStyle(document.documentElement).overflowX,
    };
    document.documentElement.style.setProperty('overflow-x', 'visible', 'important');
    document.body.style.setProperty('overflow-x', 'visible', 'important');
    return actual;
  });
}

async function activateGallery(cdp, carouselId) {
  const activated = await callPage(cdp, function activate(id) {
    const carousel = document.getElementById(id);
    if (!carousel) return false;
    if (carousel.hidden) {
      const target = id.replace(/^gallery-carousel-/, '');
      const tab = [...document.querySelectorAll('.gallery-tab')]
        .find(candidate => candidate.dataset.target === target);
      if (!tab) return false;
      tab.click();
    }
    const media = carousel.querySelector(
      carousel.dataset.transition === 'crossfade'
        ? '.gallery-slide.is-active .gallery-img, .gallery-slide.is-active .gallery-video'
        : '.gallery-slide .gallery-img, .gallery-slide .gallery-video'
    );
    if (media?.tagName === 'IMG') media.loading = 'eager';
    return !carousel.hidden;
  }, carouselId);
  if (!activated) throw new Error('Unable to activate gallery: ' + carouselId);
  await waitForCarouselMedia(cdp, carouselId);
  await callPage(cdp, function refreshActivatedCarousel(id) {
    const carousel = document.getElementById(id);
    if (typeof carousel._updateCarousel === 'function') carousel._updateCarousel();
    return true;
  }, carouselId);
  await settleLayout(cdp);
}

async function measureGallery(cdp, carouselId, initiallyHidden) {
  return callPage(cdp, function measure(id, wasInitiallyHidden) {
    const carousel = document.getElementById(id);
    const section = carousel.closest('section.series, .literatura-subsection');
    const viewport = carousel.querySelector('.gallery-viewport');
    const slide = carousel.dataset.transition === 'crossfade'
      ? carousel.querySelector('.gallery-slide.is-active')
      : carousel.querySelector('.gallery-slide');
    const media = slide?.querySelector('.gallery-img, .gallery-video');
    const seriesGallery = carousel.closest('.series-gallery');
    const rect = element => {
      const value = element.getBoundingClientRect();
      return {
        bottom: value.bottom,
        height: value.height,
        left: value.left,
        right: value.right,
        top: value.top,
        width: value.width,
      };
    };
    return {
      bodyScrollWidth: document.body.scrollWidth,
      carouselId: id,
      documentScrollWidth: document.documentElement.scrollWidth,
      gallery: rect(carousel),
      initiallyHidden: wasInitiallyHidden,
      media: rect(media),
      mediaComplete: media.tagName === 'VIDEO'
        ? media.readyState >= 1
        : media.complete && media.naturalWidth > 0,
      mediaKind: media.tagName.toLowerCase(),
      section: rect(section),
      sectionId: section.id,
      seriesOverflowX: seriesGallery ? getComputedStyle(seriesGallery).overflowX : null,
      seriesOverflowY: seriesGallery ? getComputedStyle(seriesGallery).overflowY : null,
      viewport: rect(viewport),
    };
  }, carouselId, initiallyHidden);
}

async function measureAllGalleries(cdp) {
  const inventory = await callPage(cdp, function galleryInventory() {
    return [...document.querySelectorAll('.gallery-carousel')].map(carousel => ({
      id: carousel.id,
      initiallyHidden: carousel.hidden,
    }));
  });
  const galleries = [];
  for (const item of inventory) {
    await activateGallery(cdp, item.id);
    galleries.push(await measureGallery(cdp, item.id, item.initiallyHidden));
  }
  return galleries;
}

async function measureSlide(cdp, sectionId, slideIndex) {
  return callPage(cdp, function measureTargetSlide(id, index) {
    const section = document.getElementById(id);
    const carousel = section.querySelector('.gallery-carousel');
    const viewport = carousel.querySelector('.gallery-viewport');
    const track = carousel.querySelector('.gallery-track');
    const slide = carousel.querySelectorAll('.gallery-slide')[index];
    const media = slide.querySelector('.gallery-img, .gallery-video');
    const rect = element => {
      const value = element.getBoundingClientRect();
      return {
        bottom: value.bottom,
        height: value.height,
        left: value.left,
        right: value.right,
        top: value.top,
        width: value.width,
      };
    };
    const naturalWidth = media.videoWidth || media.naturalWidth;
    const naturalHeight = media.videoHeight || media.naturalHeight;
    return {
      complete: media.tagName === 'VIDEO' ? media.readyState >= 1 : media.complete,
      media: rect(media),
      naturalAspect: naturalWidth / naturalHeight,
      naturalHeight,
      naturalWidth,
      objectFit: getComputedStyle(media).objectFit,
      renderedAspect: media.getBoundingClientRect().width / media.getBoundingClientRect().height,
      section: rect(section),
      src: media.currentSrc || media.src,
      trackInlineTransform: track.style.transform,
      trackTransform: getComputedStyle(track).transform,
      viewport: rect(viewport),
    };
  }, sectionId, slideIndex);
}

async function advanceToSlide(cdp, sectionId, slideIndex) {
  await callPage(cdp, function advance(id, index) {
    const carousel = document.getElementById(id).querySelector('.gallery-carousel');
    const previous = carousel.querySelector('.gallery-btn--prev');
    const next = carousel.querySelector('.gallery-btn--next');
    while (!previous.disabled) previous.click();
    for (let position = 0; position < index; position += 1) next.click();
  }, sectionId, slideIndex);
  const selector = '#' + sectionId + ' .gallery-slide:nth-child(' + (slideIndex + 1) +
    ') .gallery-img';
  await waitForImage(cdp, selector);
  await callPage(cdp, async function waitForSlidePosition(id, targetSelector) {
    const carousel = document.getElementById(id).querySelector('.gallery-carousel');
    if (typeof carousel._updateCarousel === 'function') carousel._updateCarousel();
    await new Promise((resolve, reject) => {
      const deadline = performance.now() + 3000;
      const ready = () => {
        const media = document.querySelector(targetSelector);
        const viewport = media.closest('.gallery-viewport');
        const mediaBounds = media.getBoundingClientRect();
        const viewportBounds = viewport.getBoundingClientRect();
        if (
          mediaBounds.left >= viewportBounds.left - 2 &&
          mediaBounds.right <= viewportBounds.right + 2
        ) {
          return resolve(true);
        }
        if (performance.now() > deadline) {
          return reject(new Error('slide transition timeout: ' + targetSelector));
        }
        requestAnimationFrame(ready);
      };
      ready();
    });
    return true;
  }, sectionId, selector);
  await settleLayout(cdp);
  return measureSlide(cdp, sectionId, slideIndex);
}

async function measureBrands(cdp, prefix) {
  const brands = await callPage(cdp, function brandState() {
    const state = (containerSelector, textSelector, markSelector) => {
      const container = document.querySelector(containerSelector);
      const text = container.querySelector(textSelector);
      const mark = container.querySelector(markSelector);
      const bounds = container.getBoundingClientRect();
      return {
        height: bounds.height,
        markComplete: mark.complete && mark.naturalWidth > 0,
        markNaturalHeight: mark.naturalHeight,
        markNaturalWidth: mark.naturalWidth,
        text: text.textContent.trim(),
      };
    };
    return {
      footer: state('.footer-brand-mark', '.footer-brand-mark__fc', '.footer-brand-mark__fish'),
      header: state('.nav-logo', '.nav-logo-text', '.nav-logo-mark'),
    };
  });
  await scrollAndCapture(cdp, '#site-header', prefix + '-brand-header');
  await scrollAndCapture(cdp, '.footer-brand-mark', prefix + '-brand-footer');
  return brands;
}

async function measureTimeline(cdp, prefix) {
  await callPage(cdp, function collapseTimeline() {
    const toggle = document.querySelector('[data-timeline-toggle]');
    if (toggle.getAttribute('aria-expanded') === 'true') toggle.click();
    return true;
  });
  await settleLayout(cdp);
  const readState = () => callPage(cdp, function timelineState() {
    const toggle = document.querySelector('[data-timeline-toggle]');
    const content = document.getElementById(toggle.getAttribute('aria-controls'));
    return {
      collapsibleItemCount: content.querySelectorAll('.timeline-item').length,
      contentHidden: content.hidden,
      expanded: toggle.getAttribute('aria-expanded') === 'true',
      label: toggle.textContent.trim(),
      toggleHidden: toggle.hidden,
    };
  });
  const collapsed = await readState();
  await scrollAndCapture(cdp, '.timeline', prefix + '-timeline-collapsed');
  await callPage(cdp, function expandTimeline() {
    document.querySelector('[data-timeline-toggle]').click();
    return true;
  });
  await settleLayout(cdp);
  const expanded = await readState();
  await scrollAndCapture(cdp, '.timeline', prefix + '-timeline-expanded');
  return { collapsed, expanded };
}

async function measureCritica(cdp, prefix) {
  const result = await callPage(cdp, function criticismState() {
    const cards = [...document.querySelectorAll('#critica .literatura-card')];
    return {
      backgroundColors: [...new Set(cards.map(card => getComputedStyle(card).backgroundColor))],
      cardCount: cards.length,
      cardIds: cards.map(card => card.id),
    };
  });
  await scrollAndCapture(cdp, '#critica .literatura-grid', prefix + '-critica-cards');
  return result;
}

async function measureMasterTaxi(cdp, prefix) {
  const carouselId = 'gallery-carousel-proyectos-especiales-master-taxi';
  await activateGallery(cdp, carouselId);
  const result = await callPage(cdp, function masterTaxiState(id) {
    const panel = document.getElementById(id);
    const synopsis = panel.querySelector('.master-taxi-synopsis');
    const documentCard = panel.querySelector('.project-document');
    return {
      documentLinkCount: documentCard.querySelectorAll('a').length,
      documentName: documentCard.querySelector('.project-document__name').textContent.trim(),
      panelVisible: !panel.hidden,
      synopsisHeading: synopsis.querySelector('h3').textContent.trim(),
      synopsisParagraphCount: synopsis.querySelectorAll('p').length,
    };
  }, carouselId);
  await scrollAndCapture(
    cdp,
    '#' + carouselId + ' .master-taxi-synopsis h3',
    prefix + '-master-taxi-synopsis'
  );
  await scrollAndCapture(
    cdp,
    '#' + carouselId + ' .project-document',
    prefix + '-master-taxi-dinamica'
  );
  return result;
}

async function measureLaberintos(cdp, prefix) {
  const carouselId = 'gallery-carousel-los-laberintos-cadaver-exquisito';
  await activateGallery(cdp, carouselId);
  const imageCaptureName = prefix + '-laberintos-image';
  const textCaptureName = prefix + '-laberintos-text';
  await scrollAndCapture(
    cdp,
    '#' + carouselId + ' .gallery-viewport',
    imageCaptureName
  );
  await scrollAndCapture(cdp, '#los-laberintos .series-copy-display', textCaptureName);
  return callPage(cdp, function laberintosState(imageName, textName, sequence) {
    const display = document.querySelector('#los-laberintos .series-copy-display');
    const panel = document.getElementById('gallery-carousel-los-laberintos-cadaver-exquisito');
    return {
      activePanelVisible: !panel.hidden,
      copyTextLength: display.textContent.trim().length,
      imageCapturedBeforeText: sequence.indexOf(imageName) < sequence.indexOf(textName),
    };
  }, imageCaptureName, textCaptureName, captureFrames);
}

async function measureFiction(cdp, prefix) {
  const elNombreId = 'gallery-carousel-ficcao-el-nombre';
  const floresId = 'gallery-carousel-ficcao-flores';
  await activateGallery(cdp, elNombreId);
  const elNombre = await callPage(cdp, function elNombreState(panelId) {
    const section = document.getElementById('ficcao');
    const title = section.querySelector('.literatura-work-title');
    const gallery = document.getElementById(panelId);
    const copy = section.querySelector(
      '[data-rendered-series-copy="ficcao-el-nombre"]'
    );
    const follows = (first, second) =>
      Boolean(first.compareDocumentPosition(second) & Node.DOCUMENT_POSITION_FOLLOWING);
    return {
      copyTextLength: copy.textContent.trim().length,
      panelVisible: !gallery.hidden,
      title: title.textContent.trim(),
      titleGalleryCopyOrder: follows(title, gallery) && follows(gallery, copy),
    };
  }, elNombreId);
  await scrollAndCapture(cdp, '#ficcao .literatura-work-title', prefix + '-el-nombre-title');
  await scrollAndCapture(cdp, '#' + elNombreId, prefix + '-el-nombre-gallery');
  await scrollAndCapture(
    cdp,
    '[data-rendered-series-copy="ficcao-el-nombre"]',
    prefix + '-el-nombre-text'
  );

  const before = await callPage(cdp, function floresBefore(panelId) {
    const panel = document.getElementById(panelId);
    const template = document.querySelector('template[data-series-copy="ficcao-flores"]');
    return {
      slides: [...panel.querySelectorAll('.gallery-slide')].map(slide => {
        const image = slide.querySelector('.gallery-img');
        return {
          alt: image.alt,
          caption: slide.querySelector('.gallery-caption')?.textContent.trim() || '',
          src: image.getAttribute('src'),
        };
      }),
      templateText: template.content.textContent.trim(),
    };
  }, floresId);
  await activateGallery(cdp, floresId);
  const flores = await callPage(cdp, function floresAfter(panelId, original) {
    const panel = document.getElementById(panelId);
    const template = document.querySelector('template[data-series-copy="ficcao-flores"]');
    const slides = [...panel.querySelectorAll('.gallery-slide')].map(slide => {
      const image = slide.querySelector('.gallery-img');
      return {
        alt: image.alt,
        caption: slide.querySelector('.gallery-caption')?.textContent.trim() || '',
        src: image.getAttribute('src'),
      };
    });
    return {
      panelPresent: Boolean(panel),
      panelVisible: !panel.hidden,
      templatePreserved:
        JSON.stringify(slides) === JSON.stringify(original.slides) &&
        template.content.textContent.trim() === original.templateText &&
        original.templateText.length > 0,
    };
  }, floresId, before);
  await scrollAndCapture(cdp, '#' + floresId, prefix + '-flores-gallery');
  await scrollAndCapture(
    cdp,
    '#ficcao .series-copy-display:not([data-rendered-series-copy])',
    prefix + '-flores-text'
  );
  return { elNombre, flores };
}

async function measurePecesMotion(cdp, sectionId, prefix) {
  await cdp.send('Emulation.setEmulatedMedia', {
    features: [{ name: 'prefers-reduced-motion', value: 'no-preference' }],
  });
  const before = await callPage(cdp, function preparePeces(id) {
    const carousel = document.getElementById(id).querySelector('.gallery-carousel');
    const previous = carousel.querySelector('.gallery-btn--prev');
    carousel.dispatchEvent(new PointerEvent('pointerenter'));
    while (!previous.disabled) previous.click();
    const slides = [...carousel.querySelectorAll('.gallery-slide')];
    const active = slides.findIndex(slide => slide.classList.contains('is-active'));
    carousel.querySelector('.gallery-btn--next').click();
    const style = getComputedStyle(slides[1]);
    const durations = style.transitionDuration.split(',').map(value => {
      const trimmed = value.trim();
      return trimmed.endsWith('ms')
        ? Number.parseFloat(trimmed)
        : Number.parseFloat(trimmed) * 1000;
    });
    return {
      beforeActiveIndex: active,
      reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
      transitionDurationMs: Math.max(...durations),
      transitionProperty: style.transitionProperty,
    };
  }, sectionId);
  await wait(650);
  const after = await callPage(cdp, function readPeces(id) {
    const carousel = document.getElementById(id).querySelector('.gallery-carousel');
    const slides = [...carousel.querySelectorAll('.gallery-slide')];
    return {
      activeIndex: slides.findIndex(slide => slide.classList.contains('is-active')),
      activeOpacity: getComputedStyle(slides[1]).opacity,
      previousOpacity: getComputedStyle(slides[0]).opacity,
      trackTransform: getComputedStyle(carousel.querySelector('.gallery-track')).transform,
    };
  }, sectionId);
  await scrollAndCapture(cdp, '#' + sectionId + ' .series-gallery', prefix + '-peces-crossfade');
  return {
    ...before,
    activeOpacity: after.activeOpacity,
    afterActiveIndex: after.activeIndex,
    previousOpacity: after.previousOpacity,
    trackTransform: after.trackTransform,
  };
}

async function measureLightbox(cdp, cuadernosId, prefix) {
  await advanceToSlide(cdp, cuadernosId, 0);
  await callPage(cdp, function openLightbox(id) {
    document.querySelector('#' + id + ' .gallery-slide:first-child .gallery-img').click();
    return true;
  }, cuadernosId);
  await waitForImage(cdp, '#lightbox-img');
  await callPage(cdp, function resetLightboxScroll() {
    document.querySelector('.lightbox-content').scrollTop = 0;
    return true;
  });
  const focus = await callPage(cdp, function focusLightboxContent() {
    const close = document.querySelector('#lightbox-close');
    const content = document.querySelector('.lightbox-content');
    close.focus();
    const closeFocusedBeforeContent = document.activeElement === close;
    content.focus();
    return {
      closeFocusedBeforeContent,
      contentFocused: document.activeElement === content,
    };
  });
  await settleLayout(cdp);
  const result = await callPage(cdp, function lightboxState(backgroundSectionId, focusState) {
    const image = document.querySelector('#lightbox-img');
    const caption = document.querySelector('#lightbox-caption');
    const content = document.querySelector('.lightbox-content');
    const lightbox = document.querySelector('#lightbox');
    const parseColor = value => {
      const parts = value.match(/[\d.]+/g).map(Number);
      return { r: parts[0], g: parts[1], b: parts[2], a: parts[3] ?? 1 };
    };
    const composite = (foreground, background) => ({
      r: foreground.r * foreground.a + background.r * (1 - foreground.a),
      g: foreground.g * foreground.a + background.g * (1 - foreground.a),
      b: foreground.b * foreground.a + background.b * (1 - foreground.a),
      a: 1,
    });
    const luminance = color => {
      const channels = [color.r, color.g, color.b].map(value => {
        const normalized = value / 255;
        return normalized <= 0.04045
          ? normalized / 12.92
          : ((normalized + 0.055) / 1.055) ** 2.4;
      });
      return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
    };
    const pageBackground = parseColor(
      getComputedStyle(document.getElementById(backgroundSectionId)).backgroundColor
    );
    const overlay = composite(parseColor(getComputedStyle(lightbox).backgroundColor), pageBackground);
    const foreground = composite(parseColor(getComputedStyle(caption).color), overlay);
    const light = Math.max(luminance(foreground), luminance(overlay));
    const dark = Math.min(luminance(foreground), luminance(overlay));
    const rect = element => {
      const value = element.getBoundingClientRect();
      return {
        bottom: value.bottom,
        height: value.height,
        left: value.left,
        right: value.right,
        top: value.top,
        width: value.width,
      };
    };
    return {
      caption: rect(caption),
      captionContrast: (light + 0.05) / (dark + 0.05),
      captionText: caption.textContent.trim(),
      closeFocusedBeforeContent: focusState.closeFocusedBeforeContent,
      contentFocusable: content.tabIndex >= 0,
      contentFocused: focusState.contentFocused,
      contentIsScrollOwner: ['auto', 'scroll'].includes(getComputedStyle(content).overflowY),
      hidden: lightbox.hidden,
      image: rect(image),
      imageComplete: image.complete,
      imageNaturalHeight: image.naturalHeight,
      imageNaturalWidth: image.naturalWidth,
      viewport: { height: innerHeight, width: innerWidth },
    };
  }, cuadernosId, focus);
  await screenshot(cdp, prefix + '-lightbox-cuadernos');
  await callPage(cdp, function closeLightbox() {
    document.querySelector('#lightbox-close').click();
    return true;
  });
  return result;
}

async function probePage(cdp, baseUrl, language, viewport) {
  const pagePath = language === 'pt' ? 'index.html' : 'es/index.html';
  const cuadernosId = language === 'pt' ? 'cadernos' : 'cuadernos';
  const pecesId = language === 'pt' ? 'peixes' : 'peces';
  const prefix = language + '-' + viewport.width + 'x' + viewport.height;
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    deviceScaleFactor: 1,
    height: viewport.height,
    mobile: viewport.width < 600,
    screenHeight: viewport.height,
    screenWidth: viewport.width,
    width: viewport.width,
  });
  await cdp.send('Emulation.setEmulatedMedia', {
    features: [{ name: 'prefers-reduced-motion', value: 'reduce' }],
  });
  await navigate(cdp, baseUrl + '/' + pagePath + '#' + cuadernosId);
  const actualOverflow = await disableHorizontalOverflowMask(cdp);
  await settleLayout(cdp);
  const galleries = await measureAllGalleries(cdp);
  const pageGeometry = await callPage(cdp, function pageGeometryState(actual) {
    return {
      actualOverflow: actual,
      bodyScrollWidth: document.body.scrollWidth,
      documentScrollWidth: document.documentElement.scrollWidth,
      innerWidth,
      overflowMaskDisabled:
        getComputedStyle(document.body).overflowX === 'visible' &&
        getComputedStyle(document.documentElement).overflowX === 'visible',
    };
  }, actualOverflow);

  const brands = await measureBrands(cdp, prefix);
  const timeline = await measureTimeline(cdp, prefix);
  const critica = await measureCritica(cdp, prefix);
  const masterTaxi = await measureMasterTaxi(cdp, prefix);
  const laberintos = await measureLaberintos(cdp, prefix);
  const fiction = await measureFiction(cdp, prefix);
  const cuadernosSquare = await advanceToSlide(cdp, cuadernosId, 0);
  await scrollAndCapture(cdp, '#' + cuadernosId + ' .series-gallery', prefix + '-cuadernos-square');
  const cuadernosVertical = await advanceToSlide(cdp, cuadernosId, 1);
  await scrollAndCapture(cdp, '#' + cuadernosId + ' .series-gallery', prefix + '-cuadernos-vertical');
  const cuadernosPanoramic = await advanceToSlide(cdp, cuadernosId, 9);
  await scrollAndCapture(
    cdp,
    '#' + cuadernosId + ' .series-gallery',
    prefix + '-cuadernos-panoramic'
  );
  const vlak = await measureSlide(cdp, 'juego-del-tren', 0);
  await scrollAndCapture(cdp, '#juego-del-tren .series-gallery', prefix + '-vlak-video');
  const peces = await measurePecesMotion(cdp, pecesId, prefix);
  const lightbox = await measureLightbox(cdp, cuadernosId, prefix);

  return {
    brands,
    critica,
    cuadernosPanoramic,
    cuadernosSquare,
    cuadernosVertical,
    fiction,
    galleries,
    laberintos,
    language,
    lightbox,
    masterTaxi,
    pageGeometry,
    pagePath,
    peces,
    timeline,
    viewport,
    vlak,
  };
}

export async function runCommand(command, args, { timeoutMs = contactSheetCommandTimeoutMs } = {}) {
  let child;
  const completion = new Promise((resolve, reject) => {
    child = spawn(command, args, { stdio: ['ignore', 'ignore', 'pipe'] });
    let stderr = '';
    child.stderr.on('data', chunk => {
      if (stderr.length < 8000) stderr += chunk.toString();
    });
    child.once('error', reject);
    child.once('exit', code => {
      if (code === 0) resolve();
      else reject(new Error(command + ' exited ' + code + ': ' + stderr.trim()));
    });
  });
  try {
    await withTimeout(completion, timeoutMs, command + ' timed out after ' + timeoutMs + 'ms');
  } catch (error) {
    if (!childHasExited(child)) {
      child.kill('SIGTERM');
      if (!(await waitForChildExit(child, 1000))) child.kill('SIGKILL');
    }
    throw error;
  }
}

async function createContactSheets() {
  if (!captureDir) return [];
  const sheets = [];
  for (const language of ['pt', 'es']) {
    for (const viewport of ['390x844', '1440x1000']) {
      const prefix = language + '-' + viewport;
      const files = captureFrames
        .filter(name => name.startsWith(prefix + '-'))
        .map(name => join(captureDir, name + '.png'));
      const output = join(captureDir, prefix + '-contact-sheet.png');
      await runCommand('magick', [
        'montage',
        ...files,
        '-thumbnail', '360x240',
        '-tile', '4x',
        '-geometry', '+8+24',
        '-background', '#171513',
        '-fill', '#ffffff',
        '-pointsize', '12',
        '-set', 'label', '%t',
        output,
      ], { timeoutMs: contactSheetCommandTimeoutMs });
      sheets.push(output);
    }
  }
  return sheets;
}

function childHasExited(child) {
  return !child || child.exitCode !== null || child.signalCode !== null;
}

async function waitForChildExit(child, timeoutMs) {
  if (childHasExited(child)) return true;
  return new Promise(resolve => {
    const onExit = () => {
      clearTimeout(timer);
      resolve(true);
    };
    const timer = setTimeout(() => {
      child.removeListener('exit', onExit);
      resolve(childHasExited(child));
    }, timeoutMs);
    child.once('exit', onExit);
  });
}

function signalBrowser(browser, signal) {
  if (!browser || childHasExited(browser)) return false;
  try {
    if (process.platform !== 'win32' && browser.pid) process.kill(-browser.pid, signal);
    else browser.kill(signal);
    return true;
  } catch (error) {
    if (error.code === 'ESRCH') return false;
    throw error;
  }
}

async function processIdsUsingProfile(profile) {
  const entries = await readdir('/proc', { withFileTypes: true });
  const matches = [];
  for (const entry of entries) {
    if (!entry.isDirectory() || !/^\d+$/.test(entry.name)) continue;
    try {
      const commandLine = await readFile('/proc/' + entry.name + '/cmdline');
      if (commandLine.toString().includes(profile)) matches.push(Number(entry.name));
    } catch {
      // Processes can disappear while /proc is being inspected.
    }
  }
  return matches;
}

async function terminateBrowser(browser, profile) {
  const cleanup = {
    browserExited: childHasExited(browser),
    killSent: false,
    residualProcessIds: [],
    termSent: false,
  };
  if (!cleanup.browserExited) {
    cleanup.termSent = signalBrowser(browser, 'SIGTERM');
    cleanup.browserExited = await waitForChildExit(browser, PROBE_TIMING.cleanupTermWaitMs);
  }
  if (!cleanup.browserExited) {
    cleanup.killSent = signalBrowser(browser, 'SIGKILL');
    cleanup.browserExited = await waitForChildExit(browser, PROBE_TIMING.cleanupKillWaitMs);
  }

  let residuals = profile ? await processIdsUsingProfile(profile) : [];
  for (const pid of residuals) {
    try {
      process.kill(pid, 'SIGKILL');
    } catch (error) {
      if (error.code !== 'ESRCH') throw error;
    }
  }
  const deadline = Date.now() + PROBE_TIMING.cleanupResidualWaitMs;
  while (profile && residuals.length && Date.now() < deadline) {
    await wait(50);
    residuals = await processIdsUsingProfile(profile);
  }
  cleanup.residualProcessIds = residuals;
  return cleanup;
}

async function main() {
  let browser;
  let browserStderr = '';
  let cdp;
  let profile;
  let payload;
  let failure;
  let cleanup = {
    browserExited: false,
    killSent: false,
    profileRemoved: false,
    residualProcessIds: [],
    termSent: false,
  };
  try {
    const baseUrl = pathToFileURL(ROOT).href.replace(/\/$/, '');
    profile = await mkdtemp(join(tmpdir(), 'crisanti-gallery-cdp-'));
    browser = spawn(chromium, [
      '--allow-file-access-from-files',
      '--disable-background-networking',
      '--disable-breakpad',
      '--disable-crash-reporter',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--headless=new',
      '--hide-scrollbars',
      '--no-first-run',
      '--no-sandbox',
      '--remote-debugging-pipe',
      '--user-data-dir=' + profile,
      'about:blank',
    ], {
      detached: process.platform !== 'win32',
      stdio: ['ignore', 'ignore', 'pipe', 'pipe', 'pipe'],
    });
    browser.stderr.on('data', chunk => {
      if (browserStderr.length < 8000) browserStderr += chunk.toString();
    });
    try {
      cdp = await withTimeout(
        connectToPage(browser),
        PROBE_TIMING.startupMs,
        'Chromium CDP startup timed out'
      );
    } catch (error) {
      const diagnostic = browserStderr.trim();
      throw new Error(error.message + (diagnostic ? '\nChromium stderr:\n' + diagnostic : ''));
    }
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Network.enable');
    await cdp.send('Network.setBlockedURLs', {
      urls: ['https://fonts.googleapis.com/*', 'https://fonts.gstatic.com/*'],
    });

    const measured = await withTimeout((async () => {
      const measured = [];
      for (const viewport of [
        { height: 844, width: 390 },
        { height: 1000, width: 1440 },
      ]) {
        for (const language of ['pt', 'es']) {
          measured.push(await probePage(cdp, baseUrl, language, viewport));
        }
      }
      const contactSheets = await createContactSheets();
      return { contactSheets, results: measured };
    })(), probeTimeoutMs, 'Gallery CDP probe exceeded ' + probeTimeoutMs + 'ms');
    payload = {
      capture: captureDir ? {
        contactSheets: measured.contactSheets,
        directory: captureDir,
        frameCount: captureFrames.length,
        frames: captureFrames.map(name => name + '.png'),
      } : null,
      results: measured.results,
    };
  } catch (error) {
    failure = error;
  } finally {
    cdp?.close();
    try {
      cleanup = {
        ...cleanup,
        ...(await terminateBrowser(browser, profile)),
      };
      if (profile) {
        await rm(profile, { force: true, maxRetries: 5, recursive: true, retryDelay: 100 });
        cleanup.profileRemoved = !existsSync(profile);
        cleanup.profilePath = profile;
      }
    } catch (error) {
      if (!failure) failure = error;
    }
  }

  if (failure) {
    const failurePayload = JSON.stringify({ cleanup, error: failure.message }, null, 2) + '\n';
    if (outputPath) await writeFile(outputPath, failurePayload, 'utf8');
    throw new Error(failure.message + '\nCleanup: ' + JSON.stringify(cleanup));
  }
  const output = JSON.stringify({ ...payload, cleanup }, null, 2) + '\n';
  if (outputPath) await writeFile(outputPath, output, 'utf8');
  process.stdout.write(output);
}

const isEntryPoint = process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url;
if (isEntryPoint) await main();
