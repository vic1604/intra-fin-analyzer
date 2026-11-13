"""Gera a EXTRAÇÃO DE REFERÊNCIA (curada) em data/reference/.

O que é isto?
  Um conjunto de valores esperados, lidos por humano+IA diretamente dos PDFs, com
  página e trecho. Serve a dois propósitos:
    1. modo `--mode reference` do pipeline: roda o pipeline inteiro (grounding,
       validação, Q&A, relatório) SEM chave de API, de forma 100% reproduzível;
    2. "gabarito" do conjunto de avaliação: `python -m finanalyzer eval` compara
       a extração por LLM (ou o baseline de regras) contra estes valores.

Como evita erro de transcrição?
  Os trechos NÃO são digitados: este script os recorta do texto real do PDF
  (`grab`) por regex de linha e checa por código que o número está no trecho
  (`val`). Se alguma linha não existir, o script quebra.

Uso:  python scripts/build_reference.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from finanalyzer.config import KNOWN_DOCS, get_settings  # noqa: E402
from finanalyzer.ingest import load_or_ingest  # noqa: E402
from finanalyzer.schema import Extracao, Qualitativo  # noqa: E402
from finanalyzer.text_utils import normalize_text, number_in_text  # noqa: E402

S = get_settings()
DOCS = {d: load_or_ingest(S.input_dir / f"{d}.pdf", S.cache_dir) for d in KNOWN_DOCS}


# ------------------------------------------------------------- helpers ----
def grab(doc: str, page: int, pattern: str, lines: int = 1, nth: int = 1) -> str:
    """Recorta (normalizado) `lines` linhas a partir da `nth` linha da página que casa `pattern`."""
    rows = DOCS[doc].page(page).text.split("\n")
    seen = 0
    for i, row in enumerate(rows):
        if re.search(pattern, row):
            seen += 1
            if seen == nth:
                return normalize_text(" ".join(rows[i : i + lines]))
    raise ValueError(f"[{doc} p{page}] padrão não encontrado: {pattern!r} (nth={nth})")


def ev(doc, page, pattern, lines=1, nth=1):
    return {"documento": doc, "pagina": page, "trecho": grab(doc, page, pattern, lines, nth)}


def val(doc, page, pattern, value, escala="mil", unidade="R$", rotulo=None, lines=1, nth=1):
    e = ev(doc, page, pattern, lines, nth)
    assert number_in_text(value, e["trecho"]), f"[{doc} p{page}] {value} não está em: {e['trecho']}"
    return {"valor": value, "escala": escala, "unidade": unidade, "rotulo": rotulo, "evidencia": e}


def M(atual=None, anterior=None, **kw):
    return {"status": "encontrado", "atual": atual, "anterior": anterior, **kw}


def NF(motivo, termos=(), **kw):
    return {"status": "nao_encontrado", "motivo_ausencia": motivo, "termos_verificados": list(termos), **kw}


# =============================================================== LIGHT =====
def light() -> dict:
    d = "light"
    return dict(
        doc_id=d,
        empresa="Light S.A. (consolidado)",
        periodo_referencia="Exercício de 2022 (findo em 31/12/2022); comparativo: 2021",
        tipo_documento="Relatório da Administração + DFs anuais auditadas (Deloitte). Não é release trimestral.",
        moeda_escala_declarada="DFs em R$ mil; Relatório da Administração em R$ milhões",
        receita_liquida=M(
            val(d, 20, r"^\s*RECEITA LÍQUIDA\s+31", 13253286),
            val(d, 20, r"^\s*RECEITA LÍQUIDA\s+31", 14897920),
            observacao="Receita líquida consolidada da DRE (inclui receita de construção). O texto da administração usa a receita SEM construção (ver campo próprio).",
        ),
        receita_liquida_ex_construcao=M(
            val(d, 9, r"desconsiderando a receita de construção", 12107, "milhoes", lines=2),
            None,
            variacao_reportada_pct=val(d, 9, r"desconsiderando a receita de construção", -13, "milhoes", "%", lines=2),
            observacao="Base usada pela administração no texto (R$ milhões, -13%).",
        ),
        receita_construcao=M(
            val(d, 93, r"^\s*Receita de construção", 1146446),
            val(d, 93, r"^\s*Receita de construção", 967268),
            observacao="Nota 31; usada para verificar o -13% da administração.",
        ),
        ebitda=M(
            val(d, 9, r"o EBITDA CVM foi de R\$1\.180", 1180, "milhoes", rotulo="EBITDA CVM consolidado (como impresso no texto)"),
            None,
            variacao_reportada_abs=val(d, 9, r"o EBITDA CVM foi de R\$1\.180", -3001, "milhoes", rotulo="redução reportada"),
            observacao="Texto imprime R$1.180 milhões SEM sinal. A recomposição pelas DFs (EBIT + D&A) dá valor NEGATIVO — ver alertas.",
        ),
        margem_ebitda=NF("O Relatório da Administração e as DFs não informam margem EBITDA.", ["margem ebitda", "margem do ebitda"]),
        lucro_liquido=M(
            val(d, 20, r"LUCRO \(PREJUÍZO\) LÍQUIDO DO EXERCÍCIO", -5672203),
            val(d, 20, r"LUCRO \(PREJUÍZO\) LÍQUIDO DO EXERCÍCIO", 397945),
            variacao_reportada_abs=val(d, 10, r"apurou um resultado líquido de", -6070, "milhoes", rotulo="queda reportada pela administração"),
            alternativas=[val(d, 10, r"apurou um resultado líquido de", -5673, "milhoes", rotulo="resultado líquido segundo o texto da administração")],
        ),
        divida_liquida=M(
            val(d, 105, r"^\s*Dívida líquida \(A\)", 9032236),
            val(d, 105, r"^\s*Dívida líquida \(A\)", 7352919),
            variacao_reportada_pct=val(d, 10, r"aumento de 23% em comparação", 23, "milhoes", "%"),
            alternativas=[val(d, 10, r"^A dívida líquida da Companhia em 31", 9032, "milhoes", rotulo="dívida líquida segundo o texto da administração")],
        ),
        alavancagem=M(
            val(d, 10, r"2021 em 3,32x", 3.32, "unidade", "x", rotulo="Dívida líquida / EBITDA ajustado p/ covenants"),
            val(d, 10, r"2021 em 3,32x", 3.48, "unidade", "x"),
            observacao="Indicador de covenants (EBITDA ajustado, exclui efeitos não caixa). O texto diz 'encerrou 2021 em 3,32x … (3,48x)' — o ano está trocado; interpretado como 2022 vs 2021.",
        ),
        fco=M(
            val(d, 23, r"Caixa líquido gerado \(aplicado\) pelas atividades operacionais", 200763),
            val(d, 23, r"Caixa líquido gerado \(aplicado\) pelas atividades operacionais", -42045),
        ),
        capex=M(
            val(d, 10, r"O valor total de investimentos no ano de 2022", 1506, "milhoes", rotulo="investimentos totais (visão da administração)"),
            None,
            variacao_reportada_pct=val(d, 10, r"O valor total de investimentos no ano de 2022", 6, "milhoes", "%"),
            complementares=[
                val(d, 23, r"Aquisições de bens do ativo imobilizado", 307759, rotulo="capex_componente: imobilizado (caixa)"),
                val(d, 23, r"Aquisições de bens do ativo intangível e do ativo de contrato", 1162533, rotulo="capex_componente: intangível e ativo de contrato (caixa)"),
            ],
            observacao="Administração reporta 'investimentos' (R$1.506 mi, base competência). Capex de caixa = soma dos dois componentes do fluxo de caixa.",
        ),
        ebit=M(
            val(d, 20, r"LUCRO \(PREJUÍZO\) ANTES DO RESULTADO FINANCEIRO E IMPOSTOS", -1910411),
            val(d, 20, r"LUCRO \(PREJUÍZO\) ANTES DO RESULTADO FINANCEIRO E IMPOSTOS", 1143301),
        ),
        depreciacao_amortizacao=M(
            val(d, 23, r"^\s*Depreciação e amortização\s+32", 730767),
            val(d, 23, r"^\s*Depreciação e amortização\s+32", 678110),
        ),
        caixa_equivalentes=M(
            val(d, 105, r"\(-\) Caixa e equivalentes de caixa e TVM", 2083551, rotulo="Caixa e equivalentes + TVM"),
            val(d, 105, r"\(-\) Caixa e equivalentes de caixa e TVM", 3604973),
        ),
        aplicacoes_financeiras=NF("Incluídas na linha 'Caixa e equivalentes de caixa e TVM' da nota 34.3."),
        divida_bruta=M(
            val(d, 105, r"^\s*Dívida bruta", 11115787),
            val(d, 105, r"^\s*Dívida bruta", 10957892),
        ),
        anomalias_documento=[
            dict(
                id="LIGHT-A1",
                severidade="alta",
                descricao=(
                    "EBITDA CVM da distribuidora: o texto diz R$1.817 mi, 'redução de R$2.996 mi' em relação a R$1.179 mi em 2021. "
                    "Os números não fecham (1.817 − 1.179 = +638, não −2.996). 1.817 + 1.179 = 2.996 sugere que os anos estão invertidos "
                    "(2021 = +1.817; 2022 = −1.179) e o sinal negativo foi omitido."
                ),
                evidencias=[ev(d, 8, r"o EBITDA CVM1 da distribuidora", 2)],
            ),
            dict(
                id="LIGHT-A2",
                severidade="media",
                descricao="Alavancagem de covenants: o texto diz que o indicador 'encerrou 2021 em 3,32x, menor do que no 2021 (3,48x)' — período repetido; o correto seria 2022 vs 2021.",
                evidencias=[ev(d, 10, r"O indicador de covenants Dívida Líquida/EBITDA", 2)],
            ),
            dict(
                id="LIGHT-A3",
                severidade="alta",
                descricao="Auditor (Deloitte) chama a atenção para incerteza significativa sobre a continuidade operacional (nota 1.1).",
                evidencias=[ev(d, 111, r"Incerteza significativa relacionada com a continuidade")],
            ),
        ],
    )


# ============================================================== MILLET =====
def millet() -> dict:
    d = "millet"
    return dict(
        doc_id=d,
        empresa="Millet Participações S.A. (consolidado; controla 85% da Alibra)",
        periodo_referencia="Exercício de 2022 (findo em 31/12/2022); comparativo: 2021",
        tipo_documento="DFs anuais auditadas + notas explicativas. Não há Relatório da Administração nem release.",
        moeda_escala_declarada="R$ mil",
        receita_liquida=M(
            val(d, 7, r"^\s*Receita operacional líquida\s+18", 462127),
            val(d, 7, r"^\s*Receita operacional líquida\s+18", 199259),
            complementares=[
                val(d, 29, r"^\s*Receita operacional líquida\s+462\.127", 318317, rotulo="pro_forma_anterior: receita da Alibra em 2021 (ano cheio, nota 7)"),
            ],
            observacao="2021 consolida a Alibra apenas a partir de 18/06/2021: a variação NÃO é comparável (ver alertas).",
        ),
        ebitda=NF("O documento não apresenta EBITDA/LAJIDA.", ["EBITDA", "LAJIDA"]),
        margem_ebitda=NF("Sem EBITDA no documento, não há margem EBITDA reportada.", ["margem ebitda", "margem do ebitda"]),
        lucro_liquido=M(
            val(d, 7, r"^\s*Lucro líquido do exercício\s+14\.743\s+5\.371\s+18\.891", 18891, rotulo="Lucro líquido consolidado (inclui minoritários)"),
            val(d, 7, r"^\s*Lucro líquido do exercício\s+14\.743\s+5\.371\s+18\.891", 6470),
            complementares=[
                val(d, 7, r"^\s*Lucro líquido do exercício\s+14\.743\s+5\.371\s+14\.743", 14743, rotulo="Lucro líquido atribuível aos controladores", nth=1),
            ],
        ),
        divida_liquida=M(
            val(d, 42, r"Dívida líquida \(a\)", 13520),
            val(d, 42, r"Dívida líquida \(a\)", 16877),
        ),
        alavancagem=NF(
            "Não há Dívida líquida/EBITDA. O documento traz apenas dívida líquida / capital ajustado (0,08x).",
            ["dívida líquida/ebitda", "divida liquida/ebitda"],
            complementares=[val(d, 42, r"Relação dívida liquida sobre capital ajustado", 0.08, "unidade", "x", rotulo="Dívida líquida / patrimônio (não é alavancagem sobre EBITDA)")],
        ),
        fco=M(
            val(d, 10, r"Caixa liquido gerado pelas \(consumido nas\)", 24799, lines=3),
            val(d, 10, r"Caixa liquido gerado pelas \(consumido nas\)", -14293, lines=3),
        ),
        capex=NF(
            "Não há linha única de capex; há duas linhas de aquisição (imobilizado e intangível).",
            complementares=[
                val(d, 10, r"Aquisição de imobilizado", 6263, rotulo="capex_componente: imobilizado"),
                val(d, 10, r"Aquisição de intangível", 11469, rotulo="capex_componente: intangível"),
            ],
        ),
        ebit=M(
            val(d, 7, r"^\s*Resultado antes do resultado\s*$", 25298, lines=3),
            val(d, 7, r"^\s*Resultado antes do resultado\s*$", 4482, lines=3),
        ),
        depreciacao_amortizacao=M(
            val(d, 10, r"^\s*Depreciação e amortização\s+13\.295", 18248),
            val(d, 10, r"^\s*Depreciação e amortização\s+13\.295", 2975),
        ),
        caixa_equivalentes=M(
            val(d, 6, r"^\s*Caixa e equivalente de caixa\s+3\s+355", 10656),
            val(d, 6, r"^\s*Caixa e equivalente de caixa\s+3\s+355", 8195),
        ),
        aplicacoes_financeiras=NF("Não há linha de aplicações financeiras no balanço consolidado."),
        divida_bruta=M(
            val(d, 42, r"Total dos empréstimos com terceiros", 24176),
            val(d, 42, r"Total dos empréstimos com terceiros", 25072),
        ),
        anomalias_documento=[
            dict(
                id="MILLET-A1",
                severidade="alta",
                descricao=(
                    "Comparabilidade da receita: a Alibra foi adquirida em 18/06/2021; a receita consolidada de 2021 (R$199.259 mil) reflete só parte do ano. "
                    "A própria nota 7 mostra a receita da Alibra em 2021 como R$318.317 mil (ano cheio) — a variação like-for-like seria ≈ +45%, não +132%."
                ),
                evidencias=[ev(d, 27, r"A Transação foi concluída em 18 de junho de 2021"), ev(d, 29, r"^\s*Receita operacional líquida\s+462\.127")],
            ),
            dict(
                id="MILLET-A2",
                severidade="media",
                descricao="Patrimônio líquido na nota 22.2 (R$167.233 mil) difere do balanço (R$163.931 mil de controladores; R$185.321 mil consolidado).",
                evidencias=[ev(d, 42, r"Total do patrimônio líquido \(b\)"), ev(d, 6, r"^\s*Patrimônio líquido\s+163\.931")],
            ),
            dict(
                id="MILLET-A3",
                severidade="baixa",
                descricao="Empréstimos em 31/12/2021: R$25.072 mil na nota 22.2 vs R$25.075 mil na nota 22.1/22.3 (e na soma do balanço).",
                evidencias=[ev(d, 42, r"Total dos empréstimos com terceiros"), ev(d, 41, r"Empréstimos e Financiamentos \(Taxas Pré-fixadas\)")],
            ),
            dict(
                id="MILLET-A4",
                severidade="media",
                descricao="Nota 2.2 diz que as DFs de 2022 foram aprovadas pela administração em 14/03/2022 (data anterior ao fim do exercício) — provável erro de digitação (2023).",
                evidencias=[ev(d, 12, r"foi aprovada e pela administração em 14 de março de 2022")],
            ),
            dict(
                id="MILLET-A5",
                severidade="media",
                descricao="Nota 7 (investida Alibra): 'Lucro antes dos impostos' 2022 aparece como (65.750), mas lucro bruto − despesas − resultado financeiro = 98.338 − 63.419 − 2.331 = 32.588 (e 32.588 − 4.070 = 28.518, o lucro líquido informado).",
                evidencias=[ev(d, 29, r"^\s*Lucro antes dos impostos")],
            ),
        ],
    )


# ============================================================== BRASAL =====
def brasal() -> dict:
    d = "brasal"
    return dict(
        doc_id=d,
        empresa="Brasal Brasília Holding S.A. (consolidado; controla a Brasal Refrigerantes – Coca-Cola/Heineken)",
        periodo_referencia="Exercício de 2022 (findo em 31/12/2022); comparativo 2021 NÃO AUDITADO",
        tipo_documento="DFs anuais auditadas (EY) + notas explicativas. Não há Relatório da Administração nem release.",
        moeda_escala_declarada="R$ mil",
        receita_liquida=M(
            val(d, 8, r"^\s*Receita operacional líquida\s+21", 1325059),
            val(d, 8, r"^\s*Receita operacional líquida\s+21", 1061410),
            observacao="Coluna 2021 marcada '(não auditado)'.",
        ),
        ebitda=NF("O documento não apresenta EBITDA/LAJIDA.", ["EBITDA", "LAJIDA"]),
        margem_ebitda=NF("Sem EBITDA no documento, não há margem EBITDA reportada.", ["margem ebitda", "margem do ebitda"]),
        lucro_liquido=M(
            val(d, 8, r"^\s*Lucro líquido do exercício\s+174\.602", 174602),
            val(d, 8, r"^\s*Lucro líquido do exercício\s+174\.602", 275560),
        ),
        divida_liquida=NF("O documento não apresenta 'dívida líquida'.", ["dívida líquida", "divida liquida"]),
        alavancagem=NF("O documento não apresenta Dívida líquida/EBITDA nem outra medida de alavancagem numérica.", ["dívida líquida/ebitda"]),
        fco=M(
            val(d, 11, r"Caixa líquido gerado pelas atividades operacionais", 258248),
            val(d, 11, r"Caixa líquido gerado pelas atividades operacionais", 121462),
        ),
        capex=M(
            val(d, 11, r"^\s*Imobilizado e intangível", 45761, rotulo="Aquisição de imobilizado e intangível (caixa)"),
            val(d, 11, r"^\s*Imobilizado e intangível", 53388),
        ),
        ebit=M(
            val(d, 8, r"^Lucro operacional antes das receitas e despesas", 192840, lines=3),
            val(d, 8, r"^Lucro operacional antes das receitas e despesas", 238224, lines=3),
        ),
        depreciacao_amortizacao=M(
            val(d, 11, r"^\s*Depreciações e amortizações\s+507", 29014),
            val(d, 11, r"^\s*Depreciações e amortizações\s+507", 22837),
        ),
        caixa_equivalentes=M(
            val(d, 6, r"^Caixa e equivalentes de caixa\s+4", 96453),
            val(d, 6, r"^Caixa e equivalentes de caixa\s+4", 62166),
        ),
        aplicacoes_financeiras=M(
            val(d, 6, r"^Aplicações financeiras\s+5", 78569),
            val(d, 6, r"^Aplicações financeiras\s+5", 95766),
        ),
        divida_bruta=M(
            val(d, 48, r"^\s*Empréstimos e financiamentos\s+-\s+-\s+3\.417", 3417),
            val(d, 48, r"^\s*Empréstimos e financiamentos\s+226\s+226\s+6\.478", 6478),
        ),
        anomalias_documento=[
            dict(
                id="BRASAL-A1",
                severidade="alta",
                descricao="Os valores comparativos de 2021 (DRE, balanço, fluxo de caixa) estão marcados como 'não auditado' e o auditor declara não os ter auditado — variações vs 2021 têm menor confiabilidade.",
                evidencias=[ev(d, 3, r"não foram auditadas por nós"), ev(d, 8, r"^Receita operacional líquida\s+21|\(não auditado\)")],
            ),
            dict(
                id="BRASAL-A2",
                severidade="alta",
                descricao="Comparabilidade do resultado: 2021 inclui R$105.633 mil de 'créditos extemporâneos' (exclusão do ICMS da base do PIS/COFINS) em outras receitas operacionais, vs R$231 mil em 2022 — não recorrente que distorce a variação do lucro.",
                evidencias=[ev(d, 46, r"Créditos extemporâneos")],
            ),
            dict(
                id="BRASAL-A3",
                severidade="media",
                descricao="Nota 20: o capital social é descrito como dividido em 3.256.699 ações e, no parágrafo seguinte, em 1.374.240 ações.",
                evidencias=[ev(d, 42, r"divididos em 3\.256\.699"), ev(d, 42, r"1\.374\.240 ações")],
            ),
            dict(
                id="BRASAL-A4",
                severidade="media",
                descricao="Nota 24 (IR/CS): o 'resultado contábil antes da tributação' (IRPJ 54.297; CSLL 19.547) não bate com o lucro antes do IR da DRE (R$217.187 mil).",
                evidencias=[ev(d, 47, r"Resultado contábil antes da", 3), ev(d, 8, r"^Lucro antes do imposto de renda e da contribuição social\s+174\.602")],
            ),
            dict(
                id="BRASAL-A5",
                severidade="baixa",
                descricao="Depreciação e amortização: R$20.347 mil na DRE (linha de despesa) vs R$29.014 mil no fluxo de caixa (total, inclui parcela no custo). Usamos o do fluxo de caixa no EBITDA derivado.",
                evidencias=[ev(d, 8, r"Depreciações e amortizações\s+23\.d"), ev(d, 11, r"^\s*Depreciações e amortizações\s+507")],
            ),
            dict(
                id="BRASAL-A6",
                severidade="baixa",
                descricao="Nota 3.3: rubrica 'Custos dos imóveis vendidos' (a empresa é industrial/distribuidora de bebidas) e números com ';' em vez de '.' (1;061;410) — erros de digitação no documento.",
                evidencias=[ev(d, 25, r"Custos dos imóveis vendidos")],
            ),
        ],
    )


def build_extracoes() -> dict[str, dict]:
    return {"light": light(), "millet": millet(), "brasal": brasal()}


# =============================================================== QUALITATIVO
def I(texto, evidencias, categoria=None):
    return {"texto": texto, "evidencias": evidencias, "categoria": categoria}


def q_light() -> dict:
    d = "light"
    return dict(
        doc_id=d,
        empresa="Light S.A.",
        fonte_qualitativa="Relatório da Administração (págs. 2-14) + notas explicativas",
        nota_cobertura="Único dos três documentos com comentário da administração. Não traz guidance numérico.",
        motivos_resultado=[
            I(
                "Provisões de R$2.513 mi no período explicam a queda do EBITDA: devolução de créditos de PIS/COFINS aos consumidores (Lei 14.385/22; −R$1.081 mi), revisão de PECLD (−R$855 mi) e contingências JEC e Cível (−R$379 mi).",
                [ev(d, 10, r"para devolução de créditos de PIS/COFINS aos consumidores, conforme Lei", 3)],
            ),
            I(
                "Prejuízo líquido de R$5,7 bi: além da provisão do PIS/COFINS, houve atualização financeira desses valores (−R$1.584 mi) e impairment do IR/CS diferido (−R$1.634 mi).",
                [ev(d, 10, r"Essa retração ocorreu, principalmente, no segmento", 3)],
            ),
            I(
                "Juros mais altos: a Selic subiu de 2,00% (jan/2021) para 13,75% (ago/2022), agravando o desequilíbrio de capital.",
                [ev(d, 26, r"aumento das taxas de juros SELIC")],
            ),
        ],
        motivo_variacao_receita=I(
            "Receita líquida (ex-construção) −13%: estornos de faturamento de regularizações, não acionamento das bandeiras tarifárias e variação negativa da CVA.",
            [ev(d, 9, r"Essa redução foi influenciada pelos", 3)],
        ),
        riscos=[
            I(
                "Incerteza significativa sobre a continuidade operacional do Grupo Light e da Light SESA (reconhecida pela administração e destacada pelo auditor).",
                [ev(d, 28, r"Administração da Companhia, a existência de incerteza", 2)],
                "continuidade_operacional",
            ),
            I(
                "A concessão da Light SESA vence em junho de 2026; a renovação depende de processo formal e de negociação fora do controle da companhia.",
                [ev(d, 26, r"A concessão da controlada Light SESA", 2)],
                "regulatorio_concessao",
            ),
            I(
                "Análise preliminar indica risco de descumprimento dos indicadores de sustentabilidade econômico-financeira exigidos pela ANEEL para 2022.",
                [ev(d, 27, r"análise preliminar indica um risco")],
                "regulatorio_concessao",
            ),
            I(
                "Sem linhas de crédito contratadas e disponíveis em 31/12/2022 e rebaixamentos de rating; cláusula de rating abaixo de BBB- pode causar vencimento antecipado cruzado das dívidas.",
                [ev(d, 26, r"não possui linhas de créditos contratadas", 2), ev(d, 27, r"Com relação ao covenant não financeiro relacionado a ratings", 3)],
                "liquidez_endividamento",
            ),
            I(
                "Elevado índice de perdas não técnicas (furto de energia) e inadimplência.",
                [ev(d, 26, r"elevado índice de perdas não técnicas")],
                "credito_inadimplencia",
            ),
            I(
                "Devolução de cerca de R$2,8 bi de créditos de PIS/COFINS (exclusão do ICMS da base) aos consumidores e contingências JEC/Cível provisionadas.",
                [ev(d, 26, r"efeito da determinação de devolução de cerca de R\$2.8 bilhões", 2)],
                "contingencias_judiciais",
            ),
            I(
                "Juros elevados: a Selic foi de 2,00% para 13,75% no período, pressionando despesa financeira e endividamento.",
                [ev(d, 26, r"aumento das taxas de juros SELIC")],
                "juros_mercado",
            ),
        ],
        guidance=[
            I(
                "Perspectiva qualitativa: concentrar investimentos no estritamente necessário até a renovação da concessão, para maximizar o fluxo de caixa nos próximos 36 meses.",
                [ev(d, 3, r"Concentramos nossos investimentos", 3)],
            ),
            I(
                "Objetivo de antecipar a renovação da concessão da Light SESA (vence em 2026), em bases sustentáveis.",
                [ev(d, 2, r"Essas alternativas passam pela renovação", 2)],
            ),
            I(
                "Reajuste tarifário médio de 7,0% aprovado pela ANEEL em 15/03/2023 (evento subsequente) e pleitos sobre perdas não técnicas em análise.",
                [ev(d, 107, r"O resultado representa um reajuste tarifário médio")],
            ),
        ],
        guidance_numerico_encontrado=False,
        eventos_relevantes=[
            I("Lei 14.385/22 (27/06/2022) obriga o repasse aos consumidores dos créditos tributários de PIS/COFINS sobre ICMS.", [ev(d, 28, r"1\.2 Promulgação da Lei")]),
            I("Revisão tarifária periódica de 2022: reajuste médio de 14,68% nas contas de energia.", [ev(d, 4, r"O efeito conjunto desse processo", 2)]),
            I("Troca de liderança: novo CEO assumiu em agosto de 2022 e a companhia intensificou a reestruturação interna.", [ev(d, 2, r"Assumi, em agosto de 2022"), ev(d, 3, r"intensificamos o processo de reestruturação")]),
            I("Rebaixamentos de rating em fev/2023 (Fitch CCC(bra)/CCC+; Moody's B.br/B3; S&P brBB-).", [ev(d, 26, r"^\s*Fitch\s+CCC")]),
            I("Compra dos 49% da CEMIG na Axxiom por R$1,00 (contrato de 21/12/2022; aprovado pelo CADE em 25/01/2023).", [ev(d, 107, r"Em 21 de dezembro de 2022, a Light S\.A\. assinou", 2)]),
        ],
        tom="negativo",
        tom_justificativa=(
            "Prejuízo de R$5,7 bi, EBITDA CVM negativo, alavancagem de covenants de 3,32x, ratings na faixa CCC/B3, ausência de linhas de crédito disponíveis "
            "e parágrafo de incerteza significativa sobre continuidade no relatório do auditor. A mensagem do CEO usa linguagem de 'turnaround' e destaca os "
            "melhores DEC/FEC em 20 anos, mas os fatos relatados são predominantemente adversos."
        ),
        tom_evidencias=[ev(d, 2, r"o desequilíbrio que já existia", 2), ev(d, 111, r"Incerteza significativa relacionada com a continuidade")],
        confianca_tom="alta",
    )


def q_millet() -> dict:
    d = "millet"
    return dict(
        doc_id=d,
        empresa="Millet Participações S.A.",
        fonte_qualitativa="Apenas notas explicativas (não há relatório da administração)",
        nota_cobertura="Sem comentário de desempenho da administração: motivos/tom derivam de notas (1.1, 7, 22) e são evidência documental, não discurso gerencial.",
        motivos_resultado=[
            I(
                "Nota 1.1: a performance de vendas 'atendeu às projeções', mesmo com demanda mais fraca que o previsto.",
                [ev(d, 11, r"performance das vendas atendeu", 2)],
            ),
            I(
                "Custo de matérias-primas (derivados lácteos) continuou subindo, com repasse ao preço; a margem não voltou ao nível pré-pandemia.",
                [ev(d, 11, r"Como ponto residual e contínuo de 2020", 4)],
            ),
            I(
                "Amortização da mais-valia da aquisição da Alibra (R$13.295 mil) pressionou o resultado consolidado.",
                [ev(d, 7, r"Amortização da Mais-Valia")],
            ),
        ],
        motivo_variacao_receita=I(
            "[Evidência documental — não é afirmação da administração] A Alibra foi adquirida em 18/06/2021, então a receita consolidada de 2021 cobre só parte do ano; a receita da Alibra em 2021 (ano cheio) foi R$318.317 mil.",
            [ev(d, 27, r"A Transação foi concluída em 18 de junho de 2021"), ev(d, 29, r"^\s*Receita operacional líquida\s+462\.127")],
        ),
        riscos=[
            I(
                "Aumento do custo de matérias-primas (derivados lácteos) e dificuldade de recuperar margem.",
                [ev(d, 11, r"Como ponto residual e contínuo de 2020", 4)],
                "custo_insumos",
            ),
            I(
                "Risco de crédito: perdas por falha de clientes em cumprir obrigações (contas a receber de R$98,7 mi).",
                [ev(d, 40, r"Risco de crédito é o risco de a Companhia", 2), ev(d, 40, r"Contas a receber de clientes\s+-\s+-\s+98\.663")],
                "credito_inadimplencia",
            ),
            I(
                "Risco de liquidez: dificuldade em cumprir obrigações financeiras; R$18,1 mi de empréstimos vencem em até 12 meses vs caixa de R$10,7 mi.",
                [ev(d, 41, r"Risco de liquidez é o risco em que", 2), ev(d, 41, r"Empréstimos e Financiamentos\s+24\.176\s+24\.176")],
                "liquidez_endividamento",
            ),
            I(
                "Risco de taxa de juros e de câmbio (dívida a taxas pré-fixadas).",
                [ev(d, 41, r"Risco de taxa de juros:", 2)],
                "juros_mercado",
            ),
            I(
                "Contingências trabalhistas e previdenciárias provisionadas (R$3.284 mil).",
                [ev(d, 36, r"^\s*Trabalhistas\s+722", 3)],
                "contingencias_judiciais",
            ),
            I(
                "Dependência de uma única investida: a holding consolida somente a Alibra (85%).",
                [ev(d, 12, r"^Alibra Ingredientes S\.A\.")],
                "concentracao_dependencia",
            ),
        ],
        guidance=[
            I(
                "Intenção qualitativa: acumular recursos e reservas para investimentos projetados e para o capital de giro necessário nos próximos anos.",
                [ev(d, 42, r"acumulando recursos e reservas de lucros", 3)],
            )
        ],
        guidance_numerico_encontrado=False,
        eventos_relevantes=[
            I("Aquisição de 85% da Alibra Ingredientes em junho de 2021 por R$179.350 mil (parte a prazo).", [ev(d, 27, r"adquiriu 85% de participação na Alibra", 2)]),
            I("Laudo da KPMG (jun/2022) alocou o preço de compra: mais-valia amortizada linearmente (R$13.295 mil em 2022).", [ev(d, 27, r"Em junho de 2022, foi emitido pela KPMG", 2), ev(d, 28, r"Amortização da Mais-Valia\s+-")]),
            I("Revisão de crédito tributário de ação ajuizada em 2009 (abr/2022): créditos reduzidos.", [ev(d, 36, r"Em 04 de abril de 2022, a Companhia revisou", 2)]),
            I("Nenhum evento subsequente exigindo divulgação.", [ev(d, 43, r"não ocorreram eventos que necessitam de divulgação")]),
        ],
        tom="neutro",
        tom_justificativa=(
            "Sem discurso gerencial. As notas combinam um sinal positivo (vendas 'atenderam às projeções') com ressalvas (demanda mais fraca, custo de lácteos, "
            "margem abaixo do pré-pandemia). Não há juízo de valor consolidado — classificação neutra com baixa confiança."
        ),
        tom_evidencias=[ev(d, 11, r"performance das vendas atendeu", 4)],
        confianca_tom="baixa",
    )


def q_brasal() -> dict:
    d = "brasal"
    return dict(
        doc_id=d,
        empresa="Brasal Brasília Holding S.A.",
        fonte_qualitativa="Apenas notas explicativas (não há relatório da administração)",
        nota_cobertura="Sem comentário de desempenho da administração e sem explicação para a variação da receita. Os 'motivos' abaixo são evidência extraída das DFs, não afirmação gerencial.",
        motivos_resultado=[
            I(
                "[Evidência documental] O lucro líquido caiu em 2022 em parte porque 2021 incluía R$105.633 mil de créditos extemporâneos (exclusão do ICMS da base do PIS/COFINS) em outras receitas operacionais.",
                [ev(d, 46, r"Créditos extemporâneos")],
            ),
            I(
                "[Evidência documental] As receitas financeiras recuaram de R$116.653 mil (2021) para R$29.541 mil (2022).",
                [ev(d, 8, r"^\s*Receitas financeiras\s+23\.f")],
            ),
        ],
        motivo_variacao_receita=None,
        riscos=[
            I(
                "Crédito concedido a clientes é apontado como o principal fator de risco de mercado.",
                [ev(d, 49, r"O principal fator de risco de mercado", 2)],
                "credito_inadimplencia",
            ),
            I(
                "Oscilação de preços dos produtos em razão da compra de matéria-prima (commodities).",
                [ev(d, 49, r"Os produtos comercializados pela Companhia estão sujeitos", 2)],
                "custo_insumos",
            ),
            I(
                "Oscilação de taxas de juros incidentes sobre ativos e passivos financeiros (CDI).",
                [ev(d, 49, r"Decorre da possibilidade de a Companhia sofrer ganhos", 2)],
                "juros_mercado",
            ),
            I(
                "Contratos por prazo determinado com Coca-Cola, Heineken e Leão: dependência de marcas licenciadas.",
                [ev(d, 12, r"A Controlada mantém por prazo determinado contrato", 2)],
                "concentracao_dependencia",
            ),
            I(
                "Incentivo fiscal Emprega/DF (crédito presumido de 67% do ICMS) condicionado a manutenção de empregos, regularidade fiscal e contrapartidas.",
                [ev(d, 12, r"Neste programa é concedido um percentual de crédito presumido", 3)],
                "regulatorio_concessao",
            ),
            I(
                "Ações judiciais de risco possível (52 trabalhistas, 9 cíveis e fiscais — IPI, PIS) não provisionadas; STF (fev/2023) limitou a 'coisa julgada' em tributos recorrentes (sem impacto identificado).",
                [ev(d, 41, r"Existem atualmente 52", 2), ev(d, 51, r"Em decisão tomada no dia 08 de fevereiro 2023", 2)],
                "contingencias_judiciais",
            ),
            I(
                "Comparativos de 2021 não auditados.",
                [ev(d, 3, r"não foram auditadas por nós")],
                "qualidade_informacao",
            ),
        ],
        guidance=[],
        guidance_numerico_encontrado=False,
        eventos_relevantes=[
            I("Aumento de capital de R$60.000 mil por capitalização de reservas (28/03/2022), sem emissão de ações.", [ev(d, 42, r"Em 28 de março de 2022, através de assembleia", 3)]),
            I("Dividendos intermediários de R$206.000 mil em 2022 (a partir de reservas de lucros).", [ev(d, 10, r"^\s*Dividendos intermediários")]),
            I("Incentivo fiscal: R$103.940 mil reconhecidos em 2022 como reserva de incentivos fiscais.", [ev(d, 12, r"Em 2022 foi reconhecido o total de R\$103\.940", 2)]),
            I("Evento subsequente: decisão do STF (08/02/2023) sobre perda de efeitos da coisa julgada em tributos de trato continuado; administração não identificou impacto.", [ev(d, 51, r"Em decisão tomada no dia 08 de fevereiro 2023", 2)]),
        ],
        tom="neutro",
        tom_justificativa=(
            "Sem discurso gerencial. As DFs mostram receita +24,8% e caixa líquido positivo, mas lucro −36,6% (2021 tinha ganhos não recorrentes) e comparativos não auditados; "
            "a linguagem das notas é técnica e descritiva — classificação neutra com baixa confiança."
        ),
        tom_evidencias=[ev(d, 51, r"não identificou$", 2)],
        confianca_tom="baixa",
    )


def main() -> None:
    out_e = S.reference_dir / "extracao"
    out_q = S.reference_dir / "qualitativo"
    out_e.mkdir(parents=True, exist_ok=True)
    out_q.mkdir(parents=True, exist_ok=True)
    for doc_id, data in build_extracoes().items():
        ext = Extracao.model_validate({**data, "modo": "reference"})
        (out_e / f"{doc_id}.json").write_text(ext.model_dump_json(indent=2, exclude_none=True), encoding="utf-8")
    for doc_id, fn in {"light": q_light, "millet": q_millet, "brasal": q_brasal}.items():
        q = Qualitativo.model_validate({**fn(), "modo": "reference"})
        (out_q / f"{doc_id}.json").write_text(q.model_dump_json(indent=2, exclude_none=True), encoding="utf-8")
    print("referência gerada em", S.reference_dir)


if __name__ == "__main__":
    main()
