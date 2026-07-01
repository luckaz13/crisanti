'use strict';

(function initLanguageRouting() {
  const storageKey = 'fc-lang-choice';
  const spanishRegions = new Set([
    'AR', 'BO', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'ES', 'GQ',
    'GT', 'HN', 'MX', 'NI', 'PA', 'PE', 'PR', 'PY', 'SV', 'UY', 'VE'
  ]);
  const portugueseRegions = new Set(['BR', 'PT', 'AO', 'CV', 'GW', 'MZ', 'ST', 'TL']);
  const brazilianZones = [
    'America/Bahia', 'America/Belem', 'America/Boa_Vista', 'America/Campo_Grande',
    'America/Cuiaba', 'America/Eirunepe', 'America/Fortaleza', 'America/Maceio',
    'America/Manaus', 'America/Noronha', 'America/Porto_Velho', 'America/Recife',
    'America/Rio_Branco', 'America/Santarem', 'America/Sao_Paulo'
  ];
  const spanishZones = [
    'America/Argentina', 'America/Bogota', 'America/Caracas',
    'America/Costa_Rica', 'America/Guatemala', 'America/Havana',
    'America/Lima', 'America/Mexico_City', 'America/Montevideo',
    'America/Panama', 'America/Santiago', 'Europe/Madrid'
  ];

  document.addEventListener('click', (event) => {
    const link = event.target.closest('[data-lang-choice]');
    if (!link) return;
    localStorage.setItem(storageKey, link.dataset.langChoice);
  });

  const path = window.location.pathname;
  const inSpanishPage = /\/es\/?$/.test(path) || path.includes('/es/');
  const savedChoice = localStorage.getItem(storageKey);
  if (inSpanishPage || savedChoice) return;

  const languages = navigator.languages && navigator.languages.length
    ? navigator.languages
    : [navigator.language].filter(Boolean);

  const parsedLanguages = languages.map((language) => {
    const parts = String(language).split(/[-_]/);
    return {
      lang: parts[0]?.toLowerCase(),
      region: parts[1]?.toUpperCase()
    };
  });

  const primaryLanguage = parsedLanguages[0] || {};
  const primaryIsPortuguese = primaryLanguage.lang === 'pt' || portugueseRegions.has(primaryLanguage.region);
  const primaryIsSpanish = primaryLanguage.lang === 'es' || spanishRegions.has(primaryLanguage.region);
  const firstPtOrEs = parsedLanguages.find(({ lang }) => lang === 'pt' || lang === 'es');

  let zoneSuggestsBrazil = false;
  let zoneSuggestsSpanish = false;
  try {
    const zone = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
    zoneSuggestsBrazil = brazilianZones.some(prefix => zone.startsWith(prefix));
    zoneSuggestsSpanish = spanishZones.some(prefix => zone.startsWith(prefix));
  } catch (error) {
    zoneSuggestsBrazil = false;
    zoneSuggestsSpanish = false;
  }

  if (primaryIsPortuguese || zoneSuggestsBrazil || firstPtOrEs?.lang === 'pt') return;

  const languageSuggestsSpanish = primaryIsSpanish || firstPtOrEs?.lang === 'es';
  if (languageSuggestsSpanish || zoneSuggestsSpanish) {
    const spanishPath = window.location.protocol === 'file:' ? 'es/index.html' : 'es/';
    window.location.replace(new URL(spanishPath, window.location.href).href);
  }
})();
