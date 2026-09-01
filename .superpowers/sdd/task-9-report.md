# Tarefa 9 — relatório da primeira passagem

Status: **aguardando revisões sêniores A/B**.

## RED

- `python3 -m unittest -q tests.test_critica_card_style tests.test_acervo_pt_br`
- Falhou como esperado em 3 contratos: override terroso presente; 5 de 8 artigos sem entrada editorial PT-BR; fronteiras de parágrafo incompletas.

## GREEN

- Removidos somente os overrides `#critica .literatura-card`; Crítica volta a herdar fundo `#201E1C`, títulos `#FFFFFF` e corpo `#EAE6DF`.
- Contraste calculado: corpo/fundo **13,36:1**; título/fundo **16,62:1**.
- Regenerado `index.html` com o JSON editorial completo.
- Testes focados/integrados: **32 aprovados**.
- Suíte completa: **136 aprovados**.
- Detector Impeccable: **0 achados**.
- Auditoria de 103 trechos de `#critica`: **0 resíduos de espanhol**.
- O auditor global foi executado e manteve 4 ocorrências (2 textos únicos) preexistentes fora de `#critica`; não foram alteradas porque o restante do site está fora do escopo.

## Inventário traduzido

| Artigo | Parágrafos preservados |
|---|---:|
| Celso Ricardo | 17 |
| El nombre | 4 |
| Flores | 5 |
| Fotografía y Escultura | 8 |
| Hugo França | 16 |
| Juliana Hoffmann | 15 |
| Mauricio Capellari | 8 |
| Mítica - Gaya | 13 |

## Próximo passo

Não foi feita reconciliação editorial nesta passagem. **Aguardando revisões sêniores A/B** do Step 5 para comparar fidelidade ES→PT-BR, naturalidade, terminologia, pontuação e voz antes da revisão final.
