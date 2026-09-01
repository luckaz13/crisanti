# Reconciliação editorial — Crítica ES → PT-BR

## Metodologia

Os pareceres sêniores A e B foram avaliados item a item contra a seção `#critica` de `es/index.html` e a primeira passagem em `data/acervo/editorial-literatura-critica.json`. A decisão combinou, nesta ordem: fidelidade semântica ao original publicado em espanhol, naturalidade em PT-BR e preservação da dicção ensaística de Fabio Crisanti. Trechos que já estavam em português no original foram tratados como voz autoral e só receberam correções gramaticais inequívocas.

Os DOCX citados pelo revisor A foram usados como evidência auxiliar para diagnosticar quebras e conferir nomes, não para acrescentar títulos, assinaturas ou frases ausentes do original espanhol publicado. A grafia `Florencio Yllana` foi aceita porque é corroborada por `manifest.json`, `documents.json` e legendas do próprio acervo. As quatro fusões foram aceitas apenas porque o original separava determinante/substantivo, oração relativa ou núcleo/complemento, sempre com continuação em minúscula.

Cobertura: **8/8 artigos e 86/86 posições-fonte revisadas**. Resultado: **82 parágrafos finais**, após quatro fusões sem supressão. Decisões consolidadas: **39 loci aceitos e 18 rejeitados/mantidos**.

Na tabela, “texto final” mostra o trecho decisório; a redação integral está no JSON editorial.

## Tabela reconciliada

| ID | Artigo/posição | Origem | Decisão | Texto final | Justificativa |
|---|---|---|---|---|---|
| R01 | Introdução | B opcional | Rejeitado | `JLB sempre se reconheceu... importância e significação` | A solução atual é fiel e preserva a autorreferência incomum; a reescrita não corrige erro. |
| R02 | Celso §3 | B necessária | Aceito | `excelente e estranha, mas sólida... É como se...` | Remove calque e pontuação inadequada sem apagar a imagem final do parágrafo. |
| R03 | Celso §5 | A/B opcional | Aceito | `articula a matéria e os elementos pictóricos` | Recupera a dimensão construtiva de `ensambla` com léxico natural de crítica de arte. |
| R04 | Celso §6 | B necessária | Aceito | `elementos tradicionais das artes plásticas... acontecimentos artísticos se dão no interior do quadro` | Corrige dois calques evidentes. |
| R05 | Celso §7 | B opcional | Rejeitado | `Depois, esses julgamentos... derivar para outros julgamentos` | A repetição e o encadeamento pertencem à voz; `supostas` acrescentaria avaliação ausente. |
| R06 | Celso §§8–9 | A/B necessária | Aceito | Um parágrafo: `a atenção que deveria estar absorvida...` | A quebra separava pronome relativo e oração subordinada; 17 posições-fonte passam a 16 parágrafos finais. |
| R07 | Celso §10 | B necessária | Aceito | `a representação dos bancos... fiel àquela gestualidade pessoal e imediata` | `Resolução dos bancos` e a regência anterior eram artificiais em PT-BR. |
| R08 | Celso §12 | B necessária | Aceito | `transmite, já na escolha desse formato “angustiante”, o vértigo` | Remove `desde a escolha` e organiza os encaixes preservando a vertigem sintática. |
| R09 | Celso §13 | B necessária | Rejeitado | `Isso é dar conta da disciplina!` | O trecho já é português no documento e foi confirmado por A; não se substitui imagem autoral por conjectura. |
| R10 | Celso §14 | B necessária | Aceito | `uma potência expressiva equivalente à de qualquer outra tradição expressionista` | Recompõe uma comparação gramaticalmente completa. |
| R11 | Celso §15 | B necessária | Aceito | `a precisão com que elas refletem... — tudo isso se dá por meio de...` | Dá predicação plena às duas frases sem simplificar a imagem. |
| R12 | El nombre §1 | A opcional | Aceito | `e mais: de uma estirpe extinta` | Restitui a inflexão abrupta e os dois-pontos do espanhol. |
| R13 | El nombre §2 | A opcional / B necessária | Aceito (B) | `homens cientes dessa necessidade urgente de se explicar` | `Cientes` corresponde ao contexto justificativo; rejeita-se `precavidos contra`, que inverteria o sentido. |
| R14 | El nombre §3 | B opcional | Aceito | `diante de uma moral qualquer` | Recupera o corte seco de `una moral, cualquiera` em PT natural. |
| R15 | Flores §2 | A necessária | Aceito | `permite outra inauguração. Talvez mais significativa` | Mantém o referente feminino `inauguración`, perdido na primeira passagem. |
| R16 | Flores §3 | A opcional / B necessária | Aceito (B) | `uma órbita menor, atribuível a uma alma... disparo de um projétil` | Remove relação causal inexistente e colocação imprópria; `grava` foi rejeitado porque o original diz `registra`. |
| R17 | Flores §4 | A necessária / B opcional | Aceito (A) | `Uma sentença desmedida serve-lhes de prólogo... vinculação formal entre “finais”` | Restitui a função paratextual; `desfechos` foi rejeitado para preservar a polissemia de `finales`. |
| R18 | Fotografia §2 | B necessária | Aceito | `sob quais condições, se dá a expressividade máxima — ou a verdadeira expressividade —` | Retira `acontece a expressividade` e conserva a hesitação retórica. |
| R19 | Fotografia §3 | A/B necessária | Aceito (B) | `Um mistério que... talvez encontre... para manifestar sua ambiguidade.` | Mantém o fragmento do HTML espanhol; rejeita-se acrescentar `É um mistério.`, presente apenas no DOCX. |
| R20 | Fotografia §4 | B necessária | Aceito | `as diferentes obras se entreolham, em busca da resolução desse “punctum”` | Remove espanholismo e preserva a personificação. |
| R21 | Fotografia §5 | B opcional | Aceito | `Essa necessidade, essa busca, parece mais evidente na obra de Fabio.` | Ordem direta mais natural, sem mudança semântica. |
| R22 | Fotografia §6 | B necessária | Aceito | `A obra contém um potencial performático que permanece latente...` | Estabiliza o sujeito lógico e a progressão latência–expressão. |
| R23 | Fotografia §7 | A/B necessária | Aceito | `o que as fotografias de Kati encontram...` | Elimina ambiguidade entre fotos feitas por Kati e fotos que a retratam. |
| R24 | Hugo, título | A necessária | Rejeitado | Cartão permanece `Hugo França` | `A Terra como Fluido` não consta do original espanhol publicado nem do contrato editorial atual. |
| R25 | Hugo §2 | A opcional / B necessária | Aceito (B) | `seguir adiante... A maioria era constituída por seções gigantescas dessas árvores` | Corrige ambiguidade e concordância, preservando a repetição evocativa. |
| R26 | Hugo §3 | B necessária | Aceito | `a seção escolhida... ia da base... até as extremidades` | Naturaliza a sintaxe e mantém o vocabulário escultórico. |
| R27 | Hugo §4 | B opcional | Aceito | `comecei a avistar aquelas peças monumentais` | Elimina perífrase pesada coerentemente com a aproximação espacial. |
| R28 | Hugo §5 | A/B opcional | Aceito (A) | `Julguei identificar um vínculo` | `Julguei` preserva provisoriedade; mantém-se `identificar`, mais próximo do original que `perceber`. |
| R29 | Hugo §§6–7 | A/B necessária | Aceito | Um parágrafo: `essa pulsão inata do espírito humano` | A quebra separava demonstrativo e substantivo. |
| R30 | Hugo §9 | B opcional | Aceito | `a idade da árvore da qual provinham e as características...` | Corrige referente e reduz repetição sem alterar informação. |
| R31 | Hugo §§10–11 | A/B necessária | Aceito, reconciliado | Um parágrafo: `A exposição muito interessante que França fez sobre a materialidade... num lampejo, julguei compreender` | A relativa esclarece que se trata da explicação de França, não de uma mostra; intensidade sóbria e `lampejo` seguem o português documental. |
| R32 | Hugo §§13–14 | A/B necessária | Aceito | Um parágrafo: `um dançarino virtuoso, ingrávido, mas densíssimo` | A quebra separava substantivo e adjetivos; `C.G. Jung` foi mantido como no original. |
| R33 | Hugo §15 | A/B necessária | Aceito, reconciliado | `havia recebido em casa o amigo Florencio Yllana... — deliciosa, segundo ele!` | Resolve a ligação sintática; a grafia do nome é corroborada pelo acervo, superando a cautela de B. |
| R34 | Hugo, assinatura/data | A opcional | Rejeitado | Nenhum metadado acrescentado | Ausente do espanhol publicado e fora do escopo tradutório/estrutura do cartão. |
| R35 | Juliana, título | A necessária | Rejeitado | Cartão permanece `Juliana Hoffmann` | `Exaptações` não consta do original espanhol publicado nem do JSON de origem. |
| R36 | Juliana §2 | B opcional | Rejeitado | `afetação patética do espanto... pretendida impostação` | A densidade e os substantivos abstratos são parte da voz; o atual é semanticamente correto. |
| R37 | Juliana §3 | B opcional | Rejeitado | `tensionam-se as percepções diacrônicas e sincrônicas` | Formulação válida no registro crítico e mais próxima do original. |
| R38 | Juliana §4 | B necessária | Aceito | `formas... que se deixavam ver... caminho... pela montanha ou pela floresta` | Corrige regência e peso sintático. |
| R39 | Juliana §6 | B necessária | Aceito | `emergiu... quando se estabeleceu determinado nível dos oceanos` | Remove nominalização e corrige a coordenação final. |
| R40 | Juliana §7 | B opcional | Rejeitado | `estratificações... marcas estratificadas... margens litorâneas` | A repetição científica é deliberada e sustenta a analogia; A confirmou o trecho. |
| R41 | Juliana §8 | B necessária | Aceito | `toma como ponto de partida algumas dessas marcas` | Elimina ambiguidade sem mudar o processo descrito. |
| R42 | Juliana §10 | B necessária | Aceito | `folhas de papel em que ocorreram as intervenções` | Corrige regência e registro. |
| R43 | Juliana §11 | A/B necessária | Aceito, reconciliado | `ondas... que se sobrepõem, provocadas pelo impacto de pedras de ordens diferentes` | Remove o falso cognato `incitação`; conserva `ordens`, presente no original, em vez de inferir `naturezas`. |
| R44 | Juliana §14 | B necessária | Aceito | `reviver essa ação ao folheá-lo` | Recompõe com clareza o gesto do livro animado. |
| R45 | Juliana §15 | A/B opcional | Aceito | `inevitavelmente sensorial` | No contraste com `conceitual`, `sensitiva` refere-se à experiência dos sentidos. |
| R46 | Mauricio, título | A necessária | Rejeitado | Cartão permanece `Mauricio Capellari`; `“Trama”` permanece no texto | O título externo não consta do espanhol publicado nem do contrato editorial. |
| R47 | Mauricio §3 | B necessária | Rejeitado | `poderíamos nos fazer a seguinte pergunta` | O trecho já é português autoral, é idiomático e foi confirmado integralmente por A. |
| R48 | Mauricio §5 | B opcional | Rejeitado | `surge a necessidade inevitável de introduzir` | A aparente redundância integra a ênfase autoral do original em português. |
| R49 | Mauricio §6 | B necessária | Rejeitado | `desliza sua sensibilidade artística... cinismo acolhedor` | Texto já autoral em português; a reescrita alisaria uma imagem deliberadamente incomum. |
| R50 | Mauricio §7 | B necessária | Rejeitado | `A abordagem da série que Capellari nos oferece...` | A ambiguidade é baixa e A confirmou a redação; preserva-se a voz. |
| R51 | Mítica §6 | B necessária | Aceito | `Em duas pequenas peças especialmente significativas, encontramos` | Correção inequívoca de pontuação após adjunto longo. |
| R52 | Mítica §7 | B opcional | Rejeitado | `aderidas à natureza de sua existência` | `Própria` seria adição de ênfase ausente no português autoral. |
| R53 | Mítica §8 | B opcional | Rejeitado | `como material de obra da arquitetura de algum tipo de cosmogonia` | A aspereza lexical consta do original em português e foi confirmada por A. |
| R54 | Mítica §10 | B necessária | Aceito | `reside em fazê-lo a partir de uma materialidade radicalmente concreta` | Resolve referente/concordância sem alterar a tese. |
| R55 | Mítica §11 | B necessária | Aceito | `registro superficial, mas, ao mesmo tempo` | Corrige pontuação antes da adversativa. |
| R56 | Mítica §12 | B opcional | Rejeitado | `ao operar sobre o espaço da galeria` | Colocação compreensível e deliberadamente conceitual no original em português. |
| R57 | Mítica, assinatura/data | A opcional | Rejeitado | Nenhum metadado acrescentado | Ausente do espanhol publicado e fora do escopo/estrutura editorial. |

## Divergências rejeitadas

- Não foram incorporadas frases, títulos, assinaturas ou datas presentes apenas nos DOCX: o original contratual desta tarefa é o espanhol já publicado em `es/index.html`.
- Em *El nombre* §2, rejeitou-se `precavidos contra` (A) porque inverte a necessidade de autoexplicação; adotou-se `cientes` (B).
- Em *Flores* §3, rejeitou-se `grava` (A) porque `registra` é o verbo do original; em §4, rejeitou-se `desfechos` (B) para manter a polissemia de `finales`.
- Em Fotografia §3, rejeitou-se acrescentar `É um mistério.` (A), ausente do HTML espanhol; preservou-se o fragmento com a naturalização de B.
- Em Hugo §5, manteve-se `identificar` (A) em vez de `perceber` (B); em §§13–14, preservou-se `C.G. Jung`; em §15, a evidência interna do acervo justificou `Yllana` apesar da cautela de B.
- Em Juliana §11, adotou-se `impacto` (A/B), mas preservou-se `ordens` (A/original) em vez da inferência `naturezas` (B).
- Não foram “corrigidos” por estilo os trechos que o próprio original já apresenta em português, sobretudo Mauricio §§3, 5–7 e Mítica §§7–8, 12.

## Checks finais

- Cobertura editorial: **8/8 artigos; 86/86 posições-fonte; 82 parágrafos finais**.
- Fusões sustentadas pelo original: **4** — Celso §§8–9; Hugo §§6–7, §§10–11 e §§13–14.
- Render PT determinístico executado; `es/index.html` permaneceu sem alteração material.
- Auditoria focada em `#critica`: **99 trechos, 0 achados**.
- Auditoria global: **4 ocorrências / 2 textos únicos preexistentes fora de Crítica** (`corcho, yute`; `elementos del universo del cuento`), mantidos fora do escopo.
- Testes focados/integrados: **32 aprovados**.
- Suíte completa: **136 aprovados**.
- Contraste: corpo `#EAE6DF`/fundo `#201E1C` = **13,36:1**; título `#FFFFFF`/fundo = **16,62:1**.
- Detector Impeccable: **0 achados**.
