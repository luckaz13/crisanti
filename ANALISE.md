# 🔍 ANÁLISE TÉCNICA SÊNIOR — Portfólio Fabio Crisanti

> **Autor:** Analista Sênior em HTML5 Semântico, CSS3 e JavaScript Vanilla  
> **Data:** Abril 2026  
> **Escopo:** Auditoria completa de qualidade, performance, acessibilidade e manutenibilidade  

---

## 📋 Índice

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [HTML5 — Semântica e Estrutura](#2-html5--semântica-e-estrutura)
3. [CSS3 — Estilização e Arquitetura](#3-css3--estilização-e-arquitetura)
4. [JavaScript — Funcionalidade e Qualidade](#4-javascript--funcionalidade-e-qualidade)
5. [Performance e Otimização](#5-performance-e-otimização)
6. [Acessibilidade (A11y)](#6-acessibilidade-a11y)
7. [SEO](#7-seo)
8. [Segurança e Boas Práticas](#8-segurança-e-boas-práticas)
9. [Resumo Executivo — Matriz de Impacto](#9-resumo-executivo--matriz-de-impacto)

---

## 1. Visão Geral do Projeto

| Item | Valor |
|---|---|
| **Tipo** | Site-catálogo de artista plástico (estático) |
| **Páginas** | 4 (`index.html`, `critica.html`, `ensaio.html`, `projetos.html`) |
| **CSS** | 1 arquivo (`css/style.css` — 1.140 linhas / 27KB) |
| **JavaScript** | 2 arquivos (`js/main.js` — 304 linhas, `js/gallery.js` — 75 linhas) |
| **Imagens** | **1.935 arquivos** totalizando **555 MB** |
| **Galeria** | **396 slides** no carrossel embutidos diretamente no HTML |
| **Tamanho do index.html** | **530 KB** (!) |

### Diagnóstico Inicial

O projeto demonstra **bom gosto estético** e utiliza elementos semânticos HTML5, custom properties CSS e padrões modernos de JavaScript. No entanto, há problemas **críticos de performance** derivados da injeção massiva de conteúdo estático no HTML e da falta de uma estratégia de gerenciamento de assets.

---

## 2. HTML5 — Semântica e Estrutura

### ✅ Pontos Positivos

- Uso correto de elementos semânticos: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<figure>`, `<figcaption>`
- Atributos `aria-label` nos botões de navegação da galeria
- Uso de `<details>` / `<summary>` para materiais das obras — componente nativo e acessível
- Seções com `id` para navegação por âncoras
- Hierarquia de headings bem organizada na página principal (`h1` → `h2` → `h3`)

### 🔴 Problemas Críticos

#### 2.1 — Arquivo `index.html` com 530 KB

**Impacto:** 🔴 Crítico

O arquivo `index.html` possui **530 KB** devido à injeção de ~396 slides da galeria diretamente no HTML, todos em **uma única linha** (minificados inline). Isso:

- Torna o arquivo **impossível de manter manualmente**
- Aumenta drasticamente o TTFB (Time to First Byte)
- Força o browser a parsear ~500 KB de DOM antes de renderizar
- Prejudica o cache — qualquer mudança na galeria invalida o HTML inteiro

**Recomendação:**
```
Estratégia A (Simples): Mover dados da galeria para um arquivo JSON e
  renderizar via JavaScript no carregamento
Estratégia B (Avançada): Implementar paginação virtual / infinite scroll
  carregando sob demanda via fetch()
```

#### 2.2 — Tags `<h3>` Vazias na Galeria

**Impacto:** 🟡 Médio

**217 de 396 slides** possuem `<h3 class="gallery-title"></h3>` completamente vazio. Headings vazios:

- Geram *noise* para leitores de tela
- Prejudicam a estrutura do documento
- São considerados um anti-padrão pelo WCAG

**Recomendação:**
```html
<!-- ANTES: heading vazio sempre renderizado -->
<h3 class="gallery-title"></h3>

<!-- DEPOIS: renderização condicional via JS ou omissão no HTML -->
<!-- Se não houver título, não incluir o <h3> -->
```

#### 2.3 — Atributos `alt` Vazios ou Genéricos

**Impacto:** 🟡 Médio

**217 imagens** com `alt=""` (vazio) e várias com `alt="arte"` (genérico e sem valor descritivo).

Para imagens que são **o conteúdo principal** de um portfólio artístico, o `alt` deveria conter descrições significativas:

```html
<!-- ANTES -->
<img alt="" />
<img alt="arte" />

<!-- DEPOIS -->
<img alt="Pintura acrílica sobre papel de seda — série SEDA 2023, 30x50cm" />
```

#### 2.4 — HTML Minificado Inline (Galeria)

**Impacto:** 🟡 Médio

Os slides da galeria estão comprimidos numa única linha sem quebras, tornando debug e manutenção praticamente impossíveis. O arquivo `galeria-items.html` existe formatado mas o conteúdo no `index.html` está tudo numa só linha.

**Recomendação:** Separar dados da apresentação usando JSON + template rendering.

### 🟡 Melhorias Sugeridas

#### 2.5 — Atributo `lang` nas Páginas Internas

Verificar que todas as páginas possuem `lang="pt-BR"` no `<html>`. Conteúdo misto PT-BR/ES/EN deveria usar `lang` inline:

```html
<p lang="es">Acrílico sobre papel de seda.</p>
```

#### 2.6 — Meta Tags Open Graph / Twitter Cards

Nenhuma das páginas possui meta tags para redes sociais. Para um artista plástico, isso é especialmente importante:

```html
<meta property="og:title" content="Fabio Crisanti — Artes Plásticas" />
<meta property="og:description" content="Portfólio e catálogo de obras" />
<meta property="og:image" content="images/og-cover.jpg" />
<meta property="og:type" content="website" />
<meta name="twitter:card" content="summary_large_image" />
```

#### 2.7 — Falta de `<meta name="description">`

Nenhuma página principal possui meta description, essencial para SEO.

#### 2.8 — Favicon / Web App Manifest

Não há `<link rel="icon">` nem `manifest.json`. Recomendado para credibilidade:

```html
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="icon" href="/icon.svg" type="image/svg+xml" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
```

---

## 3. CSS3 — Estilização e Arquitetura

### ✅ Pontos Positivos

- **Design system** bem definido com Custom Properties em `:root` (paleta, tipografia, espaçamento)
- Uso de `clamp()` para tipografia fluida — excelente
- `scroll-behavior: smooth` no `html`
- Reset moderno com `box-sizing: border-box`
- `backdrop-filter: blur()` no header — toque de modernidade
- Animações com `@keyframes` e `cubic-bezier` personalizados
- Media queries organizadas por componente (não centralizadas no final)
- Uso de `margin-inline`, `padding-inline`, `padding-block` — propriedades lógicas modernas

### 🔴 Problemas Críticos

#### 3.1 — Seletor `.gallery-btn` Duplicado

**Impacto:** 🟡 Médio

O seletor `.gallery-btn` aparece **duas vezes** no CSS (linhas ~994-1010 e ~1031-1050), com regras **conflitantes**:

```css
/* Primeira declaração (L994) */
.gallery-btn {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 60px;
  height: 60px;
  /* ... */
}

/* Segunda declaração (L1031) — SOBRESCREVE a primeira */
.gallery-btn {
  background: transparent; /* ← ANULA a anterior */
  /* ... */
}
```

A segunda declaração **anula** `background`, `border-radius`, `box-shadow`, `width` e `height` da primeira. Isso é um bug — o botão provavelmente deveria ter o estilo da primeira declaração.

**Correção:** Remover a segunda declaração duplicada.

#### 3.2 — Uso de `!important`

**Impacto:** 🟡 Médio

Existem 3 usos de `!important` no CSS. Dois deles são justificáveis (override de contexto no mobile nav), mas este não:

```css
/* L682 — !important desnecessário */
.series-credit p {
  color: var(--c-accent-lt) !important;
  margin: 0 !important;
}
```

**Recomendação:** Aumentar a especificidade do seletor ao invés de forçar com `!important`.

### 🟡 Melhorias Sugeridas

#### 3.3 — Inconsistência em Unidades de Espaçamento

Misturas de valores hardcoded (`1.25rem`, `2.5rem`, `0.75rem`) com custom properties (`--sp-sm`, `--sp-md`). O design system define tokens de espaçamento mas não os utiliza consistentemente:

```css
/* Usando token (BOM) */
padding-block: var(--sp-xl);

/* Valor arbitrário (PODERIA usar token) */
margin-bottom: 1.25rem;  /* ≈ --sp-sm + 0.25rem ? */
padding-bottom: 0.75rem; /* Não corresponde a nenhum token */
```

**Recomendação:** Criar tokens intermediários e utilizá-los consistentemente:
```css
:root {
  --sp-2xs: 0.25rem;
  --sp-xs:  0.5rem;
  --sp-sm:  1rem;
  --sp-md:  2rem;
  /* ... */
}
```

#### 3.4 — Falta de `prefers-reduced-motion`

O site possui diversas animações (parallax, scroll reveal, fade-in, hover zoom). Nenhuma respeita a preferência do usuário por movimento reduzido:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

#### 3.5 — Falta de `prefers-color-scheme`

Para um site de arte com fundo claro, seria interessante oferecer modo escuro:

```css
@media (prefers-color-scheme: dark) {
  :root {
    --c-bg: #1A1714;
    --c-ink: #F3EFE8;
    /* ... */
  }
}
```

#### 3.6 — `overflow-x: hidden` no `body`

```css
body { overflow-x: hidden; }
```

Isso é um **anti-padrão** comum. Mascara problemas de layout ao invés de corrigi-los. Deveria ser investigado qual elemento causa overflow horizontal e corrigir a raiz do problema.

#### 3.7 — Falta de Estilo para Estado `:focus` em Todos os Interativos

O seletor `:focus-visible` existe como utilitário global, mas os cards de obra e botões de filtro não possuem indicadores visuais de foco adequados para navegação por teclado.

#### 3.8 — `will-change: transform` na Gallery Track

```css
.gallery-track { will-change: transform; }
```

`will-change` é útil, mas **deve ser aplicado dinamicamente** (via JS, apenas quando a animação está prestes a ocorrer) e não de forma permanente, pois cria uma compositing layer que consome memória GPU continuamente.

#### 3.9 — Container Queries (Oportunidade de Inovação)

Os breakpoints atuais são baseados no viewport (`@media max-width`). Para os cards de obras, `@container` queries ofereceriam um layout mais inteligente e componentizado:

```css
.obra-grid { container-type: inline-size; }

@container (max-width: 400px) {
  .obra-card { /* layout single-column */ }
}
```

---

## 4. JavaScript — Funcionalidade e Qualidade

### ✅ Pontos Positivos

- `'use strict'` ativado globalmente
- IIFE pattern para isolamento de escopo — evita poluição do namespace global
- Helpers `$` e `$$` — úteis e concisos
- Uso de `IntersectionObserver` para scroll reveal — excelente performance
- `{ passive: true }` nos scroll listeners — boa prática
- Null checks (`if (!element) return`) em todos os módulos
- `aria-expanded` controlado programaticamente no toggle do menu

### 🔴 Problemas Críticos

#### 4.1 — Conflito no Listener de Teclado (Galeria × Lightbox)

**Impacto:** 🔴 Crítico

Tanto `gallery.js` (L51-59) quanto `main.js` (L207-212) escutam `ArrowLeft` / `ArrowRight` no `document`:

```javascript
// gallery.js — SEMPRE ATIVO
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft' && currentIndex > 0) { /* ... */ }
  if (e.key === 'ArrowRight' && ...) { /* ... */ }
});

// main.js — Só ativo quando lightbox está aberto
document.addEventListener('keydown', e => {
  if (lightbox.hidden) return;
  if (e.key === 'ArrowLeft')  navigate(-1);
  if (e.key === 'ArrowRight') navigate(1);
});
```

O listener da galeria **não verifica** se o lightbox está aberto, causando navegação simultânea em ambos os componentes. Além disso, pressionar setas **em qualquer lugar da página** movimenta o carrossel — mesmo em campos de texto:

**Correção:**
```javascript
// gallery.js — adicionar guards
document.addEventListener('keydown', (e) => {
  // Não atuar se o lightbox estiver aberto
  if (!document.getElementById('lightbox')?.hidden) return;
  // Não atuar se o foco estiver em input/textarea
  if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;
  // Verificar se o carrossel está visível na viewport
  // ...
});
```

#### 4.2 — `console.log` em Produção

**Impacto:** 🟡 Médio

`gallery.js` contém 3 `console.log()` de debug em produção (L5, L13, L34). Esses devem ser removidos:

```javascript
console.log('Gallery carousel initializing...');
console.log('Gallery carousel elements not found:', {...});
console.log(`Carousel updated: index=${currentIndex}...`);
```

#### 4.3 — Variável `cards` Não Utilizada no Lightbox

**Impacto:** 🟢 Baixo

No módulo lightbox (L135), `cards` é declarada mas nunca utilizada:

```javascript
const cards = $$('.obra-card:not(.hidden)'); // ← nunca referenciada
```

#### 4.4 — Observer de Scroll Reveal Duplicado

**Impacto:** 🟡 Médio

`main.js` cria **dois** IntersectionObservers para scroll reveal:

1. Módulo 6 (`initReveal`, L218-232) — IIFE executada imediatamente
2. Módulo 7 (DOMContentLoaded, L237-281) — adiciona `.reveal` classes e cria **outro** observer

O problema: módulo 6 executa **antes** das classes serem adicionadas pelo módulo 7, então nunca observa nada. É código morto.

**Correção:** Remover o módulo 6 inteiro e manter apenas o módulo 7 que funciona corretamente.

### 🟡 Melhorias Sugeridas

#### 4.5 — Debounce no Resize do Carrossel

O `gallery.js` já usa `setTimeout` para debounce, mas com 250ms fixos. Seria melhor usar `requestAnimationFrame`:

```javascript
let rafId;
window.addEventListener('resize', () => {
  cancelAnimationFrame(rafId);
  rafId = requestAnimationFrame(updateCarousel);
});
```

#### 4.6 — Parallax sem `requestAnimationFrame`

O efeito parallax do hero (L73-78) aplica `transform` diretamente no scroll event sem throttle via `requestAnimationFrame`:

```javascript
// ATUAL — pode causar 60+ style recalcs/segundo
window.addEventListener('scroll', () => {
  heroBg.style.transform = `scale(1) translateY(${y * 0.18}px)`;
}, { passive: true });

// MELHOR — sincronizado com o frame do browser
let ticking = false;
window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      heroBg.style.transform = `...`;
      ticking = false;
    });
    ticking = true;
  }
}, { passive: true });
```

#### 4.7 — Gestão de Focus Trap no Lightbox

Quando o lightbox abre, o foco vai para o botão de fechar (`lbClose.focus()`), mas **não há focus trap**. O usuário pode tabular para fora do lightbox e interagir com elementos ocultos. Implementar:

```javascript
const focusableEls = lightbox.querySelectorAll('button, [tabindex]');
const firstEl = focusableEls[0];
const lastEl = focusableEls[focusableEls.length - 1];

lightbox.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    if (e.shiftKey && document.activeElement === firstEl) {
      e.preventDefault();
      lastEl.focus();
    } else if (!e.shiftKey && document.activeElement === lastEl) {
      e.preventDefault();
      firstEl.focus();
    }
  }
});
```

#### 4.8 — Sem Suporte a Touch/Swipe no Carrossel

O carrossel da galeria só responde a cliques nos botões e setas do teclado. Em dispositivos touch, deveria suportar swipe:

```javascript
let startX, startY;
track.addEventListener('touchstart', (e) => {
  startX = e.touches[0].clientX;
  startY = e.touches[0].clientY;
}, { passive: true });

track.addEventListener('touchend', (e) => {
  const dx = e.changedTouches[0].clientX - startX;
  const dy = e.changedTouches[0].clientY - startY;
  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) {
    dx > 0 ? prev() : next();
  }
});
```

#### 4.9 — Modularização (ESM)

Atualmente os scripts usam IIFEs e estão organizados sequencialmente. Considere migrar para ES Modules nativos:

```html
<script type="module" src="js/main.js"></script>
```

```javascript
// js/modules/header.js
export function initHeader() { /* ... */ }

// js/main.js
import { initHeader } from './modules/header.js';
```

Benefícios: `defer` automático, isolamento real de escopo, tree-shaking futuro.

---

## 5. Performance e Otimização

### 🔴 Problemas Críticos

#### 5.1 — Payload Excessivo do DOM (530 KB de HTML)

**Impacto:** 🔴 Crítico — **Problema #1 do projeto**

O `index.html` com 530 KB é o maior gargalo. Para contexto:

| Métrica | Valor Atual | Recomendado |
|---|---|---|
| Tamanho do HTML | **530 KB** | < 50 KB |
| Nós DOM estimados | **~5.000+** | < 1.500 |
| Slides no HTML | **396** | 0 (carregamento dinâmico) |

**Solução proposta — Galeria como JSON:**

```json
// data/gallery.json
[
  {
    "src": "images/fabio.crisanti.artes.plasticas/2023-06-10_12-37-23_UTC.webp",
    "title": "",
    "meta": "",
    "desc": "",
    "date": "2023-06-10"
  },
  // ...
]
```

```javascript
// js/gallery.js — carregamento sob demanda
const BATCH_SIZE = 12;
let loaded = 0;

async function loadGallery() {
  const res = await fetch('data/gallery.json');
  const items = await res.json();
  renderBatch(items, loaded, BATCH_SIZE);
}

function renderBatch(items, start, count) {
  const fragment = document.createDocumentFragment();
  items.slice(start, start + count).forEach(item => {
    fragment.appendChild(createSlide(item));
  });
  track.appendChild(fragment);
  loaded += count;
}
```

#### 5.2 — 555 MB de Imagens (1.935 Arquivos)

**Impacto:** 🔴 Crítico

| Formato | Quantidade |
|---|---|
| `.webp` | 1.152 |
| `.jpg` | 279 |
| `.png` | 0 |

Apesar do uso predominante de WebP (bom), o volume total é enorme. Recomendações:

1. **Gerar variantes responsivas** com `srcset`:
```html
<img
  srcset="images/thumb/obra-300.webp 300w,
          images/medium/obra-600.webp 600w,
          images/full/obra-1200.webp 1200w"
  sizes="(max-width: 640px) 100vw, 33vw"
  src="images/medium/obra-600.webp"
  alt="Descrição"
  loading="lazy"
/>
```

2. **Converter os 279 JPGs restantes** para WebP (economia de ~25-35%)
3. **Gerar thumbnails** para o carrossel (~300px largura) — o slide de 100% viewport não precisa de imagem full-res

#### 5.3 — Todas as 396 Imagens com `loading="lazy"` mas DOM Poluído

Embora `loading="lazy"` esteja presente (bom), o browser ainda precisa parsear os 396 elementos `<img>` no DOM inicial, consumindo memória para cada nó.

**Solução:** Carregamento virtual — inserir no DOM apenas os slides visíveis ± 2 adjacentes.

#### 5.4 — Falta de `<link rel="preload">` para Assets Críticos

A imagem do hero e as fontes não possuem preload:

```html
<link rel="preload" as="image" href="images/hero.webp" />
<link rel="preload" as="font" href="fonts/cormorant.woff2" crossorigin />
```

#### 5.5 — Google Fonts Carregado via `@import` ou `<link>`

Verificar se as fontes (Cormorant Garamond, Lato) estão sendo servidas com `font-display: swap` para evitar FOIT (Flash of Invisible Text):

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
```

### 🟡 Melhorias Sugeridas

#### 5.6 — `requestIdleCallback` para Inicialização Não-Crítica

Scroll reveal e active nav podem ser inicializados durante idle time:

```javascript
requestIdleCallback(() => {
  initReveal();
  initActiveNav();
});
```

#### 5.7 — Minificação de CSS/JS para Produção

Os arquivos de produção não estão minificados. Para um site estático sem build tool, considere:

```bash
# Usando esbuild (leve e rápido)
npx -y esbuild css/style.css --minify --outfile=css/style.min.css
npx -y esbuild js/main.js js/gallery.js --bundle --minify --outfile=js/bundle.min.js
```

---

## 6. Acessibilidade (A11y)

### ✅ Pontos Positivos

- `aria-label` nos botões de navegação da galeria
- `aria-expanded` controlado no menu mobile
- `aria-selected` atualizado nos filtros
- `:focus-visible` global definido
- Contraste de cores adequado (paleta terra sobre fundo claro)

### 🔴 Problemas

#### 6.1 — 217 Imagens sem Texto Alternativo

Para um portfólio artístico, os `alt` são **críticos**. Cada imagem é conteúdo principal, não decorativa. Imagens decorativas usam `alt=""`, mas essas são obras de arte que devem ser descritas.

**WCAG 2.1 — Critério 1.1.1 (Nível A):** Falha

#### 6.2 — 217 Headings `<h3>` Vazios

Headings vazios confundem leitores de tela e a estrutura do documento.

**WCAG 2.1 — Critério 1.3.1 (Nível A):** Falha

#### 6.3 — Falta de `role="region"` ou `aria-roledescription` no Carrossel

O carrossel deveria ter marcação ARIA adequada:

```html
<div class="gallery-carousel"
     role="region"
     aria-roledescription="carrossel"
     aria-label="Galeria de obras">
  <div role="group"
       aria-roledescription="slide"
       aria-label="Slide 1 de 396">
    <!-- conteúdo -->
  </div>
</div>
```

#### 6.4 — Contraste do Lightbox Caption

O caption do lightbox usa `color: rgba(255,255,255,0.55)` sobre fundo `rgba(10,8,6,0.95)`. Embora calculando dê ~7:1 (ok), o texto é pequeno e itálico, dificultando leitura. Considere aumentar para `rgba(255,255,255,0.75)`.

#### 6.5 — Sem Skip Navigation

Nenhuma das páginas possui link "Pular para o conteúdo principal":

```html
<a href="#main-content" class="skip-link">Pular para o conteúdo</a>
```

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  z-index: 999;
  transition: top 0.3s;
}
.skip-link:focus { top: 0; }
```

#### 6.6 — Lightbox sem `role="dialog"` e `aria-modal`

```html
<!-- ANTES -->
<div class="lightbox" id="lightbox" hidden>

<!-- DEPOIS -->
<div class="lightbox" id="lightbox" hidden
     role="dialog"
     aria-modal="true"
     aria-label="Visualização ampliada da obra">
```

---

## 7. SEO

### 🔴 Problemas

| Item | Status |
|---|---|
| `<meta name="description">` | ❌ Ausente |
| Open Graph / Twitter meta | ❌ Ausente |
| Canonical URL (`<link rel="canonical">`) | ❌ Ausente |
| JSON-LD (Schema.org) | ❌ Ausente |
| `robots.txt` | ❌ Ausente |
| `sitemap.xml` | ❌ Ausente |

#### 7.1 — Implementar Schema.org para Artista e Obras

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Fabio Crisanti",
  "jobTitle": "Artista Plástico",
  "url": "https://fabiocrisanti.com",
  "sameAs": ["https://instagram.com/fabio.crisanti.artes.plasticas"],
  "knowsAbout": ["Pintura", "Escultura", "Artes Plásticas"]
}
</script>
```

Para cada obra do catálogo:
```json
{
  "@type": "VisualArtwork",
  "name": "SEDA XLVI",
  "artist": { "@type": "Person", "name": "Fabio Crisanti" },
  "artMedium": "Acrílico sobre papel de seda",
  "width": "30cm",
  "height": "50cm"
}
```

#### 7.2 — `sitemap.xml` e `robots.txt`

```xml
<!-- sitemap.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://fabiocrisanti.com/</loc></url>
  <url><loc>https://fabiocrisanti.com/critica.html</loc></url>
  <url><loc>https://fabiocrisanti.com/ensaio.html</loc></url>
  <url><loc>https://fabiocrisanti.com/projetos.html</loc></url>
</urlset>
```

```
# robots.txt
User-agent: *
Allow: /
Sitemap: https://fabiocrisanti.com/sitemap.xml
```

---

## 8. Segurança e Boas Práticas

#### 8.1 — Links Externos sem `rel="noopener"`

Links para Instagram e redes sociais deveriam ter:

```html
<a href="https://instagram.com/..." target="_blank" rel="noopener noreferrer">
```

#### 8.2 — Script Python no Diretório de Imagens

O arquivo `images/615_import_firefox_session.py` está no diretório de imagens do projeto web. Isso:

- Não deveria estar no diretório público
- Pode expor informações se o site for deployado
- Deve ser movido para fora do diretório `images/` ou adicionado ao `.gitignore`

#### 8.3 — CSP (Content Security Policy)

Para um site estático, uma CSP básica via `<meta>` tag:

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; style-src 'self' fonts.googleapis.com; font-src fonts.gstatic.com; img-src 'self'" />
```

---

## 9. Resumo Executivo — Matriz de Impacto

### 🔴 Prioridade Alta (Fazer Agora)

| # | Item | Categoria | Esforço |
|---|---|---|---|
| 1 | Extrair galeria para JSON + render dinâmico | Performance | Alto |
| 2 | Gerar imagens responsivas (srcset/sizes) | Performance | Médio |
| 3 | Corrigir 217 atributos `alt` vazios | A11y/SEO | Médio |
| 4 | Remover headings `<h3>` vazios | A11y | Baixo |
| 5 | Corrigir conflito de keyboard entre galeria e lightbox | JS/Bug | Baixo |
| 6 | Remover `.gallery-btn` duplicado no CSS | CSS/Bug | Baixo |
| 7 | Remover `console.log` de produção | JS | Baixo |
| 8 | Adicionar meta description + Open Graph | SEO | Baixo |

### 🟡 Prioridade Média (Próxima Iteração)

| # | Item | Categoria | Esforço |
|---|---|---|---|
| 9 | Implementar focus trap no lightbox | A11y | Baixo |
| 10 | Adicionar swipe/touch no carrossel | UX | Médio |
| 11 | Implementar `prefers-reduced-motion` | A11y/CSS | Baixo |
| 12 | Adicionar ARIA correto ao carrossel (`role`, `roledescription`) | A11y | Baixo |
| 13 | `role="dialog"` + `aria-modal` no lightbox | A11y | Baixo |
| 14 | Remover IntersectionObserver duplicado | JS | Baixo |
| 15 | Parallax com `requestAnimationFrame` | Performance | Baixo |
| 16 | Adicionar skip navigation | A11y | Baixo |

### 🟢 Prioridade Baixa (Refinamento)

| # | Item | Categoria | Esforço |
|---|---|---|---|
| 17 | Migrar para ES Modules | JS/Arquitetura | Médio |
| 18 | Converter 279 JPGs para WebP | Performance | Médio |
| 19 | Implementar Schema.org JSON-LD | SEO | Baixo |
| 20 | Criar `sitemap.xml` e `robots.txt` | SEO | Baixo |
| 21 | Implementar dark mode (`prefers-color-scheme`) | CSS/UX | Médio |
| 22 | Container queries nos cards | CSS/Inovação | Médio |
| 23 | Remover `overflow-x: hidden` do body | CSS | Baixo |
| 24 | Padronizar espaçamentos com tokens | CSS | Médio |
| 25 | Remover script Python da pasta images | Segurança | Baixo |

---

### 💡 Inovações Sugeridas

1. **Virtual Gallery (WebGL/Three.js):** Para um artista plástico, uma galeria 3D imersiva seria um diferencial único. Ferramentas como Three.js com scroll-driven navigation.

2. **Comparador de Obras:** Slider interativo para comparar detalhes de obras lado a lado.

3. **Filtro por Timeline:** Slider temporal para filtrar obras por período, aproveitando os `data-date` já presentes.

4. **View Transitions API:** Nova API nativa do browser para transições entre páginas/estados:
```javascript
document.startViewTransition(() => {
  // transição entre filtros de obras
});
```

5. **Scroll-driven Animations (CSS):** Substituir IntersectionObserver por animações nativas do CSS `animation-timeline: scroll()`:
```css
.reveal {
  animation: fadeIn linear;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
```

---

*Fim da análise original.*

---

## 10. Seleção de Problemas Atualizados — Pós-Implementação (Abril 2026)

Após a integração dos modos de galeria (Cards, Carrossel, Virtual 3D) e refatoração da seção de Obras, novos problemas e regressões foram identificados na varredura constante do projeto.

### 🔴 Problemas Críticos

#### 10.1 — Lightbox Quebrado no Modo Grid (Regressão)
**Impacto:** 🔴 Crítico
O script `gallery-modes.js` reutiliza o Lightbox nativo para abrir imagens do modo Grid via `openGalleryLightbox(index)`. No entanto, a navegação e carrossel internos do Lightbox (setas de teclado, botões Prev/Next) controlados pelo módulo 5 do `main.js` buscam exclusivamente imagens com base nos elementos visíveis `.obra-card:not(.hidden)`. Como a galeria de obras agora depende de outro escopo, ao tentar usar setas, o Lightbox quebrará (arrays vazios) ou fará loop pelas imagens visíveis equivocadas.
**Correção:** Desacoplar a lógica do Lightbox (`open`, `navigate`) para aceitar fonte de dados injetável ou parametrizar qual listagem de cards usar (Galeria vs Obras).

#### 10.2 — Fuga de Memória WebGL e Ausência de Dispose
**Impacto:** 🔴 Crítico
O modo 3D instanciado em `galeria3d.js` entra em render loop contínuo e aloca as texturas da placa gráfica WebGL. Quando o usuário clica para alternar para "Carrossel" ou "Grid", a div 3D é simplesmente mascarada pelo CSS. O WebGL continua renderizando frame-a-frame no background, causando lentidão, aquecimento e fechamentos do browser no longo prazo sem `dispose()`.
**Correção:** Introduzir função explícita de montagem/desmontagem (destroy) no script 3D (ex `window.destroy3DGallery`). Destruir a malha da cena, limpar o `requestAnimationFrame` e desalocar materiais texturas quando transicionar de modo.

#### 10.3 — Gargalo HTML (530KB) Persistente na Abordagem Híbrida 
**Impacto:** 🔴 Crítico
Apesar da ótima implementação de exibição sob demanda (Chunking no Grid / Lazy loader do 3D), os dados base (`galleryData`) são populados rasgando o DOM massivo com base em todos os +396 itens escondidos do `index.html`. 
**Solução recomendada:** Em vez de usar DOM Parsing, isolar tudo em um arquivo `data/galeria.json` como originalmente proposto até o fim do projeto.

### 🟡 Melhorias Sugeridas

#### 10.4 — Listeners de Teclado Sobrepostos
Adições como `isGalleryPaused` não resolvem todos os problemas de foco do teclado. Pressionar `Escape` dispara funções em múltiplos contextos não descarregados. O comportamento não está encapsulado, pois `main.js`, `gallery.js` e `galeria3d.js` empilham ouvintes sobre a árvore DOM Global (`document`). Recomenda-se registrar KeyDown base em Stack.

---

*Documento gerado e atualizado continuamente com foco em excelência técnica e performance.*
