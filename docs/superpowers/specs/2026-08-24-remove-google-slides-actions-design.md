# Remoção das ações do Google Slides — Design

## Objetivo

Simplificar o acesso às apresentações de La Fuente y los Simios, mantendo apenas o download dos arquivos PowerPoint originais.

## Alteração

- Remover os dois links `Ver no Google Slides` da versão em português.
- Remover os dois links `Ver en Google Slides` da versão em espanhol.
- Manter um botão `Baixar PowerPoint` / `Descargar PowerPoint` em cada card.
- Preservar os nomes dos arquivos, os rótulos de tipo e os quatro arquivos públicos.
- Não alterar os links `Ver no Google Docs` / `Ver en Google Docs` de Master Taxi neste momento.

## Decisão pendente

Os links do Google Docs de Master Taxi serão avaliados após o push, quando os arquivos estiverem disponíveis nas URLs públicas usadas pelo visualizador. Esta mudança não antecipa essa decisão.

## Apresentação e acessibilidade

Os cards de PowerPoint continuarão usando a estrutura e o estilo existentes. Com uma única ação, o botão de download permanecerá claramente identificado, acessível por teclado e associado ao arquivo correto por `aria-label`.

## Verificação

A alteração será considerada concluída quando:

1. La Fuente y los Simios tiver dois cards e exatamente dois links de download em cada idioma.
2. Nenhum link ou texto do Google Slides permanecer nos painéis de La Fuente y los Simios.
3. Os quatro links do Google Docs de Master Taxi — dois por idioma — permanecerem inalterados.
4. Os downloads dos dois PowerPoints continuarem retornando HTTP 200.
5. A troca de abas e o layout responsivo continuarem funcionando.

