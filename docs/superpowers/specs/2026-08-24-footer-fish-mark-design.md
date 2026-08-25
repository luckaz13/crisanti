# Marca com peixe no rodapé — Design

## Objetivo

Reforçar a coerência da identidade visual replicando no rodapé a assinatura `FC` acompanhada pelo peixe já usada no cabeçalho.

## Estrutura

Nas versões PT-BR e espanhol, inserir a marca imediatamente abaixo de `Fabio Crisanti` e antes do subtítulo profissional/localização.

A composição será um link interno para `#hero`, contendo:

- o texto `FC`;
- a imagem transparente `img/Peces/03-header-mark.png` na página principal;
- a mesma imagem com caminho `../img/Peces/03-header-mark.png` na página em espanhol.

O link terá a classe própria `footer-brand-mark`. O texto terá `footer-brand-mark__text` e a imagem terá `footer-brand-mark__fish`, com `alt=""` por ser parte decorativa de uma marca já identificada pelo rótulo do link.

O rótulo acessível será `Fabio Crisanti — voltar ao início` em português e `Fabio Crisanti — volver al inicio` em espanhol.

## Apresentação visual

A assinatura ficará centralizada e em linha, com espaçamento proporcional ao cabeçalho. O texto usará a fonte serifada da identidade; texto e peixe serão brancos sobre o fundo escuro do rodapé. O peixe reutilizará o arquivo processado existente, com filtro branco aplicado via CSS.

A marca será menor que a versão expandida do cabeçalho, para preservar a hierarquia do rodapé. O tamanho será fluido dentro de limites compactos e não terá a animação de escala do cabeçalho.

O link terá transição sutil de opacidade no hover e contorno perceptível em `:focus-visible`. Em telas estreitas, a composição permanecerá em uma linha e dentro da largura disponível.

## Escopo

- Não alterar a marca do cabeçalho.
- Não criar nem processar um novo arquivo de imagem.
- Não alterar os demais textos, links ou ordem do rodapé, exceto pela inserção da assinatura entre nome e subtítulo.
- Aplicar a mesma estrutura visual às versões PT-BR e espanhol.

## Verificação

A implementação será considerada concluída quando:

1. Cada rodapé contiver exatamente uma `.footer-brand-mark` abaixo de `.footer-name`.
2. Cada marca contiver `FC` e o arquivo `03-header-mark.png` com o caminho correto para o idioma.
3. O link apontar para `#hero` e tiver o rótulo acessível localizado.
4. A imagem for decorativa (`alt=""`) e carregada com sucesso pelo servidor.
5. O peixe tiver contraste branco sobre o rodapé escuro.
6. A marca couber sem overflow em desktop e em uma viewport móvel de 390 px.
7. O cabeçalho e os demais elementos do rodapé permanecerem inalterados.

