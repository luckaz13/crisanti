# Design: vídeo Vlak no Jogo do Trem

## Objetivo

Apresentar `vlak.mp4` como a primeira mídia da seção atualmente chamada “Jogo do Trem”, renomeando-a de forma bilíngue e integrando o vídeo ao comportamento existente do carrossel.

## Conteúdo e títulos

- Incorporar o arquivo canônico em `videos/vlak.mp4` ao repositório.
- O vídeo será o primeiro slide do carrossel; todas as imagens atuais permanecerão depois dele, na ordem existente.
- Título PT-BR: `Vlak: O jogo do trem`.
- Título espanhol: `Vlak: El juego del tren`.
- Preservar o identificador técnico `juego-del-tren` para não quebrar âncoras, controles ou referências existentes.

## Apresentação do vídeo

- Renderizar um elemento `<video>` vertical dentro da mesma estrutura visual dos slides de imagem.
- Usar `muted`, `playsinline`, `preload="metadata"` e controles nativos.
- Não usar `autoplay` estático nem `loop`; a reprodução será controlada pelo estado real de visibilidade.
- Exibir o vídeo inteiro dentro do quadro, sem recorte.
- Não abrir o vídeo no lightbox de imagens.

## Reprodução automática

O vídeo deve tocar somente quando as duas condições forem verdadeiras:

1. seu slide for o slide ativo do carrossel;
2. o carrossel estiver visível na viewport.

Ao trocar de slide ou tirar o carrossel da viewport, o vídeo será pausado sem alterar `currentTime`. Ao retornar ao primeiro slide e à área visível, ele retomará do ponto anterior. Ao chegar ao fim, permanecerá no último quadro e não reiniciará automaticamente.

Uma tentativa de `play()` rejeitada pelo navegador deve ser tratada silenciosamente, mantendo os controles disponíveis. Como o vídeo começa mudo, os navegadores modernos permitem o autoplay sem exigir interação prévia; o usuário poderá controlar reprodução e volume manualmente.

## Implementação

- O manifesto continuará sendo a fonte da ordem das imagens; o slide de vídeo será uma mídia editorial fixa inserida antes dos slides renderizados do grupo `juego-del-tren`.
- Um controlador JavaScript isolado observará o carrossel e sincronizará o vídeo quando o slide mudar, quando a janela rolar/redimensionar e quando a visibilidade do carrossel mudar.
- A integração não deve alterar o avanço manual, as setas, os indicadores nem os demais carrosséis.
- O CSS do vídeo será restrito à classe própria do slide Vlak.

## Verificação

- Testes de fonte devem proteger os títulos bilíngues, o primeiro slide, os atributos do vídeo e a preservação das imagens atuais.
- Testes do controlador devem proteger as condições de tocar, pausar, retomar e não reiniciar.
- No navegador, validar PT-BR e espanhol em desktop e mobile: carregamento, enquadramento completo, autoplay mudo quando ativo e visível, pausa ao sair, retomada ao voltar, controles manuais e ausência de overflow.
- A auditoria de referências deve reconhecer `videos/vlak.mp4` como um arquivo existente.
