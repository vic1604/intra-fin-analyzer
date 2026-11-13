# Relatório de Análise Financeira — Light, Millet e Brasal

*Gerado em 13/11/2026 13:57 · modo `llm` · exercício 2022 vs 2021 · valores em R$ (conforme indicado)*

> **Leia primeiro:** os 3 PDFs são demonstrações financeiras anuais, não releases trimestrais. Só a Light inclui Relatório da Administração; Millet e Brasal têm apenas DFs e notas explicativas — por isso EBITDA, margem EBITDA, dívida líquida e guidance estão frequentemente *não encontrados*. Indicadores marcados com ¤ são **calculados** pelo pipeline, nunca extraídos.

## 1. Resumo executivo

### Light S.A.

1. Receita líquida de **R$ 13,25 bi** em 2022 (−11,0% vs 2021) [Light p.20].
2. EBITDA: texto cita R$ 1.180 mi, mas **recomposto pelas DFs = −R$ 1,18 bi** — diverge, ver alertas [Light p.9].
3. Lucro líquido de **−R$ 5,67 bi** (−1.525,4% vs 2021) [Light p.20].
4. Dívida líquida de **R$ 9,03 bi**; alavancagem de covenants **3,32x** [Light p.10].
5. Tom: **negativo** (confiança alta).

### Millet Participações S.A.

1. Receita líquida de **R$ 462,1 mi** em 2022 (+131,9% vs 2021) (⚠ 2021 parcial: Alibra só desde jun/21) [Millet p.7].
2. EBITDA **não publicado**; derivado (EBIT + D&A) = R$ 43,5 mi, margem ≈ 9,4% (calculado ¤) [Millet p.7].
3. Lucro líquido de **R$ 18,9 mi** (+192,0% vs 2021) [Millet p.7].
4. Dívida líquida de **R$ 13,5 mi** [Millet p.42].
5. Tom: **neutro** (confiança baixa).

### Brasal Brasília Holding S.A.

1. Receita líquida de **R$ 1,33 bi** em 2022 (+24,8% vs 2021) [Brasal p.8].
2. EBITDA **não publicado**; derivado (EBIT + D&A) = R$ 221,9 mi, margem ≈ 16,7% (calculado ¤) [Brasal p.8].
3. Lucro líquido de **R$ 174,6 mi** (−36,6% vs 2021) [Brasal p.8].
4. Dívida líquida **não publicada**; derivada = **−R$ 171,6 mi** (caixa líquido; calculado ¤) [Brasal p.48].
5. Tom: **neutro** (confiança baixa).

## 2. Tabela comparativa

| Indicador (R$ milhões, salvo indicação) | Light | Millet | Brasal |
|---|---|---|---|
| **Período** | FY2022 vs FY2021 | FY2022 vs FY2021 | FY2022 vs FY2021 |
| Receita líquida 2022 | 13.253,3 · p.20 | 462,1 · p.7 | 1.325,1 · p.8 |
| Receita líquida 2021 | 14.897,9 · p.20 | 199,3 · p.7 | 1.061,4 · p.8 |
| Variação da receita (calculada) | −11,0% | +131,9% ⚠¹ | +24,8% ⚠² |
| EBITDA publicado | 1.180 (texto, sem sinal) ⚠³ · p.9 | não encontrado | não encontrado |
| EBITDA derivado (EBIT + D&A)¤ | −1.179,6 | 43,5 | 221,9 |
| Margem EBITDA publicada | não encontrado | não encontrado | não encontrado |
| Margem EBITDA derivada¤ (2022 / 2021) | −8,9% / 12,2% | 9,4% / 3,7% | 16,7% / 24,6% |
| Lucro líquido 2022 | −5.672,2 · p.20 | 18,9 · p.7 | 174,6 · p.8 |
| Lucro líquido 2021 | 397,9 · p.20 | 6,5 · p.7 | 275,6 · p.8 |
| Variação do lucro (calculada) | −1.525,4% | +192,0% | −36,6% |
| Dívida líquida 2022 | 9.032,0 · p.10 | 13,5 · p.42 | não encontrado (derivada¤: −171,6) |
| Dívida líquida / EBITDA | **3,32x** (covenants) · p.10 | não encontrado (derivada¤: 0,31x) | não encontrado (caixa líquido¤) |
| Fluxo de caixa operacional 2022 | 200,8 · p.23 | não encontrado | 258,2 · p.11 |
| Capex 2022 | não encontrado | não encontrado (soma das linhas de caixa¤: 17,7) | não encontrado |

¤ **Calculado pelo pipeline** a partir de linhas do documento (fórmulas na seção *Anexo A*); não é número publicado pela empresa.
¹ Millet: a Alibra foi consolidada só a partir de 18/06/2021; a variação não é comparável (base comparável ≈ +45%).
² Brasal: coluna 2021 marcada como *não auditada* pelo auditor.
³ Light: o texto imprime R$ 1.180 mi **sem sinal**; as DFs (EBIT + D&A) dão −R$ 1.179,6 mi. Light capex: 'investimentos' da administração (competência); capex de caixa = soma das duas linhas do DFC.
Células com `· p.N` indicam a página do PDF (1 = capa) onde o valor foi encontrado e verificado.

## 3. Análise qualitativa do comentário da administração

### Light
*Fonte da análise:* Relatório da Administração e Notas Explicativas da Light S.A. (2022). Completa para as seções selecionadas do relatório da administração e notas explicativas sobre reestruturação, PIS/COFINS e endividamento.

**Principais motivos do resultado**

- [Evidência documental] O resultado líquido consolidado foi impactado negativamente pelo reconhecimento de provisões e atualizações monetárias relacionadas à devolução de créditos de PIS/COFINS aos consumidores e impairment de IR/CS diferidos. *[Light p.10]*

**Motivo da variação da receita**

- Não encontrado no documento.

**Riscos e pontos de atenção**

- `Liquidez e endividamento` Elevado nível de endividamento e geração de caixa operacional historicamente insuficiente para honrar compromissos sozinhos. *[Light p.26]*
- `Juros e risco de mercado` Impacto do patamar elevado da taxa Selic na estrutura de capital e nos custos financeiros. *[Light p.26]*
- `Continuidade operacional` Incerteza significativa quanto à capacidade de continuidade operacional (going concern) da Light e da Light SESA. *[Light p.3]*
- `Regulatório / fiscal / concessão` Riscos regulatórios associados à necessidade de renovação da concessão da Light SESA, que vence em junho de 2026, cujos termos não estão sob o controle exclusivo da administração. *[Light p.26]*

**Guidance / perspectivas**

- **Guidance numérico: não encontrado.**

**Eventos relevantes** (aquisições, reestruturações, contingências, mudanças contábeis)

- Aprovação da Revisão Tarifária Periódica (RTP) da Light SESA em março de 2022 com reajuste médio de 14,68%. *[Light p.56]*

**Tom geral da administração: NEGATIVO** (confiança alta) — A administração reporta um prejuízo líquido multibilionário, forte queda no EBITDA devido a provisões massivas (créditos de PIS/COFINS e PECLD), aumento da dívida líquida, rebaixamento de ratings e menção explícita de auditores e administração sobre incerteza significativa quanto à continuidade operacional (going concern). *[Light p.3, p.10]*

### Millet
*Fonte da análise:* Notas Explicativas às Demonstrações Financeiras de 2022 e 2021 da Millet Participações S.A.. Análise baseada em notas explicativas e demonstrações contábeis selecionadas do exercício de 2022.

**Principais motivos do resultado**

- [Evidência documental] O resultado antes dos impostos no consolidado atingiu R$ 22.961 milhares em 2022, comparado a R$ 3.736 milhares em 2021, refletindo o desempenho das operações do grupo. *[Millet p.10]*
- [Evidência documental] A Companhia registrou lucro líquido do exercício de R$ 28.518 milhares na controlada Alibra em 2022. *[Millet p.28]*

**Motivo da variação da receita**

- Não encontrado no documento.

**Riscos e pontos de atenção**

- `Crédito / inadimplência de clientes` [Evidência documental] A exposição máxima ao risco de crédito do Contas a Receber de clientes na data das demonstrações financeiras é o valor contábil de cada faixa de idade de vencimento, totalizando R$ 98.663 milhares no consolidado em 2022. *[Millet p.19, p.40]*

**Guidance / perspectivas**

- **Guidance numérico: não encontrado.**

**Eventos relevantes** (aquisições, reestruturações, contingências, mudanças contábeis)

- [Evidência documental] Em 2022, a Companhia efetuou investimentos em imobilizado e intangível, destacando-se ampliações na unidade de Marechal Cândido Rondon/PR no montante de imobilizado em andamento de R$ 7.993 milhares. *[Millet p.31]*

**Tom geral da administração: NEUTRO** (confiança baixa) — O tom é estritamente descritivo e baseado em notas explicativas contábeis e demonstrações financeiras, sem discursos prospectivos ou avaliações subjetivas da administração sobre o desempenho comercial. *[Millet p.15]*

### Brasal
*Fonte da análise:* Notas Explicativas às Demonstrações Financeiras Individuais e Consolidadas da Brasal Brasília Holding S.A. para o exercício findo em 31 de dezembro de 2022. completa

**Principais motivos do resultado**

- [Evidência documental] O resultado antes do imposto de renda e contribuição social consolidado foi de R$ 217.187 mil em 2022 comparado a R$ 346.061 mil em 2021. *[Brasal p.11]*

**Motivo da variação da receita**

- Não encontrado no documento.

**Riscos e pontos de atenção**

- `Custo de insumos / matérias-primas` Possibilidade de oscilação de preços de matérias-primas e estoques, mitigada por operações com futuros para açúcar e commodities. *[Brasal p.17]*

**Guidance / perspectivas**

- **Guidance numérico: não encontrado.**

**Eventos relevantes** (aquisições, reestruturações, contingências, mudanças contábeis)

- Nenhum encontrado.

**Tom geral da administração: NEUTRO** (confiança baixa) — O documento apresenta notas explicativas contábeis padronizadas, focadas em políticas contábeis, variações patrimoniais e detalhamento de saldos sem um discurso gerencial otimista ou pessimista explícito por parte da administração. *[Brasal p.15]*


## 4. Respostas às 5 perguntas

### 1. Qual empresa teve a maior margem EBITDA no período?

**Brasal**, com margem EBITDA de ≈ **16,7%** em 2022 — mas atenção: é uma margem **derivada pelo pipeline**, não publicada. Nenhum dos três documentos informa margem EBITDA, e só a Light publica EBITDA.
A Light imprime EBITDA CVM de R$ 1.180 mi [Light p.9], porém as DFs mostram EBIT + D&A = −R$ 1,18 bi (**negativo**; ver alerta de sinal).
Para comparar de forma padronizada usei **EBITDA derivado = EBIT + D&A (fluxo de caixa) ÷ receita líquida da DRE**:

1. Brasal: **16,7%** (EBITDA derivado R$ 221,9 mi; 2021: 24,6%) [Brasal p.8]
2. Millet: **9,4%** (EBITDA derivado R$ 43,5 mi; 2021: 3,7%) [Millet p.7]
3. Light: **−8,9%** (EBITDA derivado −R$ 1,18 bi; 2021: 12,2%) (−9,7% sobre receita ex-construção) [Light p.20]
*Comparação com ressalvas: os três usam critérios contábeis e setores diferentes (energia, alimentos, bebidas).*

<details><summary>Fontes (documento · página · trecho)</summary>

- **Light p.20** — “LUCRO (PREJUÍZO) ANTES DO RESULTADO FINANCEIRO E IMPOSTOS (5.681.153) 397.043 (1.910.411) 1.143.301”
- **Light p.23** — “Depreciação e amortização 32 - - 730.767 678.110”
- **Light p.20** — “RECEITA LÍQUIDA 31 - - 13.253.286 14.897.920”
- **Millet p.7** — “Resultado antes do resultado 14.750 5.374 25.298 4.482 financeiro”
- **Millet p.10** — “Depreciação e amortização 13.295 - 18.248 2.975”
- **Millet p.7** — “Receita operacional líquida 18 - - 462.127 199.259”
- **Brasal p.8** — “Lucro operacional antes das receitas e despesas 173.736 275.244 192.840 238.224 financeiras”
- **Brasal p.11** — “Depreciações e amortizações 507 465 29.014 22.837”
- **Brasal p.8** — “Receita operacional líquida 21 - - 1.325.059 1.061.410”

</details>

### 2. O que a administração de cada empresa apontou como principal motivo da variação da receita?

- **Light** (receita R$ 13,25 bi vs R$ 14,90 bi; −11,0%): **Não encontrado**: o documento não traz explicação da administração para a variação da receita. (a DRE total varia −11,0%; o −13% da administração exclui receita de construção)
- **Millet** (receita R$ 462,1 mi vs R$ 199,3 mi; +131,9%): **Não encontrado**: o documento não traz explicação da administração para a variação da receita.
- **Brasal** (receita R$ 1,33 bi vs R$ 1,06 bi; +24,8%): **Não encontrado**: o documento não traz explicação da administração para a variação da receita.

<details><summary>Fontes (documento · página · trecho)</summary>

- **Light p.20** — “RECEITA LÍQUIDA 31 - - 13.253.286 14.897.920”
- **Millet p.7** — “Receita operacional líquida 18 - - 462.127 199.259”
- **Brasal p.8** — “Receita operacional líquida 21 - - 1.325.059 1.061.410”

</details>

### 3. Alguma das empresas está com alavancagem acima de 3x? Qual?

**Sim — Light.** Único múltiplo **publicado** acima de 3x: Light.

- **Light: 3,32x** (Dívida líquida/EBITDA ajustado de covenants, publicado) [Light p.10]; dívida líquida R$ 9,03 bi [Light p.10]; pelo EBITDA CVM recomposto (negativo) o múltiplo é n.s., o que é pior, não melhor
- Millet: não publica alavancagem sobre EBITDA; **derivado 0,31x** (dívida líquida R$ 13,5 mi ÷ EBITDA derivado R$ 43,5 mi).
- Brasal: não publica alavancagem; dívida líquida derivada = **−R$ 171,6 mi** (caixa líquido: mais caixa e aplicações do que dívida) — sem alavancagem.

<details><summary>Fontes (documento · página · trecho)</summary>

- **Light p.10** — “O indicador de covenants Dívida Líquida/EBITDA ajustado para fins de covenants encerrou 2021 em 3,32x, menor do que no 2021 (3,48x).”
- **Light p.10** — “A dívida líquida da Companhia em 31 de dezembro de 2022 totalizou R$9.032 milhões, aumento de 23% em comparação a 2021, de R$7.353 milhões.”
- **Millet p.7** — “Resultado antes do resultado 14.750 5.374 25.298 4.482 financeiro”
- **Millet p.10** — “Depreciação e amortização 13.295 - 18.248 2.975”
- **Millet p.42** — “Total dos empréstimos com terceiros 24.176 25.072”
- **Millet p.10** — “Saldo final de caixa e equivalentes de caixa 354 871 10.655 8.195”
- **Millet p.42** — “(=) Dívida líquida (a) 13.520 16.877”
- **Brasal p.8** — “Lucro operacional antes das receitas e despesas 173.736 275.244 192.840 238.224 financeiras”
- **Brasal p.11** — “Depreciações e amortizações 507 465 29.014 22.837”
- **Brasal p.48** — “Empréstimos e financiamentos - - 3.417 3.417”
- **Brasal p.11** — “No fim do exercício 3.714 1.145 96.453 62.166”
- **Brasal p.48** — “Aplicação Financeira - - 78.569 78.569”

</details>

### 4. Quais riscos são citados por mais de uma empresa?

**0 categorias de risco aparecem em mais de uma empresa**; 0 aparecem nas três: nenhuma.

- Citados por **apenas uma** empresa: Liquidez e endividamento (Light); Juros e risco de mercado (Light); Continuidade operacional (Light); Regulatório / fiscal / concessão (Light); Crédito / inadimplência de clientes (Millet); Custo de insumos / matérias-primas (Brasal).
*Metodologia: cada risco recebe uma categoria de uma taxonomia fixa; a pergunta é respondida pela interseção das categorias (código), não por um parecer livre. Para Millet e Brasal, a base são as notas explicativas (não há relatório da administração).*

<details><summary>Fontes (documento · página · trecho)</summary>

- **Light p.26** — “A Administração da Companhia entende que o Grupo Light e sua controlada Light SESA apresentam situação operacional e financeira complexa,…”
- **Light p.26** — “Esta situação foi agravada pelo(a): (i) aumento das taxas de juros SELIC de 2.00% em janeiro de 2021 para 13.75% em agosto de 2022;”
- **Light p.3** — “Os eventos e condições, anteriormente mencionados, individual ou coletivamente, indicam, no julgamento da Administração da Companhia, a e…”
- **Light p.26** — “A concessão da controlada Light SESA, a distribuidora de energia elétrica do Grupo, vencerá em junho de 2026. A Administração da Companhi…”
- **Millet p.19** — “A exposição máxima ao risco de crédito do Contas a Receber de clientes na data das demonstrações financeiras é o valor contábil de cada f…”
- **Millet p.40** — “Contas a receber de clientes - - 98.663 69.645”
- **Brasal p.17** — “Para mitigar os riscos de preços causados pelas oscilações do mercado dos estoques de matéria prima, principalmente relacionado ao açúcar…”

</details>

### 5. Qual é o guidance de cada empresa para o próximo ano?

**Nenhuma das três empresas divulga guidance numérico para 2023** nos documentos fornecidos (são demonstrações financeiras anuais de 2022, não releases com projeções).

- **Light** — **nenhum guidance numérico**; o documento também não traz perspectivas/projeções (**não encontrado**).
- **Millet** — **nenhum guidance numérico**; o documento também não traz perspectivas/projeções (**não encontrado**).
- **Brasal** — **nenhum guidance numérico**; o documento também não traz perspectivas/projeções (**não encontrado**).

<details><summary>Fontes (documento · página · trecho)</summary>


</details>

## 5. Alertas de inconsistência e de informações não encontradas

### Inconsistências e alertas de validação

| Sev. | Empresa | Check | Campo | Descrição | Págs. |
|---|---|---|---|---|---|
| 🔴 alta | Light | C04 | `ebitda` | EBITDA reportado no texto = 1.180 mi (positivo), mas a recomposição pelas DFs (EBIT + D&A) = -1.179,6 mi (NEGATIVO). Mesmo módulo, sinal oposto: provável omissão do sinal negativo no texto. O pipeline usa o valor recomposto na comparação. | 9 |
| 🔴 alta | Light | C00 | `grounding` | 1 evidência(s) da extração falharam no grounding. | 21 |
| 🔴 alta | Millet | C00 | `grounding` | 1 evidência(s) da extração falharam no grounding. | 10 |
| 🟠 média | Light | C11 | `LIGHT-A1` | Cabeçalho da Demonstração de Resultados Abrangentes apresenta o ano de 2021 repetido três vezes nas colunas. | 21 |
| 🟠 média | Millet | C10 | `receita_liquida` | Variação extrema (131,9%): confirme comparabilidade dos períodos (ver anomalias do documento). | 7 |
| 🟠 média | Millet | C10 | `lucro_liquido` | Variação extrema (192,0%): confirme comparabilidade dos períodos (ver anomalias do documento). | 7 |
| 🟠 média | Millet | C11 | `MILLET-A1` | Na DFC consolidada de 2022, o valor do caixa líquido das atividades operacionais aparece desalinhado na mesma linha dos valores da controladora nas colunas de cabeçalho, exigindo cruzamento com os totais calculados. | 10 |
| 🟠 média | Brasal | C10 | `fco` | Variação extrema (112,6%): confirme comparabilidade dos períodos (ver anomalias do documento). | 11 |
| 🟠 média | Brasal | C11 | `BRASAL-A1` | Uso de ponto e vírgula incorreto nos milhares da linha de custos na nota explicativa 3.3. | 25 |

**4 verificações passaram** (variações, margem, dívida líquida = bruta − caixa, reconciliação com notas). Notas informativas:

- *Light · C09 · alavancagem:* Alavancagem reportada 3,32x (EBITDA ajustado p/ covenants). Não é replicável com o EBITDA recomposto (≤ 0 → n.s.): o EBITDA de covenants exclui provisões e itens não caixa.
- *Light · C10 · lucro_liquido:* Sinal negativo em um dos períodos (-5.672,2 mi vs 397,9 mi): variação percentual não significativa (n.s.).
- *Light · C10 · fco:* Sinal negativo em um dos períodos (200,8 mi vs -42,0 mi): variação percentual não significativa (n.s.).
- *Millet · C10 · fco:* Sinal negativo em um dos períodos (-14,3 mi vs 7,4 mi): variação percentual não significativa (n.s.).

### Informações não encontradas nos documentos

| Empresa | Campo | Motivo | Ausência re-verificada por busca no PDF |
|---|---|---|---|
| Light | `margem_ebitda` | O termo margem EBITDA publicada em percentual não foi encontrado explicitamente no texto fornecido. | — |
| Light | `capex` | A linha consolidada de Capex não é apresentada em um único montante consolidado nas DFs, havendo apenas linhas separadas de imobilizado e intangível na DFC, portanto listadas como complementar. | — |
| Millet | `ebitda` | O termo EBITDA ou LAJIDA não aparece explicitamente nas demonstrações financeiras publicadas. | — |
| Millet | `margem_ebitda` | O termo Margem EBITDA não aparece explicitamente nas demonstrações financeiras publicadas. | — |
| Millet | `alavancagem` | O indicador de alavancagem Dívida líquida / EBITDA não é publicado diretamente no texto. | — |
| Millet | `capex` | A linha consolidada de Capex total não possui um somatório único explícito no DFC, havendo linhas separadas de imobilizado e intangível. | — |
| Brasal | `ebitda` | O termo EBITDA ou LAJIDA não aparece explicitamente publicado nas DFs consolidadas. | — |
| Brasal | `margem_ebitda` | O termo margem EBITDA não consta no documento. | — |
| Brasal | `divida_liquida` | O termo 'dívida líquida' não aparece publicado de forma consolidada nas tabelas. | — |
| Brasal | `alavancagem` | O indicador de alavancagem não é citado ou publicado no documento. | — |
| Brasal | `capex` | O valor consolidado de capex precisa ser extraído por componente ou linha de fluxo de caixa conforme regra estrita para não utilizar o total das atividades de investimento. | — |

*Campos 'não encontrado' **não foram estimados**. Quando útil à comparação, o relatório mostra um indicador derivado, sempre rotulado como calculado (¤).*

### Verificação de ancoragem (grounding)

⚠️ **9 falhas de ancoragem de 78 evidências** — os itens abaixo foram marcados como *não verificado* e NÃO entram nas conclusões:

- Light p.21 · `anomalia:LIGHT-A1[0]` · trecho não encontrado literalmente na página citada
- Light p.9 · `motivos[1]` · trecho não encontrado literalmente na página citada
- Light p.26 · `riscos[2]` · trecho não encontrado literalmente na página citada
- Light p.56 · `eventos[1]` · trecho não encontrado literalmente na página citada
- Millet p.10 · `fco.anterior` · valor 7424.0 não aparece no trecho citado
- Millet p.36 · `riscos[1]` · trecho não encontrado literalmente na página citada
- Brasal p.26 · `motivos[1]` · trecho não encontrado literalmente na página citada
- Brasal p.12 · `riscos[1]` · trecho não encontrado literalmente na página citada
- Brasal p.26 · `eventos[0]` · trecho não encontrado literalmente na página citada

### Segurança do conteúdo (varredura de prompt injection)

✅ Nenhum padrão suspeito em 218 páginas.

## Anexo A — Indicadores derivados (fórmulas e insumos)

Cada indicador **derivado** lista fórmula e as entradas (página + trecho do PDF).

**Light**

- `ebitda_derivado` = EBIT + Depreciação e Amortização (fluxo de caixa): 2022 = **−R$ 1,18 bi**, 2021 = R$ 1,82 bi
    - ebit: −R$ 1,91 bi — [Light p.20] “LUCRO (PREJUÍZO) ANTES DO RESULTADO FINANCEIRO E IMPOSTOS (5.681.153) 397.043 (1.910.411) 1.143.301”
    - depreciacao_amortizacao: R$ 730,8 mi — [Light p.23] “Depreciação e amortização 32 - - 730.767 678.110”
- `margem_ebitda_derivada` = EBITDA derivado / Receita líquida (DRE): 2022 = **−8,9%**, 2021 = 12,2%. Receita líquida consolidada da DRE.
    - receita_liquida: R$ 13,25 bi — [Light p.20] “RECEITA LÍQUIDA 31 - - 13.253.286 14.897.920”
- `margem_ebitda_derivada_ex_construcao` = EBITDA derivado / (Receita líquida − receita de construção): 2022 = **−9,7%**, 2021 = 13,1%. Base de receita usada pela administração da Light no texto.
    - receita_liquida: R$ 13,25 bi — [Light p.20] “RECEITA LÍQUIDA 31 - - 13.253.286 14.897.920”
    - receita_construcao: R$ 1,15 bi — [Light p.93] “Receita de construção 1.146.446 967.268”
- `divida_liquida_derivada` = Dívida bruta − Caixa − Aplicações financeiras: 2022 = **R$ 9,03 bi**, 2021 = R$ 7,35 bi. Valor negativo = caixa líquido (empresa com mais caixa do que dívida).
    - divida_bruta: R$ 11,12 bi — [Light p.105] “Dívida bruta 11.115.787 10.957.892”
    - caixa_equivalentes: R$ 43,9 mi — [Light p.47] “TOTAL 2.693 9 43.886 396.777”
    - aplicacoes_financeiras: R$ 2,04 bi — [Light p.47] “TOTAL 720.172 62.647 2.039.665 3.208.196”
- `alavancagem_derivada` = Dívida líquida / EBITDA derivado: 2022 = **n.s.**, 2021 = 4,04x. n.s. (não significativo) quando o EBITDA é negativo. Dívida líquida = valor reportado, se existir; senão derivada.

**Millet**

- `ebitda_derivado` = EBIT + Depreciação e Amortização (fluxo de caixa): 2022 = **R$ 43,5 mi**, 2021 = R$ 7,5 mi
    - ebit: R$ 25,3 mi — [Millet p.7] “Resultado antes do resultado 14.750 5.374 25.298 4.482 financeiro”
    - depreciacao_amortizacao: R$ 18,2 mi — [Millet p.10] “Depreciação e amortização 13.295 - 18.248 2.975”
- `margem_ebitda_derivada` = EBITDA derivado / Receita líquida (DRE): 2022 = **9,4%**, 2021 = 3,7%. Receita líquida consolidada da DRE.
    - receita_liquida: R$ 462,1 mi — [Millet p.7] “Receita operacional líquida 18 - - 462.127 199.259”
- `divida_liquida_derivada` = Dívida bruta − Caixa − Aplicações financeiras: 2022 = **R$ 13,5 mi**, 2021 = R$ 16,9 mi. Valor negativo = caixa líquido (empresa com mais caixa do que dívida).
    - divida_bruta: R$ 24,2 mi — [Millet p.42] “Total dos empréstimos com terceiros 24.176 25.072”
    - caixa_equivalentes: R$ 10,7 mi — [Millet p.10] “Saldo final de caixa e equivalentes de caixa 354 871 10.655 8.195”
- `alavancagem_derivada` = Dívida líquida / EBITDA derivado: 2022 = **0,31x**, 2021 = 2,26x. n.s. (não significativo) quando o EBITDA é negativo. Dívida líquida = valor reportado, se existir; senão derivada.
- `capex_caixa_derivado` = Σ aquisições de imobilizado e intangível (fluxo de caixa): 2022 = **R$ 17,7 mi**, 2021 = n/d
    - capex: R$ 6,3 mi — [Millet p.10] “Aquisição de imobilizado - - (6.263) (3.803)”
    - capex: R$ 11,5 mi — [Millet p.10] “Aquisição de intangível - - (11.469) (12)”

**Brasal**

- `ebitda_derivado` = EBIT + Depreciação e Amortização (fluxo de caixa): 2022 = **R$ 221,9 mi**, 2021 = R$ 261,1 mi
    - ebit: R$ 192,8 mi — [Brasal p.8] “Lucro operacional antes das receitas e despesas 173.736 275.244 192.840 238.224 financeiras”
    - depreciacao_amortizacao: R$ 29,0 mi — [Brasal p.11] “Depreciações e amortizações 507 465 29.014 22.837”
- `margem_ebitda_derivada` = EBITDA derivado / Receita líquida (DRE): 2022 = **16,7%**, 2021 = 24,6%. Receita líquida consolidada da DRE.
    - receita_liquida: R$ 1,33 bi — [Brasal p.8] “Receita operacional líquida 21 - - 1.325.059 1.061.410”
- `divida_liquida_derivada` = Dívida bruta − Caixa − Aplicações financeiras: 2022 = **−R$ 171,6 mi**, 2021 = −R$ 151,5 mi. Valor negativo = caixa líquido (empresa com mais caixa do que dívida).
    - divida_bruta: R$ 3,4 mi — [Brasal p.48] “Empréstimos e financiamentos - - 3.417 3.417”
    - caixa_equivalentes: R$ 96,5 mi — [Brasal p.11] “No fim do exercício 3.714 1.145 96.453 62.166”
    - aplicacoes_financeiras: R$ 78,6 mi — [Brasal p.48] “Aplicação Financeira - - 78.569 78.569”
- `alavancagem_derivada` = Dívida líquida / EBITDA derivado: 2022 = **−0,77x**, 2021 = −0,58x. n.s. (não significativo) quando o EBITDA é negativo. Dívida líquida = valor reportado, se existir; senão derivada.


## Anexo B — Abordagem tradicional (estatística / ML clássico) vs regras e LLM

Comparação entre a abordagem **estatística / ML clássico** (sem LLM, sem rótulos) e as **regras + leitura do documento** usadas no restante do relatório. O detector olha as linhas das demonstrações (DRE, balanço, fluxo de caixa) e procura variações atípicas **dentro de cada documento**: z-score robusto (|z| >= 3.5 (mediana/MAD)) e Isolation Forest. Ele **não explica** nada e **não vê texto**; serve para gerar candidatos a revisão.

| Documento | Linhas pontuadas | Sinalizadas (z-score) | Sinalizadas (Isolation Forest) | Ambos | Coincidem com alerta existente¹ | Inversões de sinal² |
|---|---|---|---|---|---|---|
| Light | 104 | 7 | 5 | 3 | 0 | 22 |
| Millet | 61 | 4 | 3 | 3 | 0 | 3 |
| Brasal | 66 | 6 | 4 | 3 | 0 | 4 |

**Light — maiores desvios**

- Instrumentos financeiros derivativos swaps: 396.946 vs 3.975 (R$ mil), z = +7.3 [Light p.19] — _candidato novo_
- Perdas cambiais e monetárias de atividades financeiras: 16.260 vs 743.095 (R$ mil), z = -5.8 [Light p.23] — _candidato novo_
- LUCRO (PREJUÍZO) ANTES DO IR E CSLL: −5.357.738 vs −186.889 (R$ mil), z = +5.4 [Light p.20] — _candidato novo_
- Valor justo do ativo financeiro da concessão 13/31: −38.365 vs −574.231 (R$ mil), z = -4.1 [Light p.23] — _candidato novo_
- Instrumentos financeiros derivativos swaps: 13.611 vs 190.409 (R$ mil), z = -4.0 [Light p.18] — _candidato novo_

**Millet — maiores desvios**

- Aquisição de intangível: −11.469 vs −12 (R$ mil), z = +9.0 [Millet p.10] — _candidato novo_
- Juros sobre arrendamentos: 3.752 vs 35 (R$ mil), z = +6.0 [Millet p.10] — _candidato novo_
- Saldo inicial de caixa e equivalentes de caixa: 8.195 vs 199 (R$ mil), z = +4.7 [Millet p.10] — _candidato novo_
- Diferido: 166 vs 3.333 (R$ mil), z = -4.5 [Millet p.7] — _candidato novo_

**Brasal — maiores desvios**

- Crédito ICMS na base de PIS e COFINS: −233 vs −105.633 (R$ mil), z = -8.8 [Brasal p.11] — _candidato novo_
- Obrigações fiscais: −49.818 vs −125 (R$ mil), z = +8.7 [Brasal p.11] — _candidato novo_
- Outras receitas operacionais, líquidas 23.g: 2.182 vs 105.328 (R$ mil), z = -5.5 [Brasal p.8] — _candidato novo_
- Ajuste a valor presente do incentivo governamental: −770 vs −36.453 (R$ mil), z = -5.5 [Brasal p.11] — _candidato novo_
- Empréstimos e financiamentos (incluindo juros pagos): −3.369 vs −112.259 (R$ mil), z = -5.0 [Brasal p.11] — _candidato novo_

**Tom da administração: léxico (sem ML) vs classificação**

| Documento | Classificado | Léxico | Score léxico | Concorda |
|---|---|---|---|---|
| Light | negativo | negativo | -1.00 | sim |
| Millet | neutro | neutro | +0.00 | sim |
| Brasal | neutro | neutro | +0.00 | sim |

_Leitura honesta:_ (1) coincidência por palavras do rótulo, heurística imperfeita; (2) linhas que mudam de sinal não têm razão logarítmica e ficam fora da pontuação. Um classificador de tom **supervisionado não foi treinado**: com 3 documentos não há corpus rotulado, e o léxico (n = 3) é só um sanity-check — não prova nada. O detector estatístico acerta números atípicos que as regras não procuram, mas gera ruído e não distingue efeito contábil legítimo de erro; as regras e a leitura do texto dão o *porquê*. A comparação com o **LLM** só é possível rodando `--mode llm` (veja o README).

## Anexo C — Metodologia desta execução

- **Modo de extração:** `llm` (LLM com saída estruturada; cada valor passa por grounding)
- **Documentos** (SHA-256 abreviado · páginas · tempo de ingestão):
    - Light: `light.pdf` · `a87339d09747` · 124 págs · 28.57s (pdftotext)
    - Millet: `millet.pdf` · `42589e4b7ad3` · 43 págs · 7.49s (pdftotext)
    - Brasal: `brasal.pdf` · `5905cd3412e4` · 51 págs · 4.75s (pdftotext)
- **LLM:** gemini/gemini-3.5-flash-lite · 6 chamadas · 91,878 tokens de entrada · 13,387 de saída · 32.1s · custo estimado US$ 0.061 (preços configuráveis em .env).
- **Convenção de páginas:** posição física no PDF (1 = capa); pode diferir do número impresso no rodapé.
- **Premissa de escopo:** os PDFs são demonstrações financeiras **anuais de 2022** (não releases trimestrais). 'Período de referência' = exercício 2022 vs 2021.
