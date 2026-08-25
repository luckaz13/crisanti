/* ═════════════════════════════════════════════════════
    9. GALLERY CAROUSELS
   ══════════════════════════════════════════════════════ */
(function initGalleryCarousels() {
    const $ = (sel, ctx = document) => ctx.querySelector(sel);
    const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

    function setupCarousel(carouselEl) {
        const track = carouselEl.querySelector('.gallery-track');
        const viewport = carouselEl.querySelector('.gallery-viewport');
        const prevBtn = carouselEl.querySelector('.gallery-btn--prev');
        const nextBtn = carouselEl.querySelector('.gallery-btn--next');

        if (!carouselEl || !track || !viewport || !prevBtn || !nextBtn) return;
        if (carouselEl.dataset.carouselInitialized === 'true') {
            if (typeof carouselEl._updateCarousel === 'function') {
                carouselEl._updateCarousel();
            }
            return;
        }

        const slides = carouselEl.querySelectorAll('.gallery-slide');
        if (!slides.length) return;

        let currentIndex = 0;
        const slideCount = slides.length;
        const preloadRadius = 4;
        const captionClearance = 8;
        const autoplayDelay = Number.parseInt(carouselEl.dataset.autoplay || '', 10);
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        let autoplayTimer = null;
        let pointerPaused = false;
        let focusPaused = false;
        let controlsAnchorWidth = null;
        const videos = [...carouselEl.querySelectorAll('.gallery-video')];
        let carouselVisible = false;

        function preloadImage(img) {
            if (!img || img.dataset.preloaded === 'true') return;
            img.loading = 'eager';
            img.decoding = 'async';
            img.dataset.preloaded = 'true';
            const src = img.currentSrc || img.src;
            if (!src) return;
            const probe = new Image();
            probe.decoding = 'async';
            probe.src = src;
        }

        function preloadAround(index, direction = 1) {
            const start = Math.max(0, index - 1);
            const end = Math.min(slideCount - 1, index + preloadRadius);
            for (let i = start; i <= end; i++) {
                preloadImage(slides[i].querySelector('.gallery-img'));
            }
            for (let step = 1; step <= preloadRadius; step++) {
                const target = index + (direction * step);
                if (target >= 0 && target < slideCount) {
                    preloadImage(slides[target].querySelector('.gallery-img'));
                }
            }
        }

        function updateControlsAnchor() {
            const width = carouselEl.getBoundingClientRect().width;
            if (width <= 0) return;
            if (controlsAnchorWidth !== null && Math.abs(width - controlsAnchorWidth) < 1) return;

            const anchorSlide = [...slides].find(slide => slide.querySelector('.gallery-img')) || slides[0];
            const anchorImage = anchorSlide.querySelector('.gallery-img');
            const anchorFigure = anchorSlide.querySelector('.gallery-figure');
            if (anchorImage && (!anchorImage.complete || anchorImage.naturalWidth === 0)) return;

            const anchorTarget = anchorImage || anchorFigure || anchorSlide;
            const anchorHeight = anchorTarget.getBoundingClientRect().height;
            if (anchorHeight <= 0) return;

            carouselEl.style.setProperty('--gallery-controls-top', `${Math.ceil(anchorHeight / 2)}px`);
            controlsAnchorWidth = width;
        }

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

        function updateCarousel() {
            track.style.transform = `translateX(${-currentIndex * 100}%)`;
            updateViewportHeight();
            updateControlsAnchor();
            prevBtn.disabled = currentIndex === 0;
            nextBtn.disabled = currentIndex === slideCount - 1;
            prevBtn.setAttribute('aria-disabled', currentIndex === 0);
            nextBtn.setAttribute('aria-disabled', currentIndex === slideCount - 1);
            syncVideoPlayback();
        }

        carouselEl._updateCarousel = updateCarousel;
        carouselEl.dataset.carouselInitialized = 'true';

        function canAutoplay() {
            return Number.isFinite(autoplayDelay) && autoplayDelay > 0 && slideCount > 1 &&
                !pointerPaused && !focusPaused && !reducedMotion.matches &&
                document.visibilityState === 'visible';
        }

        function stopAutoplay() {
            if (autoplayTimer !== null) {
                window.clearTimeout(autoplayTimer);
                autoplayTimer = null;
            }
        }

        function scheduleAutoplay() {
            stopAutoplay();
            if (!canAutoplay()) return;
            autoplayTimer = window.setTimeout(() => {
                currentIndex = (currentIndex + 1) % slideCount;
                preloadAround(currentIndex, 1);
                updateCarousel();
                scheduleAutoplay();
            }, autoplayDelay);
        }

        function updateViewportHeight() {
            const activeSlide = slides[currentIndex];
            if (!activeSlide) return;
            window.requestAnimationFrame(() => {
                const img = activeSlide.querySelector('.gallery-img');
                const figure = activeSlide.querySelector('.gallery-figure');
                const target = figure || img || activeSlide;
                const height = target.getBoundingClientRect().height;
                if (height > 0) {
                    viewport.style.height = `${Math.ceil(height) + captionClearance}px`;
                }
            });
        }

        updateCarousel();
        preloadAround(0, 1);
        carouselEl.style.cursor = 'grab';

        slides.forEach(slide => {
            const img = slide.querySelector('.gallery-img');
            if (!img) return;
            if (img.complete) return;
            img.addEventListener('load', updateCarousel, { once: true });
            img.addEventListener('error', updateCarousel, { once: true });
        });

        videos.forEach(video => {
            video.addEventListener('loadedmetadata', updateCarousel, { once: true });
        });

        if ('ResizeObserver' in window) {
            const resizeObserver = new ResizeObserver(updateCarousel);
            resizeObserver.observe(carouselEl);
            const figureResizeObserver = new ResizeObserver(entries => {
                const activeFigure = slides[currentIndex].querySelector('.gallery-figure');
                if (entries.some(entry => entry.target === activeFigure)) {
                    updateViewportHeight();
                }
            });
            slides.forEach(slide => {
                const figure = slide.querySelector('.gallery-figure');
                if (figure) figureResizeObserver.observe(figure);
            });
        } else {
            window.addEventListener('resize', updateCarousel);
        }

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

        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                preloadAround(currentIndex, -1);
                updateCarousel();
                scheduleAutoplay();
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentIndex < slideCount - 1) {
                currentIndex++;
                preloadAround(currentIndex, 1);
                updateCarousel();
                scheduleAutoplay();
            }
        });

        let startX = 0;
        let startY = 0;
        track.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });

        track.addEventListener('touchend', (e) => {
            const dx = e.changedTouches[0].clientX - startX;
            const dy = e.changedTouches[0].clientY - startY;
            if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) {
                if (dx > 0 && currentIndex > 0) {
                    currentIndex--;
                    preloadAround(currentIndex, -1);
                    updateCarousel();
                    scheduleAutoplay();
                }
                else if (dx < 0 && currentIndex < slideCount - 1) {
                    currentIndex++;
                    preloadAround(currentIndex, 1);
                    updateCarousel();
                    scheduleAutoplay();
                }
            }
        });

        carouselEl.addEventListener('pointerenter', () => {
            pointerPaused = true;
            stopAutoplay();
        });
        carouselEl.addEventListener('pointerleave', () => {
            pointerPaused = false;
            scheduleAutoplay();
        });
        carouselEl.addEventListener('focusin', () => {
            focusPaused = true;
            stopAutoplay();
        });
        carouselEl.addEventListener('focusout', () => {
            window.setTimeout(() => {
                focusPaused = carouselEl.contains(document.activeElement);
                scheduleAutoplay();
            }, 0);
        });
        document.addEventListener('visibilitychange', () => {
            scheduleAutoplay();
            syncVideoPlayback();
        });
        if (typeof reducedMotion.addEventListener === 'function') {
            reducedMotion.addEventListener('change', scheduleAutoplay);
        } else if (typeof reducedMotion.addListener === 'function') {
            reducedMotion.addListener(scheduleAutoplay);
        }
        scheduleAutoplay();
    }

    // Expose for lazy initialization from gallery tabs
    window.initSingleCarousel = setupCarousel;

    function generateJSONLD(data) {
        try {
            const baseUrl = window.location.origin + window.location.pathname.replace(/\/$/, "");
            const schemas = data.filter(item => item.src).map(item => {
                const title = (item.title && item.title.trim().toLowerCase() !== 'arte') ? item.title : `Obra de Arte (Acervo ${item.idx})`;
                return {
                    "@context": "https://schema.org",
                    "@type": "VisualArtwork",
                    "name": title.trim(),
                    "image": `${baseUrl}/${item.src}`,
                    "creator": { "@type": "Person", "name": "Fabio Crisanti" },
                    "description": item.desc || item.meta || "Catálogo online Fabio Crisanti"
                };
            });
            const staticCards = document.querySelectorAll('.obra-card');
            staticCards.forEach((card) => {
                const img = card.querySelector('.obra-img');
                const titleEl = card.querySelector('.obra-title');
                if (img && titleEl) {
                    schemas.push({
                        "@context": "https://schema.org",
                        "@type": "VisualArtwork",
                        "name": titleEl.textContent.trim().replace(/\s+/g, ' '),
                        "image": `${baseUrl}/${img.getAttribute('src')}`,
                        "creator": { "@type": "Person", "name": "Fabio Crisanti" },
                        "artMedium": card.querySelector('.obra-serie')?.textContent.trim() || undefined
                    });
                }
            });
            if (schemas.length === 0) return;
            const script = document.createElement('script');
            script.type = 'application/ld+json';
            script.text = JSON.stringify(schemas);
            document.head.appendChild(script);
        } catch (e) {
            console.error('Failed to generate VisualArtwork JSON-LD schema', e);
        }
    }

    // --- Main gallery (dynamic from galleryData) ---
    const mainCarousel = document.getElementById('gallery-carousel');
    const mainTrack = document.getElementById('gallery-track');

    if (mainCarousel && mainTrack) {
        function loadMainGallery() {
            try {
                const data = typeof galleryData !== 'undefined' ? galleryData : [];
                if (!data.length) {
                    console.warn('Main gallery data not loaded.');
                    return;
                }
                const fragment = document.createDocumentFragment();
                data.forEach(item => {
                    const slide = document.createElement('div');
                    slide.className = 'gallery-slide';
                    if (item.idx !== undefined) slide.dataset.index = item.idx;
                    if (item.date) slide.dataset.date = item.date;
                    let altAttr = item.alt;
                    if (altAttr === 'arte' || !altAttr) altAttr = item.title || 'Obra de arte';
                    let fp = `<figure class="gallery-figure">`;
                    fp += `<img src="${item.src}" alt="${altAttr}" class="gallery-img" loading="lazy" />`;
                    fp += `<figcaption class="gallery-caption">`;
                    if (item.title) fp += `<h3 class="gallery-title">${item.title}</h3>`;
                    if (item.meta) fp += `<p class="gallery-meta">${item.meta}</p>`;
                    if (item.desc) fp += `<p class="gallery-desc">${item.desc}</p>`;
                    fp += `</figcaption></figure>`;
                    slide.innerHTML = fp;
                    fragment.appendChild(slide);
                });
                mainTrack.appendChild(fragment);
                setupCarousel(mainCarousel);
                generateJSONLD(data);
            } catch (error) {
                console.error('Error loading main gallery:', error);
            }
        }
        loadMainGallery();
    }

    // --- High-res carousels (slides already in HTML) ---
    document.querySelectorAll('.gallery-carousel').forEach(carousel => {
        if (carousel.id === 'gallery-carousel') return;
        setupCarousel(carousel);
    });

})();
