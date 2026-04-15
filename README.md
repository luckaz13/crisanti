# Fabio Crisanti — Site Catálogo

Site-catálogo digital elegante e artístico para apresentar a obra do artista plástico e fotógrafo **Fabio Crisanti**, radicado na Bahia, Brasil.

## Objetivo

Apresentar a produção do artista de modo editorial, autêntico e leve, com atmosfera museológica contemporânea, valorizando as obras, a trajetória e a identidade visual do trabalho.

## Funcionalidades implementadas

- **Hero de impacto** — imagem de obra em tela cheia com tipografia Cormorant Garamond e efeito parallax suave
- **Navegação fixa** — header transparente que escurece ao rolar, com indicação de seção ativa
- **Menu mobile** — overlay com transição suave para dispositivos móveis
- **Seção Sobre** — biografia curada com citação do artista e link para Instagram e Blog
- **Catálogo de obras** — grid responsivo com:
  - 13 obras das séries Cometas, Objetos e Fotografia
  - Filtro interativo por série (Todas, Cometas, Objetos, Fotografia)
  - Informações técnicas expandíveis (materiais, medidas, preço)
  - Botão de zoom em cada card
  - **Galeria de Fotografia** — 6 obras das séries históricas (Luz Líquida, Cotidiano) e contemporâneas (Bambú)
- **Lightbox** — visualização ampliada das obras com navegação por teclado (←→ Esc) e toque
- **Seção Série Seda** — destaque curatorial em fundo escuro
- **Trajetória** — currículo completo organizado em 3 colunas (Cometas, Fotografia, Artes Plásticas & Cinema)
- **Seção Contato** — links para Instagram e Blog originais
- **Scroll reveal** — animações suaves de entrada ao rolar
- **Design totalmente responsivo** — funciona em mobile, tablet e desktop

## Estrutura de arquivos

```
index.html          — Página única (one page)
css/style.css       — Todos os estilos (design editorial)
js/main.js          — Interatividade (filtro, lightbox, nav, reveal)
images/
  addis-ababa.jpg   — Obra Addis Ababa
  hana-detalhe.jpg  — Obra Hana (detalhe)
  lalibela.jpg      — Obra Lalibela
  pez-a.jpg         — Obra Pez III (vista geral)
  pez-iii-01.jpg    — Obra Pez III (vista 2)
  pez-iii-02.jpg    — Obra Pez III (vista 3) — usada no hero
  puzzle.jpg        — Obra Puzzle 2012
  cometas.jpg       — Série Cometas de Grande Formato
  fabio.crisanti.artes.plasticas/
    — Galeria do Instagram (fotografias históricas e contemporâneas)
    — 2024-08-19_22-51-41_UTC.webp  — Luz Líquida (1995)
    — 2023-12-03_16-40-16_UTC.webp  — Cotidiano I (2004)
    — 2023-12-08_16-23-51_UTC.jpg   — Fotogaleria (2010)
    — 2023-12-11_04-30-15_UTC.jpg   — Bambú I (2023)
    — 2023-12-13_21-30-38_UTC.jpg   — Bambú II (2023)
    — 2023-12-13_21-32-02_UTC.jpg   — Bambú III (2023)
```

## URIs / Âncoras

| Âncora       | Seção               |
|-------------|---------------------|
| `#hero`     | Capa / Hero         |
| `#sobre`    | Sobre o Artista     |
| `#obras`    | Catálogo de Obras   |
| `#series`   | Série Seda          |
| `#trajetoria` | Trajetória / CV   |
| `#contato`  | Contato             |

## Fontes de conteúdo

- Instagram: [@fabio.crisanti.artes.plasticas](https://www.instagram.com/fabio.crisanti.artes.plasticas/)
- Blog/catálogo original: [fabiocrisanti.blogspot.com](https://fabiocrisanti.blogspot.com/)
- Galeria 33: [galeria33.com/fabiocrisanti](https://www.galeria33.com/fabiocrisanti)
- Saatchi Art: [saatchiart.com/account/profile/2168629](https://www.saatchiart.com/account/profile/2168629)

## Próximos passos sugeridos

- [ ] Adicionar galeria de fotografias (série Exílio, Cotidiano, Perfume)
- [ ] Integrar feed do Instagram via API para atualização automática de obras recentes
- [ ] Adicionar página ou modal de detalhes individuais de cada obra
- [ ] Adicionar formulário de contato funcional
- [ ] Traduzir para inglês/espanhol para alcance internacional
- [ ] Otimizar imagens com formatos modernos (WebP/AVIF)
- [ ] Adicionar metatags Open Graph para compartilhamento em redes sociais

## Tecnologias

- HTML5 semântico
- CSS3 (Custom Properties, Grid, Flexbox, animações puras)
- JavaScript vanilla (ES6+, IntersectionObserver, sem dependências)
- Fontes: Google Fonts (Cormorant Garamond + Lato)
