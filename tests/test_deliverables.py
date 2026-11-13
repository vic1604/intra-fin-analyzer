"""Auditoria automática dos ENTREGÁVEIS contra o enunciado.

Lê os artefatos gerados por `run_pipeline(write=True)` num diretório temporário
(nunca os de `outputs/`) e confere, item a item, o que o brief exige. Se alguém
quebrar um requisito (ex.: um número sem página), este teste falha.
"""

from __future__ import annotations

import dataclasses
import json
import re

import pytest

from finanalyzer.pipeline import run_pipeline

DOCS = ("light", "millet", "brasal")
CAMPOS_BRIEF = ("receita_liquida", "ebitda", "margem_ebitda", "lucro_liquido", "divida_liquida", "alavancagem", "fco", "capex")


@pytest.fixture(scope="module")
def out(settings, tmp_path_factory):
    if not list(settings.input_dir.glob("*.pdf")):
        pytest.skip("PDFs não estão em data/input")
    d = tmp_path_factory.mktemp("outputs")
    s = dataclasses.replace(settings, output_dir=d)
    run_pipeline(s, mode="reference", write=True)
    return d


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


@pytest.mark.parametrize("doc", DOCS)
def test_json_por_documento_tem_origem_ou_nao_encontrado(out, doc):
    d = json.loads((out / "extracao" / f"{doc}.json").read_text(encoding="utf-8"))
    ind = d["indicadores"]
    assert set(CAMPOS_BRIEF) <= set(ind)
    for nome in CAMPOS_BRIEF:
        m = ind[nome]
        if m["status"] == "encontrado":
            assert m["valor_periodo_atual"]["origem"]["pagina"] >= 1
            assert len(m["valor_periodo_atual"]["origem"]["trecho"]) >= 3
        else:  # "não encontrado" explícito, com motivo — nunca zero/estimativa
            assert m["status"] == "não encontrado" and m["motivo"]
            assert "valor_periodo_atual" not in m
    # toda "origem" em qualquer ponto do JSON tem página + trecho + foi verificada
    for o in _walk(d):
        if "origem" in o:
            assert o["origem"]["pagina"] >= 1 and o["origem"]["trecho"]
            assert o["origem"].get("verificada") is True, (doc, o["origem"])


@pytest.mark.parametrize("doc", DOCS)
def test_qualitativo_tem_os_cinco_elementos_com_evidencia(out, doc):
    q = json.loads((out / "qualitativo" / f"{doc}.json").read_text(encoding="utf-8"))
    for chave in ("motivos_resultado", "riscos", "guidance", "eventos_relevantes", "tom", "tom_justificativa"):
        assert chave in q, chave
    assert q["tom"] in ("positivo", "neutro", "negativo") and len(q["tom_justificativa"]) > 20
    assert q["riscos"], "sem riscos"
    for lista in ("motivos_resultado", "riscos", "eventos_relevantes"):
        for item in q[lista]:
            assert item["evidencias"] and all(e["pagina"] >= 1 and e["trecho"] for e in item["evidencias"])


def test_cinco_respostas_com_citacao_documento_e_pagina(out):
    r = json.loads((out / "respostas.json").read_text(encoding="utf-8"))
    assert [x["numero"] for x in r] == [1, 2, 3, 4, 5]
    for x in r:
        assert len(x["resposta"]) > 40 and x["fontes"], x["numero"]
        assert all(f["documento"] and f["pagina"] >= 1 for f in x["fontes"])
    md = (out / "respostas.md").read_text(encoding="utf-8")
    assert md.count("**Fontes:**") == 5


def test_relatorio_tem_todas_as_secoes_do_brief(out):
    md = (out / "relatorio.md").read_text(encoding="utf-8")
    low = md.lower()
    for sec in ("resumo executivo", "tabela comparativa", "análise qualitativa", "respostas", "alertas"):
        assert sec in low, sec
    # tabela comparativa cobre as 3 empresas
    tab = md.lower().split("tabela comparativa")[1].split("\n## ")[0]
    assert all(e in tab for e in ("light", "millet", "brasal"))
    # resumo executivo: ≤ 5 linhas por empresa
    resumo = md.split("## 2.")[0]
    for emp in resumo.split("### ")[1:]:
        assert len([l for l in emp.splitlines() if re.match(r"^\d\. ", l)]) <= 5
    # alertas de validação aparecem no relatório (não foram silenciados)
    assert "C04" in md or "EBITDA" in md
    assert (out / "relatorio.html").read_text(encoding="utf-8").count("<table") >= 2


def test_validacoes_nao_foram_corrigidas_em_silencio(out):
    """A Light imprime EBITDA 1.180 (p.9) e o recomposto é negativo: os DOIS aparecem + alerta."""
    d = json.loads((out / "extracao" / "light.json").read_text(encoding="utf-8"))
    assert d["indicadores"]["ebitda"]["valor_periodo_atual"]["valor"] == 1180.0
    val = json.dumps(d["validacoes"], ensure_ascii=False)
    assert "C04" in val and "NEGATIVO" in val
    assert d["indicadores_derivados_calculados_pelo_pipeline"]


def test_artefatos_de_apoio_existem(out):
    for f in ("run_manifest.json", "ml_tradicional.json", "logs/run.jsonl"):
        assert (out / f).exists(), f
    man = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
    assert all(len(v["sha256"]) == 64 for v in man["documentos"].values())
    assert sum(g["falhas"] for g in man["grounding"].values()) == 0
