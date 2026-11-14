# Roteiro da apresentação — 20 min + 10 min de perguntas

**Regra de ouro:** conte uma história — *"os dados não eram o que o enunciado sugeria; por isso o desenho é este; e aqui está a prova de que ele não inventa números."* Mostre **honestidade** sobre limites: é o que mais impressiona.

**Antes de começar, deixe abertos:** ① README · ② `outputs/relatorio.html` (Anexo B à mão) · ③ `outputs/extracao/light.json` · ④ `light.pdf` na **p.9** · ⑤ terminal na raiz · ⑥ `outputs/avaliacao_baseline.json` (+ `avaliacao_llm.json` se rodou a Parte D) · ⑦ `outputs/logs/run.jsonl`.

---

## 0:00–2:00 · Abertura e a descoberta  → *abra o README (topo)*
**Diga:** "Recebi 3 PDFs e um enunciado que fala em indicadores, guidance e tom da administração. Antes de escrever código, li os documentos e descobri algo que muda o projeto: **são demonstrações financeiras anuais de 2022, não releases trimestrais, e só a Light tem Relatório da Administração.** Então EBITDA, margem e guidance muitas vezes **não existem** nos documentos. Por isso desenhei o sistema em torno de uma regra: **melhor dizer 'não encontrado' do que inventar.**"

## 2:00–5:00 · Arquitetura  → *README, diagrama Mermaid*
**Aponte o diagrama, da esquerda para a direita:**
- "Ingestão com `pdftotext` preservando layout + `pdfplumber` para tabelas, com cache por SHA-256."
- "Varredura de prompt injection **antes** de qualquer LLM — PDF é entrada não confiável."
- "Três papéis: **Extractor** extrai, **Validator** faz grounding e checagens, **Writer** responde e monta o relatório **por código**, só com dados já verificados. Em paralelo roda uma camada de **ML tradicional** (z-score robusto + Isolation Forest) e um **log estruturado** por etapa."
- "O LLM é plugável — Claude, OpenAI, Azure OpenAI, **Ollama local** ou **Gemini gratuito** — e só entra na extração e na análise qualitativa. Como eu não tinha chave paga, deixei o sistema rodar com modelo local, sem custo."
**Trade-off a dizer:** "Usei BM25 e não embeddings: 218 páginas cabem em memória, termos financeiros são lexicais e é explicável. Em escala, busca híbrida no Azure AI Search."

## 5:00–9:00 · O núcleo: anti-alucinação, com prova  → *`light.json` → `light.pdf` p.9 → terminal*
1. **Abra `light.json`**, em `receita_liquida`. **Diga:** "Todo valor tem página e trecho **literal**."
2. **Abra `light.pdf` na p.20** e mostre a linha "RECEITA LÍQUIDA". "Aqui está, igual."
3. **Volte ao terminal e rode** `python -m pytest -q tests/test_llm_path.py -v`. **Diga:** "Este teste simula um LLM que **inventa** um lucro com citação falsa. O grounding exige que o trecho exista literalmente na página **e** contenha o número. O valor inventado é barrado."
4. **Diga:** "Resultado nos 3 documentos: **150 evidências, 0 falhas**."

## 9:00–12:30 · Inconsistências: o caso Light  → *`relatorio.html` seção 5 + `light.pdf` p.9*
**Diga:** "A Light imprime **EBITDA de R$ 1.180 milhões** no texto (p.9). Mas EBIT + depreciação das DFs dá **−R$ 1.179,6 milhões**: mesmo módulo, **sinal oposto**. O pipeline **não escolhe em silêncio**: mostra os dois e levanta um alerta de severidade alta. Na p.8 há ainda uma conta que não fecha: 1.817 − 1.179 não dá −2.996, mas 1.817 + 1.179 dá — sinal de anos invertidos e sinal negativo omitido."
**Mostre também (rápido):** Millet — "variação de receita de +132% é enganosa: a Alibra só foi consolidada a partir de junho/2021; na base comparável é ≈ +45%." Brasal — "o auditor declara não ter auditado a coluna 2021."
**Frase-chave:** "Total: 19 alertas, todos visíveis no relatório. **Nada foi corrigido em silêncio.**"

## 12:30–15:30 · Resultados e as 5 respostas  → *`relatorio.html` seções 1, 2 e 4*
- **Tabela comparativa:** "Valores com página; derivados marcados com ¤ e fórmula no Anexo A — nunca misturados com publicados."
- **P1 maior margem EBITDA:** "**Brasal, ≈16,7%** — mas é margem **derivada** (EBIT + D&A ÷ receita), porque nenhum documento publica margem. Millet 9,4%; Light −8,9%."
- **P3 alavancagem > 3x:** "**Sim, Light: 3,32x** — publicado, EBITDA ajustado de covenants. Millet 0,31x derivado; Brasal está com **caixa líquido**."
- **P5 guidance:** "**Nenhuma** divulga guidance numérico para 2023 — e dizer isso é a resposta correta."
- **P4 riscos comuns:** "7 categorias aparecem em mais de uma empresa; 3 nas três: crédito, contingências e juros."

## 15:30–18:00 · Qualidade, ML × LLM e honestidade  → *terminal: `eval --mode baseline`; `relatorio.html` Anexo B; `ask`*
**Diga:** "Para medir qualidade criei um gabarito e um extrator **regex** como baseline: recall **64%**, precisão **95%**, **0 alucinação**. Ele erra de formas instrutivas — pegou o EBITDA da distribuidora (1.817) em vez do consolidado. É o argumento por LLM com grounding." **Diga também (medido com `gemini-3.5-flash-lite`, camada gratuita):** "Com LLM real: recall **78,6%**, precisão **100%**, **0 alucinação**, 62 s para os 3 documentos, custo real US$ 0 (≈ US$ 0,06 a preço de tabela). Fui iterando: a v1 tinha grounding estrito demais; a v2 subiu o recall para 82% mas deixou passar 3 valores errados (escala e coluna); na versão final o modelo prefere dizer 'não encontrado' a chutar. **O grounding garante que o número existe no PDF, não que é o número certo — quem pega isso é o eval set.**"
**ML tradicional (Anexo B):** "Implementei também a abordagem **sem LLM e sem rótulos**: z-score robusto e Isolation Forest sobre as linhas das demonstrações. Ele sinaliza **linhas de movimento grande** — ex.: swaps da Light de 3,9 mil para 397 mil — mas não vê o EBITDA com sinal omitido nem o comparativo 'não auditado'. Quase não há sobreposição com os alertas: são **complementares**. Não treinei classificador supervisionado porque são 3 documentos e zero rótulos — qualquer acurácia seria ruído."
**Pergunta livre (demo de 30 s):** `python -m finanalyzer ask "Quais são os riscos de crédito mencionados?"` → mostra linhas com `[doc p.N]` e citações `✓`. Depois `ask "preço do bitcoin"` → **"Sem evidência suficiente"**. "Offline, extrativo: só devolve o que está no documento."
**Seja franco (isto gera confiança):** "Limites: (1) o gabarito foi montado com apoio de ferramentas de IA e verificado por mim: `verify_numbers.py` confere cada trecho direto no PDF e conferi 8 valores à mão (`docs/CONFERENCIA_MANUAL.md`); (2) o caminho LLM foi testado com modelo simulado, servidor HTTP falso **e com modelo real** (gemini-3.5-flash-lite, números acima); (3) o qualitativo em modo LLM é mais fraco que a curadoria e está medido no README; (4) o Docker foi construído e rodou: 106 testes passaram dentro da imagem."

## 18:00–20:00 · Segurança, diferenciais e produção  → *README seções "Segurança" e "Azure"*
- "Chaves só por ambiente; `check_secrets.py` falha se achar chave."
- "Injection: varredura, isolamento em tags, LLM **sem ferramentas** e saída só aceita se passar no grounding."
- "Diferenciais: 3 **papéis** separados (Extractor/Validator/Writer — código linear, não agentes autônomos), **servidor MCP** com 6 ferramentas, eval set, **ML tradicional comparado**, perguntas livres, Docker, **111 testes** (incl. validações com dados sintéticos), manifesto de execução e **log estruturado** (`run.jsonl`: spans por etapa, sem texto de PDF nem segredos)."
- "Em produção no Azure: Blob + Document Intelligence para escaneados + Azure OpenAI privado + AI Search híbrido + Key Vault + Application Insights/OpenTelemetry (meu `Tracer` já emite os mesmos campos) + fila de revisão humana para alertas altos."

---

## Perguntas prováveis (10 min) — respostas curtas

**1. Por que não usar só um LLM e pronto?** "LLM sozinho cita página errada e arredonda número. O grounding transforma 'confie no modelo' em 'verifique o modelo'."
**2. Como sabe que o EBITDA da Light está errado, não o EBIT?** "Não afirmo qual está certo — **sinalizo a divergência** com as duas fontes e as páginas. O texto diz 'provável omissão do sinal', e a conta da p.8 reforça, mas a decisão é de quem lê."
**3. Por que Brasal tem a maior margem se nem publica EBITDA?** "É margem **derivada** e rotulada como tal; sem padronizar, não há como comparar. Mostro a fórmula e as páginas dos insumos."
**4. E se o PDF for escaneado?** "Aqui tinha texto. Em produção: Azure AI Document Intelligence (OCR + layout) antes da ingestão."
**5. E prompt injection?** "Varredura prévia, texto em tags `<documento>`, LLM sem ferramentas e saída restrita a schema + grounding. Uma instrução maliciosa não consegue fabricar um número ancorado na página."
**6. Como mediria isso em produção?** "Conjunto de avaliação com gabarito, recall/precisão por campo, taxa de falha de grounding em monitoramento e amostra de revisão humana."
**7. Custo?** "Estimo ~100 mil tokens de entrada por execução (≈ US$ 0,3–0,6 em API paga com preços placeholder; US$ 0 com modelo local ou camada gratuita); o manifesto registra o real. Reduzo com prompt caching e modelo menor na extração."
**8. Por que não LangGraph/AutoGen?** "O fluxo é linear; um orquestrador simples é mais auditável. Com laços de re-extração eu migraria para LangGraph ou Foundry Agent Service."
**9. O que você faria com mais tempo?** "Rodar o eval em LLM com várias execuções por campo, adicionar revisão humana para alertas altos, OCR, e busca híbrida."
**10. O gabarito é confiável?** "Cada trecho é verificado por código contra o PDF; os valores eu conferi por amostragem. Reconheço o viés de ter sido assistido por IA, por isso o relato no README."

**11. Por que não treinou um modelo de ML?** "Três documentos, nenhum rótulo. Um classificador supervisionado seria acurácia inventada. Usei métodos não supervisionados (MAD e Isolation Forest) e mostrei, no Anexo B, o que eles pegam e o que escapa — comparando honestamente com regras e LLM."
**12. Seu modelo local é pior que um grande?** "Provavelmente erra mais — por isso existe o `eval` (números: recall 78,6%, precisão 100%, alucinação 0%) e o grounding garante que, mesmo errando, ele **não inventa**: o erro vira 'não encontrado' ou 'não verificado', nunca um número falso."
**13. Os logs vazam dados?** "Não: gravam etapa, documento, duração e contagens — nunca texto de PDF, prompt, resposta ou chave. Há teste automatizado para isso."
**14. Como o `ask` evita inventar?** "No modo offline ele só devolve linhas existentes e exige cobertura mínima dos termos da pergunta; sem isso responde 'Sem evidência suficiente'. No modo LLM, cada citação é re-checada contra a página."

## Se algo der errado ao vivo
Mostre `outputs/` já gerado (ele está na pasta) e diga: "rodei antes para não depender de tempo de execução". Nunca improvise um número: abra o PDF.


---
## Respostas curtas para as perguntas previstas (Q&A)

**Por que a saída principal (`outputs/`) é o modo `reference`?** Porque é o teto de qualidade: valores curados, verificados contra o PDF e com grounding total (150 evidências, 0 falhas). O modo `llm` (`outputs_llm/`) é a extração real e a medição honesta: 78,6% de recall e 100% de precisão contra o gabarito. Os dois estão no repositório e o README diz qual é qual. A avaliação do modo `reference` contra o próprio gabarito é circular e não é medida de qualidade; a medida de qualidade é a do modo `llm`.

**Por que o qualitativo em LLM é pior que a curadoria?** Cada documento vira uma única chamada com até 24 páginas escolhidas por BM25, e só entram itens com trecho literal verificado: o modelo gera menos itens, mas nenhum sem evidência. Medi com `python -m finanalyzer eval-quali --llm-dir outputs_llm` em 3 iterações: categorias de risco do gabarito encontradas **33% → 79%**, páginas citadas **16% → 43%**, falhas de grounding **9 → 4**; tom 2/3 e guidance 3/3. A pergunta 2 da Light passou de "Não encontrado" para a resposta certa (p.9) e a da Millet agora cita a consolidação da Alibra (p.38), a causa real do +131,9%. Ainda fraco: eventos (Light 2 contra 5 da curadoria) e guidance qualitativo. A causa que achei lendo a resposta crua: o modelo citava o número impresso no rodapé (p.90) em vez da página física (p.107). Corrigi com uma realocação **registrada** (só se o trecho literal ≥ 40 caracteres existir em exatamente uma outra página; fica "página corrigida de 90 para 107" na evidência; números nunca são realocados). Caminho de melhoria: uma chamada por tema.

**O que significa "agente" aqui?** Três papéis explícitos (Extractor, Validator, Writer) em código linear, sem laço de decisão do LLM e sem escolha de ferramentas pelo modelo. Chamo de papéis porque é isso que são; o diferencial de agente real é o servidor MCP (6 ferramentas) que um agente externo pode chamar.

**Por que o recall caiu de 82% para 78,6% de propósito?** A v2 tinha 82,1% de recall, mas 11,1% de alucinação (3 valores errados por escala e coluna). A versão final prefere "não encontrado" a chutar: recall 78,6%, precisão 100%, alucinação 0%. Em análise financeira, um número ausente é visível; um número errado passa despercebido.

