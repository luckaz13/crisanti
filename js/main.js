/* ═══════════════════════════════════════════════════
   FABIO CRISANTI — main.js
   ═══════════════════════════════════════════════════ */

'use strict';

/* ── Helper ──────────────────────────────────────── */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

/* ═══════════════════════════════════════════════════
   1. STICKY HEADER
═══════════════════════════════════════════════════ */
(function initHeader() {
  const header = $('#site-header');
  if (!header) return;

  const onScroll = () => {
    header.classList.toggle('scrolled', window.scrollY > 60);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

/* ═══════════════════════════════════════════════════
   2. MOBILE NAVIGATION TOGGLE
═══════════════════════════════════════════════════ */
(function initMobileNav() {
  const toggle = $('#nav-toggle');
  const links  = $('#nav-links');
  if (!toggle || !links) return;

  const open = () => {
    links.classList.add('open');
    toggle.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  };
  const close = () => {
    links.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  };

  toggle.addEventListener('click', () => {
    links.classList.contains('open') ? close() : open();
  });

  // Close on nav link click
  $$('.nav-link', links).forEach(link => {
    link.addEventListener('click', close);
  });

  // Close on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && links.classList.contains('open')) close();
  });
})();

/* ═══════════════════════════════════════════════════
   3. HERO IMAGE PARALLAX / LOAD
═══════════════════════════════════════════════════ */
(function initHero() {
  const heroBg = $('.hero-bg');
  if (!heroBg) return;

  if (heroBg.complete) {
    heroBg.classList.add('loaded');
  } else {
    heroBg.addEventListener('load', () => heroBg.classList.add('loaded'));
  }

  // Subtle parallax on scroll
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y < window.innerHeight) {
      heroBg.style.transform = `scale(1) translateY(${y * 0.18}px)`;
    }
  }, { passive: true });
})();

/* ═══════════════════════════════════════════════════
   4. LIGHTBOX
═══════════════════════════════════════════════════ */
(function initLightbox() {
  const lightbox  = $('#lightbox');
  const lbImg     = $('#lightbox-img');
  const lbCaption = $('#lightbox-caption');
  const lbClose   = $('#lightbox-close');
  const lbPrev    = $('#lightbox-prev');
  const lbNext    = $('#lightbox-next');

  if (!lightbox || !lbImg) return;

  let currentIndex = 0;
  let currentItems = [];

  const close = () => {
    lightbox.hidden = true;
    document.body.style.overflow = '';
    lbImg.src = '';
    currentItems = [];
    lbImg.classList.remove('zoomed');
  };

  const open = (index) => {
    if (!currentItems.length) return;
    const len = currentItems.length;
    currentIndex = ((index % len) + len) % len;
    const item = currentItems[currentIndex];
    lbImg.src = item.src;
    lbImg.alt = item.alt;
    lbCaption.textContent = [item.title, item.serie, item.dims].filter(Boolean).join(' · ');
    lightbox.hidden = false;
    document.body.style.overflow = 'hidden';
    lbClose.focus();
    // Expose meta for counter enhancements
    lightbox.dataset.lbIndex = String(currentIndex + 1);
    lightbox.dataset.lbTotal = String(len);
    const counter = $('#lightbox-counter');
    if (counter) counter.textContent = `${currentIndex + 1} / ${len}`;
  };

  const navigate = (dir) => {
    open(currentIndex + dir);
  };

  const getObraItems = () =>
    $$('.obra-card').map(card => ({
      src:   card.querySelector('.obra-img')?.src     || '',
      alt:   card.querySelector('.obra-img')?.alt     || '',
      title: card.querySelector('.obra-title')?.textContent?.trim() || '',
      serie: card.querySelector('.obra-serie')?.textContent?.trim() || '',
      dims:  card.querySelector('.obra-dims')?.textContent?.trim()  || '',
    })).filter(item => item.src);

  const getCarouselItems = (carouselEl) =>
    $$('.gallery-slide', carouselEl).map(slide => ({
      src:   slide.querySelector('.gallery-img')?.src || '',
      alt:   slide.querySelector('.gallery-img')?.alt || '',
      title: slide.querySelector('.gallery-title')?.textContent?.trim() || '',
      serie: '',
      dims:  '',
    })).filter(item => item.src);

  const getInstagramItems = () =>
    $$('#instagram-grid img').map(img => ({
      src: img.src || '',
      alt: img.alt || '',
      title: img.closest('a,button,[data-ig-card]')?.getAttribute('aria-label') || img.alt || '',
      serie: '',
      dims: '',
    })).filter(item => item.src);

  // Event delegation so every gallery works (including late/tab-hidden panels)
  document.addEventListener('click', (e) => {
    if (e.target.closest('#lightbox')) return;

    const zoomBtn = e.target.closest('.obra-zoom');
    if (zoomBtn) {
      e.preventDefault();
      e.stopPropagation();
      const card = zoomBtn.closest('.obra-card');
      const items = getObraItems();
      const src = card?.querySelector('.obra-img')?.src;
      const idx = items.findIndex(i => i.src === src);
      currentItems = items;
      open(idx >= 0 ? idx : 0);
      return;
    }

    const obraImg = e.target.closest('.obra-img');
    if (obraImg) {
      e.preventDefault();
      const items = getObraItems();
      const idx = items.findIndex(i => i.src === obraImg.src);
      currentItems = items;
      open(idx >= 0 ? idx : 0);
      return;
    }

    const galleryImg = e.target.closest('.gallery-img');
    if (galleryImg) {
      const carousel = galleryImg.closest('.gallery-carousel');
      if (!carousel) return;
      if (e.target.closest('.gallery-btn')) return;
      e.preventDefault();
      const slides = $$('.gallery-slide', carousel);
      const slide = galleryImg.closest('.gallery-slide');
      const idx = slides.indexOf(slide);
      currentItems = getCarouselItems(carousel);
      open(idx >= 0 ? idx : 0);
      return;
    }

    const igCard = e.target.closest('#instagram-grid a.instagram-card, #instagram-grid [data-ig-card]');
    if (igCard) {
      const img = igCard.querySelector('img');
      if (!img) return;
      e.preventDefault();
      const items = getInstagramItems();
      const idx = items.findIndex(i => i.src === img.src);
      currentItems = items;
      open(idx >= 0 ? idx : 0);
    }
  });

  // ── Controls ──
  lbClose.addEventListener('click', close);
  lbPrev.addEventListener('click', () => navigate(-1));
  lbNext.addEventListener('click', () => navigate(1));

  lightbox.addEventListener('click', e => {
    if (e.target === lightbox) close();
  });

  document.addEventListener('keydown', e => {
    if (lightbox.hidden) return;
    if (e.key === 'Escape')     close();
    if (e.key === 'ArrowLeft')  navigate(-1);
    if (e.key === 'ArrowRight') navigate(1);
  });

  // Public API for other scripts if needed
  window.fcLightbox = { openItems: (items, index = 0) => {
    currentItems = (items || []).filter(i => i && i.src);
    open(index);
  }};
})();

/* ═══════════════════════════════════════════════════
   6. ADD REVEAL TO SECTIONS ON LOAD
═══════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  // Hero content already animated via CSS
  // Add reveal to major content blocks
  const toReveal = [
    '.section-header',
    '.sobre-body',
    '.sobre-links',
    '.sobre-figure',
    '.sobre-quote',
    '.obra-card',
    '.series-text > *',
    '.series-figure',
    '.traj-col',
    '.literatura-card',
    '.instagram-card',
    '.contato-text',
    '.contato-visual',
  ];

  const delayMap = {
    '.obra-card': true,
    '.traj-col': true,
    '.series-text > *': true,
    '.literatura-card': true,
    '.instagram-card': true,
  };

  toReveal.forEach(sel => {
    $$(sel).forEach((el, i) => {
      el.classList.add('reveal');
      if (delayMap[sel]) {
        el.classList.add(`reveal-delay-${Math.min(i % 4 + 1, 4)}`);
      }
    });
  });

  // Re-init reveal observer after adding classes
  const revealEls = $$('.reveal');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.04, rootMargin: '100px 0px 100px 0px' });

  revealEls.forEach(el => observer.observe(el));

  // Scroll progress indicator
  const progressEl = document.getElementById('scroll-progress');
  if (progressEl) {
    window.addEventListener('scroll', () => {
      const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
      progressEl.style.transform = `scaleX(${scrolled / 100})`;
    }, { passive: true });
  }
});

/* ═══════════════════════════════════════════════════
   8. SMOOTH ACTIVE NAV ON SCROLL
═══════════════════════════════════════════════════ */
(function initActiveNav() {
  const sections = $$('section[id]');
  const navLinks = $$('.nav-link');
  if (!sections.length || !navLinks.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        navLinks.forEach(link => {
          link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
        });
      }
    });
  }, { rootMargin: '-40% 0px -55% 0px' });

  sections.forEach(s => observer.observe(s));
})();

/* ═══════════════════════════════════════════════════
   TIMELINE — Reveal on scroll
═══════════════════════════════════════════════════ */
(function initTimeline() {
  const items = $$('.timeline-item');
  if (!items.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });

  items.forEach(item => observer.observe(item));
})();

/* ═══════════════════════════════════════════════════
   LIGHTBOX ENHANCEMENTS — Zoom, Counter, WhatsApp, Swipe
═══════════════════════════════════════════════════ */
(function initLightboxEnhancements() {
  const lightbox = $('#lightbox');
  if (!lightbox) return;

  const img = $('#lightbox-img');
  const counter = $('#lightbox-counter');
  const zoomBtn = $('#lightbox-zoom');
  const consultBtn = $('#lightbox-consult');

  // Zoom toggle
  if (zoomBtn && img) {
    const toggleZoom = () => {
      img.classList.toggle('zoomed');
    };
    zoomBtn.addEventListener('click', toggleZoom);
    img.addEventListener('click', toggleZoom);
  }

  // Reset zoom on navigation
  const resetZoom = () => {
    if (img) img.classList.remove('zoomed');
  };
  const prevBtn = $('#lightbox-prev');
  const nextBtn = $('#lightbox-next');
  if (prevBtn) prevBtn.addEventListener('click', resetZoom);
  if (nextBtn) nextBtn.addEventListener('click', resetZoom);

  // Touch swipe for mobile
  let touchStartX = 0;
  let touchEndX = 0;
  const minSwipe = 50;

  lightbox.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  lightbox.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    const diff = touchStartX - touchEndX;
    if (Math.abs(diff) > minSwipe) {
      if (diff > 0 && nextBtn) {
        nextBtn.click();
      } else if (diff < 0 && prevBtn) {
        prevBtn.click();
      }
    }
  }, { passive: true });

  // Update counter and consult button whenever lightbox image changes
  const updateLightboxMeta = () => {
    if (counter) {
      const idx = lightbox.dataset.lbIndex;
      const total = lightbox.dataset.lbTotal;
      if (idx && total) {
        counter.textContent = idx + ' / ' + total;
      }
    }

    // WhatsApp consult button
    if (consultBtn && img) {
      const alt = img.alt || 'uma obra';
      const msg = 'Olá, tenho interesse na obra "' + alt + '". Está disponível?';
      consultBtn.href = 'https://wa.me/5548991155260?text=' + encodeURIComponent(msg);
    }
  };

  // Observe lightbox image src changes
  if (img) {
    const srcObserver = new MutationObserver(updateLightboxMeta);
    srcObserver.observe(img, { attributes: true, attributeFilter: ['src'] });
  }

  // Also update on lightbox show
  if (lightbox) {
    const showObserver = new MutationObserver((mutations) => {
      mutations.forEach(m => {
        if (m.attributeName === 'hidden' && !lightbox.hidden) {
          resetZoom();
          updateLightboxMeta();
        }
      });
    });
    showObserver.observe(lightbox, { attributes: true, attributeFilter: ['hidden'] });
  }
})();
