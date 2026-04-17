/* ═════════════════════════════════════════════════════
    9. GALERY CAROUSEL
══════════════════════════════════════════════════════ */
(function initGalleryCarousel() {
    console.log('Gallery carousel initializing with JSON...');
    const carousel = $('#gallery-carousel');
    const prevBtn = $('#gallery-prev');
    const nextBtn = $('#gallery-next');
    const track = $('#gallery-track');
    
    // Assegura que todos os containers existam antes de continuar
    if (!carousel || !prevBtn || !nextBtn || !track) {
        console.warn('Gallery carousel elements not found. Stopping setup.');
        return;
    }

    async function loadGallery() {
        try {
            const response = await fetch('data/gallery.json');
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            
            const fragment = document.createDocumentFragment();
            data.forEach(item => {
                const slide = document.createElement('div');
                slide.className = 'gallery-slide';
                if (item.idx !== undefined) slide.dataset.index = item.idx;
                if (item.date) slide.dataset.date = item.date;
                
                let fp = `<figure class="gallery-figure">`;
                
                // Tratar alt para não exibir placeholder 'arte' sem valor e vazio
                let altAttr = item.alt;
                if (altAttr === 'arte' || !altAttr) altAttr = item.title || 'Obra de arte';
                fp += `<img src="${item.src}" alt="${altAttr}" class="gallery-img" loading="lazy" />`;
                
                fp += `<figcaption class="gallery-caption">`;
                
                // Renderização condicional do h3 (corrigindo heading vazio reclamado na analise)
                if (item.title) {
                    fp += `<h3 class="gallery-title">${item.title}</h3>`;
                }
                
                if (item.meta) {
                    fp += `<p class="gallery-meta">${item.meta}</p>`;
                }
                
                if (item.desc) {
                    fp += `<p class="gallery-desc">${item.desc}</p>`;
                }
                
                fp += `</figcaption></figure>`;
                
                slide.innerHTML = fp;
                fragment.appendChild(slide);
            });
            track.appendChild(fragment);
            
            // Só inicializa o carrossel em si após a renderização ter sido completada
            setupCarousel();
        } catch (error) {
            console.error('Error loading gallery details:', error);
        }
    }

    function setupCarousel() {
        // Agora que estamos montados dinamicamente, buscamos de volta as slides
        const slides = $$('.gallery-slide');
        if (!slides || !slides.length) return;

        let currentIndex = 0;
        const slideCount = slides.length;

        // Function to update carousel position
        function updateCarousel() {
            const slideWidth = slides[0].getBoundingClientRect().width;
            const moveAmount = -(currentIndex * slideWidth);
            track.style.transform = `translateX(${moveAmount}px)`;
            
            // Update button states
            prevBtn.disabled = currentIndex === 0;
            nextBtn.disabled = currentIndex === slideCount - 1;
            
            // For accessibility
            prevBtn.setAttribute('aria-disabled', currentIndex === 0);
            nextBtn.setAttribute('aria-disabled', currentIndex === slideCount - 1);
        }

        // Initialize display
        updateCarousel();
        carousel.style.cursor = 'grab';

        // Handle window resize debounce request
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                updateCarousel();
            }, 250);
        });

        // Button event listeners for arrow keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Prevenir execução caso as setas precisem ser usadas do Lightbox (conflito resolvido) ou em inputs
            const lb = document.getElementById('lightbox');
            if (lb && !lb.hidden) return;
            if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return;
            
            if (e.key === 'ArrowLeft' && currentIndex > 0) {
                currentIndex--;
                updateCarousel();
            } else if (e.key === 'ArrowRight' && currentIndex < slideCount - 1) {
                currentIndex++;
                updateCarousel();
            }
        });

        // Button click events for mouse interaction
        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateCarousel();
            }
        });
        
        nextBtn.addEventListener('click', () => {
            if (currentIndex < slideCount - 1) {
                currentIndex++;
                updateCarousel();
            }
        });
    }

    loadGallery();
})();