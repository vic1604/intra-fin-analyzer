# Relatório de Análise Financeira — Light, Millet e Brasal

*Gerado em 14/11/2026 11:22 · modo `llm` · exercício 2022 vs 2021 · valores em R$ (conforme indicado)*

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
5. Tom: **positivo** (confiança alta).

### Brasal Brasília Holding S.A.

1. Receita líquida de **R$ 1,33 bi** em 2022 (+24,8% vs 2021) [Brasal p.8].
2. EBITDA **não publicado**; derivado (EBIT + D&A) = R$ 221,9 mi, margem ≈ 16,7% (calculado ¤) [Brasal p.8].
3. Lucro líquido de **R$ 174,6 mi** (−36,6% vs 2021) [Brasal p.8].
4. Dívida líquida **não publicada**; derivada = **−R$ 171,6 mi** (caixa líquido; calculado ¤) [Brasal p.48].
5. Tom: **neutro** (confiança alta).

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
*Fonte da análise:* Relatório da Administração e Demonstrações Financeiras de 2022 da Light S.A.. 

**Principais motivos do resultado**

- O resultado líquido da Light Energia foi beneficiado pela melhora do cenário hidrológico, elevando o GSF e reduzindo os custos de compra de energia. *[Light p.9]*

**Motivo da variação da receita**

- A receita operacional líquida consolidada foi influenciada pelos estornos de faturamento de regularizações, pelo não acionamento das bandeiras tarifárias e pela variação negativa na conta CVA. *[Light p.9]*

**Riscos e pontos de atenção**

- `Crédito / inadimplência de clientes` Inadimplência elevada e perdas não técnicas de energia persistentes na área de concessão. *[Light p.2]*
- `Juros e risco de mercado` Elevado patamar das taxas de juros que encarece o custo da dívida e pressiona a estrutura de capital. *[Light p.2]*
- `Liquidez e endividamento` Nível elevado de endividamento financeiro e geração de caixa operacional insuficiente para honrar compromissos. *[Light p.26]*
- `Regulatório / fiscal / concessão` Riscos regulatórios associados à renovação da concessão da Light SESA que vence em 2026. *[Light p.26]*
- `Contingências judiciais e tributárias` Elevado volume de contingências judiciais cíveis, trabalhistas e fiscais em aberto. *[Light p.76]*
- `Continuidade operacional` Existência de incerteza significativa que pode levantar dúvida quanto à capacidade de continuidade operacional. *[Light p.3]*
- `Custo de insumos / matérias-primas` Risco hidrológico e escassez de chuvas que podem afetar o volume dos reservatórios e elevar os custos de energia. *[Light p.101]*

**Guidance / perspectivas**

- **Guidance numérico: não encontrado.**

**Eventos relevantes** (aquisições, reestruturações, contingências, mudanças contábeis)

- Assinatura de contrato de compra e venda para aquisição da totalidade das ações da Axxiom Soluções pertencentes à Cemig. *[Light p.107]*

**Tom geral da administração: NEGATIVO** (confiança alta) — A administração reconhece desafios estruturais severos, necessidade de readequação da estrutura de capital, alto endividamento e a existência de incertezas significativas quanto à continuidade operacional da companhia. *[Light p.2, p.3]*

### Millet
*Fonte da análise:* Notas explicativas da Millet Participações S.A.. 

**Principais motivos do resultado**

- Aumento da receita operacional líquida em razão da consolidação integral e expansão das operações da controlada Alibra Ingredientes S.A. *[Millet p.29]*

**Motivo da variação da receita**

- A expansão da receita operacional líquida consolidada para R$ 462.127 em 2022 decorre principalmente do crescimento das vendas tanto no mercado interno quanto no mercado externo. *[Millet p.38]*

**Riscos e pontos de atenção**

- `Crédito / inadimplência de clientes` Risco de crédito associado à inadimplência de clientes no recebimento de títulos e contas a receber. *[Millet p.40]*
- `Liquidez e endividamento` Risco de liquidez referente a dificuldades potenciais para honrar passivos financeiros de curto e longo prazos. *[Millet p.41]*
- `Juros e risco de mercado` Risco de taxa de juros decorrente da flutuação nas taxas incidentes sobre passivos captados e ativos aplicados. *[Millet p.41]*
- `Juros e risco de mercado` Risco de taxa de câmbio atrelado à oscilação de moedas estrangeiras que afetam despesas e receitas financeiras. *[Millet p.41]*
- `Custo de insumos / matérias-primas` Exposição a variações de preços e custos de matérias-primas e materiais de uso e consumo na fabricação. *[Millet p.38]*

**Guidance / perspectivas**

- **Guidance numérico: não encontrado.**

**Eventos relevantes** (aquisições, reestruturações, contingências, mudanças contábeis)

- Aquisição de 85% de participação na Alibra Ingredientes S.A. ocorrida em junho de 2021 e seus desdobramentos contábeis em 2022. *[Millet p.27]*

**Tom geral da administração: POSITIVO** (confiança alta) — A companhia apresentou crescimento relevante na receita operacional líquida e lucros sólidos decorrentes da consolidação e expansão das operações da subsidiária. *[Millet p.29]*

### Brasal
*Fonte da análise:* Notas Explicativas da Administração e Demonstrações Financeiras da Brasal Brasília Holding S.A.. 

**Principais motivos do resultado**

- [Evidência documental] O lucro líquido do exercício consolidado foi de R$ 177.244 milhares em 2022 comparado a R$ 276.804 milhares em 2021. *[Brasal p.25]*
- [Evidência documental] A receita operacional líquida consolidada atingiu R$ 1.325.059 milhares no exercício findo em 31 de dezembro de 2022. *[Brasal p.25]*

**Motivo da variação da receita**

- [Evidência documental] A receita operacional líquida consolidada registrou crescimento em relação ao exercício anterior, passando de R$ 1.061.410 milhares para R$ 1.325.059 milhares. *[Brasal p.25]*

**Riscos e pontos de atenção**

- `Crédito / inadimplência de clientes` Risco de crédito decorrente da concessão de crédito aos clientes, mitigado por análises de perfil e monitoramento de saldos a receber. *[Brasal p.49]*
- `Custo de insumos / matérias-primas` Risco de variação de preços de matérias-primas e insumos utilizados na fabricação dos produtos comercializados. *[Brasal p.49]*
- `Juros e risco de mercado` Risco de oscilação das taxas de juros incidentes sobre ativos e passivos financeiros da Companhia. *[Brasal p.49]*
- `Regulatório / fiscal / concessão` Risco regulatório e de incentivos fiscais, visto que a controlada possui incentivos do programa Emprega/DF condicionados ao cumprimento de obrigações específicas. *[Brasal p.12]*
- `Contingências judiciais e tributárias` Risco de contingências judiciais e administrativas associadas a demandas cíveis, fiscais e trabalhistas avaliadas periodicamente com assessores jurídicos. *[Brasal p.20]*
- `Concentração / dependência de contratos ou investida` Risco de concentração ou dependência de contratos de longo prazo com fornecedores de marcas e concentrados, como Coca-Cola e Cervejaria Heineken. *[Brasal p.12]*

**Guidance / perspectivas**

- **Guidance numérico: não encontrado.**

**Eventos relevantes** (aquisições, reestruturações, contingências, mudanças contábeis)

- [Evidência documental] Em decisão de fevereiro de 2023, o Plenário do STF considerou que a coisa julgada sobre tributos de trato continuado perde efeitos caso a corte se pronuncie em sentido contrário. *[Brasal p.51]*
- [Evidência documental] A Companhia realizou a migração do incentivo fiscal IDEAS-DF para o Emprega/DF em setembro de 2020, passando a contar com crédito presumido de ICMS. *[Brasal p.12]*

**Tom geral da administração: NEUTRO** (confiança alta) — A administração apresenta um relatório financeiro regular com demonstrações auditadas sem ressalvas, evidenciando crescimento na receita líquida, mas redução pontual no lucro líquido do exercício e monitoramento contínuo de riscos de mercado e tributários sem projeções quantitativas futuras. *[Brasal p.3, p.25]*


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

- **Light** (receita R$ 13,25 bi vs R$ 14,90 bi; −11,0%): A receita operacional líquida consolidada foi influenciada pelos estornos de faturamento de regularizações, pelo não acionamento das bandeiras tarifárias e pela variação negativa na conta CVA. [Light p.9] (a DRE total varia −11,0%; o −13% da administração exclui receita de construção)
- **Millet** (receita R$ 462,1 mi vs R$ 199,3 mi; +131,9%): A expansão da receita operacional líquida consolidada para R$ 462.127 em 2022 decorre principalmente do crescimento das vendas tanto no mercado interno quanto no mercado externo. [Millet p.38]
- **Brasal** (receita R$ 1,33 bi vs R$ 1,06 bi; +24,8%): [Evidência documental] A receita operacional líquida consolidada registrou crescimento em relação ao exercício anterior, passando de R$ 1.061.410 milhares para R$ 1.325.059 milhares. [Brasal p.25]

<details><summary>Fontes (documento · página · trecho)</summary>

- **Light p.9** — “Essa redução foi influenciada pelos estornos de faturamento de regularizações, pelo não acionamento das bandeiras tarifárias e pela varia…”
- **Light p.20** — “RECEITA LÍQUIDA 31 - - 13.253.286 14.897.920”
- **Millet p.38** — “Receita operacional liquida 462.127 199.259”
- **Millet p.7** — “Receita operacional líquida 18 - - 462.127 199.259”
- **Brasal p.25** — “Receita operacional líquida 1.325.059 1;061;410”
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

**6 categorias de risco aparecem em mais de uma empresa**; 3 aparecem nas três: Crédito / inadimplência de clientes, Juros e risco de mercado, Custo de insumos / matérias-primas.

- **Crédito / inadimplência de clientes** — 3 empresas (Light, Millet, Brasal):
    - Light: Inadimplência elevada e perdas não técnicas de energia persistentes na área de concessão. [Light p.2]
    - Millet: Risco de crédito associado à inadimplência de clientes no recebimento de títulos e contas a receber. [Millet p.40]
    - Brasal: Risco de crédito decorrente da concessão de crédito aos clientes, mitigado por análises de perfil e monitoramento de saldos a receber. [Brasal p.49]
- **Custo de insumos / matérias-primas** — 3 empresas (Light, Millet, Brasal):
    - Light: Risco hidrológico e escassez de chuvas que podem afetar o volume dos reservatórios e elevar os custos de energia. [Light p.101]
    - Millet: Exposição a variações de preços e custos de matérias-primas e materiais de uso e consumo na fabricação. [Millet p.38]
    - Brasal: Risco de variação de preços de matérias-primas e insumos utilizados na fabricação dos produtos comercializados. [Brasal p.49]
- **Juros e risco de mercado** — 3 empresas (Light, Millet, Brasal):
    - Light: Elevado patamar das taxas de juros que encarece o custo da dívida e pressiona a estrutura de capital. [Light p.2]
    - Millet: Risco de taxa de juros decorrente da flutuação nas taxas incidentes sobre passivos captados e ativos aplicados. [Millet p.41]
    - Brasal: Risco de oscilação das taxas de juros incidentes sobre ativos e passivos financeiros da Companhia. [Brasal p.49]
- **Contingências judiciais e tributárias** — 2 empresas (Light, Brasal):
    - Light: Elevado volume de contingências judiciais cíveis, trabalhistas e fiscais em aberto. [Light p.76]
    - Brasal: Risco de contingências judiciais e administrativas associadas a demandas cíveis, fiscais e trabalhistas avaliadas periodicamente com assessores… [Brasal p.20]
- **Liquidez e endividamento** — 2 empresas (Light, Millet):
    - Light: Nível elevado de endividamento financeiro e geração de caixa operacional insuficiente para honrar compromissos. [Light p.26]
    - Millet: Risco de liquidez referente a dificuldades potenciais para honrar passivos financeiros de curto e longo prazos. [Millet p.41]
- **Regulatório / fiscal / concessão** — 2 empresas (Light, Brasal):
    - Light: Riscos regulatórios associados à renovação da concessão da Light SESA que vence em 2026. [Light p.26]
    - Brasal: Risco regulatório e de incentivos fiscais, visto que a controlada possui incentivos do programa Emprega/DF condicionados ao cumprimento de… [Brasal p.12]
- Citados por **apenas uma** empresa: Continuidade operacional (Light); Concentração / dependência de contratos ou investida (Brasal).
*Metodologia: cada risco recebe uma categoria de uma taxonomia fixa; a pergunta é respondida pela interseção das categorias (código), não por um parecer livre. Para Millet e Brasal, a base são as notas explicativas (não há relatório da administração).*

<details><summary>Fontes (documento · página · trecho)</summary>

- **Light p.2** — “Ao mesmo tempo, as perdas não técnicas - aquelas relacionadas ao furto de energia - e a inadimplência continuam sua gradual trajetória de…”
- **Millet p.40** — “Risco de crédito é o risco de a Companhia incorrer em perdas decorrentes de um cliente ou de uma”
- **Brasal p.49** — “O principal fator de risco de mercado que afeta o negócio é a concessão de crédito aos clientes.”
- **Light p.101** — “Um período prolongado de escassez de chuva pode resultar na redução do volume de água dos reservatórios das usinas, acarretar perdas em f…”
- **Millet p.38** — “Matéria-prima e materiais de uso e consumo - (327.291) (140.326)”
- **Brasal p.49** — “Os produtos comercializados pela Companhia estão sujeitos a oscilações em razão da compra de matéria-prima.”
- **Light p.2** — “E as taxas de juros no Brasil voltaram para um patamar muito alto; a expectativa é que permaneçam nesse patamar.”
- **Millet p.41** — “Risco de taxa de juros: é oriundo da possibilidade de a Companhia vir a sofrer perdas ou auferir ganhos”
- **Brasal p.49** — “Decorre da possibilidade de a Companhia sofrer ganhos ou perdas decorrentes de oscilações de taxas de juros incidentes sobre seus ativos …”
- **Light p.76** — “TOTAL 11.983.344 3.030 10.465.349 44.623”
- **Brasal p.20** — “As demandas judiciais são avaliadas e revisadas periodicamente, com base em pareceres de advogados internos e externos”
- **Light p.26** — “(i) elevado nível de endividamento; (ii) geração de caixa operacional historicamente insuficiente para sozinha honrar os compromissos;”
- **Millet p.41** — “Risco de liquidez é o risco em que a Companhia irá encontrar dificuldades em cumprir com as obrigações”
- **Light p.26** — “A concessão da controlada Light SESA, a distribuidora de energia elétrica do Grupo, vencerá em junho de 2026.”
- **Brasal p.12** — “No mês de setembro de 2020, migrou do então incentivo Fiscal IDEAS-DF para o Emprega/DF - Programa de Incentivo Fiscal à Industrialização”
- **Light p.3** — “Os eventos e condições, anteriormente mencionados, individual ou coletivamente, indicam, no julgamento da Administração da Companhia, a e…”
- **Brasal p.12** — “A Controlada mantém por prazo determinado contrato com a Coca-Cola Indústrias Ltda., com a Cervejaria Heineken e a Leão Alimentos e Bebid…”

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

⚠️ **6 falhas de ancoragem de 96 evidências** — os itens abaixo foram marcados como *não verificado* e NÃO entram nas conclusões:

- Light p.21 · `anomalia:LIGHT-A1[0]` · trecho não encontrado literalmente na página citada
- Light p.8 · `motivos[0]` · trecho não encontrado literalmente na página citada
- Light p.2 · `tom` · trecho não encontrado literalmente na página citada
- Millet p.10 · `fco.anterior` · valor 7424.0 não aparece no trecho citado
- Millet p.34 · `riscos[4]` · trecho não encontrado literalmente na página citada
- Millet p.33 · `eventos[1]` · trecho não encontrado literalmente na página citada

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
| Light | negativo | negativo | -0.71 | sim |
| Millet | positivo | negativo | -0.50 | não |
| Brasal | neutro | negativo | -0.75 | não |

_Leitura honesta:_ (1) coincidência por palavras do rótulo, heurística imperfeita; (2) linhas que mudam de sinal não têm razão logarítmica e ficam fora da pontuação. Um classificador de tom **supervisionado não foi treinado**: com 3 documentos não há corpus rotulado, e o léxico (n = 3) é só um sanity-check — não prova nada. O detector estatístico acerta números atípicos que as regras não procuram, mas gera ruído e não distingue efeito contábil legítimo de erro; as regras e a leitura do texto dão o *porquê*. A comparação com o **LLM** só é possível rodando `--mode llm` (veja o README).

## Anexo C — Metodologia desta execução

- **Modo de extração:** `llm` (LLM com saída estruturada; cada valor passa por grounding)
- **Documentos** (SHA-256 abreviado · páginas · tempo de ingestão):
    - Light: `light.pdf` · `a87339d09747` · 124 págs · 28.57s (pdftotext)
    - Millet: `millet.pdf` · `42589e4b7ad3` · 43 págs · 7.49s (pdftotext)
    - Brasal: `brasal.pdf` · `5905cd3412e4` · 51 págs · 4.75s (pdftotext)
- **LLM:** gemini/gemini-3.5-flash-lite · 6 chamadas · 104,064 tokens de entrada · 13,965 de saída · 15.0s · custo estimado US$ 0.066 (preços configuráveis em .env).
- **Convenção de páginas:** posição física no PDF (1 = capa); pode diferir do número impresso no rodapé.
- **Premissa de escopo:** os PDFs são demonstrações financeiras **anuais de 2022** (não releases trimestrais). 'Período de referência' = exercício 2022 vs 2021.
