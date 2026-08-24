# Der Elefant dentro de As Crianças / Los Niños

## Objetivo

Transferir a apresentação completa de “Der Elefant” da seção independente para a aba correspondente dentro de “As Crianças” em português e “Los Niños” em espanhol.

## Estrutura

- Renomear o título português “Los Niños” para “As Crianças”.
- Manter o título espanhol “Los Niños”.
- Manter a aba “Der Elefant” nas duas versões, removendo o símbolo `↗` que hoje indica navegação externa.
- Substituir o painel de encaminhamento atual pelo conteúdo integral da série: texto curatorial, ação de consulta e carrossel completo.
- Remover a seção independente `#der-elefant` das duas páginas.
- Preservar uma âncora `#der-elefant` dentro do novo painel para compatibilidade com links diretos existentes.

## Ativos e carregamento

As imagens continuarão em `images/highres/Der Elefant/`; nenhum arquivo será duplicado, movido ou excluído. O carrossel transferido continuará usando `loading="lazy"`, evitando o carregamento imediato das imagens que permanecem em uma aba oculta.

## Comportamento

Ao clicar na aba “Der Elefant”, o sistema genérico de `js/gallery-tabs.js` revelará o painel completo. O carrossel deverá manter navegação anterior/próxima, gestos, lightbox e contagem de imagens. A aba “Cósimo” continuará selecionada por padrão ao carregar a seção.

## Verificação

- Confirmar que existe uma única apresentação completa de “Der Elefant” em cada página.
- Confirmar que não existe mais uma seção independente com `id="der-elefant"`.
- Confirmar que a âncora `#der-elefant` existe dentro do novo painel.
- Confirmar que cada aba de As Crianças / Los Niños possui painel correspondente.
- Confirmar que o clique em “Der Elefant” revela texto, consulta e todas as imagens.
- Conferir carrossel, lightbox, lazy loading, desktop e mobile em PT e ES.
