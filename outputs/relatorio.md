# Relatório de Análise Financeira — Light, Millet e Brasal

*Gerado em 14/11/2026 14:31 · modo `reference` · exercício 2022 vs 2021 · valores em R$ (conforme indicado)*

> **Leia primeiro:** os 3 PDFs são demonstrações financeiras anuais, não releases trimestrais. Só a Light inclui Relatório da Administração; Millet e Brasal têm apenas DFs e notas explicativas — por isso EBITDA, margem EBITDA, dívida líquida e guidance estão frequentemente *não encontrados*. Indicadores marcados com ¤ são **calculados** pelo pipeline, nunca extraídos.

## 1. Resumo executivo

### Light S.A. (consolidado)

1. Receita líquida de **R$ 13,25 bi** em 2022 (−11,0% vs 2021) [Light p.20].
2. EBITDA: texto cita R$ 1.180 mi, mas **recomposto pelas DFs = −R$ 1,18 bi** — diverge, ver alertas [Light p.9].
3. Lucro líquido de **−R$ 5,67 bi** (−1.525,4% vs 2021) [Light p.20].
4. Dívida líquida de **R$ 9,03 bi**; alavancagem de covenants **3,32x** [Light p.105].
5. Tom: **negativo** (confiança alta). Alerta: EBITDA CVM da distribuidora: o texto diz R$1.817 mi… [Light p.8]

### Millet Participações S.A. (consolidado; controla 85% da Alibra)

1. Receita líquida de **R$ 462,1 mi** em 2022 (+131,9% vs 2021) (⚠ 2021 parcial: Alibra só desde jun/21) [Millet p.7].
2. EBITDA **não publicado**; derivado (EBIT + D&A) = R$ 43,5 mi, margem ≈ 9,4% (calculado ¤) [Millet p.7].
3. Lucro líquido de **R$ 18,9 mi** (+192,0% vs 2021) [Millet p.7].
4. Dívida líquida de **R$ 13,5 mi** [Millet p.42].
5. Tom: **neutro** (confiança baixa). Alerta: Comparabilidade da receita: a Alibra foi adquirida em 18/06/2021… [Millet p.27]

### Brasal Brasília Holding S.A. (consolidado; controla a Brasal Refrigerantes – Coca-Cola/Heineken)

1. Receita líquida de **R$ 1,33 bi** em 2022 (+24,8% vs 2021) [Brasal p.8].
2. EBITDA **não publicado**; derivado (EBIT + D&A) = R$ 221,9 mi, margem ≈ 16,7% (calculado ¤) [Brasal p.8].
3. Lucro líquido de **R$ 174,6 mi** (−36,6% vs 2021) [Brasal p.8].
4. Dívida líquida **não publicada**; derivada = **−R$ 171,6 mi** (caixa líquido; calculado ¤) [Brasal p.48].
5. Tom: **neutro** (confiança baixa). Alerta: Os valores comparativos de 2021 (DRE, balanço… [Brasal p.3]

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
| Dívida líquida 2022 | 9.032,2 · p.105 | 13,5 · p.42 | não encontrado (derivada¤: −171,6) |
| Dívida líquida / EBITDA | **3,32x** (covenants) · p.10 | não encontrado (derivada¤: 0,31x) | não encontrado (caixa líquido¤) |
| Fluxo de caixa operacional 2022 | 200,8 · p.23 | 24,8 · p.10 | 258,2 · p.11 |
| Capex 2022 | 1.506,0 · p.10 | não encontrado (soma das linhas de caixa¤: 17,7) | 45,8 · p.11 |

¤ **Calculado pelo pipeline** a partir de linhas do documento (fórmulas na seção *Anexo A*); não é número publicado pela empresa.
¹ Millet: a Alibra foi consolidada só a partir de 18/06/2021; a variação não é comparável (base comparável ≈ +45%).
² Brasal: coluna 2021 marcada como *não auditada* pelo auditor.
³ Light: o texto imprime R$ 1.180 mi **sem sinal**; as DFs (EBIT + D&A) dão −R$ 1.179,6 mi. Light capex: 'investimentos' da administração (competência); capex de caixa = soma das duas linhas do DFC.
Células com `· p.N` indicam a página do PDF (1 = capa) onde o valor foi encontrado e verificado.

## 3. Análise qualitativa do comentário da administração

### Light
*Fonte da análise:* Relatório da Administração (págs. 2-14) + notas explicativas. Único dos três documentos com comentário da administração. Não traz guidance numérico.

**Principais motivos do resultado**

- Provisões de R$2.513 mi no período explicam a queda do EBITDA: devolução de créditos de PIS/COFINS aos consumidores (Lei 14.385/22; −R$1.081 mi), revisão de PECLD (−R$855 mi) e contingências JEC e Cível (−R$379 mi). *[Light p.10]*
- Prejuízo líquido de R$5,7 bi: além da provisão do PIS/COFINS, houve atualização financeira desses valores (−R$1.584 mi) e impairment do IR/CS diferido (−R$1.634 mi). *[Light p.10]*
- Juros mais altos: a Selic subiu de 2,00% (jan/2021) para 13,75% (ago/2022), agravando o desequilíbrio de capital. *[Light p.26]*

**Motivo da variação da receita**

- Receita líquida (ex-construção) −13%: estornos de faturamento de regularizações, não acionamento das bandeiras tarifárias e variação negativa da CVA. *[Light p.9]*

**Riscos e pontos de atenção**

- `Continuidade operacional` Incerteza significativa sobre a continuidade operacional do Grupo Light e da Light SESA (reconhecida pela administração e destacada pelo auditor). *[Light p.28]*
- `Regulatório / fiscal / concessão` A concessão da Light SESA vence em junho de 2026; a renovação depende de processo formal e de negociação fora do controle da companhia. *[Light p.26]*
- `Regulatório / fiscal / concessão` Análise preliminar indica risco de descumprimento dos indicadores de sustentabilidade econômico-financeira exigidos pela ANEEL para 2022. *[Light p.27]*
- `Liquidez e endividamento` Sem linhas de crédito contratadas e disponíveis em 31/12/2022 e rebaixamentos de rating; cláusula de rating abaixo de BBB- pode causar vencimento antecipado cruzado das dívidas. *[Light p.26, p.27]*
- `Crédito / inadimplência de clientes` Elevado índice de perdas não técnicas (furto de energia) e inadimplência. *[Light p.26]*
- `Contingências judiciais e tributárias` Devolução de cerca de R$2,8 bi de créditos de PIS/COFINS (exclusão do ICMS da base) aos consumidores e contingências JEC/Cível provisionadas. *[Light p.26]*
- `Juros e risco de mercado` Juros elevados: a Selic foi de 2,00% para 13,75% no período, pressionando despesa financeira e endividamento. *[Light p.26]*

**Guidance / perspectivas**

- **Guidance numérico: não encontrado.**
- Perspectiva qualitativa: concentrar investimentos no estritamente necessário até a renovação da concessão, para maximizar o fluxo de caixa nos próximos 36 meses. *[Light p.3]*
- Objetivo de antecipar a renovação da concessão da Light SESA (vence em 2026), em bases sustentáveis. *[Light p.2]*
- Reajuste tarifário médio de 7,0% aprovado pela ANEEL em 15/03/2023 (evento subsequente) e pleitos sobre perdas não técnicas em análise. *[Light p.107]*

**Eventos relevantes** (aquisições, reestruturações, contingências, mudanças contábeis)

- Lei 14.385/22 (27/06/2022) obriga o repasse aos consumidores dos créditos tributários de PIS/COFINS sobre ICMS. *[Light p.28]*
- Revisão tarifária periódica de 2022: reajuste médio de 14,68% nas contas de energia. *[Light p.4]*
- Troca de liderança: novo CEO assumiu em agosto de 2022 e a companhia intensificou a reestruturação interna. *[Light p.2, p.3]*
- Rebaixamentos de rating em fev/2023 (Fitch CCC(bra)/CCC+; Moody's B.br/B3; S&P brBB-). *[Light p.26]*
- Compra dos 49% da CEMIG na Axxiom por R$1,00 (contrato de 21/12/2022; aprovado pelo CADE em 25/01/2023). *[Light p.107]*

**Tom geral da administração: NEGATIVO** (confiança alta) — Prejuízo de R$5,7 bi, EBITDA CVM negativo, alavancagem de covenants de 3,32x, ratings na faixa CCC/B3, ausência de linhas de crédito disponíveis e parágrafo de incerteza significativa sobre continuidade no relatório do auditor. A mensagem do CEO usa linguagem de 'turnaround' e destaca os melhores DEC/FEC em 20 anos, mas os fatos relatados são predominantemente adversos. *[Light p.2, p.111]*

### Millet
*Fonte da análise:* Apenas notas explicativas (não há relatório da administração). Sem comentário de desempenho da administração: motivos/tom derivam de notas (1.1, 7, 22) e são evidência documental, não discurso gerencial.

**Principais motivos do resultado**

- Nota 1.1: a performance de vendas 'atendeu às projeções', mesmo com demanda mais fraca que o previsto. *[Millet p.11]*
- Custo de matérias-primas (derivados lácteos) continuou subindo, com repasse ao preço; a margem não voltou ao nível pré-pandemia. *[Millet p.11]*
- Amortização da mais-valia da aquisição da Alibra (R$13.295 mil) pressionou o resultado consolidado. *[Millet p.7]*

**Motivo da variação da receita**

- [Evidência documental — não é afirmação da administração] A Alibra foi adquirida em 18/06/2021, então a receita consolidada de 2021 cobre só parte do ano; a receita da Alibra em 2021 (ano cheio) foi R$318.317 mil. *[Millet p.27, p.29]*

**Riscos e pontos de atenção**

- `Custo de insumos / matérias-primas` Aumento do custo de matérias-primas (derivados lácteos) e dificuldade de recuperar margem. *[Millet p.11]*
- `Crédito / inadimplência de clientes` Risco de crédito: perdas por falha de clientes em cumprir obrigações (contas a receber de R$98,7 mi). *[Millet p.40]*
- `Liquidez e endividamento` Risco de liquidez: dificuldade em cumprir obrigações financeiras; R$18,1 mi de empréstimos vencem em até 12 meses vs caixa de R$10,7 mi. *[Millet p.41]*
- `Juros e risco de mercado` Risco de taxa de juros e de câmbio (dívida a taxas pré-fixadas). *[Millet p.41]*
- `Contingências judiciais e tributárias` Contingências trabalhistas e previdenciárias provisionadas (R$3.284 mil). *[Millet p.36]*
- `Concentração / dependência de contratos ou investida` Dependência de uma única investida: a holding consolida somente a Alibra (85%). *[Millet p.12]*

**Guidance / perspectivas**

- **Guidance numérico: não encontrado.**
- Intenção qualitativa: acumular recursos e reservas para investimentos projetados e para o capital de giro necessário nos próximos anos. *[Millet p.42]*

**Eventos relevantes** (aquisições, reestruturações, contingências, mudanças contábeis)

- Aquisição de 85% da Alibra Ingredientes em junho de 2021 por R$179.350 mil (parte a prazo). *[Millet p.27]*
- Laudo da KPMG (jun/2022) alocou o preço de compra: mais-valia amortizada linearmente (R$13.295 mil em 2022). *[Millet p.27, p.28]*
- Revisão de crédito tributário de ação ajuizada em 2009 (abr/2022): créditos reduzidos. *[Millet p.36]*
- Nenhum evento subsequente exigindo divulgação. *[Millet p.43]*

**Tom geral da administração: NEUTRO** (confiança baixa) — Sem discurso gerencial. As notas combinam um sinal positivo (vendas 'atenderam às projeções') com ressalvas (demanda mais fraca, custo de lácteos, margem abaixo do pré-pandemia). Não há juízo de valor consolidado — classificação neutra com baixa confiança. *[Millet p.11]*

### Brasal
*Fonte da análise:* Apenas notas explicativas (não há relatório da administração). Sem comentário de desempenho da administração e sem explicação para a variação da receita. Os 'motivos' abaixo são evidência extraída das DFs, não afirmação gerencial.

**Principais motivos do resultado**

- [Evidência documental] O lucro líquido caiu em 2022 em parte porque 2021 incluía R$105.633 mil de créditos extemporâneos (exclusão do ICMS da base do PIS/COFINS) em outras receitas operacionais. *[Brasal p.46]*
- [Evidência documental] As receitas financeiras recuaram de R$116.653 mil (2021) para R$29.541 mil (2022). *[Brasal p.8]*

**Motivo da variação da receita**

- Não encontrado no documento.

**Riscos e pontos de atenção**

- `Crédito / inadimplência de clientes` Crédito concedido a clientes é apontado como o principal fator de risco de mercado. *[Brasal p.49]*
- `Custo de insumos / matérias-primas` Oscilação de preços dos produtos em razão da compra de matéria-prima (commodities). *[Brasal p.49]*
- `Juros e risco de mercado` Oscilação de taxas de juros incidentes sobre ativos e passivos financeiros (CDI). *[Brasal p.49]*
- `Concentração / dependência de contratos ou investida` Contratos por prazo determinado com Coca-Cola, Heineken e Leão: dependência de marcas licenciadas. *[Brasal p.12]*
- `Regulatório / fiscal / concessão` Incentivo fiscal Emprega/DF (crédito presumido de 67% do ICMS) condicionado a manutenção de empregos, regularidade fiscal e contrapartidas. *[Brasal p.12]*
- `Contingências judiciais e tributárias` Ações judiciais de risco possível (52 trabalhistas, 9 cíveis e fiscais — IPI, PIS) não provisionadas; STF (fev/2023) limitou a 'coisa julgada' em tributos recorrentes (sem impacto identificado). *[Brasal p.41, p.51]*
- `Qualidade / auditoria da informação` Comparativos de 2021 não auditados. *[Brasal p.3]*

**Guidance / perspectivas**

- **Guidance numérico: não encontrado.**

**Eventos relevantes** (aquisições, reestruturações, contingências, mudanças contábeis)

- Aumento de capital de R$60.000 mil por capitalização de reservas (28/03/2022), sem emissão de ações. *[Brasal p.42]*
- Dividendos intermediários de R$206.000 mil em 2022 (a partir de reservas de lucros). *[Brasal p.10]*
- Incentivo fiscal: R$103.940 mil reconhecidos em 2022 como reserva de incentivos fiscais. *[Brasal p.12]*
- Evento subsequente: decisão do STF (08/02/2023) sobre perda de efeitos da coisa julgada em tributos de trato continuado; administração não identificou impacto. *[Brasal p.51]*

**Tom geral da administração: NEUTRO** (confiança baixa) — Sem discurso gerencial. As DFs mostram receita +24,8% e caixa líquido positivo, mas lucro −36,6% (2021 tinha ganhos não recorrentes) e comparativos não auditados; a linguagem das notas é técnica e descritiva — classificação neutra com baixa confiança. *[Brasal p.51]*


## 4. Respostas às 5 perguntas

### 1. Qual empresa teve a maior margem EBITDA no período?

**Brasal**, com margem EBITDA de ≈ **16,7%** em 2022 — mas atenção: é uma margem **derivada pelo pipeline**, não publicada. Nenhum dos três documentos informa margem EBITDA, e só a Light publica EBITDA.
A Light imprime EBITDA CVM de R$ 1.180 mi [Light p.9], porém as DFs mostram EBIT + D&A = −R$ 1,18 bi (**negativo**; ver alerta de sinal).
Para comparar de forma padronizada usei **EBITDA derivado = EBIT + D&A (fluxo de caixa) ÷ receita líquida da DRE**:

1. Brasal: **16,7%** (EBITDA derivado R$ 221,9 mi; 2021: 24,6%) — 2021 inflado por R$ 105,6 mi de créditos extemporâneos não recorrentes [Brasal p.8]
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

- **Light** (receita R$ 13,25 bi vs R$ 14,90 bi; −11,0%): Receita líquida (ex-construção) −13%: estornos de faturamento de regularizações, não acionamento das bandeiras tarifárias e variação negativa da CVA. [Light p.9] (a DRE total varia −11,0%; o −13% da administração exclui receita de construção)
- **Millet** (receita R$ 462,1 mi vs R$ 199,3 mi; +131,9%): [Evidência documental — não é afirmação da administração] A Alibra foi adquirida em 18/06/2021, então a receita consolidada de 2021 cobre só parte do ano; a receita da Alibra em 2021 (ano cheio) foi R$318.317 mil. [Millet p.27, p.29] Em base comparável (Alibra com 2021 inteiro) a receita cresceria ≈ +45,2% [Millet p.29].
- **Brasal** (receita R$ 1,33 bi vs R$ 1,06 bi; +24,8%): **Não encontrado**: o documento não traz explicação da administração para a variação da receita.

<details><summary>Fontes (documento · página · trecho)</summary>

- **Light p.9** — “R$12.107 milhões, 13% abaixo da registrada em 2021. Essa redução foi influenciada pelos estornos de faturamento de regularizações, pelo n…”
- **Light p.20** — “RECEITA LÍQUIDA 31 - - 13.253.286 14.897.920”
- **Millet p.27** — “Adquirida. A Transação foi concluída em 18 de junho de 2021, em continuidade à celebração de contrato de”
- **Millet p.29** — “Receita operacional líquida 462.127 318.317”
- **Millet p.7** — “Receita operacional líquida 18 - - 462.127 199.259”
- **Brasal p.8** — “Receita operacional líquida 21 - - 1.325.059 1.061.410”

</details>

### 3. Alguma das empresas está com alavancagem acima de 3x? Qual?

**Sim — Light.** Único múltiplo **publicado** acima de 3x: Light.

- **Light: 3,32x** (Dívida líquida/EBITDA ajustado de covenants, publicado) [Light p.10]; dívida líquida R$ 9,03 bi [Light p.105]; pelo EBITDA CVM recomposto (negativo) o múltiplo é n.s., o que é pior, não melhor
- Millet: não publica alavancagem sobre EBITDA; **derivado 0,31x** (dívida líquida R$ 13,5 mi ÷ EBITDA derivado R$ 43,5 mi).
- Brasal: não publica alavancagem; dívida líquida derivada = **−R$ 171,6 mi** (caixa líquido: mais caixa e aplicações do que dívida) — sem alavancagem.

<details><summary>Fontes (documento · página · trecho)</summary>

- **Light p.10** — “2021 em 3,32x, menor do que no 2021 (3,48x). O EBITDA ajustado para fins de covenants”
- **Light p.105** — “Dívida líquida (A) 9.032.236 7.352.919”
- **Millet p.7** — “Resultado antes do resultado 14.750 5.374 25.298 4.482 financeiro”
- **Millet p.10** — “Depreciação e amortização 13.295 - 18.248 2.975”
- **Millet p.42** — “Total dos empréstimos com terceiros 24.176 25.072”
- **Millet p.6** — “Caixa e equivalente de caixa 3 355 871 10.656 8.195”
- **Millet p.42** — “(=) Dívida líquida (a) 13.520 16.877”
- **Brasal p.8** — “Lucro operacional antes das receitas e despesas 173.736 275.244 192.840 238.224 financeiras”
- **Brasal p.11** — “Depreciações e amortizações 507 465 29.014 22.837”
- **Brasal p.48** — “Empréstimos e financiamentos - - 3.417 3.417”
- **Brasal p.6** — “Caixa e equivalentes de caixa 4 3.714 1.146 96.453 62.166”
- **Brasal p.6** — “Aplicações financeiras 5 - - 78.569 95.766”

</details>

### 4. Quais riscos são citados por mais de uma empresa?

**7 categorias de risco aparecem em mais de uma empresa**; 3 aparecem nas três: Crédito / inadimplência de clientes, Contingências judiciais e tributárias, Juros e risco de mercado.

- **Contingências judiciais e tributárias** — 3 empresas (Light, Millet, Brasal):
    - Light: Devolução de cerca de R$2,8 bi de créditos de PIS/COFINS (exclusão do ICMS da base) aos consumidores e contingências JEC/Cível provisionadas. [Light p.26]
    - Millet: Contingências trabalhistas e previdenciárias provisionadas (R$3.284 mil). [Millet p.36]
    - Brasal: Ações judiciais de risco possível (52 trabalhistas, 9 cíveis e fiscais — IPI, PIS) não provisionadas; STF (fev/2023) limitou a 'coisa julgada' em… [Brasal p.41]
- **Crédito / inadimplência de clientes** — 3 empresas (Light, Millet, Brasal):
    - Light: Elevado índice de perdas não técnicas (furto de energia) e inadimplência. [Light p.26]
    - Millet: Risco de crédito: perdas por falha de clientes em cumprir obrigações (contas a receber de R$98,7 mi). [Millet p.40]
    - Brasal: Crédito concedido a clientes é apontado como o principal fator de risco de mercado. [Brasal p.49]
- **Juros e risco de mercado** — 3 empresas (Light, Millet, Brasal):
    - Light: Juros elevados: a Selic foi de 2,00% para 13,75% no período, pressionando despesa financeira e endividamento. [Light p.26]
    - Millet: Risco de taxa de juros e de câmbio (dívida a taxas pré-fixadas). [Millet p.41]
    - Brasal: Oscilação de taxas de juros incidentes sobre ativos e passivos financeiros (CDI). [Brasal p.49]
- **Concentração / dependência de contratos ou investida** — 2 empresas (Millet, Brasal):
    - Millet: Dependência de uma única investida: a holding consolida somente a Alibra (85%). [Millet p.12]
    - Brasal: Contratos por prazo determinado com Coca-Cola, Heineken e Leão: dependência de marcas licenciadas. [Brasal p.12]
- **Custo de insumos / matérias-primas** — 2 empresas (Millet, Brasal):
    - Millet: Aumento do custo de matérias-primas (derivados lácteos) e dificuldade de recuperar margem. [Millet p.11]
    - Brasal: Oscilação de preços dos produtos em razão da compra de matéria-prima (commodities). [Brasal p.49]
- **Liquidez e endividamento** — 2 empresas (Light, Millet):
    - Light: Sem linhas de crédito contratadas e disponíveis em 31/12/2022 e rebaixamentos de rating; cláusula de rating abaixo de BBB- pode causar vencimento… [Light p.26]
    - Millet: Risco de liquidez: dificuldade em cumprir obrigações financeiras; R$18,1 mi de empréstimos vencem em até 12 meses vs caixa de R$10,7 mi. [Millet p.41]
- **Regulatório / fiscal / concessão** — 2 empresas (Light, Brasal):
    - Light: A concessão da Light SESA vence em junho de 2026; a renovação depende de processo formal e de negociação fora do controle da companhia. [Light p.26]
    - Brasal: Incentivo fiscal Emprega/DF (crédito presumido de 67% do ICMS) condicionado a manutenção de empregos, regularidade fiscal e contrapartidas. [Brasal p.12]
- Citados por **apenas uma** empresa: Continuidade operacional (Light); Qualidade / auditoria da informação (Brasal).
*Metodologia: cada risco recebe uma categoria de uma taxonomia fixa; a pergunta é respondida pela interseção das categorias (código), não por um parecer livre. Para Millet e Brasal, a base são as notas explicativas (não há relatório da administração).*

<details><summary>Fontes (documento · página · trecho)</summary>

- **Light p.26** — “(ii) efeito da determinação de devolução de cerca de R$2.8 bilhões de créditos decorrentes da exclusão do ICMS das bases de cálculo do PI…”
- **Millet p.36** — “Trabalhistas 722 91 Risco Previdenciário 2.562 2.264”
- **Brasal p.41** — “Existem atualmente 52 (Cinquenta e Dois) ações judiciais e referem-se a pedidos, tais como: indenizações, horas extras, verbas rescisória…”
- **Brasal p.51** — “Em decisão tomada no dia 08 de fevereiro 2023, por unanimidade, o Plenário do Supremo Tribunal Federal (STF) considerou que uma decisão d…”
- **Light p.26** — “(iii) elevado índice de perdas não técnicas (furto de energia) e inadimplência;”
- **Millet p.40** — “Risco de crédito é o risco de a Companhia incorrer em perdas decorrentes de um cliente ou de uma contraparte em um instrumento financeiro…”
- **Millet p.40** — “Contas a receber de clientes - - 98.663 69.645”
- **Brasal p.49** — “O principal fator de risco de mercado que afeta o negócio é a concessão de crédito aos clientes. Para reduzir as possíveis perdas com ina…”
- **Light p.26** — “(i) aumento das taxas de juros SELIC de 2.00% em janeiro de 2021 para 13.75% em agosto de 2022;”
- **Millet p.41** — “Risco de taxa de juros: é oriundo da possibilidade de a Companhia vir a sofrer perdas ou auferir ganhos) por conta de flutuações nas taxa…”
- **Brasal p.49** — “Decorre da possibilidade de a Companhia sofrer ganhos ou perdas decorrentes de oscilações de taxas de juros incidentes sobre seus ativos …”
- **Millet p.12** — “Alibra Ingredientes S.A. ("Alibra") Direta 85,00% 85,00%”
- **Brasal p.12** — “A Controlada mantém por prazo determinado contrato com a Coca-Cola Indústrias Ltda., com a Cervejaria Heineken e a Leão Alimentos e Bebid…”
- **Millet p.11** — “era previsto para o ano. Como ponto residual e contínuo de 2020, verificou-se a continuidade de aumento no custo de matérias primas princ…”
- **Brasal p.49** — “Os produtos comercializados pela Companhia estão sujeitos a oscilações em razão da compra de matéria-prima. Para mitigar os riscos, a Com…”
- **Light p.26** — “A Administração da Companhia informa que não possui linhas de créditos contratadas e disponíveis para utilização em 31 de dezembro de 202…”
- **Light p.27** — “Com relação ao covenant não financeiro relacionado a ratings do Grupo Light, a Administração da Companhia verificou que conforme item XXI…”
- **Millet p.41** — “Risco de liquidez é o risco em que a Companhia irá encontrar dificuldades em cumprir com as obrigações associadas com seus passivos finan…”
- **Millet p.41** — “Empréstimos e Financiamentos 24.176 24.176 18.115 6.061 -”
- **Light p.26** — “A concessão da controlada Light SESA, a distribuidora de energia elétrica do Grupo, vencerá em junho de 2026. A Administração da Companhi…”
- **Brasal p.12** — “Federal. Neste programa é concedido um percentual de crédito presumido de 67% incidente sobre o ICMS apurado das saídas de produtos de fa…”
- **Light p.28** — “Administração da Companhia, a existência de incerteza significativa que pode levantar dúvida significativa quanto à capacidade de continu…”
- **Brasal p.3** — “de dezembro de 2021, apresentadas para fins de comparação, não foram auditadas por nós ou por”

</details>

### 5. Qual é o guidance de cada empresa para o próximo ano?

**Nenhuma das três empresas divulga guidance numérico para 2023** nos documentos fornecidos (são demonstrações financeiras anuais de 2022, não releases com projeções).

- **Light** — **nenhum guidance numérico**. Perspectivas qualitativas: (1) Perspectiva qualitativa: concentrar investimentos no estritamente necessário até a renovação da concessão, para maximizar o fluxo de caixa nos próximos 36 meses. [Light p.3] (2) Objetivo de antecipar a renovação da concessão da Light SESA (vence em 2026), em bases sustentáveis. [Light p.2] (3) Reajuste tarifário médio de 7,0% aprovado pela ANEEL em 15/03/2023 (evento subsequente) e pleitos sobre perdas não técnicas em análise. [Light p.107]
- **Millet** — **nenhum guidance numérico**. Perspectivas qualitativas: (1) Intenção qualitativa: acumular recursos e reservas para investimentos projetados e para o capital de giro necessário nos próximos anos. [Millet p.42]
- **Brasal** — **nenhum guidance numérico**; o documento também não traz perspectivas/projeções (**não encontrado**).

<details><summary>Fontes (documento · página · trecho)</summary>

- **Light p.3** — “Concentramos nossos investimentos naqueles estritamente necessários para a sustentabilidade do nosso serviço até a renovação da concessão…”
- **Light p.2** — “Essas alternativas passam pela renovação da concessão da Light SESA, que vence em 2026. Nosso objetivo é antecipar esse processo. Nós ini…”
- **Light p.107** — “O resultado representa um reajuste tarifário médio para o consumidor de 7,0%, e engloba todas as”
- **Millet p.42** — “acumulando recursos e reservas de lucros de forma a corresponder com os investimentos que estão sendo projetados com a necessidade de cap…”

</details>

## 5. Alertas de inconsistência e de informações não encontradas

### Inconsistências e alertas de validação

| Sev. | Empresa | Check | Campo | Descrição | Págs. |
|---|---|---|---|---|---|
| 🔴 alta | Light | C04 | `ebitda` | EBITDA reportado no texto = 1.180 mi (positivo), mas a recomposição pelas DFs (EBIT + D&A) = -1.179,6 mi (NEGATIVO). Mesmo módulo, sinal oposto: provável omissão do sinal negativo no texto. O pipeline usa o valor recomposto na comparação. | 9 |
| 🔴 alta | Light | C11 | `LIGHT-A1` | EBITDA CVM da distribuidora: o texto diz R$1.817 mi, 'redução de R$2.996 mi' em relação a R$1.179 mi em 2021. Os números não fecham (1.817 − 1.179 = +638, não −2.996). 1.817 + 1.179 = 2.996 sugere que os anos estão invertidos (2021 = +1.817; 2022 = −1.179) e o sinal negativo foi omitido. | 8 |
| 🔴 alta | Light | C11 | `LIGHT-A3` | Auditor (Deloitte) chama a atenção para incerteza significativa sobre a continuidade operacional (nota 1.1). | 111 |
| 🔴 alta | Millet | C11 | `MILLET-A1` | Comparabilidade da receita: a Alibra foi adquirida em 18/06/2021; a receita consolidada de 2021 (R$199.259 mil) reflete só parte do ano. A própria nota 7 mostra a receita da Alibra em 2021 como R$318.317 mil (ano cheio) — a variação like-for-like seria ≈ +45%, não +132%. | 27, 29 |
| 🔴 alta | Brasal | C11 | `BRASAL-A1` | Os valores comparativos de 2021 (DRE, balanço, fluxo de caixa) estão marcados como 'não auditado' e o auditor declara não os ter auditado — variações vs 2021 têm menor confiabilidade. | 3, 8 |
| 🔴 alta | Brasal | C11 | `BRASAL-A2` | Comparabilidade do resultado: 2021 inclui R$105.633 mil de 'créditos extemporâneos' (exclusão do ICMS da base do PIS/COFINS) em outras receitas operacionais, vs R$231 mil em 2022 — não recorrente que distorce a variação do lucro. | 46 |
| 🟠 média | Light | C11 | `LIGHT-A2` | Alavancagem de covenants: o texto diz que o indicador 'encerrou 2021 em 3,32x, menor do que no 2021 (3,48x)' — período repetido; o correto seria 2022 vs 2021. | 10 |
| 🟠 média | Millet | C10 | `receita_liquida` | Variação extrema (131,9%): confirme comparabilidade dos períodos (ver anomalias do documento). | 7 |
| 🟠 média | Millet | C10 | `lucro_liquido` | Variação extrema (192,0%): confirme comparabilidade dos períodos (ver anomalias do documento). | 7 |
| 🟠 média | Millet | C11 | `MILLET-A2` | Patrimônio líquido na nota 22.2 (R$167.233 mil) difere do balanço (R$163.931 mil de controladores; R$185.321 mil consolidado). | 6, 42 |
| 🟠 média | Millet | C11 | `MILLET-A4` | Nota 2.2 diz que as DFs de 2022 foram aprovadas pela administração em 14/03/2022 (data anterior ao fim do exercício) — provável erro de digitação (2023). | 12 |
| 🟠 média | Millet | C11 | `MILLET-A5` | Nota 7 (investida Alibra): 'Lucro antes dos impostos' 2022 aparece como (65.750), mas lucro bruto − despesas − resultado financeiro = 98.338 − 63.419 − 2.331 = 32.588 (e 32.588 − 4.070 = 28.518, o lucro líquido informado). | 29 |
| 🟠 média | Brasal | C10 | `fco` | Variação extrema (112,6%): confirme comparabilidade dos períodos (ver anomalias do documento). | 11 |
| 🟠 média | Brasal | C11 | `BRASAL-A3` | Nota 20: o capital social é descrito como dividido em 3.256.699 ações e, no parágrafo seguinte, em 1.374.240 ações. | 42 |
| 🟠 média | Brasal | C11 | `BRASAL-A4` | Nota 24 (IR/CS): o 'resultado contábil antes da tributação' (IRPJ 54.297; CSLL 19.547) não bate com o lucro antes do IR da DRE (R$217.187 mil). | 8, 47 |
| 🟡 baixa | Light | C03 | `lucro_liquido` | resultado líquido segundo o texto da administração: -5.673,000 mi (escala milhoes) vs DFs -5.672,203 mi — diferença 0,797 mi (0,014%); EXCEDE o arredondamento da escala impressa. | 10, 20 |
| 🟡 baixa | Millet | C11 | `MILLET-A3` | Empréstimos em 31/12/2021: R$25.072 mil na nota 22.2 vs R$25.075 mil na nota 22.1/22.3 (e na soma do balanço). | 41, 42 |
| 🟡 baixa | Brasal | C11 | `BRASAL-A5` | Depreciação e amortização: R$20.347 mil na DRE (linha de despesa) vs R$29.014 mil no fluxo de caixa (total, inclui parcela no custo). Usamos o do fluxo de caixa no EBITDA derivado. | 8, 11 |
| 🟡 baixa | Brasal | C11 | `BRASAL-A6` | Nota 3.3: rubrica 'Custos dos imóveis vendidos' (a empresa é industrial/distribuidora de bebidas) e números com ';' em vez de '.' (1;061;410) — erros de digitação no documento. | 25 |

**10 verificações passaram** (variações, margem, dívida líquida = bruta − caixa, reconciliação com notas). Notas informativas:

- *Light · C07 · receita_liquida:* Receita líquida TOTAL da DRE varia -11,0%; a administração comenta -13,0% porque exclui a receita de construção (bases diferentes).
- *Light · C09 · alavancagem:* Alavancagem reportada 3,32x (EBITDA ajustado p/ covenants). Não é replicável com o EBITDA recomposto (≤ 0 → n.s.): o EBITDA de covenants exclui provisões e itens não caixa.
- *Light · C10 · lucro_liquido:* Sinal negativo em um dos períodos (-5.672,2 mi vs 397,9 mi): variação percentual não significativa (n.s.).
- *Light · C10 · fco:* Sinal negativo em um dos períodos (200,8 mi vs -42,0 mi): variação percentual não significativa (n.s.).
- *Millet · C10 · fco:* Sinal negativo em um dos períodos (24,8 mi vs -14,3 mi): variação percentual não significativa (n.s.).

### Informações não encontradas nos documentos

| Empresa | Campo | Motivo | Ausência re-verificada por busca no PDF |
|---|---|---|---|
| Light | `margem_ebitda` | O Relatório da Administração e as DFs não informam margem EBITDA. | “margem ebitda”, “margem do ebitda” |
| Millet | `ebitda` | O documento não apresenta EBITDA/LAJIDA. | “EBITDA”, “LAJIDA” |
| Millet | `margem_ebitda` | Sem EBITDA no documento, não há margem EBITDA reportada. | “margem ebitda”, “margem do ebitda” |
| Millet | `alavancagem` | Não há Dívida líquida/EBITDA. O documento traz apenas dívida líquida / capital ajustado (0,08x). | “dívida líquida/ebitda”, “divida liquida/ebitda” |
| Millet | `capex` | Não há linha única de capex; há duas linhas de aquisição (imobilizado e intangível). | — |
| Brasal | `ebitda` | O documento não apresenta EBITDA/LAJIDA. | “EBITDA”, “LAJIDA” |
| Brasal | `margem_ebitda` | Sem EBITDA no documento, não há margem EBITDA reportada. | “margem ebitda”, “margem do ebitda” |
| Brasal | `divida_liquida` | O documento não apresenta 'dívida líquida'. | “dívida líquida”, “divida liquida” |
| Brasal | `alavancagem` | O documento não apresenta Dívida líquida/EBITDA nem outra medida de alavancagem numérica. | “dívida líquida/ebitda” |

*Campos 'não encontrado' **não foram estimados**. Quando útil à comparação, o relatório mostra um indicador derivado, sempre rotulado como calculado (¤).*

### Verificação de ancoragem (grounding)

✅ **150 evidências verificadas, 0 falhas**: todo trecho citado existe literalmente na página indicada e contém o número extraído.

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
    - caixa_equivalentes: R$ 2,08 bi — [Light p.105] “(-) Caixa e equivalentes de caixa e TVM 2.083.551 3.604.973”
- `alavancagem_derivada` = Dívida líquida / EBITDA derivado: 2022 = **n.s.**, 2021 = 4,04x. n.s. (não significativo) quando o EBITDA é negativo. Dívida líquida = valor reportado, se existir; senão derivada.
- `capex_caixa_derivado` = Σ aquisições de imobilizado e intangível (fluxo de caixa): 2022 = **R$ 1,47 bi**, 2021 = n/d
    - capex: R$ 307,8 mi — [Light p.23] “Aquisições de bens do ativo imobilizado - - (307.759) (219.601)”
    - capex: R$ 1,16 bi — [Light p.23] “Aquisições de bens do ativo intangível e do ativo de contrato (234) - (1.162.533) (1.029.744)”

**Millet**

- `ebitda_derivado` = EBIT + Depreciação e Amortização (fluxo de caixa): 2022 = **R$ 43,5 mi**, 2021 = R$ 7,5 mi
    - ebit: R$ 25,3 mi — [Millet p.7] “Resultado antes do resultado 14.750 5.374 25.298 4.482 financeiro”
    - depreciacao_amortizacao: R$ 18,2 mi — [Millet p.10] “Depreciação e amortização 13.295 - 18.248 2.975”
- `margem_ebitda_derivada` = EBITDA derivado / Receita líquida (DRE): 2022 = **9,4%**, 2021 = 3,7%. Receita líquida consolidada da DRE.
    - receita_liquida: R$ 462,1 mi — [Millet p.7] “Receita operacional líquida 18 - - 462.127 199.259”
- `divida_liquida_derivada` = Dívida bruta − Caixa − Aplicações financeiras: 2022 = **R$ 13,5 mi**, 2021 = R$ 16,9 mi. Valor negativo = caixa líquido (empresa com mais caixa do que dívida).
    - divida_bruta: R$ 24,2 mi — [Millet p.42] “Total dos empréstimos com terceiros 24.176 25.072”
    - caixa_equivalentes: R$ 10,7 mi — [Millet p.6] “Caixa e equivalente de caixa 3 355 871 10.656 8.195”
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
    - caixa_equivalentes: R$ 96,5 mi — [Brasal p.6] “Caixa e equivalentes de caixa 4 3.714 1.146 96.453 62.166”
    - aplicacoes_financeiras: R$ 78,6 mi — [Brasal p.6] “Aplicações financeiras 5 - - 78.569 95.766”
- `alavancagem_derivada` = Dívida líquida / EBITDA derivado: 2022 = **−0,77x**, 2021 = −0,58x. n.s. (não significativo) quando o EBITDA é negativo. Dívida líquida = valor reportado, se existir; senão derivada.


## Anexo B — Abordagem tradicional (estatística / ML clássico) vs regras e LLM

Comparação entre a abordagem **estatística / ML clássico** (sem LLM, sem rótulos) e as **regras + leitura do documento** usadas no restante do relatório. O detector olha as linhas das demonstrações (DRE, balanço, fluxo de caixa) e procura variações atípicas **dentro de cada documento**: z-score robusto (|z| >= 3.5 (mediana/MAD)) e Isolation Forest. Ele **não explica** nada e **não vê texto**; serve para gerar candidatos a revisão.

| Documento | Linhas pontuadas | Sinalizadas (z-score) | Sinalizadas (Isolation Forest) | Ambos | Coincidem com alerta existente¹ | Inversões de sinal² |
|---|---|---|---|---|---|---|
| Light | 104 | 7 | 5 | 3 | 0 | 22 |
| Millet | 61 | 4 | 3 | 3 | 0 | 3 |
| Brasal | 66 | 6 | 4 | 3 | 2 | 4 |

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

- Crédito ICMS na base de PIS e COFINS: −233 vs −105.633 (R$ mil), z = -8.8 [Brasal p.11] — _já coberto por alerta_
- Obrigações fiscais: −49.818 vs −125 (R$ mil), z = +8.7 [Brasal p.11] — _candidato novo_
- Outras receitas operacionais, líquidas 23.g: 2.182 vs 105.328 (R$ mil), z = -5.5 [Brasal p.8] — _já coberto por alerta_
- Ajuste a valor presente do incentivo governamental: −770 vs −36.453 (R$ mil), z = -5.5 [Brasal p.11] — _candidato novo_
- Empréstimos e financiamentos (incluindo juros pagos): −3.369 vs −112.259 (R$ mil), z = -5.0 [Brasal p.11] — _candidato novo_

**Tom da administração: léxico (sem ML) vs classificação**

| Documento | Classificado | Léxico | Score léxico | Concorda |
|---|---|---|---|---|
| Light | negativo | negativo | -1.00 | sim |
| Millet | neutro | negativo | -0.56 | não |
| Brasal | neutro | neutro | +0.00 | sim |

_Leitura honesta:_ (1) coincidência por palavras do rótulo, heurística imperfeita; (2) linhas que mudam de sinal não têm razão logarítmica e ficam fora da pontuação. Um classificador de tom **supervisionado não foi treinado**: com 3 documentos não há corpus rotulado, e o léxico (n = 3) é só um sanity-check — não prova nada. O detector estatístico acerta números atípicos que as regras não procuram, mas gera ruído e não distingue efeito contábil legítimo de erro; as regras e a leitura do texto dão o *porquê*. A comparação com o **LLM** só é possível rodando `--mode llm` (veja o README).

## Anexo C — Metodologia desta execução

- **Modo de extração:** `reference` (extração curada + verificada por código; não usa LLM nesta execução)
- **Documentos** (SHA-256 abreviado · páginas · tempo de ingestão):
    - Light: `light.pdf` · `a87339d09747` · 124 págs · 28.57s (pdftotext)
    - Millet: `millet.pdf` · `42589e4b7ad3` · 43 págs · 7.49s (pdftotext)
    - Brasal: `brasal.pdf` · `5905cd3412e4` · 51 págs · 4.75s (pdftotext)
- **Convenção de páginas:** posição física no PDF (1 = capa); pode diferir do número impresso no rodapé.
- **Premissa de escopo:** os PDFs são demonstrações financeiras **anuais de 2022** (não releases trimestrais). 'Período de referência' = exercício 2022 vs 2021.
