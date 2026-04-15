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
   4. OBRA FILTER
═══════════════════════════════════════════════════ */
(function initFilter() {
  const filterBtns = $$('.filter-btn');
  const cards      = $$('.obra-card');
  if (!filterBtns.length || !cards.length) return;

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;

      // Update button states
      filterBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      // Show/hide cards with stagger
      let visibleIndex = 0;
      cards.forEach(card => {
        const matches = filter === 'all' || card.dataset.series === filter;
        if (matches) {
          card.classList.remove('hidden');
          card.style.animationDelay = `${visibleIndex * 0.07}s`;
          card.style.animation = 'none';
          // Force reflow
          void card.offsetWidth;
          card.style.animation = '';
          visibleIndex++;
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });
})();

/* ═══════════════════════════════════════════════════
   5. LIGHTBOX
═══════════════════════════════════════════════════ */
(function initLightbox() {
  const lightbox  = $('#lightbox');
  const lbImg     = $('#lightbox-img');
  const lbCaption = $('#lightbox-caption');
  const lbClose   = $('#lightbox-close');
  const lbPrev    = $('#lightbox-prev');
  const lbNext    = $('#lightbox-next');

  if (!lightbox || !lbImg) return;

  // Collect all obra images
  const cards = $$('.obra-card:not(.hidden)');
  let currentIndex = 0;

  const getImages = () => {
    return $$('.obra-card').filter(c => !c.classList.contains('hidden')).map(card => ({
      src:     card.querySelector('.obra-img')?.src     || '',
      alt:     card.querySelector('.obra-img')?.alt     || '',
      title:   card.querySelector('.obra-title')?.textContent?.trim() || '',
      serie:   card.querySelector('.obra-serie')?.textContent?.trim() || '',
      dims:    card.querySelector('.obra-dims')?.textContent?.trim()  || '',
    }));
  };

  const open = (index) => {
    const imgs = getImages();
    if (!imgs.length) return;
    currentIndex = ((index % imgs.length) + imgs.length) % imgs.length;
    const item = imgs[currentIndex];

    lbImg.src = item.src;
    lbImg.alt = item.alt;
    lbCaption.textContent = [item.title, item.serie, item.dims].filter(Boolean).join(' · ');

    lightbox.hidden = false;
    document.body.style.overflow = 'hidden';
    lbClose.focus();
  };

  const close = () => {
    lightbox.hidden = true;
    document.body.style.overflow = '';
    lbImg.src = '';
  };

  const navigate = (dir) => {
    const imgs = getImages();
    open((currentIndex + dir + imgs.length) % imgs.length);
  };

  // Attach zoom buttons
  $$('.obra-zoom').forEach((btn, i) => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const allCards = $$('.obra-card');
      const card = btn.closest('.obra-card');
      const visibleCards = $$('.obra-card').filter(c => !c.classList.contains('hidden'));
      const idx = visibleCards.indexOf(card);
      open(idx >= 0 ? idx : 0);
    });
  });

  // Also open on card image click
  $$('.obra-img').forEach((img, i) => {
    img.style.cursor = 'zoom-in';
    img.addEventListener('click', () => {
      const card = img.closest('.obra-card');
      const visibleCards = $$('.obra-card').filter(c => !c.classList.contains('hidden'));
      const idx = visibleCards.indexOf(card);
      open(idx >= 0 ? idx : 0);
    });
  });

  lbClose.addEventListener('click', close);
  lbPrev.addEventListener('click', () => navigate(-1));
  lbNext.addEventListener('click', () => navigate(1));

  // Click outside to close
  lightbox.addEventListener('click', e => {
    if (e.target === lightbox) close();
  });

  // Keyboard
  document.addEventListener('keydown', e => {
    if (lightbox.hidden) return;
    if (e.key === 'Escape')     close();
    if (e.key === 'ArrowLeft')  navigate(-1);
    if (e.key === 'ArrowRight') navigate(1);
  });
})();

/* ═══════════════════════════════════════════════════
   6. SCROLL REVEAL
═══════════════════════════════════════════════════ */
(function initReveal() {
  const revealEls = $$('.reveal');
  if (!revealEls.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  revealEls.forEach(el => observer.observe(el));
})();

/* ═══════════════════════════════════════════════════
   7. ADD REVEAL TO SECTIONS ON LOAD
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
    '.contato-text',
    '.contato-visual',
  ];

  const delayMap = {
    '.obra-card': true,
    '.traj-col': true,
    '.series-text > *': true,
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
  }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });

  revealEls.forEach(el => observer.observe(el));
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
