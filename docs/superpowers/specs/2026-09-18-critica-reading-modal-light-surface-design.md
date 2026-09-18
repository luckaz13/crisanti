# Janela de leitura da subseção Crítica — superfície clara

## Objetivo

Adaptar a janela que abre ao selecionar um texto da subseção “Crítica”, na seção “Literatura”, para priorizar legibilidade em uma superfície clara. A mudança deve preservar a estrutura e o comportamento atuais da janela, sem alterar o conteúdo editorial ou o restante da seção.

## Direção visual aprovada

- Manter o backdrop, o cabeçalho e o rodapé da janela em tons escuros.
- Aplicar fundo branco exclusivamente à área de leitura (`.lit-modal-body`).
- Usar texto e título em quase preto sobre o fundo branco.
- Remover ou substituir o dourado apenas nos elementos que ficam sobre o fundo branco da área de leitura, como divisor, capitular e scrollbar.
- Preservar o dourado nos elementos que permanecem sobre fundos escuros, como badge, subtítulo, indicador de tamanho e estados do cabeçalho/rodapé.
- Usar uma escala neutra nos elementos sobre o branco, preservando hierarquia e estados interativos.
- Manter a capitular inicial, o controle de tamanho de fonte, a rolagem interna e os botões existentes.

## Escopo técnico

- Atualizar os estilos da janela em `css/style.css`.
- Aplicar a mesma adaptação à página em espanhol, caso os estilos sejam compartilhados pela folha global.
- Não alterar a estrutura do modal, o JavaScript de abertura/fechamento ou o conteúdo dos textos.

## Critérios de aceite

1. O texto da leitura aparece sobre fundo branco.
2. O corpo do texto, o título e a capitular têm contraste adequado sobre branco.
3. Nenhum elemento sobre o fundo branco depende do dourado para comunicar estado ou hierarquia.
4. Cabeçalho e rodapé permanecem escuros e legíveis.
5. A rolagem e os controles de tamanho continuam utilizáveis em desktop e mobile.
6. Os testes existentes e o detector visual não reportam regressões relevantes.
