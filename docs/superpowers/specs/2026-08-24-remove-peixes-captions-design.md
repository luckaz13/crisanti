# Remoção das legendas visíveis de Peixes — Design

## Objetivo

Remover as legendas visíveis `Peixe 01`–`Peixe 34` e `Pez 01`–`Pez 34` dos carrosséis da seção Peixes/Peces.

## Alteração

- Remover de cada um dos 34 slides em PT-BR o elemento `figcaption.gallery-caption` e seu título visível.
- Aplicar a mesma remoção aos 34 slides em espanhol.
- Manter `alt="Peixe NN — Fabio Crisanti"` em PT-BR.
- Manter `alt="Pez NN — Fabio Crisanti"` em espanhol.
- Preservar imagens, ordem, autoplay de dois segundos, controles, swipe, lightbox, textos curatoriais e CTAs.
- Não alterar as legendas visíveis de Cadernos, Collagem ou qualquer outra galeria.

## Comportamento esperado

Sem `figcaption`, a altura do viewport será calculada apenas pela figura/imagem, eliminando o espaço anteriormente reservado abaixo das obras. O texto alternativo continuará fornecendo identificação acessível sem aparecer visualmente.

## Verificação

1. Os painéis Peixes e Peces terão 34 slides e zero `.gallery-caption`.
2. Os 68 textos alternativos localizados permanecerão corretos.
3. Cadernos e Collagem continuarão exibindo suas legendas.
4. Autoplay, controles e lightbox continuarão funcionando.
5. O layout permanecerá sem overflow em 390 px.

