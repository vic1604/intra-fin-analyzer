"""Caminho LLM testado com FakeLLM (sem rede): prova que valores inventados são barrados."""
from finanalyzer.grounding import ground_extraction
from finanalyzer.llm.client import FakeLLM, LLMResult, UsageMeter, parse_json_loose


def test_parse_json_loose_handles_fences():
    assert parse_json_loose('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json_loose("lixo sem json") is None


def test_usage_meter_cost():
    m = UsageMeter()
    m.add("x", LLMResult("", None, 1_000_000, 1_000_000, 1.0))
    assert m.cost_usd(3.0, 15.0) == 18.0


def test_fake_llm_records_calls():
    llm = FakeLLM([{"ok": True}])
    r = llm.complete("s", "u", json_schema={"type": "object"})
    assert r.data == {"ok": True} and llm.calls[0]["schema"]


def test_fabricated_value_is_caught_by_grounding(mini_doc, settings):
    """LLM 'alucina' uma receita e inventa a citação: o grounding precisa marcar como falha."""
    from finanalyzer.extract import extract_with_llm
    from finanalyzer.retrieval import BM25Index

    boa = {"campo": "receita_liquida", "periodo": "atual", "valor": 1000000, "escala": "mil", "unidade": "R$", "pagina": 2, "trecho": "RECEITA LÍQUIDA   1.000.000   800.000"}
    inventada = {"campo": "lucro_liquido", "periodo": "atual", "valor": 777777, "escala": "mil", "unidade": "R$", "pagina": 2, "trecho": "LUCRO LÍQUIDO 777.777"}
    llm = FakeLLM([{"empresa": "Exemplo", "periodo_referencia": "2022", "tipo_documento": "DF", "moeda_escala_declarada": "R$ mil", "campos": [boa, inventada], "nao_encontrados": [], "anomalias": []}])
    ext = extract_with_llm(mini_doc, BM25Index([mini_doc]), llm, UsageMeter(), settings)
    fails = ground_extraction(mini_doc, ext)
    assert {f.campo.split(".")[0] for f in fails} == {"lucro_liquido"}
    assert ext.receita_liquida.status == "encontrado"
    assert ext.lucro_liquido.status != "encontrado"  # rebaixado, nunca aceito em silêncio
    assert ext.ebitda.status == "nao_encontrado" and ext.ebitda.motivo_ausencia


# ------------------------------------------------ saída "torta" de LLM real --
def _campo_ok():
    return {"campo": "receita_liquida", "periodo": "atual", "valor": 1000000, "escala": "mil", "unidade": "R$", "pagina": 2, "trecho": "RECEITA LÍQUIDA   1.000.000   800.000"}


def test_extraction_tolerates_anomaly_without_id_and_flat_evidence(mini_doc, settings):
    """Caso real (Gemini): anomalia sem `id` e com pagina/trecho 'planos' derrubava o documento."""
    from finanalyzer.extract import extract_with_llm
    from finanalyzer.retrieval import BM25Index

    anom = {"pagina": "2", "trecho": "RECEITA LÍQUIDA   1.000.000   800.000", "descricao": "teste"}
    llm = FakeLLM([{"campos": [_campo_ok()], "nao_encontrados": [], "anomalias": [anom]}])
    ext = extract_with_llm(mini_doc, BM25Index([mini_doc]), llm, UsageMeter(), settings)
    assert ext.receita_liquida.status == "encontrado"
    assert len(ext.anomalias_documento) == 1 and ext.anomalias_documento[0].id.endswith("-A1")
    assert ext.anomalias_documento[0].evidencias[0].pagina == 2


def test_extraction_drops_only_the_malformed_item(mini_doc, settings):
    from finanalyzer.extract import extract_with_llm
    from finanalyzer.retrieval import BM25Index

    ruim = {"campo": "ebitda", "periodo": "atual", "valor": "n/d", "pagina": 2, "trecho": "x"}  # valor inválido
    sem_trecho = {"campo": "capex", "periodo": "atual", "valor": 1, "pagina": 2}
    texto_br = {**_campo_ok(), "campo": "lucro_liquido", "valor": "1.234,5", "trecho": "LUCRO LÍQUIDO 1.234,5"}
    llm = FakeLLM([{"campos": [_campo_ok(), ruim, sem_trecho, texto_br], "anomalias": ["texto solto"]}])
    ext = extract_with_llm(mini_doc, BM25Index([mini_doc]), llm, UsageMeter(), settings)
    assert ext.receita_liquida.status == "encontrado"            # item bom sobrevive
    assert ext.lucro_liquido.atual.valor == 1234.5               # "1.234,5" em texto é interpretado
    assert ext.ebitda.status == "nao_encontrado" and ext.capex.status == "nao_encontrado"  # inválidos -> ausente
    assert ext.anomalias_documento == []


def test_lenient_validate_raises_when_required_root_field_missing():
    import pytest
    from pydantic import BaseModel, ValidationError

    from finanalyzer.llm.lenient import lenient_validate

    class M(BaseModel):
        x: int

    with pytest.raises(ValidationError):
        lenient_validate(M, {})


def test_qualitative_tolerates_string_items_and_bad_fields(mini_doc, settings):
    from finanalyzer.qualitative import analyze_with_llm
    from finanalyzer.retrieval import BM25Index

    ev = {"pagina": 2, "trecho": "RECEITA LÍQUIDA"}
    llm = FakeLLM([{
        "motivos_resultado": ["texto sem evidência", {"texto": "ok", "evidencias": [ev]}, {"evidencias": [ev]}],
        "motivo_variacao_receita": "string solta", "riscos": [{"texto": "r", "categoria": "x", "pagina": 2, "trecho": "RECEITA LÍQUIDA"}],
        "tom": "positivo", "tom_evidencias": [{"pagina": "x", "trecho": "y"}, ev],
    }])
    q = analyze_with_llm(mini_doc, BM25Index([mini_doc]), llm, UsageMeter(), settings)
    assert q.modo == "llm" and q.tom == "positivo"
    assert any(i.texto == "ok" for i in q.motivos_resultado)
    assert q.riscos and q.riscos[0].evidencias[0].pagina == 2
    assert len(q.tom_evidencias) == 1


def test_response_wrapped_in_list_is_accepted(mini_doc, settings):
    """Caso real (Gemini): a análise qualitativa veio como [ {...} ] em vez de {...}."""
    from finanalyzer.llm.lenient import lenient_validate
    from finanalyzer.qualitative import QualiOut

    o, avisos = lenient_validate(QualiOut, [{"tom": "positivo", "confianca_tom": "alta"}], "t")
    assert o.tom == "positivo" and avisos


def test_cli_transient_provider_error_exits_75(monkeypatch, capsys):
    import pytest

    import finanalyzer.cli as cli
    from finanalyzer.llm.client import LLMHTTPError

    def boom(_a):
        raise LLMHTTPError("HTTP 429 cota")

    monkeypatch.setattr(cli, "cmd_scan", boom)
    with pytest.raises(SystemExit) as e:
        cli.main(["scan"])
    assert e.value.code == cli.EXIT_RETRY == 75


def test_capex_negative_is_normalized_to_module(mini_doc, settings):
    from finanalyzer.extract import extract_with_llm
    from finanalyzer.retrieval import BM25Index

    c = {"campo": "capex", "periodo": "atual", "valor": -500, "escala": "mil", "unidade": "R$", "pagina": 2, "trecho": "RECEITA LÍQUIDA   1.000.000   800.000"}
    ext = extract_with_llm(mini_doc, BM25Index([mini_doc]), FakeLLM([{"campos": [c]}]), UsageMeter(), settings)
    assert ext.capex.atual.valor == 500 and "módulo" in (ext.capex.observacao or "")
