# Design: cores dos cards de Crítica

## Objetivo

Integrar visualmente os boxes dos textos da subseção “Crítica” ao fundo dourado claro adotado no site, preservando a legibilidade e distinguindo-os das demais subseções de Literatura.

## Escopo

- Aplicar o tratamento somente aos elementos `.literatura-card` descendentes de `#critica`.
- Compartilhar o mesmo tratamento entre as páginas PT-BR e espanhola por meio do CSS comum.
- Não alterar o HTML, os textos, os cards de outras subseções nem o modal de leitura.

## Tratamento visual

- Fundo dos cards: dourado claro já existente no projeto, `#D4B38A`.
- Títulos e excertos: tons escuros da paleta atual para manter contraste sobre o novo fundo.
- Borda: discreta e coerente com o dourado, sem aparência de contorno pesado.
- Sombra padrão: suave, curta e difusa nas bordas.
- Hover: conservar o pequeno deslocamento vertical existente e aumentar a sombra apenas de forma sutil.
- Botões: manter o acabamento claro e a legibilidade atuais.

## Implementação

Adicionar regras CSS especificamente qualificadas por `#critica`, depois das regras gerais de `.literatura-card`, para sobrescrever apenas fundo, borda, sombra e cores tipográficas necessárias. Essa abordagem evita duplicar marcação e impede efeitos colaterais nos demais conteúdos literários.

## Verificação

- Teste automatizado deve confirmar a existência do seletor isolado, do fundo `#D4B38A`, da sombra e da cor escura do texto.
- Verificação no navegador deve conferir PT-BR e espanhol, em desktop e mobile.
- Os cards fora de `#critica` devem conservar o estilo escuro atual.
