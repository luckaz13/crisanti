# Design: pipa inteira na seção Contato

## Objetivo

Substituir a imagem atual da seção Contato por uma obra de pipa inteira que represente melhor a linguagem visual do artista.

## Imagem escolhida

- Arquivo: `img/images/La Escultura/Addis Abbaba/02.jpg`
- Dimensões: 849 × 1182 pixels.
- Justificativa: a silhueta escura em forma de folha é imediatamente reconhecível, cria um ponto focal forte e se adapta naturalmente ao quadro vertical da seção.

## Comportamento visual

- Referenciar diretamente o arquivo já presente no acervo, sem duplicar mídia.
- Substituir `img/images/legacy/lalibela.jpg` nas versões PT-BR e espanhola.
- Exibir a peça inteira com `object-fit: contain` em desktop e mobile.
- Manter o quadro vertical atual e permitir que as pequenas sobras laterais se integrem ao fundo claro da seção.
- Manter a imagem decorativa, com `alt` vazio e sem legenda.

## Escopo

- Alterar somente as imagens da seção `#contato` e a regra `.contato-img` necessária para preservar a peça inteira.
- Não modificar o arquivo original, as galerias de Addis Abbaba, outras imagens ou os textos de Contato.

## Verificação

- Testar por fonte que as duas páginas apontam para o arquivo escolhido e que `.contato-img` usa `object-fit: contain`.
- Conferir no navegador PT-BR e espanhol em desktop e mobile.
- Confirmar que a imagem não é cortada, não causa overflow e conserva a estrutura em duas colunas no desktop e uma coluna no mobile.
