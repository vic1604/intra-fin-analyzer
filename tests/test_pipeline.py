import json

import pytest

from finanalyzer.evaluate import evaluate_all
from finanalyzer.extract import load_reference
from finanalyzer.baseline import extract_baseline

PDFS = {"light", "millet", "brasal"}


def test_all_three_docs_processed(real_run):
    assert set(real_run.exts) == PDFS


def test_zero_grounding_failures(real_run):
    assert sum(len(v) for v in real_run.grounding_failures.values()) == 0
    assert sum(real_run.grounding_counts.values()) > 100


def test_every_found_value_has_page_and_quote(real_run):
    for d, ext in real_run.exts.items():
        for nome, m in ext.metricas().items():
            if m.status == "encontrado":
                assert m.atual is not None, (d, nome)
                assert m.atual.evidencia.pagina >= 1 and m.atual.evidencia.trecho, (d, nome)


def test_missing_fields_are_explicit_and_justified(real_run):
    for d, ext in real_run.exts.items():
        for nome, m in ext.metricas().items():
            if m.status == "nao_encontrado":
                assert m.motivo_ausencia, (d, nome)


def test_five_answers_have_citations(real_run):
    assert len(real_run.answers) == 5
    for a in real_run.answers:
        assert a.fontes, a.numero
        assert all(f.pagina >= 1 for f in a.fontes)


def test_light_ebitda_inconsistency_is_flagged_not_fixed(real_run):
    c04 = [c for c in real_run.checks["light"] if c.id == "C04" and c.status == "alerta" and c.severidade == "alta"]
    assert c04, "esperava alerta C04 (sinal do EBITDA) de severidade alta"
    ext = real_run.exts["light"]
    # o valor PUBLICADO continua intacto (R$ 1.180 mi, positivo, p.9); o derivado é separado e negativo
    assert ext.ebitda.atual.valor == pytest.approx(1180.0) and ext.ebitda.atual.escala == "milhoes"
    assert ext.ebitda.atual.evidencia.pagina == 9
    assert real_run.ders["light"]["ebitda_derivado"].atual == pytest.approx(-1179644.0)


def test_derived_values_are_labeled(real_run):
    for d in real_run.order:
        for k, der in real_run.ders[d].items():
            assert der.formula


def test_millet_receita_variation_flagged_not_comparable(real_run):
    assert any("Alibra" in (a.descricao) for a in real_run.exts["millet"].anomalias_documento)


def test_deliverable_json_shape(real_run):
    from finanalyzer.export import to_deliverable

    j = to_deliverable(real_run.exts["light"], real_run.ders["light"], real_run.checks["light"])
    json.dumps(j, ensure_ascii=False)
    rl = j["indicadores"]["receita_liquida"]
    assert rl["valor_periodo_atual"]["origem"]["pagina"] == 20


def test_report_has_required_sections(real_run):
    from finanalyzer.pipeline import WriterAgent

    _, md, html = WriterAgent().write(real_run)
    for h in ("Resumo executivo", "Tabela comparativa", "qualitativa", "Alertas", "Anexo A"):
        assert h.lower() in md.lower(), h
    assert "<table" in html
    # resumo executivo: no máximo 5 linhas numeradas por empresa
    bloco = md.split("## 2.")[0]
    for emp in bloco.split("### ")[1:]:
        assert len([l for l in emp.splitlines() if l[:2] in ("1.", "2.", "3.", "4.", "5.", "6.")]) <= 5


def test_exec_summary_lines_are_short(real_run):
    """O brief pede resumo de até 5 linhas por empresa: cada item cabe em ~1 linha visual."""
    import re

    from finanalyzer.report import MAX_LINHA_RESUMO, _clip, exec_summary

    for d in real_run.exts:
        linhas = exec_summary(real_run, d)
        assert 1 <= len(linhas) <= 5
        for ln in linhas:
            visivel = re.sub(r"\*+", "", ln)
            assert len(visivel) <= MAX_LINHA_RESUMO, (d, len(visivel), visivel)
    # _clip nunca corta no meio de um número e sempre sinaliza o corte
    out = _clip("Valor de R$1.180.000 mil divergente do texto da administração sobre o EBITDA", 30)
    assert out.endswith("…") and "R$1.180.000" in out or "R$1." not in out


def test_baseline_is_honest(real_run, settings):
    refs = {d: load_reference(settings, d) for d in PDFS}
    preds = {d: extract_baseline(real_run.docs[d]) for d in PDFS}
    res = evaluate_all(preds, refs)
    g = res["global"]
    assert g["taxa_alucinacao"] == 0
    assert 0.3 < g["recall"] < 1.0  # baseline regex não pode ser perfeito: se for, o gabarito vazou


def test_structured_log_is_written_and_safe(settings, tmp_path):
    """Log JSONL: uma linha por evento, spans por etapa/documento, sem conteúdo de PDF nem segredos."""
    import json

    from finanalyzer.obs import Tracer
    from finanalyzer.pipeline import run_pipeline

    if not list(settings.input_dir.glob("*.pdf")):
        pytest.skip("PDFs não estão em data/input")
    path = tmp_path / "logs" / "run.jsonl"
    tr = Tracer(path)
    run = run_pipeline(settings, mode="reference", write=False, tracer=tr)
    linhas = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
    assert linhas[0]["evento"] == "run_inicio" and linhas[-1]["evento"] == "run_fim" and linhas[-1]["status"] == "ok"
    assert len({l["run_id"] for l in linhas}) == 1
    assert [l["seq"] for l in linhas] == list(range(1, len(linhas) + 1))
    etapas = {(l.get("etapa"), l.get("doc")) for l in linhas if l["evento"] == "span"}
    for d in run.order:
        assert {("extracao", d), ("qualitativo", d), ("validacao", d)} <= etapas
    assert {("ingestao", None), ("seguranca_scan", None), ("ml_tradicional", None), ("relatorio", None)} <= etapas
    bruto = path.read_text(encoding="utf-8")
    # nada de texto de PDF/trechos nem de segredos no log
    for doc in run.docs.values():
        trecho = next(p.text for p in doc.pages if len(p.text) > 200)[:120]
        assert trecho not in bruto
    for proibido in ("api_key", "sk-", "Bearer", "AIza"):
        assert proibido not in bruto


def test_tracer_records_errors_and_reraises(tmp_path):
    import json

    from finanalyzer.obs import Tracer

    tr = Tracer(tmp_path / "x.jsonl")
    with pytest.raises(ValueError):
        with tr.span("etapa_ruim", doc="d"):
            raise ValueError("segredo-que-nao-deve-ir-pro-log")
    tr.close()
    rec = json.loads((tmp_path / "x.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert rec["status"] == "erro" and rec["erro_tipo"] == "ValueError"
    assert "segredo" not in json.dumps(rec)  # só o TIPO do erro é registrado, nunca a mensagem


def test_output_dir_env_override(monkeypatch):
    from finanalyzer.config import ROOT, Settings

    monkeypatch.delenv("OUTPUT_DIR", raising=False)
    assert Settings().output_dir == ROOT / "outputs"
    monkeypatch.setenv("OUTPUT_DIR", "outputs_llm")
    assert Settings().output_dir == ROOT / "outputs_llm"
    monkeypatch.setenv("OUTPUT_DIR", "")
    assert Settings().output_dir == ROOT / "outputs"
