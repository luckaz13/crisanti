# Auditoria profunda de tradução PT-BR — Design

## Objetivo

Eliminar espanhol residual da versão PT-BR sem alterar títulos próprios de obras, séries, exposições, instituições ou publicações que devam permanecer no idioma original.

## Diagnóstico

A página portuguesa contém dois grupos de falhas:

1. Legendas do manifesto parcialmente localizadas, incluindo rótulos como `Vista general`, `Detalle`, `Boceto`, `Materiales`, nomes de materiais e construções mistas como `Acrílicos sobre papel de seda y collage`.
2. Blocos editoriais e literários cujo campo PT-BR ainda contém parágrafos integralmente em espanhol.

O HTML é gerado a partir de `data/acervo/manifest.json` e dos arquivos `data/acervo/editorial-*.json`; corrigir somente `index.html` seria transitório.

## Fonte e escopo da correção

- Corrigir primeiro os campos PT-BR no manifesto e nos arquivos editoriais.
- Regenerar `index.html` por meio do renderizador existente.
- Auditar texto visível, legendas, técnicas, materiais, descrições, texto alternativo e rótulos de acessibilidade.
- Revisar ortografia e gramática PT-BR dos trechos corrigidos, mantendo tradução fiel e sem reescrita estilística.
- Não alterar a versão espanhola, salvo se necessário para preservar a simetria estrutural do renderizador.

## Preservação editorial

Permanecem no idioma original quando usados como nomes próprios:

- títulos de obras e séries, como `El Calendario`, `El Nombre`, `La Cocina`, `El Teléfono`, `Juego del Tren`, `La Fuente y los Simios` e `Der Elefant`;
- nomes de exposições, galerias, instituições, lugares, pessoas e publicações;
- citações literárias deliberadamente apresentadas no original, desde que identificadas como citações.

Palavras espanholas fora desses contextos devem ser traduzidas. Exemplos:

- `Vista general de la seria` → `Vista geral da série`;
- `Vista general serie "Seda Bahia"` → `Vista geral da série “Seda Bahia”`;
- `Detalle` → `Detalhe`;
- `Boceto` → `Esboço`;
- `Materiales` → `Materiais`;
- `Contratapa` → `Contracapa`.

## Auditor automatizado

Criar um auditor específico da versão PT-BR que:

- examine o texto visível e atributos editoriais relevantes;
- sinalize léxico inequivocamente espanhol e construções mistas recorrentes;
- aplique uma allowlist pequena e explícita para nomes próprios aprovados;
- produza ocorrências com contexto suficiente para revisão humana;
- retorne código de erro quando houver espanhol residual não permitido.

O auditor complementa, mas não substitui, a revisão humana dos 125 candidatos encontrados inicialmente.

## Verificação

- O teste do auditor deve falhar antes das correções com exemplos reais atuais.
- Após a correção, o auditor deve retornar zero ocorrências não permitidas.
- A renderização deve ser idempotente e não reintroduzir espanhol.
- A suíte existente, a auditoria de referências e a verificação de arquivos ausentes devem continuar passando.
- A página PT-BR deve ser inspecionada no Chromium; a página espanhola deve permanecer funcional e sem alterações editoriais acidentais.
