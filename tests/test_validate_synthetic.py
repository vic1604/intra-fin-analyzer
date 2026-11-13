"""Validações C01–C10 exercitadas com dados SINTÉTICOS.

Por quê: nos 3 PDFs reais nem toda checagem dispara (ex.: nenhum dos três
publica margem EBITDA). Estes testes provam que cada regra *alerta* quando a
inconsistência existe e fica *ok* quando não existe — ou seja, que as regras
funcionam, e não apenas que "não deu erro nos dados que tínhamos".
"""

from __future__ import annotations

from finanalyzer.schema import Evidencia, Extracao, Metrica, Valor
from finanalyzer.validate import validate_extraction


def _ev(pg: int = 1) -> Evidencia:
    return Evidencia(documento="sintetico.pdf", pagina=pg, trecho="trecho sintético")


def V(x: float, escala="mil", unidade="R$", pg: int = 1) -> Valor:
    return Valor(valor=x, escala=escala, unidade=unidade, evidencia=_ev(pg))


def M(atual=None, anterior=None, **kw) -> Metrica:
    if atual is None and anterior is None and not kw:
        return Metrica(status="nao_encontrado", motivo_ausencia="sintético")
    v = kw.pop("v", {})
    return Metrica(
        atual=None if atual is None else V(atual, **v),
        anterior=None if anterior is None else V(anterior, **v),
        **kw,
    )


def ext(**campos) -> Extracao:
    base = dict(
        doc_id="sint", empresa="Sintética S.A.", periodo_referencia="FY2022", tipo_documento="DF",
        moeda_escala_declarada="R$ mil",
        receita_liquida=M(1000, 800), ebitda=M(), margem_ebitda=M(), lucro_liquido=M(100, 80),
        divida_liquida=M(), alavancagem=M(), fco=M(), capex=M(),
        ebit=M(), depreciacao_amortizacao=M(), caixa_equivalentes=M(), aplicacoes_financeiras=M(),
        divida_bruta=M(),
    )
    base.update(campos)
    return Extracao(**base)


def _checks(e: Extracao, cid: str):
    checks, _ = validate_extraction(e)
    return [c for c in checks if c.id == cid]


# ------------------------------------------------------------------ C01 ----
def test_c01_variacao_pct_confere():
    e = ext(receita_liquida=M(1000, 800, variacao_reportada_pct=V(25.0, unidade="%")))
    (c,) = _checks(e, "C01")
    assert c.status == "ok"


def test_c01_variacao_pct_divergente_gera_alerta():
    e = ext(receita_liquida=M(1000, 800, variacao_reportada_pct=V(40.0, unidade="%")))
    (c,) = _checks(e, "C01")
    assert c.status == "alerta" and c.severidade == "media"
    assert "40" in c.mensagem and "25" in c.mensagem  # mostra os dois números


# ------------------------------------------------------------------ C02 ----
def test_c02_variacao_absoluta_lucro():
    ok = ext(lucro_liquido=M(100, 80, variacao_reportada_abs=V(20)))
    ruim = ext(lucro_liquido=M(100, 80, variacao_reportada_abs=V(35)))
    assert _checks(ok, "C02")[0].status == "ok"
    assert _checks(ruim, "C02")[0].status == "alerta"


# ------------------------------------------------------------------ C04 ----
def test_c04_ebitda_sinal_trocado_e_alta():
    e = ext(ebitda=M(500, None), ebit=M(-400, -100), depreciacao_amortizacao=M(900, 700))
    # recomposto = -400 + 900 = 500 (confere) -> ok
    assert _checks(e, "C04")[0].status == "ok"
    e2 = ext(ebitda=M(500, None), ebit=M(-1400, -100), depreciacao_amortizacao=M(900, 700))
    # recomposto = -500: mesmo módulo, sinal oposto
    (c,) = _checks(e2, "C04")
    assert c.status == "alerta" and c.severidade == "alta" and "sinal" in c.mensagem.lower()


def test_c04_ebitda_modulo_diferente_e_media():
    e = ext(ebitda=M(900, None), ebit=M(100, 50), depreciacao_amortizacao=M(200, 150))
    (c,) = _checks(e, "C04")
    assert c.status == "alerta" and c.severidade == "media"


# ------------------------------------------------------------------ C05 ----
def test_c05_margem_publicada_vs_calculada():
    # EBITDA derivado 300 / receita 1000 = 30%
    base = dict(ebit=M(100, 50), depreciacao_amortizacao=M(200, 150))
    ok = ext(margem_ebitda=M(30.0, None, v={"escala": "unidade", "unidade": "%"}), **base)
    ruim = ext(margem_ebitda=M(45.0, None, v={"escala": "unidade", "unidade": "%"}), **base)
    (c_ok,) = _checks(ok, "C05")
    (c_ruim,) = _checks(ruim, "C05")
    assert c_ok.status == "ok"
    assert c_ruim.status == "alerta"
    assert "45" in c_ruim.mensagem and "30" in c_ruim.mensagem


def test_c05_sem_margem_publicada_nao_dispara():
    assert _checks(ext(ebit=M(100, 50), depreciacao_amortizacao=M(200, 150)), "C05") == []


# ------------------------------------------------------------------ C06 ----
def test_c06_divida_liquida_vs_bruta_menos_caixa():
    base = dict(divida_bruta=M(1000, 900), caixa_equivalentes=M(200, 100), aplicacoes_financeiras=M(100, 50))
    ok = ext(divida_liquida=M(700, 750), **base)
    ruim = ext(divida_liquida=M(650, 750), **base)
    assert all(c.status == "ok" for c in _checks(ok, "C06"))
    assert any(c.status == "alerta" for c in _checks(ruim, "C06"))


# ------------------------------------------------------------------ C08 ----
def test_c08_ausencia_explicita_nunca_vira_zero():
    checks, _ = validate_extraction(ext())
    cob = {c.campo for c in checks if c.id == "C08"}
    assert {"ebitda", "fco", "capex"} <= cob  # campos ausentes ficam visíveis
    assert "receita_liquida" not in cob


# ------------------------------------------------------------------ C10 ----
def test_c10_variacao_extrema_e_sinal_negativo():
    extremo = ext(receita_liquida=M(3000, 800))
    (c,) = _checks(extremo, "C10")
    assert c.status == "alerta" and "extrema" in c.mensagem.lower()
    negativo = ext(lucro_liquido=M(-5000, 80))
    assert any("n.s." in c.mensagem for c in _checks(negativo, "C10"))


# ------------------------------------------------------------------ C03 ----
def test_c03_erro_de_escala_alerta_alta():
    # texto cita 1.000.000 "mil" onde as DFs têm 1.000 mil: razão 1000 = erro de escala
    e = ext(receita_liquida=Metrica(atual=V(1000), anterior=V(800), alternativas=[V(1_000_000, escala="mil")]))
    cs = _checks(e, "C03")
    assert any(c.status == "alerta" and c.severidade == "alta" and "escala" in c.mensagem.lower() for c in cs)


def test_c03_mencao_alternativa_consistente_e_ok():
    # 1,0 milhão == 1.000 mil: mesma grandeza em escalas diferentes -> ok
    e = ext(receita_liquida=Metrica(atual=V(1000), anterior=V(800), alternativas=[V(1.0, escala="milhoes")]))
    cs = _checks(e, "C03")
    assert cs and all(c.status == "ok" for c in cs)


def test_c03_sinal_oposto_com_mesmo_modulo():
    e = ext(lucro_liquido=Metrica(atual=V(100), anterior=V(80), alternativas=[V(-100)]))
    assert any(c.severidade == "alta" and "sinais" in c.mensagem for c in _checks(e, "C03"))


# ------------------------------------------------- nada é corrigido em silêncio
def test_valores_extraidos_nao_sao_alterados_pela_validacao():
    e = ext(ebitda=M(500, None), ebit=M(-1400, -100), depreciacao_amortizacao=M(900, 700))
    antes = e.model_dump()
    validate_extraction(e)
    assert e.model_dump() == antes
