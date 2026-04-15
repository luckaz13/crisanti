/* ═════════════════════════════════════════════════════
    9. GALERY CAROUSEL
══════════════════════════════════════════════════════ */
(function initGalleryCarousel() {
    console.log('Gallery carousel initializing...');
    const carousel = $('#gallery-carousel');
    const prevBtn = $('#gallery-prev');
    const nextBtn = $('#gallery-next');
    const track = $('#gallery-track');
    const slides = $$('.gallery-slide');
    
    if (!carousel || !prevBtn || !nextBtn || !track || !slides.length) {
        console.log('Gallery carousel elements not found:', {carousel, prevBtn, nextBtn, track, slidesLength: slides.length});
        return;
    }

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
        
        console.log(`Carousel updated: index=${currentIndex}, slideWidth=${slideWidth}, moveAmount=${moveAmount}`);
    }

    // Initialize
    updateCarousel();
    carousel.style.cursor = 'grab';

    // Handle window resize
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            updateCarousel();
        }, 250);
    });

    // Button event listeners for arrow keyboard navigation
    document.addEventListener('keydown', (e) => {
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
})();