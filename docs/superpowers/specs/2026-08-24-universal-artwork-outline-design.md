# Contorno universal das obras

## Objetivo

Criar uma separação branca fina em torno de toda obra exibida no site, acompanhada de sombra sutil, sem alterar o tamanho aparente, o recorte ou a proporção das imagens.

## Decisão visual

Foi escolhida a alternativa “Contorno de 1 px”. O acabamento será composto por um contorno branco de `1px`, sem preenchimento ou espaçamento interno, e uma sombra curta de baixa opacidade. O resultado deve permanecer quase imperceptível em fundos claros e produzir separação suficiente em fundos escuros.

## Escopo

O acabamento será aplicado às superfícies que exibem obras:

- imagens dos cards da seção “Obras”;
- imagens dos carrosséis das séries;
- imagens das galerias estáticas e dinâmicas;
- prévias artísticas oriundas do Instagram;
- imagem ampliada no lightbox.

O acabamento não será aplicado a retratos do artista, imagens editoriais ou literárias, ícones, logotipos, fundos decorativos e elementos de navegação.

## Comportamento

- O contorno não poderá participar do cálculo de largura ou altura da imagem.
- A sombra-base será uniforme entre as diferentes superfícies de obra.
- Interações de hover existentes serão preservadas; quando já houver elevação, a sombra poderá se aprofundar discretamente.
- No lightbox, o contorno deverá permanecer visível sobre o fundo escuro e acompanhar a imagem durante o zoom.
- O acabamento será idêntico nas versões portuguesa e espanhola, que compartilham a mesma folha de estilos.

## Verificação

- Conferir cards, carrosséis, Instagram e lightbox.
- Conferir fundos claros, quentes e escuros.
- Conferir desktop e largura móvel.
- Confirmar que nenhuma imagem deixa de caber no contêiner ou passa a ser cortada.
- Confirmar que retratos, capas literárias e elementos não artísticos permanecem inalterados.
