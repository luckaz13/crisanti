# Fabio Crisanti — Site Catálogo

Site-catálogo digital do artista plástico e fotógrafo **Fabio Crisanti** — nascido na Patagônia Argentina e radicado na Bahia, Brasil. Apresenta obras, séries, trajetória e textos em uma experiência editorial bilíngue (português e espanhol).

**Site ao vivo:** [luckaz13.github.io/crisanti](https://luckaz13.github.io/crisanti/)

| Idioma | URL |
|--------|-----|
| Português | [/](https://luckaz13.github.io/crisanti/) |
| Español | [/es/](https://luckaz13.github.io/crisanti/es/) |

---

## O que você encontra no site

- **Hero editorial** — capa em tela cheia com tipografia Cormorant Garamond
- **Sobre** — biografia e contexto da obra
- **Obras** — seleção filtrável (Addis Ababa, Luz Líquida, Pez, Pequenas Pipas)
- **Seda** — carrosséis das séries Seda, Seda 2024 e Seda Bahia
- **Galerias temáticas** — Ensayos, La Escultura, La Fotografía, La Moda, Los Laberintos, Los Niños e Proyectos Especiales, com abas por sub-série
- **Séries em destaque** — Der Elefant e Juego del Tren
- **Trajetória** — timeline visual do percurso artístico
- **Literatura** — textos críticos e ficcionais com modal de leitura (ajuste de tamanho de fonte)
- **Instagram** — feed embutido do perfil do artista
- **Contato** — WhatsApp, Instagram e blog/catálogo original

### Experiência

- Navegação fixa com menu mobile e barra de progresso de scroll
- Alternância PT / ES com detecção automática de idioma e região
- Lightbox com zoom, legendas, navegação por teclado/toque e botão de interesse via WhatsApp
- Layout responsivo (mobile, tablet e desktop)
- Metadados Open Graph / Twitter Card e `hreflang` para SEO

---

## Stack

Site estático, sem frameworks nem bundler:

- HTML5 semântico
- CSS3 (custom properties, Grid, Flexbox)
- JavaScript vanilla (ES6+)
- Fontes: [Cormorant Garamond](https://fonts.google.com/specimen/Cormorant+Garamond) + [Outfit](https://fonts.google.com/specimen/Outfit)

---

## Estrutura do repositório

```
index.html          # Versão em português
es/index.html       # Versão em espanhol
css/style.css       # Estilos
js/
  main.js           # Nav, filtros, lightbox, scroll, literatura
  gallery.js        # Carrosséis
  gallery-tabs.js   # Abas das galerias temáticas
  language.js       # Roteamento e preferência de idioma
  gallery-data.js   # Dados auxiliares das galerias
images/             # Obras, hero e acervo das galerias
literatura/         # Fontes textuais (críticas e ficção)
```

### Âncoras principais

| Âncora | Seção |
|--------|--------|
| `#hero` | Capa |
| `#sobre` | Sobre |
| `#obras` | Catálogo de obras |
| `#series` | Seda |
| `#ensayos` … `#proyectos-especiales` | Galerias temáticas |
| `#trajetoria` | Trajetória |
| `#literatura` | Literatura |
| `#instagram` | Instagram |
| `#contato` | Contato |

---

## Como visualizar localmente

Clone o repositório e abra `index.html` no navegador, ou sirva a pasta com qualquer servidor estático:

```bash
git clone https://github.com/luckaz13/crisanti.git
cd crisanti

# exemplo com Python
python -m http.server 8080
```

Depois acesse `http://localhost:8080` (português) ou `http://localhost:8080/es/` (espanhol).

> A detecção automática de idioma redireciona visitantes hispanófonos para `/es/`. A escolha manual (PT/ES) fica salva no `localStorage`.

---

## Publicação

O site é publicado via **GitHub Pages** a partir deste repositório:

- Repositório: [github.com/luckaz13/crisanti](https://github.com/luckaz13/crisanti)
- URL pública: [luckaz13.github.io/crisanti](https://luckaz13.github.io/crisanti/)

Após atualizar o conteúdo na branch publicada, o Pages regenera o site automaticamente.

---

## Links do artista

- Instagram: [@fabio.crisanti.artes.plasticas](https://www.instagram.com/fabio.crisanti.artes.plasticas/)
- Blog / catálogo: [fabiocrisanti.blogspot.com](https://fabiocrisanti.blogspot.com/)
- Galeria 33: [galeria33.com/fabiocrisanti](https://www.galeria33.com/fabiocrisanti)
- Saatchi Art: [saatchiart.com/account/profile/2168629](https://www.saatchiart.com/account/profile/2168629)

---

© Fabio Crisanti — catálogo digital.
