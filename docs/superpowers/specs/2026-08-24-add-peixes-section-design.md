# Seção Peixes / Peces — Design

## Objetivo

Criar uma seção autônoma para 34 obras de peixes imediatamente após Seda Bahia, com texto histórico localizado e carrossel automático de uma imagem por vez, sem retirar os controles manuais.

## Títulos e posição

- PT-BR: `Peixes`, com `id="peixes"`.
- Espanhol: `Peces`, com `id="peces"`.
- Inserir a seção imediatamente após `seda-bahia` e antes de `juego-del-tren`.

Seda Bahia usa `series-grid` normal. A nova seção usará `series-grid series-grid--reverse`. Juego del Tren já usa `series-grid` normal, portanto a inserção completa a alternância nesse trecho sem exigir mudanças nas seções posteriores.

## Texto curatorial

### PT-BR

> Durante as perseguições do Império Romano, os cristãos utilizavam o peixe como um sinal discreto para se reconhecerem. Segundo uma tradição amplamente difundida, uma pessoa desenhava um arco na areia e, se a outra completasse a figura formando um peixe, ambas sabiam que eram cristãs. Embora esse relato seja difícil de verificar historicamente, está bem documentado que o símbolo do peixe foi utilizado pelas primeiras comunidades cristãs.

### Espanhol revisado

> Durante las persecuciones del Imperio romano, los cristianos utilizaban el pez como un signo discreto para reconocerse entre sí. Según una tradición muy difundida, una persona dibujaba un arco en la arena y, si la otra completaba la figura hasta formar un pez, ambas sabían que eran cristianas. Aunque este relato es difícil de verificar históricamente, está bien documentado que el símbolo del pez fue utilizado por las primeras comunidades cristianas.

`Texto para Peces.docx` será usado apenas como fonte e não será publicado.

## Acervo e legendas

Copiar exatamente `01.jpg` a `34.jpg` de `/home/lucas/Projetos/crisanti/img/Peces/` para `images/galerias/Peces/`, preservando os originais.

Cada slide terá uma legenda genérica localizada conforme o número do arquivo:

- PT-BR: `Peixe 01`, `Peixe 02`, …, `Peixe 34`.
- Espanhol: `Pez 01`, `Pez 02`, …, `Pez 34`.

O texto alternativo combinará a legenda e o nome do artista. Não serão inventados ano, técnica ou suporte.

A imagem processada `img/Peces/03-header-mark.png`, usada na identidade visual, é um ativo separado e permanecerá inalterada. O arquivo original `03.jpg` será publicado normalmente como a terceira obra da nova galeria.

## Estrutura e autoplay

A seção reutilizará `section series`, `series-grid`, o carrossel, os controles, o lightbox, o contorno branco e a sombra existentes. A galeria terá 34 slides na ordem numérica e mostrará exatamente uma obra por vez.

O carrossel receberá configuração declarativa própria, por exemplo `data-autoplay="2000"`, interpretada pelo mecanismo compartilhado. Nenhuma outra galeria terá autoplay sem esse atributo.

Comportamento:

- avançar uma imagem a cada 2.000 ms;
- ao chegar ao slide 34, voltar ao slide 1;
- manter botões anterior/próximo, swipe e lightbox;
- uma navegação manual reinicia a contagem de 2.000 ms;
- pausar durante hover do ponteiro;
- pausar enquanto o foco de teclado estiver dentro do carrossel;
- pausar quando `document.visibilityState` não for `visible`;
- desativar o avanço automático quando `prefers-reduced-motion: reduce` estiver ativo;
- retomar quando a condição de pausa deixar de existir, começando um novo intervalo completo;
- não criar múltiplos timers quando o carrossel for redimensionado ou reinicializado.

Os botões continuarão refletindo os limites durante navegação manual. O retorno automático do último para o primeiro será controlado internamente sem transformar o botão Próximo em um controle circular.

## CTA

Adicionar um botão localizado de consulta via WhatsApp:

- PT-BR: consulta sobre a série Peixes.
- Espanhol: consulta sobre a série Peces.

## Verificação

A implementação será considerada concluída quando:

1. A pasta pública contiver exatamente 34 JPEGs, `01.jpg`–`34.jpg`, idênticos às fontes.
2. O DOCX não for publicado.
3. A nova seção estiver imediatamente entre Seda Bahia e Juego del Tren nas duas páginas.
4. Os títulos, textos e CTAs estiverem corretamente localizados.
5. Cada carrossel tiver 34 slides na ordem numérica e legendas localizadas.
6. Os 34 caminhos retornarem HTTP 200.
7. O carrossel avançar exatamente um slide após 2 segundos e retornar de 34 para 1.
8. Cliques, swipe e lightbox continuarem funcionando e reiniciarem o intervalo.
9. Hover, foco, aba oculta e redução de movimento impedirem avanço automático.
10. Nenhum carrossel sem `data-autoplay` avançar sozinho.
11. A alternância visual Seda Bahia → Peixes/Peces → Juego del Tren for normal → invertida → normal em desktop.
12. O layout não apresentar overflow em uma viewport móvel de 390 px.

