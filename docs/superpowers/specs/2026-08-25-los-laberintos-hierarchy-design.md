# Hierarquia editorial de Os Labirintos

## Objetivo

Eliminar a falsa associação entre o título geral “Os Labirintos” e os textos específicos das subseções. O usuário deve reconhecer imediatamente qual galeria está ativa, qual texto pertence a ela e quando uma subseção não possui apresentação própria.

## Abordagem escolhida

A seção manterá duas áreas com responsabilidades distintas:

- A coluna esquerda apresentará permanentemente o título geral “Os Labirintos”, o texto introdutório da seção e o botão de consulta.
- A coluna direita apresentará as abas, o título explícito da subseção ativa, o texto específico correspondente e a galeria ativa.

O conteúdo específico ficará entre as abas e o carrossel, conforme a estrutura aprovada durante a auditoria. Essa organização será aplicada igualmente à versão PT-BR e à espanhola.

## Hierarquia visual

A coluna direita seguirá esta ordem:

1. Abas das subseções;
2. título da subseção ativa em nível `h3`;
3. texto específico e eventual crédito;
4. carrossel da subseção ativa.

“Os Labirintos” continuará sendo o `h2` da seção. O título dinâmico utilizará exatamente o texto da aba ativa, preservando títulos próprios como “El Calendario”, “La Papa” e “Memory”.

## Comportamento das subseções

- Cadaver Exquisito, El Calendario, El Puzzle e La Papa exibirão título e texto próprios.
- Las Etiquetas e Memory exibirão o título próprio e a galeria, sem reaproveitar o texto introdutório geral como se fosse conteúdo específico.
- O texto introdutório geral não será mais ocultado durante a troca de abas.
- A alternância continuará atualizando carrossel, estado visual da aba, `aria-selected` e texto correspondente.
- A mudança não alterará imagens, ordem das galerias, legendas das demais séries nem controles do carrossel.

## Implementação estrutural

As duas seções HTML, PT-BR e espanhola, receberão um marcador declarativo para solicitar o layout editorial junto à galeria. O JavaScript de abas continuará genérico:

- se a seção usar o novo marcador, o bloco `.series-copy-display` será criado após a lista de abas;
- o bloco receberá um `h3` com o rótulo da aba ativa;
- o template correspondente será clonado abaixo do título quando existir;
- sem template, somente o `h3` permanecerá visível;
- se a seção não usar o marcador, o comportamento atual das outras seções será preservado.

Essa separação evita condicionar o JavaScript diretamente ao identificador `los-laberintos` e permite reutilizar o padrão editorial em outra seção no futuro sem nova lógica.

## Apresentação responsiva

No desktop, o conteúdo específico permanece na coluna da galeria. No mobile, a ordem natural do grid mantém apresentação geral, abas, título ativo, texto específico e carrossel. O texto longo de “El Calendario” poderá aumentar a distância até o carrossel, mas permanecerá semanticamente associado ao título ativo e não será confundido com o título geral.

## Correção editorial de El Calendario

A mesma entrega corrigirá, na fonte de localização PT-BR, os dois registros da galeria:

- `01.jpg`: título `Capa de “El Calendario”`; detalhe `Motivo: detalhe da personagem do candombe uruguaio “Mamá Vieja”.`
- `02.jpg`: título `Imagens de “El Calendario”`; detalhe `As fotografias foram feitas a partir da série do autor “Hay agua caliente”, exposta no Consulado da República Argentina em Colônia do Sacramento, Uruguai, em 2005.`

Os títulos próprios permanecerão em espanhol. A versão espanhola não sofrerá mudanças editoriais.

## Acessibilidade

- O `h2` continuará identificando a seção geral.
- O novo `h3` identificará programaticamente a subseção ativa.
- As abas manterão `role="tab"` e `aria-selected` sincronizados.
- A ausência de texto específico não produzirá bloco vazio nem repetirá conteúdo genérico.
- A ordem de leitura seguirá a ordem visual em desktop e mobile.

## Testes e validação

- Teste estrutural verificará que PT-BR e espanhol possuem o marcador editorial na seção correta.
- Teste do controlador verificará que o título ativo é criado e atualizado a partir da aba.
- Teste verificará que o texto geral permanece visível ao trocar de aba.
- Teste verificará que Las Etiquetas e Memory exibem título próprio sem corpo específico.
- Testes de localização cobrirão as duas legendas corrigidas de El Calendario e a idempotência da regeneração.
- Validação no navegador percorrerá as seis abas em desktop e mobile nas duas línguas.
- A auditoria PT-BR será executada após regenerar as galerias.

## Fora de escopo

- Escrever novos textos para Las Etiquetas ou Memory.
- Reescrever estilisticamente os poemas ou textos curatoriais.
- Alterar a ordem das subseções.
- Redesenhar globalmente todas as seções com abas.
- Modificar o conteúdo editorial da versão espanhola.
