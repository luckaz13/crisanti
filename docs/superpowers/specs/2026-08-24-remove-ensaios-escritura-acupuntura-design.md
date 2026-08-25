# Remoção de Escritura e Acupuntura de Ensaios

## Objetivo

Remover integralmente os conjuntos “La Escritura” e “Manos en la Acupuntura” da seção Ensaios, incluindo navegação, conteúdo exibido e arquivos de imagem originais.

## Escopo

- Remover as duas abas de `index.html` e `es/index.html`.
- Remover os dois painéis/carrosséis correspondentes de ambas as páginas.
- Excluir os sete arquivos versionados em `images/galerias/Ensayos/La Escritura/`.
- Excluir os quatro arquivos versionados em `images/galerias/Ensayos/Manos en la Acupuntura/`.
- Preservar todas as demais subgalerias de Ensaios.
- Manter “Crema” como aba inicial selecionada.

## Comportamento

O sistema genérico de abas em `js/gallery-tabs.js` não será alterado. Após a remoção, a lista de abas e a lista de painéis continuarão com uma correspondência de um para um. Nenhum identificador, caminho de imagem, texto alternativo ou título relacionado aos dois conjuntos removidos poderá permanecer nas páginas.

## Recuperação

Os arquivos serão excluídos do checkout e do próximo estado publicado, mas permanecerão recuperáveis no histórico do Git.

## Verificação

- Confirmar ausência de “La Escritura”, “Escritura”, “Manos en la Acupuntura” e dos identificadores correspondentes em ambas as páginas.
- Confirmar ausência das duas pastas e dos 11 arquivos no checkout.
- Confirmar que cada aba restante de Ensaios aponta para um painel existente.
- Confirmar que “Crema” continua ativa ao carregar a seção.
- Conferir a seção Ensaios nas páginas em português e espanhol.
