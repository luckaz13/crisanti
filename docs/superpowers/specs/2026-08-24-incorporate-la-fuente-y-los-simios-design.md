# Incorporação de La Fuente y los Simios

## Objetivo

Substituir o placeholder da subgaleria “La Fuente y los Simios” por um carrossel completo com as 25 imagens JPEG localizadas na árvore de entrada `/img`.

## Ativos

- Copiar somente os 25 arquivos `.jpg` de `img/Proyectos Especiales/La Fuente y los Simios/Exposición Virtual (La Fuente...)/`.
- Não incorporar os arquivos `.pptx` ou `.docx` ao carrossel.
- Preservar os arquivos originais em `/img`; a operação será de cópia, não movimentação.
- Versionar as cópias em `images/galerias/Proyectos Especiales/La Fuente y los Simios/`.

## Ordenação

O carrossel exibirá primeiro as imagens numeradas `01`, `11 (1)`, `16 (3)`, `17 (1)` e `22`, nessa ordem. Em seguida, exibirá as imagens `20260808_*` em ordem cronológica crescente pelo timestamp do nome.

## Interface

- Substituir “Galeria em preparação” nas páginas PT e ES por um carrossel de 25 slides.
- Reutilizar controles, gestos, lazy loading, contorno, sombra e lightbox existentes.
- Usar caminhos iniciados por `images/` em PT e `../images/` em ES.
- Manter “La Fuente y los Simios” como a aba ativa inicial de Projetos Especiais / Proyectos Especiales.

## Verificação

- Confirmar exatamente 25 JPEGs no destino versionado.
- Confirmar exatamente 25 slides e 25 imagens no painel de cada idioma.
- Confirmar que todos os caminhos HTML existem no disco e respondem no servidor local.
- Confirmar ausência do placeholder nas duas páginas.
- Confirmar navegação anterior/próxima, lazy loading e abertura no lightbox.
- Confirmar que `.pptx` e `.docx` não aparecem no HTML.
