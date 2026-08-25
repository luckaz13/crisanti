# Collagem em Ensaios — Design

## Objetivo

Adicionar a série `Collagem` como a primeira subgaleria da seção Ensaios nas versões PT-BR e espanhol, preservando a ordenação alfabética das abas.

## Acervo publicado

Copiar exatamente três imagens de `/home/lucas/Projetos/crisanti/img/Ensayos/Collagem/` para uma pasta pública rastreada pelo Git sob `images/galerias/Ensayos/Collagem/`:

1. `01.jpg`
2. `02.jpg`
3. `03.jpg`

Os arquivos de origem permanecerão intactos. `Ficha Ensayos Collage.docx` será usado apenas como fonte das legendas e não será copiado, publicado nem vinculado no site.

## Navegação e galeria

- Inserir a aba `Collagem` antes de `Crema` nas duas páginas.
- Tornar `Collagem` a aba ativa inicial de Ensaios.
- Remover o estado ativo inicial de `Crema`, que continuará imediatamente após Collagem.
- Criar o painel `gallery-carousel-ensayos-collagem` no início do grupo `ensayos`.
- Usar os controles, viewport, track, slides e lightbox já existentes.
- Manter a ordem numérica `01`, `02`, `03`.

## Legendas

Cada slide exibirá título, ano e suporte conforme os metadados fornecidos pelo artista:

| Arquivo | Título | Ano | Suporte |
|---|---|---:|---|
| `01.jpg` | Collage I | 1998 | Papel fotográfico |
| `02.jpg` | Collage II | 1998 | Papel fotográfico |
| `03.jpg` | Collage III | 1999 | Papel fotográfico |

Os mesmos textos serão usados em PT-BR e espanhol. As imagens terão texto alternativo que combine título, ano, suporte e nome do artista.

## Apresentação

As três obras reutilizarão a estrutura visual dos demais carrosséis de Ensaios. A superfície universal já existente continuará fornecendo contorno branco e sombra sutil. Não serão criados estilos exclusivos para Collagem, salvo se a marcação existente exigir uma correção geral para exibir os metadados.

## Verificação

A implementação será considerada concluída quando:

1. Exatamente três JPEGs públicos forem idênticos aos arquivos de origem.
2. Nenhum DOCX for publicado na pasta da galeria.
3. `Collagem` for a primeira aba e a única aba ativa inicial de Ensaios em PT-BR e espanhol.
4. O painel correspondente tiver exatamente três slides na ordem `01`, `02`, `03`.
5. Cada slide exibir o título, ano e suporte corretos.
6. Os três caminhos de imagem retornarem HTTP 200.
7. A troca para Crema e de volta para Collagem funcionar.
8. As imagens abrirem no lightbox com navegação entre as três obras.
9. O layout permanecer sem overflow em uma viewport móvel de 390 px.

