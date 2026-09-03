# Peixes Crossfade e Altura Estável — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Tornar o crossfade de Peixes mais lento e impedir que a troca de proporções das imagens desloque a seção Vlak.

**Architecture:** O CSS de crossfade usará uma duração de 2 segundos. O controlador de galerias calculará a maior altura necessária entre as imagens de uma galeria crossfade para a largura atual e manterá o viewport nessa altura; galerias horizontais continuarão ajustando a altura ao slide ativo.

**Tech Stack:** HTML estático, CSS, JavaScript vanilla, unittest e probe visual Chromium/CDP.

## Global Constraints

- Preservar controles, autoplay e acessibilidade existentes.
- Respeitar `prefers-reduced-motion`.
- Não alterar o comportamento de outras galerias.

### Task 1: Crossfade e reserva de altura

**Files:**
- Modify: `css/style.css:1593-1598`
- Modify: `js/gallery.js:245-275`
- Test: `tests/test_gallery_modes.py`

- [ ] Adicionar teste que exija duração CSS de 2s para crossfade e uma função de altura máxima para galerias crossfade.
- [ ] Implementar duração CSS de `2s`.
- [ ] Alterar `updateViewportHeight()` para crossfade medir todos os slides com dimensões naturais disponíveis e usar a maior altura; manter o caminho atual para galerias normais.
- [ ] Recalcular a altura também quando imagens diferidas forem restauradas/carregadas e em mudanças de largura.
- [ ] Rodar os testes determinísticos e o probe visual.
- [ ] Commitar como `fix: slow peces crossfade and reserve gallery height`.
