# Peixe ao lado do monograma no cabeçalho

## Objetivo

Adicionar o desenho de `img/Peces/03.jpg` ao lado do monograma “FC” no cabeçalho, sem o retângulo branco do JPEG e sem reduzir a legibilidade sobre o hero.

## Decisão visual

Foi escolhida a alternativa “Assinatura discreta”. O “FC” continua sendo o elemento principal da marca, acompanhado por uma versão compacta do peixe. O conjunto permanece dentro do link que leva ao início da página.

## Tratamento do arquivo

- Preservar `img/Peces/03.jpg` sem alterações.
- Gerar um novo arquivo derivado com canal alfa, removendo apenas o fundo branco.
- Recortar as margens vazias para que o tamanho CSS represente o desenho, não a tela branca original.
- Manter os traços e suas pequenas irregularidades, evitando redesenhar ou vetorizar a obra.

## Comportamento do cabeçalho

- No estado aberto, sobre o hero, o peixe terá traço branco para acompanhar o “FC”.
- No estado compacto, após a rolagem, o peixe terá traço escuro sobre o fundo claro.
- O peixe terá aproximadamente 39 px no estado aberto e será reduzido proporcionalmente no estado compacto.
- “FC” e peixe serão alinhados verticalmente e separados por um espaço curto e constante.
- Em telas pequenas, o conjunto será reduzido sem ocultar o peixe e sem colidir com o botão de navegação.

## Implementação

O link `.nav-logo` passará a conter dois elementos: o texto “FC” e a imagem decorativa. O texto alternativo da imagem será vazio porque o nome acessível do link já identifica Fabio Crisanti; assim, leitores de tela não anunciam informação duplicada. O CSS existente continuará controlando os dois estados por meio de `.site-header.scrolled` e `.site-header:not(.scrolled)`.

## Verificação

- Confirmar que não há halo branco perceptível em torno dos traços.
- Conferir o alinhamento nos estados aberto e compacto.
- Conferir contraste sobre o hero e sobre o fundo claro.
- Conferir desktop e largura móvel.
- Confirmar que o link do monograma continua levando ao início da página.
