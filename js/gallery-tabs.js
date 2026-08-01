/* ═══════════════════════════════════════════════════
   GALLERY TABS — Sub-gallery tab switching & Literatura Modal
   ═══════════════════════════════════════════════════ */
'use strict';

(function initGalleryTabs() {
  // Gallery tab system — switches between sub-gallery carousels
  document.querySelectorAll('.gallery-tabs').forEach(function(tablist) {
    var tabs = tablist.querySelectorAll('.gallery-tab');
    var section = tablist.closest('.series-group') || tablist.closest('.literatura-subsection') || tablist.closest('.series');
    if (!section) return;

    tabs.forEach(function(tab) {
      tab.addEventListener('click', function() {
        var targetId = tab.dataset.target;

        // Hide all panels in this group
        section.querySelectorAll('[data-gallery-group]').forEach(function(panel) {
          panel.hidden = true;
        });

        // Show the target panel
        var target = document.getElementById('gallery-carousel-' + targetId);
        if (target) {
          target.hidden = false;
          // Re-initialize carousel if needed
          window.dispatchEvent(new Event('resize'));
          // Trigger carousel setup for lazy-initialized carousels
          if (typeof window.initSingleCarousel === 'function') {
            window.initSingleCarousel(target);
          }
        }

        // Update tab states
        tabs.forEach(function(t) {
          t.classList.remove('active');
          t.setAttribute('aria-selected', 'false');
        });
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');
      });
    });
  });

  // Init Literatura Reading Modal
  initLiteraturaModal();
})();

function initLiteraturaModal() {
  var modal = document.getElementById('literatura-modal');
  if (!modal) {
    var modalHtml = `
      <div id="literatura-modal" class="lit-modal" aria-hidden="true" role="dialog" aria-modal="true" aria-labelledby="lit-modal-title">
        <div class="lit-modal-backdrop"></div>
        <div class="lit-modal-container">
          <header class="lit-modal-header">
            <div class="lit-modal-meta">
              <span class="lit-modal-badge">Literatura</span>
              <span class="lit-modal-subtitle" id="lit-modal-subtitle">Leitura</span>
            </div>
            <div class="lit-modal-toolbar">
              <div class="font-size-controls" aria-label="Controle de tamanho de fonte">
                <button type="button" class="font-btn font-decrease" id="font-decrease-btn" title="Diminuir tamanho da fonte (a-)" aria-label="Diminuir fonte">a-</button>
                <span class="font-size-indicator" id="font-size-indicator">100%</span>
                <button type="button" class="font-btn font-increase" id="font-increase-btn" title="Aumentar tamanho da fonte (A+)" aria-label="Aumentar fonte">A+</button>
              </div>
              <button type="button" class="lit-modal-close" id="lit-modal-close-btn" aria-label="Fechar janela de leitura">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </header>
          <main class="lit-modal-body" id="lit-modal-body">
            <h2 class="lit-modal-title" id="lit-modal-title"></h2>
            <div class="lit-modal-text" id="lit-modal-text"></div>
          </main>
          <footer class="lit-modal-footer">
            <span class="lit-modal-author">Fabio Crisanti — Acervo Literatura</span>
            <button type="button" class="btn-outline lit-modal-close-foot" id="lit-modal-close-foot">Fechar leitura</button>
          </footer>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    modal = document.getElementById('literatura-modal');
  }

  var backdrop = modal.querySelector('.lit-modal-backdrop');
  var closeBtn = document.getElementById('lit-modal-close-btn');
  var closeFoot = document.getElementById('lit-modal-close-foot');
  var titleEl = document.getElementById('lit-modal-title');
  var subtitleEl = document.getElementById('lit-modal-subtitle');
  var textEl = document.getElementById('lit-modal-text');
  var btnDecrease = document.getElementById('font-decrease-btn');
  var btnIncrease = document.getElementById('font-increase-btn');
  var indicator = document.getElementById('font-size-indicator');

  var fontScales = [85, 100, 115, 130, 150, 175, 200];
  var currentScaleIndex = 1; // Default 100%

  function setFontScale(index) {
    if (index < 0) index = 0;
    if (index >= fontScales.length) index = fontScales.length - 1;
    currentScaleIndex = index;
    var scale = fontScales[currentScaleIndex];
    if (textEl) {
      textEl.style.setProperty('--lit-font-size', (1.45 * scale / 100) + 'rem');
    }
    if (indicator) {
      indicator.textContent = scale + '%';
    }
  }

  if (btnDecrease) {
    btnDecrease.addEventListener('click', function(e) {
      e.stopPropagation();
      setFontScale(currentScaleIndex - 1);
    });
  }

  if (btnIncrease) {
    btnIncrease.addEventListener('click', function(e) {
      e.stopPropagation();
      setFontScale(currentScaleIndex + 1);
    });
  }

  function openModal(article) {
    var title = article.querySelector('h4') || article.querySelector('h3');
    var fullContent = article.querySelector('.literatura-full');
    var excerpt = article.querySelector('.literatura-excerpt');

    var articleTitle = title ? title.textContent.trim() : 'Texto';
    if (titleEl) titleEl.textContent = articleTitle;

    var subsection = article.closest('.literatura-subsection') || article.closest('.series-group') || article.closest('.section');
    var subTitle = subsection ? (subsection.querySelector('.literatura-subtitle') || subsection.querySelector('.section-title')) : null;
    if (subtitleEl) subtitleEl.textContent = subTitle ? subTitle.textContent.trim() : 'Literatura';

    if (textEl) {
      textEl.innerHTML = '';
      if (fullContent) {
        textEl.innerHTML = fullContent.innerHTML;
      } else if (excerpt) {
        textEl.innerHTML = excerpt.innerHTML;
      }
    }

    modal.removeAttribute('hidden');
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    setFontScale(1); // Reset scale to 100% when opening a text
  }

  function closeModal() {
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
    modal.setAttribute('hidden', '');
    document.body.style.overflow = '';
  }

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (closeFoot) closeFoot.addEventListener('click', closeModal);
  if (backdrop) backdrop.addEventListener('click', closeModal);

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeModal();
    }
  });

  document.querySelectorAll('.literatura-expand').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      var article = btn.closest('.literatura-card') || btn.closest('article');
      if (article) {
        openModal(article);
      }
    });
  });
}
