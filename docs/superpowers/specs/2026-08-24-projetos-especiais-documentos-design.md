# Documentos de Projetos Especiais — Design

## Objetivo

Disponibilizar os materiais complementares de dois projetos especiais diretamente no site, oferecendo ao visitante tanto a visualização online pelo Google quanto o download do arquivo original.

## Escopo

### La Fuente y los Simios

Publicar, dentro do painel dessa subgaleria, as duas apresentações existentes:

- `Apresentação Captação 2024-12-13.pptx`
- `Maquete La Fuente y los Simios.pptx`

Cada apresentação terá dois controles separados:

- `Ver no Google Slides` em português e `Ver en Google Slides` em espanhol;
- `Baixar PowerPoint` em português e `Descargar PowerPoint` em espanhol.

### Master Taxi

Publicar, dentro do painel dessa subgaleria, os dois documentos existentes:

- `Master Taxi Dinámica.docx`
- `Master Taxi Sinópsis.docx`

Cada documento terá dois controles separados:

- `Ver no Google Docs` em português e `Ver en Google Docs` em espanhol;
- `Baixar DOCX` em português e `Descargar DOCX` em espanhol.

### Fora do escopo

- Os documentos de Vlak não serão publicados neste ajuste.
- Os arquivos não serão convertidos para PDF.
- Os documentos não serão enviados nem gerenciados no Google Drive.

## Arquitetura e conteúdo

Os quatro arquivos originais serão copiados de `img/Proyectos Especiales` para uma pasta pública rastreada pelo Git, sob `documents/proyectos-especiales`, organizados por projeto. Os originais permanecerão intactos.

Cada painel ganhará uma área `Documentos do projeto` / `Documentos del proyecto` abaixo do conteúdo visual existente. A área será formada por cards compactos, um por arquivo, contendo nome, tipo do documento e as duas ações.

Os links de download apontarão para os arquivos públicos relativos ao idioma da página e usarão o atributo `download`. Os links de visualização abrirão em nova aba com `rel="noopener"` e usarão o visualizador do Google com a URL absoluta e codificada do arquivo publicado em `https://luckaz13.github.io/crisanti/`.

## Comportamento por ambiente

- No site publicado, os botões de visualização enviarão ao Google a URL pública do arquivo e deverão abrir o documento no visualizador correspondente.
- No servidor local, os downloads serão testáveis normalmente.
- A visualização no Google não poderá carregar arquivos servidos por `localhost`; portanto, o destino será validado estruturalmente no ambiente local e funcionalmente após a publicação.
- Se o Google não conseguir renderizar determinado arquivo, o usuário ainda terá o botão de download do original como alternativa permanente.

## Apresentação visual e acessibilidade

A área documental seguirá o estilo editorial existente: tipografia atual, borda fina, fundo discreto e botões coerentes com os controles do site. Os cards serão responsivos e empilhados em telas estreitas.

Os nomes dos arquivos permanecerão visíveis. Os links terão rótulos específicos para cada documento, foco de teclado perceptível e indicação de abertura em nova aba nos atributos acessíveis quando aplicável.

## Verificação

A implementação será considerada concluída quando:

1. Os quatro arquivos públicos forem idênticos aos originais e acessíveis por HTTP.
2. La Fuente y los Simios exibir exatamente dois cards de PowerPoint em PT-BR e espanhol.
3. Master Taxi exibir exatamente dois cards de DOCX em PT-BR e espanhol.
4. Cada card tiver um link do Google e um link de download para o arquivo correto.
5. Os links do Google contiverem URLs públicas absolutas e corretamente codificadas.
6. A troca entre as subgalerias continuar funcionando em desktop e mobile.
7. Vlak permanecer sem a nova área documental.

