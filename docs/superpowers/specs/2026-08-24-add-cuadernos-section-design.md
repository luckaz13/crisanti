# Seção Cadernos / Cuadernos — Design

## Objetivo

Criar uma seção autônoma para o acervo de cadernos de Fabio Crisanti imediatamente após Ensaios, com texto curatorial localizado, 21 obras legendadas e preservação da alternância visual entre as seções subsequentes.

## Títulos e posição

- PT-BR: `Cadernos`, com `id="cadernos"`.
- Espanhol: `Cuadernos`, com `id="cuadernos"`.
- A nova seção será inserida imediatamente depois do fechamento de Ensaios e antes de Escultura.

## Texto curatorial

### PT-BR

> Este acervo, composto por aproximadamente doze cadernos de esboços, registra a faceta mais íntima da relação de FC com o Brasil como território de enraizamento pictórico.
>
> Podemos apreciar neles algumas descobertas que mais tarde dariam origem a séries plenamente realizadas e já expostas.
>
> Ao mesmo tempo, contêm um amplíssimo corpo de notas, exercícios e estudos para o desenvolvimento de novos ensaios.
>
> Em todo caso, são diários visuais e obras em si mesmas, por meio dos quais se pode acessar a dimensão mais pessoal do universo profissional do artista.

### Espanhol revisado

> Este acervo, compuesto por aproximadamente doce cuadernos de bocetos, registra la faceta más íntima de la relación de FC con Brasil como territorio de arraigo pictórico.
>
> Podemos apreciar en ellos algunos hallazgos que luego darían origen a series completamente consumadas y ya expuestas.
>
> Al mismo tiempo, contienen un amplísimo cuerpo de notas, ejercicios y estudios para el desarrollo de nuevos ensayos.
>
> En todo caso, son diarios visuales y obras en sí mismas, que permiten acceder a la dimensión más personal del universo profesional del artista.

## Acervo publicado

Copiar exatamente `00.jpg` a `20.jpg` de `/home/lucas/Projetos/crisanti/img/Cuadernos/` para `images/galerias/Cuadernos/`, preservando os originais.

Não publicar:

- `11(1).jpg`, que foi revisado visualmente e não possui legenda correspondente;
- `Ficha Cuadernos.docx`;
- `Texto para Cuadernos.docx`.

A revisão visual confirmou que `11.jpg`, e não `11(1).jpg`, corresponde a `Cuaderno 2 — 2021 — Acrílico sobre papel de seda`. As demais imagens `00`–`20` apresentam correspondência visual coerente com as legendas fornecidas.

## Legendas canônicas

Os títulos `Cuaderno N` são nomes das obras e permanecerão em espanhol nas duas versões. Ano e suporte serão localizados conforme a tabela.

| Arquivo | Título | Ano | PT-BR | Espanhol revisado |
|---|---|---:|---|---|
| `00.jpg` | Cuaderno 9 | 2025 | Acrílico sobre papel de seda | Acrílico sobre papel de seda |
| `01.jpg` | Cuaderno 7 | 2024 | Acrílico sobre papel de seda e colagem | Acrílico sobre papel de seda y collage |
| `02.jpg` | Cuaderno 4 | 2023 | Colagem, papéis de seda, acrílicos e papel kraft | Collage, papeles de seda, acrílicos y papel kraft |
| `03.jpg` | Cuaderno 4 | 2023 | Colagem, papéis de seda, acrílicos e papel kraft | Collage, papeles de seda, acrílicos y papel kraft |
| `04.jpg` | Cuaderno 4 | 2023 | Papel fotográfico e acrílicos | Papel fotográfico y acrílicos |
| `05.jpg` | Cuaderno 6 | 2024 | Colagem e papel fotográfico | Collage y papel fotográfico |
| `06.jpg` | Cuaderno 9 | 2025 | Storyboard para “Der Elefant” | Storyboard para “Der Elefant” |
| `07.jpg` | Cuaderno 10 | 2026 | Colagem | Collage |
| `08.jpg` | Cuaderno 3 | 2022 | Colagem, papel de seda, acrílicos, cortiça e juta | Collage, papel de seda, acrílicos, corcho y yute |
| `09.jpg` | Cuaderno 2 | 2021 | Vestígio orgânico | Vestigio orgánico |
| `10.jpg` | Cuaderno 5 | 2024 | Acrílicos sobre papel de seda | Acrílicos sobre papel de seda |
| `11.jpg` | Cuaderno 2 | 2021 | Acrílico sobre papel de seda | Acrílico sobre papel de seda |
| `12.jpg` | Cuaderno 2 | 2021 | Esboço | Boceto |
| `13.jpg` | Cuaderno 3 | 2022 | Esboço e amostras têxteis | Boceto y muestras textiles |
| `14.jpg` | Cuaderno 6 | 2024 | Estudo de cor, kraft e acrílicos | Estudio de color, kraft y acrílicos |
| `15.jpg` | Cuaderno 5 | 2024 | Esboço para peixe. Tecido sintético e acrílicos | Boceto para pez. Tela sintética y acrílicos |
| `16.jpg` | Cuaderno 5 | 2024 | Esboço para peixe. Acrílicos, linha de costura e vestígios orgânicos | Boceto para pez. Acrílicos, hilo de coser y vestigios orgánicos |
| `17.jpg` | Cuaderno 2 | 2021 | Esboços para pipas | Bocetos para cometas |
| `18.jpg` | Cuaderno 5 | 2024 | Esboço para peixe. Tecido sintético e acrílicos | Boceto para pez. Tela sintética y acrílicos |
| `19.jpg` | Cuaderno 3 | 2022 | Estudo de texturas com nanquim | Estudio de texturas con tinta china |
| `20.jpg` | Cuaderno 7 | 2024 | Estudo. Papel kraft, tinta e têxteis | Estudio. Papel kraft, tinta y textiles |

## Estrutura visual e comportamento

A seção usará `section series series-group` e uma `container series-grid` sem `series-grid--reverse`. O texto ficará à esquerda e a galeria à direita.

A galeria será um único `gallery-carousel` com 21 slides na ordem `00`–`20`. Cada slide usará a estrutura existente de figura, imagem, `gallery-caption`, `gallery-title` e `gallery-meta`. O metadado exibido combinará ano e suporte. O texto alternativo combinará título, ano, suporte e nome do artista.

O carrossel reutilizará os controles, o contorno branco, a sombra e o lightbox existentes. A seção terá um CTA localizado para contato via WhatsApp sobre Cadernos/Cuadernos.

## Alternância das seções

Com a inserção após Ensaios, as classes serão:

| Ordem | Seção | Classe do grid |
|---:|---|---|
| 1 | Ensaios | `series-grid series-grid--reverse` — inalterada |
| 2 | Cadernos / Cuadernos | `series-grid` |
| 3 | Escultura | `series-grid series-grid--reverse` |
| 4 | Fotografia | `series-grid` |
| 5 | Moda | `series-grid series-grid--reverse` |
| 6 | Labirintos | `series-grid` |
| 7 | Crianças | `series-grid series-grid--reverse` |
| 8 | Projetos Especiais | `series-grid` |

As duas páginas receberão a mesma sequência. Nenhuma seção anterior a Ensaios será alterada.

## Verificação

A implementação será considerada concluída quando:

1. A pasta pública contiver exatamente 21 JPEGs, `00.jpg`–`20.jpg`, idênticos às fontes.
2. `11(1).jpg` e os DOCX não forem publicados.
3. A nova seção estiver imediatamente entre Ensaios e Escultura nas duas páginas.
4. O título e os quatro parágrafos estiverem corretamente localizados.
5. O carrossel tiver 21 slides na ordem numérica e todas as legendas canônicas.
6. Os 21 caminhos retornarem HTTP 200.
7. O lightbox abrir e navegar apenas dentro das 21 obras, com contador correto.
8. A tabela de alternância acima corresponder às classes reais em PT-BR e espanhol.
9. O layout não apresentar overflow em uma viewport móvel de 390 px.
10. As galerias e abas de Ensaios e das seções seguintes continuarem funcionando.

