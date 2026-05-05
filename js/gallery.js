/* ═════════════════════════════════════════════════════
    9. GALLERY CAROUSELS
   ══════════════════════════════════════════════════════ */
(function initGalleryCarousels() {
    const $ = (sel, ctx = document) => ctx.querySelector(sel);
    const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

    function setupCarousel(carouselEl) {
        const track = carouselEl.querySelector('.gallery-track');
        const prevBtn = carouselEl.querySelector('.gallery-btn--prev');
        const nextBtn = carouselEl.querySelector('.gallery-btn--next');

        if (!carouselEl || !track || !prevBtn || !nextBtn) return;

        const slides = carouselEl.querySelectorAll('.gallery-slide');
        if (!slides.length) return;

        let currentIndex = 0;
        const slideCount = slides.length;

        function updateCarousel() {
            const slideWidth = slides[0].getBoundingClientRect().width;
            track.style.transform = `translateX(${-(currentIndex * slideWidth)}px)`;
            prevBtn.disabled = currentIndex === 0;
            nextBtn.disabled = currentIndex === slideCount - 1;
            prevBtn.setAttribute('aria-disabled', currentIndex === 0);
            nextBtn.setAttribute('aria-disabled', currentIndex === slideCount - 1);
        }

        updateCarousel();
        carouselEl.style.cursor = 'grab';

        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(updateCarousel, 250);
        });

        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) { currentIndex--; updateCarousel(); }
        });

        nextBtn.addEventListener('click', () => {
            if (currentIndex < slideCount - 1) { currentIndex++; updateCarousel(); }
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
                if (dx > 0 && currentIndex > 0) { currentIndex--; updateCarousel(); }
                else if (dx < 0 && currentIndex < slideCount - 1) { currentIndex++; updateCarousel(); }
            }
        });
    }

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
    document.querySelectorAll('.series .gallery-carousel').forEach(carousel => {
        if (carousel.id === 'gallery-carousel') return;
        setupCarousel(carousel);
    });
})();
