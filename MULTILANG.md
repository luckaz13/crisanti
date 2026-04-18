# Plano de Internacionalização Multi-Idioma (i18n)

**Objetivo:** Adaptar todo o portfólio de Fabio Crisanti (HTML e JavaScript) para suportar três idiomas: Português (pt-BR), Inglês (en) e Espanhol (es), buscando a máxima eficiência na implementação e preservando o desempenho e SEO do site.

---

## 1. Abordagens e Estratégias

Ao trabalharmos com um site estático (vanilla HTML/JS/CSS), temos duas arquiteturas principais. A escolha entre elas vai definir a eficiência e as vantagens de longo prazo do nosso projeto:

### Opção A: Geração Estática "Build Script" (RECOMENDADA)
Criamos um pequeno script em Python que funciona como um gerador inteligente. Ele vai ler um arquivo central de traduções (ex: `translations.json`) e um arquivo "esqueleto" do site, e "cuspir" automaticamente e separadamente as pastas ou arquivos `index.html` (PT), `en/index.html` (EN) e `es/index.html` (ES).

*   **Prós:** 
    *   **Impecável para o SEO:** O Google indexa nativamente páginas separadas e rastreia conteúdo em inglês/espanhol debaixo de domínios organizados (como `/en/`), melhorando drasticamente o ranqueamento do artista para buscas globais.
    *   **Alta Performance:** Sem JavaScript extra sendo processado no navegador do usuário visitante apenas para descobrir que o idioma devia ser outro.
    *   **Fácil Manutenção no Futuro:** Quando formos adicionar uma nova obra, alteramos um lado só. Rodamos `./build.py` e os 3 HTMLs são atualizados num instante de forma sincronizada.

### Opção B: Client-side JavaScript (Tradução Dinâmica)
Colocamos o nosso HTML de hoje cheio de de atributos e identificadores (ex: `<h1 data-i18n="hero.title">Fabio Crisanti</h1>`). Quando o site for acessado, um código JavaScript detecta o idioma, vai ler um arquivo de dicionário e vai "substituir" ao vivo as palavras na tela do usuário.

*   **Prós:** Um único arquivo `index.html` na pasta raíz que cuida de tudo. Transição de idioma sem reload de página se o usuário clicar numa bandeira.
*   **Contras:** Google não vai indexar as versões em inglês e espanhol tão bem. Além de ter uma grande carga no processamento e complexidade de atuar junto à galeria já existente.

**Recomendação:** A **Opção A (Geração Estática por Python)** vai nos poupar dores de cabeça e garantirá a rastreabilidade orgânica nas línguas estrangeiras. 

---

## 2. Roteiro Passo a Passo de Execução Super Rápida (Opção A)

Se concordarmos, podemos seguir com esse trator nas próximas etapas:

### Fase 1: Extração Estruturada e Dicionários
1. Mapear todas as "strings" textuais do `index.html` soltos no código (botões, parágrafos na sobre, críticas).
2. Transformar o atual `gallery-data.js` num objeto neutro de metadados.
3. Criar uma pasta `/data/locales/` com três dicionários limpos: `pt.json`, `en.json`, `es.json`.
*(A IA – Eu – poderá cuidar da etapa de coletar, fatiar e já emitir pra você as traduções perfeitas, de forma automática, economizando horas).*

### Fase 2: O Template e Script Construtor
1. Transformaremos o `index.html` atual em algo como `template.html`, colocando *placeholders* no estilo `{{ hero_title }}` onde os textos costumavam existir.
2. Escreverei o *script* (do zero) `build_i18n.py`.
3. Adicionaremos links no cabeçalho ou rodapé (Bandeiras / PT EN ES) com `href` trocando o path (`/` -> `/en/` -> `/es/`).

### Fase 3: Build & Deploy
1. Executamos o build script.
2. Fazemos deploy pelo Github Pages sem dor, testando os direcionamentos, validando o `<html lang="en">` e as tags `<link rel="alternate" hreflang="x">` dentro do `<head>` que serão geradas para o Google saber que há irmãos daquela página.

---

## Próximos Passos

Por favor, me dê seu "O.K" em avançarmos por este método (Geração de `index` com Python + JSON de Locales). Caso aprove, o próximo primeiro passo que tomarei será escaneamento do texto de português e a criação dos três arquivos de tradução base para o seu review.
