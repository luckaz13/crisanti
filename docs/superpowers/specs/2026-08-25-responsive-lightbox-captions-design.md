# Legendas responsivas no lightbox

## Objetivo

Exibir no lightbox, em navegadores desktop, a legenda completa disponível no slide da galeria. Em dispositivos móveis, preservar o foco exclusivo na imagem e não mostrar a legenda.

## Comportamento

- Acima de 768 px, o lightbox exibe título, ano, dimensões, técnica e descrição existentes no slide.
- Até 768 px, a legenda do lightbox fica visualmente oculta.
- A seção Peixes continua sem legenda em qualquer resolução, conforme decisão editorial anterior.
- Obras que possuam apenas parte dos metadados exibem somente os campos disponíveis, sem separadores vazios.
- Navegação, zoom, contador, fechamento e botão de consulta não mudam.
- Ao redimensionar ou girar a tela, a regra visual acompanha imediatamente o novo breakpoint por CSS.

## Arquitetura

O lightbox continuará sendo único para desktop e mobile. `js/main.js` coletará o conteúdo textual já renderizado em cada slide:

- `.gallery-title` para o título;
- `.gallery-meta` para ano, dimensões e técnica;
- `.gallery-desc` para descrição adicional.

Esses valores serão armazenados no item do lightbox e combinados no momento da abertura ou navegação. O elemento `#lightbox-caption` existente receberá a legenda completa.

`css/style.css` controlará apenas a apresentação responsiva: a legenda será exibida no desktop e ocultada dentro da media query de até 768 px. A ausência deliberada de `figcaption` em Peixes produzirá naturalmente uma legenda vazia, sem tratamento específico por nome de galeria.

## Acessibilidade

- O atributo `alt` da imagem continuará disponível em todas as resoluções.
- Ocultar a legenda visual no mobile não removerá o texto alternativo da imagem.
- Não serão duplicados elementos de lightbox nem controles interativos.

## Testes

- Teste automatizado confirmará que itens de carrossel capturam título, metadados e descrição.
- Teste automatizado confirmará que a legenda completa é composta apenas com campos presentes.
- Teste automatizado confirmará a regra CSS que oculta `.lightbox-caption` até 768 px.
- Teste automatizado confirmará que slides sem `figcaption`, como Peixes, geram legenda vazia.
- Validação no navegador verificará uma obra com legenda completa em largura desktop e sua ausência em largura mobile.
- A navegação entre imagens será verificada para garantir que a legenda acompanhe a obra ativa.

## Fora de escopo

- Alterar ou revisar o conteúdo editorial das legendas.
- Mostrar legendas em Peixes.
- Redesenhar o lightbox ou modificar seus controles.
- Criar breakpoints adicionais ou detecção por agente de usuário.
