# Reconciliação do acervo editorial e migração de mídia

## Objetivo

Reconciliar o acervo publicado com a reorganização mais recente entregue pelo artista em `/img/`. A mesma iniciativa deve atualizar a ordem das galerias, incorporar imagens novas, preservar conteúdos legados ainda utilizados, inserir textos e fichas, revisar o espanhol, produzir traduções fiéis para PT-BR e consolidar os assets publicados em `/img/images/`.

Depois da aprovação funcional e visual, uma etapa separada deverá remover do histórico Git os antigos blobs de `/images/`, reduzindo de fato o tamanho do repositório remoto.

## Princípios editoriais

1. `/img/` é a fonte de verdade editorial para as galerias que possuam pasta correspondente.
2. A ordem natural dos nomes dos arquivos (`00`, `01`, `02`...) prevalece sobre a numeração encontrada nas fichas.
3. As fichas fornecem metadados, mas não podem alterar a ordem definida pelos nomes atuais.
4. Conteúdo publicado sem equivalente em `/img/` deve ser preservado como legado até deliberação posterior do artista.
5. Conflitos não serão resolvidos por suposição. Devem ser registrados para decisão humana.
6. O espanhol pode receber revisão ortográfica e gramatical completa, sem reescrita estilística.
7. O conteúdo em PT-BR será uma tradução fiel do espanhol revisado.
8. Peixes/Peces permanece sem legenda visual, pois os nomes disponíveis são apenas numéricos. Os textos alternativos acessíveis permanecem localizados.

## Arquitetura de arquivos

### Acervo editorial local

`/img/` preserva a organização recebida do artista: imagens originais, fichas, textos, apresentações e documentos. Ele funciona como entrada editorial e não deve ser reorganizado automaticamente.

### Assets publicados

`/img/images/` será o único diretório de mídia utilizado pelo site e versionado para publicação. Sua estrutura seguirá seções e subséries, com nomes previsíveis e estáveis.

O site em português e espanhol compartilhará os mesmos arquivos físicos. Apenas textos, legendas e atributos alternativos serão localizados.

### Diretório legado

O diretório atual `/images/` deixará de ser referenciado pelo site. Depois da migração funcional, ele permanecerá somente no computador local e será ignorado pelo Git. Arquivos legados ainda utilizados serão copiados para `/img/images/` e classificados no manifesto.

A entrada do `.gitignore` deve ignorar o acervo local e o antigo `/images/`, mas permitir explicitamente o versionamento de `/img/images/` e dos documentos publicados necessários.

## Manifesto editorial

Será criado um manifesto versionado e legível por máquina. Cada registro deverá conter, quando aplicável:

- seção e subsérie;
- caminho original em `/img/`;
- posição editorial derivada do nome;
- caminho publicado em `/img/images/`;
- hash e dimensões do arquivo;
- classificação do asset;
- legenda original extraída;
- legenda em espanhol revisado;
- legenda em PT-BR;
- texto de apresentação em espanhol revisado;
- texto de apresentação em PT-BR;
- texto alternativo nos dois idiomas;
- status da conferência visual;
- alertas de conflito, duplicidade ou ausência de ficha.

As classificações possíveis são:

- `atual`: pertence ao acervo reorganizado e será publicado;
- `novo`: pertence ao acervo reorganizado e ainda não está no site;
- `legado-em-uso`: não está no novo acervo, mas continua referenciado;
- `substituído`: versão antiga que deixará de ser referenciada;
- `conflito`: correspondência editorial ambígua e pendente de decisão.

## Reconciliação de imagens

A correspondência não dependerá apenas do nome. Serão considerados hash do conteúdo, dimensões, pasta editorial, posição numérica, referências atuais no HTML e inspeção visual.

O inventário inicial encontrou:

- 453 imagens em `/img/`, representando 448 conteúdos únicos;
- 717 imagens em `/images/`, representando 683 conteúdos únicos;
- 369 arquivos de origem com conteúdo idêntico já existente em `/images/`;
- 84 imagens do acervo atual sem cópia byte a byte idêntica no conjunto publicado;
- 334 imagens publicadas sem equivalente byte a byte no novo acervo, incluindo materiais legados e assets gerais.

Mudanças materiais já detectadas:

- galerias novas: Gatos, La Papa e Flores;
- acréscimos em Cadernos, Invierno II/III, Moda, Vlak e Seda Bahia;
- substituições relevantes em Perspectiva, Pez III e Seda 2024;
- ordens divergentes em Seda, Urubús, Addis Abbaba, Soies Sauvages, Cotidiano, Cadaver Exquisito, Der Elefant e El Ciervo;
- boa correspondência inicial em Peixes, Collagem, El Teléfono, Exilio, Luz Líquida, Pez IV, La Fuente y los Simios e outras galerias, ainda sujeitas à conferência editorial completa.

Antes de desativar `/images/`, todas as referências de HTML, CSS e JavaScript serão inventariadas. A migração só será aceita quando não houver referência ativa ao diretório antigo.

## Textos, legendas e abas

Cada subsérie funcionará como uma unidade editorial. Ao selecionar uma aba, a interface deve atualizar de forma sincronizada:

- título da subsérie;
- texto de apresentação;
- galeria e ordem das imagens;
- legenda da imagem ativa;
- chamada de contato específica, quando houver.

As legendas podem combinar título, ano, técnica, materiais, dimensões, local e crédito fotográfico. Campos ausentes devem ser omitidos sem placeholders.

Textos curtos ficam diretamente associados à aba. Textos longos devem usar uma apresentação de leitura confortável e expansão acessível, seguindo o padrão já utilizado em Literatura quando adequado.

A implementação deve incorporar os textos autorais já auditados para Seda, Seda Bahia, El Teléfono, Crema/Emulsión, Urubús, Cotidiano, Luz Líquida, Moda, Cadaver Exquisito, El Calendario, El Puzzle, Cósimo, Der Elefant, El Ciervo, Seis Animales, La Fuente y los Simios, Vlak e Literatura/Ficção.

As novas subséries Gatos, La Papa e Flores devem ser incluídas sem remover abas ou galerias legadas.

Os documentos de Master Taxi e os PowerPoints de La Fuente y los Simios continuam acessíveis por download conforme as decisões anteriores. A reconciliação deve verificar seus caminhos após a migração dos assets.

## Tratamento de conflitos

- Nome do arquivo e sua ordem atual prevalecem sobre a ficha.
- Uma ficha sem imagem correspondente gera alerta, não uma entrada inventada.
- Uma imagem sem ficha permanece publicável, com `alt` descritivo e sem metadados fabricados.
- Duplicatas exatas devem apontar para um único asset publicado sempre que a semântica editorial permitir.
- Imagens visualmente semelhantes, mas não idênticas, não serão deduplicadas automaticamente.
- Conteúdo legado ambíguo permanece publicado até revisão do artista.

## Fases de execução

### 1. Inventário e manifesto

Extrair o conteúdo de DOCX, PDF e PPTX, mapear as imagens, registrar hashes e dimensões, comparar referências do site e produzir o manifesto completo e o relatório de conflitos.

### 2. Conteúdo editorial

Revisar o espanhol, traduzir para PT-BR, associar textos e fichas às subséries e validar manualmente as correspondências entre número, legenda e imagem.

### 3. Consolidação dos assets

Montar `/img/images/` com assets atuais e legados em uso, mantendo caminhos estáveis. Não remover o diretório antigo durante esta fase.

### 4. Atualização do site

Atualizar PT e ES, reordenar carrosséis, criar galerias ausentes, sincronizar textos com abas, inserir legendas e alterar todas as referências de mídia para `/img/images/`.

### 5. Verificação funcional e visual

Testar arquivos, carrosséis, abas, autoplay, lightbox, responsividade, acessibilidade, traduções, downloads e ausência de referências a `/images/`. Comparar visualmente cada sequência com `/img/`.

### 6. Aprovação humana

Disponibilizar o site local para revisão. A limpeza do histórico fica bloqueada até aprovação explícita da migração funcional.

### 7. Desativação local de `/images/`

Remover `/images/` do índice Git e adicioná-lo ao `.gitignore`, preservando uma cópia local ignorada. Confirmar novamente que o site funciona exclusivamente com `/img/images/`.

### 8. Limpeza histórica

Em operação separada:

1. criar referência de segurança;
2. reescrever o histórico removendo os blobs antigos de `/images/` e somente outros blobs substituídos previamente identificados;
3. reconstruir e comparar o site antes e depois;
4. medir o espaço recuperado;
5. executar `force push` coordenado após autorização final;
6. documentar a necessidade de recriar ou realinhar outros clones.

## Testes e critérios de aceite

A migração funcional será considerada pronta quando:

- a ordem de cada galeria corresponder à ordenação natural de `/img/`;
- todos os arquivos atuais estiverem representados ou registrados como conflito;
- conteúdos legados ainda utilizados permanecerem publicados;
- textos, legendas e atributos alternativos estiverem presentes nos dois idiomas;
- Peixes/Peces permanecer sem legenda visual;
- a troca de aba atualizar texto e galeria em conjunto;
- não houver referências ativas a `/images/`;
- não houver erro de carregamento em PT ou ES;
- carrosséis, autoplay, controles manuais e lightbox continuarem funcionando;
- desktop e mobile forem validados;
- downloads continuarem acessíveis;
- a conferência visual por galeria estiver registrada no manifesto.

A limpeza histórica será considerada pronta quando:

- houver referência de segurança verificável;
- o conteúdo publicado for idêntico antes e depois da reescrita;
- o tamanho do repositório remoto apresentar redução mensurável;
- o `force push` tiver autorização explícita e resultado verificado;
- as instruções para outros clones estiverem documentadas.

## Fora de escopo

- remover obras legadas por decisão curatorial;
- reescrever estilisticamente os textos do artista;
- criar metadados inexistentes;
- adotar CMS ou reconstruir o site como aplicação dinâmica;
- executar a limpeza histórica antes da aprovação funcional e visual;
- alterar a política editorial de Peixes/Peces.
