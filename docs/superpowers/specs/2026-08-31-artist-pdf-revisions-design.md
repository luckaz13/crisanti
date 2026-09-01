# Revisões do catálogo solicitadas pelo artista

## Objetivo

Implementar as correções descritas em `Notes_260831_202933.pdf`, refinadas nesta conversa, sem ampliar o escopo editorial. O item de criação de card para Instagram fica explicitamente excluído.

O site continuará estático, bilíngue e publicado pelo GitHub Pages. A esteira existente de inventário, reconciliação, curadoria, publicação e renderização do acervo continuará sendo a fonte estrutural das galerias.

## Fontes e política de preservação

- `drive-download-20260824T065754Z-1-001.zip` é a fonte autoritativa do acervo original.
- `Pequeñas Pipas-20260901T011313Z-1-001.zip` é a fonte suplementar autoritativa para cinco substituições de “Pequeñas Pipas”.
- `img/<categoria>/...` é a área de trabalho do acervo-fonte.
- `/images/` e `/img/images/` são cópias de segurança e não podem ser removidas, sobrescritas ou reorganizadas nesta entrega.
- `img/Peces/03-header-mark.png` é um derivado legítimo do site e deve ser preservado.
- Os ZIPs devem permanecer imutáveis. A implementação os extrairá apenas em uma área temporária, comparará hashes e copiará somente os ativos aprovados.
- A sincronização inicial restaurará do ZIP as versões de `img/Seda/SEDA 2024/04.jpg`, `07.jpg` e `14.jpg`.
- A pasta “Verde” será retirada do manifesto e do site, mas seus arquivos permanecerão no acervo-fonte e nos backups.

## Identidade: monograma e peixe

A mesma composição “FC + peixe” será usada no cabeçalho e no rodapé.

- O peixe apontará para a esquerda por espelhamento horizontal, sem rotação vertical e sem alteração destrutiva da imagem-fonte.
- Sua altura aparente será igual à altura do monograma “FC”.
- O peixe será dimensionado por altura vinculada à caixa tipográfica, com largura automática e `flex-shrink: 0`, evitando diferenças causadas por renderização de fontes entre Linux e Windows.
- Haverá regras explícitas para o cabeçalho aberto, cabeçalho compacto e rodapé.
- O contêiner não poderá apagar ou cortar a parte inferior do desenho.

## Superfície universal das obras

A margem branca será triplicada em todas as imagens de obras e galerias, incluindo cards, séries, carrosséis e lightbox. A implementação usará um único token/regra de superfície para manter consistência, sem alterar imagens decorativas como hero, retrato e contato.

No lightbox:

- a ficha técnica ficará sempre visível abaixo da obra, inclusive em celulares;
- imagem e ficha formarão uma coluna rolável quando excederem a altura disponível;
- fechar, navegar, ampliar e consultar continuarão acessíveis por teclado, mouse e toque;
- a obra não poderá ser cortada para abrir espaço para a ficha.

## Comportamento das galerias

### Peces

Somente o carrossel “Peces” trocará o deslocamento horizontal por crossfade. A imagem atual perderá opacidade enquanto a seguinte ganhará opacidade. Setas, gesto horizontal, avanço automático, pausa, preload e respeito a `prefers-reduced-motion` serão preservados. Os demais carrosséis continuarão com deslocamento lateral.

### Cuadernos

O corte observado em `CUADERNOS CORTADO.png` decorre do acoplamento entre a altura escrita por JavaScript, a medição de uma figura já limitada e o `overflow: hidden` do ancestral `.series-gallery`.

A correção deve:

- calcular a altura pela proporção intrínseca da mídia e pela largura realmente disponível;
- recalcular após `decode/load`, troca de slide e resize;
- não reutilizar uma medição feita sobre conteúdo já cortado;
- restringir apenas o eixo horizontal necessário à navegação, sem cortar imagem, margem branca ou controles no eixo vertical;
- funcionar com imagens quadradas, verticais e panorâmicas.

### Vlak

As duas apresentações de Vlak permanecem no site:

- a seção independente “Vlak: O jogo do trem” manterá o vídeo existente como primeiro slide e exibirá depois as 17 imagens do ZIP, na ordem dos arquivos;
- a subseção Vlak de “Proyectos Especiales” exibirá o mesmo conjunto das 17 imagens;
- os dois arquivos `08.jpg` e `08(1).jpg` são distintos e permanecerão; não existe `07.jpg` no acervo fornecido;
- as faixas pretas laterais são fundos CSS do player e do contêiner, não pixels do vídeo. Elas serão removidas sem recortar, esticar ou recodificar `videos/vlak.mp4`.

## Conteúdo e estrutura editorial

### Ensayos

O texto introdutório em português será:

> Séries de ensaios fotográficos que exploram o cotidiano, os gestos e as texturas do mundo ao redor — registros íntimos onde a câmera se torna instrumento de meditação visual.

A versão espanhola revisada será:

> Series de ensayos fotográficos que exploran lo cotidiano, los gestos y las texturas del mundo que nos rodea — registros íntimos en los que la cámara se convierte en un instrumento de meditación visual.

### Addis Abbaba

A palavra “poético” será removida do texto indicado pelo artista, preservando a concordância da frase nos dois idiomas.

### Los Laberintos

Em todas as subseções, a imagem/galeria virá antes do texto. O texto geral será substituído por:

**Espanhol**

> Sistemas visuales, puzles y juegos conceptuales. Los laberintos de nombrar y numerar.

**Português**

> Sistemas visuais, quebra-cabeças e jogos conceituais. Os labirintos de nomear e numerar.

### Los Niños

- O texto e a ficha de “Seis Animales” serão revistos contra os documentos-fonte.
- Em todas as subseções de “Los Niños”, ano, dimensões, materiais e técnicas deixarão de aparecer com palavras coladas.
- As correções serão feitas na fonte editorial/manifesto e não apenas no HTML renderizado.

### Master Taxi

O conteúdo integral de `Master Taxi Sinópsis.docx` será apresentado diretamente na seção, em parágrafos após a imagem de Master Taxi e sem ação de abrir ou baixar. “Master Taxi Dinámica” continuará com o comportamento atual de abrir/baixar o documento.

### Trayectoria

A timeline existente continuará sendo o CV visual. Inicialmente, aproximadamente o primeiro terço ficará visível. Um controle “Ver mais”/“Ver menos” expandirá e recolherá o restante por clique, toque ou teclado, com estado acessível e sem salto abrupto de foco.

### Literatura e Crítica

- Os boxes da subseção “Crítica” voltarão ao fundo preto do sistema, `#201E1C`.
- Títulos usarão branco e corpo usará o branco quente `#EAE6DF`, preservando contraste e a identidade editorial segundo a auditoria `impeccable`.
- O texto “Em mi obra” será corrigido para “En mi obra”.
- Todos os textos das obras de “Crítica” serão traduzidos para PT-BR.
- Após a implementação, dois agentes revisores sêniores ES→PT-BR compararão independentemente original e tradução. A reconciliação final preservará sentido, títulos, citações e voz autoral, registrando divergências relevantes.

### Ficção / El Nombre

Dentro de “Ficção”, somente a apresentação de “El Nombre” será reorganizada para:

1. título “El Nombre”;
2. galeria de “El Nombre”;
3. textos correspondentes a “El Nombre”.

“Flores” permanecerá no site e não será alterada por esta reorganização.

### Pequeñas Pipas

Cinco obras da portada serão substituídas pelas versões do ZIP suplementar:

- `10.jpg` substitui `pequenas-pipas-1.jpeg`;
- `03.jpg` substitui `pequenas-pipas-2.jpeg`;
- `04.jpg` substitui `pequenas-pipas-3.jpeg`;
- `01.jpg` substitui `pequenas-pipas-5.jpeg`;
- `02.jpg` substitui `pequenas-pipas-6.jpeg`.

`pequenas-pipas-4.jpeg`, a composição com nove estudos, permanecerá como a sexta obra por não possuir substituta no novo material.

## Arquitetura da mudança

Mudanças editoriais e de ordem serão feitas no manifesto e nos arquivos editoriais consumidos pelo renderizador. Os HTMLs PT e ES serão regenerados, evitando edições divergentes. Mudanças interativas ficarão nos módulos JavaScript existentes, com comportamentos específicos ativados por identificadores ou atributos de cada galeria. Tokens e regras visuais compartilhadas permanecerão em `css/style.css`.

Não haverá uma refatoração geral do sistema editorial, troca de framework ou redesenho fora das superfícies citadas.

## Verificação e critérios de aceite

- A auditoria do acervo não aponta referências quebradas nem mídia publicada fora da série correta.
- Os backups e ZIPs mantêm hashes e estrutura inalterados.
- As páginas PT e ES apresentam o mesmo inventário e a ordem editorial definida.
- “Peces” usa crossfade; os demais carrosséis continuam laterais.
- Vlak preserva o vídeo inteiro como primeiro slide na seção independente e não exibe fundo preto lateral.
- A primeira imagem quadrada de Cuadernos aparece inteira, com margem e controles, em desktop `1225×691` e em viewport mobile; casos vertical e panorâmico também passam.
- A ficha técnica do lightbox permanece legível e rolável em desktop e mobile.
- A marca “FC + peixe” mantém alturas visuais equivalentes no cabeçalho e rodapé, em estados aberto/compacto e em desktop/mobile.
- Timeline, Master Taxi e El Nombre obedecem às hierarquias aprovadas.
- Contraste dos cards de Crítica atende WCAG AA para texto normal.
- Testes Python, auditorias de referências, validação estrutural do HTML e detector `impeccable` passam.
- Uma inspeção visual final é feita em uma rodada conjunta desktop/mobile e confirmada em no máximo uma segunda rodada após correções.

## Fora de escopo

- Criar card de apresentação para Instagram.
- Remover “Flores”.
- Remover qualquer uma das duas apresentações de Vlak.
- Alterar ou apagar os backups `/images` e `/img/images`.
- Retraduzir o site inteiro; a revisão sênior ES→PT-BR é restrita às obras de “Crítica”.
- Substituir o stack estático ou redesenhar outras seções.
