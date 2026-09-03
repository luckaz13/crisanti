#!/usr/bin/env node

import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = fileURLToPath(new URL('../..', import.meta.url));
const CAPTURE_FLAG = '--capture-dir';
const captureFlagIndex = process.argv.indexOf(CAPTURE_FLAG);
const captureDir = captureFlagIndex >= 0 ? process.argv[captureFlagIndex + 1] : null;
const chromium = process.env.CHROMIUM_BIN || (existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : 'chromium');
const probeTimeoutMs = captureDir ? 58_000 : 45_000;
let navigationSequence = 0;

function withTimeout(promise, timeoutMs, message) {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(message)), timeoutMs);
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

async function connectToPage(child) {
  const input = child.stdio[3];
  const output = child.stdio[4];
  let nextId = 0;
  const pending = new Map();
  const eventWaiters = new Map();
  let sessionId = null;
  let buffer = Buffer.alloc(0);
  input.on('error', () => {});
  output.on('error', () => {});

  const dispatch = frame => {
    const message = JSON.parse(frame.toString('utf8'));
    if (message.id) {
      const waiter = pending.get(message.id);
      if (!waiter) return;
      pending.delete(message.id);
      if (message.error) waiter.reject(new Error(`${waiter.method}: ${message.error.message}`));
      else waiter.resolve(message.result);
      return;
    }
    const waiters = eventWaiters.get(message.method) || [];
    eventWaiters.delete(message.method);
    waiters.forEach(resolve => resolve(message.params));
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

  const rawSend = (method, params = {}, targetSessionId = null) => new Promise((resolve, reject) => {
    const id = ++nextId;
    pending.set(id, { method, resolve, reject });
    const message = { id, method, params };
    if (targetSessionId) message.sessionId = targetSessionId;
    input.write(`${JSON.stringify(message)}\0`);
  });
  const targets = await rawSend('Target.getTargets');
  const page = targets.targetInfos.find(target => target.type === 'page');
  if (!page) throw new Error('Chromium did not expose a page target');
  sessionId = (await rawSend('Target.attachToTarget', {
    flatten: true,
    targetId: page.targetId,
  })).sessionId;
  const send = (method, params = {}) => rawSend(method, params, sessionId);
  const waitEvent = method => new Promise(resolve => {
    const waiters = eventWaiters.get(method) || [];
    waiters.push(resolve);
    eventWaiters.set(method, waiters);
  });

  return { close: () => input.end(), send, waitEvent };
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

async function waitForPage(cdp) {
  await evaluate(cdp, `new Promise((resolve, reject) => {
    const deadline = performance.now() + 15000;
    const ready = () => {
      const carousels = [...document.querySelectorAll('.gallery-carousel')];
      const initialized = carousels.length > 0 && carousels.every(
        carousel => carousel.dataset.carouselInitialized === 'true'
      );
      if (document.readyState !== 'loading' && initialized) return resolve(true);
      if (performance.now() > deadline) return reject(new Error('gallery initialization timeout'));
      requestAnimationFrame(ready);
    };
    ready();
  })`);
}

async function waitForVisibleGalleryMedia(cdp) {
  await evaluate(cdp, `new Promise((resolve, reject) => {
    const deadline = performance.now() + 15000;
    const ready = () => {
      const carousels = [...document.querySelectorAll('.gallery-carousel')].filter(carousel => {
        const bounds = carousel.querySelector('.gallery-viewport').getBoundingClientRect();
        return bounds.width > 0 && bounds.height > 0;
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
      if (performance.now() > deadline) return reject(new Error('visible gallery media timeout'));
      requestAnimationFrame(ready);
    };
    ready();
  })`);
}

async function waitForUrl(cdp, url) {
  const deadline = Date.now() + 10_000;
  while (Date.now() <= deadline) {
    try {
      if (await evaluate(cdp, 'location.href') === url) return;
    } catch {
      // The previous execution context is destroyed while navigation commits.
    }
    await new Promise(resolve => setTimeout(resolve, 25));
  }
  throw new Error(`Page navigation timed out: ${url}`);
}

async function waitForImage(cdp, selector) {
  await evaluate(cdp, `new Promise((resolve, reject) => {
    const deadline = performance.now() + 15000;
    const ready = () => {
      const image = document.querySelector(${JSON.stringify(selector)});
      if (image?.complete && image.naturalWidth > 0) return resolve(true);
      if (performance.now() > deadline) return reject(new Error('image load timeout: ${selector}'));
      requestAnimationFrame(ready);
    };
    ready();
  })`);
}

async function navigate(cdp, url) {
  const target = new URL(url);
  target.searchParams.set('gallery-probe', String(++navigationSequence));
  const targetUrl = target.href;
  await cdp.send('Page.navigate', { url: targetUrl });
  await waitForUrl(cdp, targetUrl);
  await withTimeout(waitForPage(cdp), 20_000, `Page initialization timed out: ${targetUrl}`);
  await withTimeout(waitForVisibleGalleryMedia(cdp), 20_000, `Gallery media timed out: ${targetUrl}`);
}

async function screenshot(cdp, name) {
  if (!captureDir) return;
  await mkdir(captureDir, { recursive: true });
  const result = await cdp.send('Page.captureScreenshot', {
    captureBeyondViewport: false,
    format: 'png',
    fromSurface: true,
  });
  await writeFile(join(captureDir, `${name}.png`), Buffer.from(result.data, 'base64'));
}

async function scrollAndCapture(cdp, selector, name) {
  await evaluate(cdp, `document.querySelector(${JSON.stringify(selector)})?.scrollIntoView({
    behavior: 'instant', block: 'center', inline: 'nearest'
  })`);
  await evaluate(cdp, 'new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
  await screenshot(cdp, name);
}

const measurementScript = `(() => {
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
  const visible = element => {
    const bounds = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return bounds.width > 0 && bounds.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
  };
  return [...document.querySelectorAll('section.series')].flatMap(section =>
    [...section.querySelectorAll('.gallery-carousel')]
      .filter(carousel => visible(carousel.querySelector('.gallery-viewport')))
      .map(carousel => {
        const viewport = carousel.querySelector('.gallery-viewport');
        const gallery = carousel.closest('.series-gallery') || carousel.closest('.series-visual') || carousel;
        const activeSlide = carousel.dataset.transition === 'crossfade'
          ? carousel.querySelector('.gallery-slide.is-active')
          : carousel.querySelector('.gallery-slide');
        const media = activeSlide?.querySelector('.gallery-img, .gallery-video');
        const mediaStyle = media ? getComputedStyle(media) : null;
        return {
          carouselId: carousel.id,
          gallery: rect(gallery),
          media: media ? rect(media) : null,
          mediaComplete: media ? (media.tagName === 'VIDEO'
            ? media.readyState >= 1
            : media.complete && media.naturalWidth > 0) : null,
          mediaKind: media?.tagName.toLowerCase() || null,
          mediaObjectFit: mediaStyle?.objectFit || null,
          section: rect(section),
          sectionId: section.id,
          seriesOverflowX: getComputedStyle(gallery).overflowX,
          seriesOverflowY: getComputedStyle(gallery).overflowY,
          viewport: rect(viewport),
        };
      })
  );
})()`;

async function measureSlide(cdp, sectionId, slideIndex) {
  return evaluate(cdp, `(() => {
    const section = document.querySelector(${JSON.stringify(`#${sectionId}`)});
    const carousel = section.querySelector('.gallery-carousel');
    const viewport = carousel.querySelector('.gallery-viewport');
    const track = carousel.querySelector('.gallery-track');
    const slide = carousel.querySelectorAll('.gallery-slide')[${slideIndex}];
    const media = slide.querySelector('.gallery-img, .gallery-video');
    const rect = element => {
      const value = element.getBoundingClientRect();
      return { bottom: value.bottom, height: value.height, left: value.left,
        right: value.right, top: value.top, width: value.width };
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
  })()`);
}

async function advanceToSlide(cdp, sectionId, slideIndex) {
  await evaluate(cdp, `(() => {
    const section = document.querySelector(${JSON.stringify(`#${sectionId}`)});
    const previous = section.querySelector('.gallery-btn--prev');
    const next = section.querySelector('.gallery-btn--next');
    while (!previous.disabled) previous.click();
    for (let index = 0; index < ${slideIndex}; index += 1) next.click();
  })()`);
  const selector = `#${sectionId} .gallery-slide:nth-child(${slideIndex + 1}) .gallery-img`;
  await waitForImage(cdp, selector);
  await evaluate(cdp, `new Promise((resolve, reject) => {
    const deadline = performance.now() + 2000;
    const ready = () => {
      const media = document.querySelector(${JSON.stringify(selector)});
      const viewport = media.closest('.gallery-viewport');
      const mediaBounds = media.getBoundingClientRect();
      const viewportBounds = viewport.getBoundingClientRect();
      if (mediaBounds.left >= viewportBounds.left - 2 && mediaBounds.right <= viewportBounds.right + 2) {
        return resolve(true);
      }
      if (performance.now() > deadline) return reject(new Error('slide transition timeout: ${selector}'));
      requestAnimationFrame(ready);
    };
    ready();
  })`);
  return measureSlide(cdp, sectionId, slideIndex);
}

async function measureLightbox(cdp) {
  return evaluate(cdp, `(() => {
    const image = document.querySelector('#lightbox-img');
    const caption = document.querySelector('#lightbox-caption');
    const lightbox = document.querySelector('#lightbox');
    const parseColor = value => {
      const parts = value.match(/[\\d.]+/g).map(Number);
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
        return normalized <= 0.04045 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
      });
      return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
    };
    const pageBackground = parseColor(getComputedStyle(document.querySelector('#cuadernos')).backgroundColor);
    const overlay = composite(parseColor(getComputedStyle(lightbox).backgroundColor), pageBackground);
    const foreground = composite(parseColor(getComputedStyle(caption).color), overlay);
    const light = Math.max(luminance(foreground), luminance(overlay));
    const dark = Math.min(luminance(foreground), luminance(overlay));
    const rect = element => {
      const value = element.getBoundingClientRect();
      return { bottom: value.bottom, height: value.height, left: value.left,
        right: value.right, top: value.top, width: value.width };
    };
    return {
      caption: rect(caption),
      captionContrast: (light + 0.05) / (dark + 0.05),
      captionText: caption.textContent.trim(),
      hidden: lightbox.hidden,
      image: rect(image),
      imageComplete: image.complete,
      imageNaturalHeight: image.naturalHeight,
      imageNaturalWidth: image.naturalWidth,
      viewport: { height: innerHeight, width: innerWidth },
    };
  })()`);
}

async function probeViewport(cdp, baseUrl, viewport) {
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
  await navigate(cdp, `${baseUrl}/es/index.html#cuadernos`);

  const initialGalleries = await evaluate(cdp, measurementScript);
  const prefix = `es-${viewport.width}x${viewport.height}`;
  const cuadernosSquare = await measureSlide(cdp, 'cuadernos', 0);
  await scrollAndCapture(cdp, '#cuadernos .series-gallery', `${prefix}-cuadernos-square`);

  const cuadernosVertical = await advanceToSlide(cdp, 'cuadernos', 1);
  await scrollAndCapture(cdp, '#cuadernos .series-gallery', `${prefix}-cuadernos-vertical`);

  const cuadernosPanoramic = await advanceToSlide(cdp, 'cuadernos', 9);
  await scrollAndCapture(cdp, '#cuadernos .series-gallery', `${prefix}-cuadernos-panoramic`);

  const vlak = await measureSlide(cdp, 'juego-del-tren', 0);
  await scrollAndCapture(cdp, '#juego-del-tren .series-gallery', `${prefix}-vlak-video`);

  await evaluate(cdp, `(() => {
    const carousel = document.querySelector('#peces .gallery-carousel');
    const previous = carousel.querySelector('.gallery-btn--prev');
    carousel.dispatchEvent(new PointerEvent('pointerenter'));
    while (!previous.disabled) previous.click();
    carousel.querySelector('.gallery-btn--next').click();
  })()`);
  await evaluate(cdp, 'new Promise(resolve => setTimeout(resolve, 550))');
  const peces = await evaluate(cdp, `(() => {
    const carousel = document.querySelector('#peces .gallery-carousel');
    const slides = [...carousel.querySelectorAll('.gallery-slide')];
    return {
      activeIndex: slides.findIndex(slide => slide.classList.contains('is-active')),
      activeOpacity: getComputedStyle(slides[1]).opacity,
      previousOpacity: getComputedStyle(slides[0]).opacity,
      trackTransform: getComputedStyle(carousel.querySelector('.gallery-track')).transform,
    };
  })()`);
  await scrollAndCapture(cdp, '#peces .series-gallery', `${prefix}-peces-crossfade`);

  let lightbox = null;
  if (viewport.width < 600) {
    await evaluate(cdp, `document.querySelector('#cuadernos .gallery-slide:nth-child(10) .gallery-img').click()`);
    await waitForImage(cdp, '#lightbox-img');
    await evaluate(cdp, `document.querySelector('.lightbox-content').scrollTop = 0`);
    await evaluate(cdp, 'new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
    lightbox = await measureLightbox(cdp);
    await screenshot(cdp, `${prefix}-lightbox-cuadernos`);
  }

  return {
    cuadernosPanoramic,
    cuadernosSquare,
    cuadernosVertical,
    initialGalleries,
    lightbox,
    peces,
    viewport,
    vlak,
  };
}

async function capturePortuguese(cdp, baseUrl, viewport) {
  if (!captureDir) return;
  await navigate(cdp, `${baseUrl}/index.html#cadernos`);
  const prefix = `pt-${viewport.width}x${viewport.height}`;
  await scrollAndCapture(cdp, '#cadernos .series-gallery', `${prefix}-cuadernos`);
  await scrollAndCapture(cdp, '#juego-del-tren .series-gallery', `${prefix}-vlak-video`);
  await scrollAndCapture(cdp, '#peixes .series-gallery', `${prefix}-peces`);
  if (viewport.width < 600) {
    await evaluate(cdp, `document.querySelector('#cadernos .gallery-slide:first-child .gallery-img').click()`);
    await waitForImage(cdp, '#lightbox-img');
    await screenshot(cdp, `${prefix}-lightbox-cuadernos`);
  }
}

async function terminateBrowser(browser) {
  if (!browser || browser.exitCode !== null) return;
  const exited = new Promise(resolve => browser.once('exit', resolve));
  browser.kill('SIGTERM');
  await Promise.race([exited, new Promise(resolve => setTimeout(resolve, 2000))]);
}

async function main() {
  let browser;
  let cdp;
  let profile;
  try {
    const baseUrl = pathToFileURL(ROOT).href.replace(/\/$/, '');
    profile = await mkdtemp(join(tmpdir(), 'crisanti-gallery-cdp-'));
    browser = spawn(chromium, [
      '--allow-file-access-from-files',
      '--disable-background-networking',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--headless=new',
      '--hide-scrollbars',
      '--no-first-run',
      '--no-sandbox',
      '--remote-debugging-pipe',
      `--user-data-dir=${profile}`,
      'about:blank',
    ], { stdio: ['ignore', 'ignore', 'pipe', 'pipe', 'pipe'] });
    cdp = await withTimeout(connectToPage(browser), 15_000, 'Chromium CDP startup timed out');
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Network.enable');
    await cdp.send('Network.setBlockedURLs', {
      urls: ['https://fonts.googleapis.com/*', 'https://fonts.gstatic.com/*'],
    });

    const results = await withTimeout((async () => {
      const measured = [];
      for (const viewport of [
        { height: 844, width: 390 },
        { height: 1000, width: 1440 },
      ]) {
        measured.push(await probeViewport(cdp, baseUrl, viewport));
        await capturePortuguese(cdp, baseUrl, viewport);
      }
      return measured;
    })(), probeTimeoutMs, `Gallery CDP probe exceeded ${probeTimeoutMs}ms`);
    process.stdout.write(`${JSON.stringify({ results }, null, 2)}\n`);
  } finally {
    cdp?.close();
    await terminateBrowser(browser);
    if (profile) await rm(profile, { force: true, maxRetries: 5, recursive: true, retryDelay: 100 });
  }
}

await main();
