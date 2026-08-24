# Simplificação da seção Instagram — Design

## Objetivo

Remover o carrossel local do Instagram e transformar a seção em um convite editorial simples para visitar o perfil oficial de Fabio Crisanti.

## Conteúdo e comportamento

A seção continuará ocupando sua posição atual e mantendo o identificador `instagram` para não quebrar navegação interna.

Em português:

- o título `@fabio.crisanti.artes.plasticas` será um link para o perfil;
- a descrição será `Acompanhe novos trabalhos, processos e registros do artista no Instagram.`;
- o único botão será `Ver Instagram`.

Em espanhol:

- o mesmo título será um link para o perfil;
- a descrição será `Sigue nuevos trabajos, procesos y registros del artista en Instagram.`;
- o único botão será `Ver Instagram`.

O link do título e o botão apontarão para `https://www.instagram.com/fabio.crisanti.artes.plasticas/`, abrirão em nova aba e usarão `rel="noopener"`. O botão incluirá uma marca do Instagram em SVG inline antes do texto, sem dependência externa.

## Apresentação visual e acessibilidade

A seção permanecerá centralizada e sóbria, seguindo a tipografia, as cores e o botão contornado já usados pelo site. O título clicável terá estado de foco visível e não dependerá apenas de cor para indicar interação. O SVG será decorativo, com `aria-hidden="true"`, enquanto o texto do botão continuará fornecendo o nome acessível.

## Remoções

- Remover o elemento `#instagram-grid` das páginas PT-BR e espanhol.
- Remover os estilos exclusivos de `.instagram-grid` e `.instagram-card`, inclusive suas regras responsivas.
- Remover de `js/gallery.js` a geração do preview local do Instagram.
- Remover de `js/main.js` a coleta e o tratamento de cards do Instagram no lightbox, além das referências de animação exclusivas de `.instagram-card`.
- Preservar qualquer referência ao Instagram usada em outras áreas, como cabeçalho, contato e rodapé.
- Preservar os dados e imagens locais existentes; esta mudança não apaga arquivos de acervo.

## Verificação

A alteração será considerada concluída quando:

1. Não existir `#instagram-grid` nem `.instagram-card` nas páginas ou scripts ativos.
2. A seção Instagram continuar presente em PT-BR e espanhol.
3. O título e o único botão da seção apontarem para o perfil correto em cada página.
4. Cada seção tiver exatamente um botão `Ver Instagram`, com SVG decorativo.
5. Os links abrirem em nova aba com `rel="noopener"` e foco de teclado visível.
6. Nenhum carrossel ou lightbox for acionado nessa seção.
7. As outras galerias e seus lightboxes continuarem funcionando.
8. O layout permanecer centralizado e sem overflow em desktop e mobile.

