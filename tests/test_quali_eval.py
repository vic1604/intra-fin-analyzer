from finanalyzer.config import get_settings
from finanalyzer.evaluate_quali import compare_llm, retrieval_recall, run_quali_eval
from finanalyzer.pipeline import discover_docs
from finanalyzer.qualitative import QUALI_MAX_PAGES, select_quali_pages
from finanalyzer.retrieval import BM25Index
from finanalyzer.schema import Qualitativo


def _docs():
    s = get_settings()
    return s, discover_docs(s)


def test_select_quali_pages_respeita_teto_e_inclui_ancoras():
    s, docs = _docs()
    idx = BM25Index(list(docs.values()))
    for doc in docs.values():
        pages = select_quali_pages(doc, idx, k=8, max_pages=QUALI_MAX_PAGES)
        assert len(pages) <= QUALI_MAX_PAGES
        assert pages == sorted(set(pages))
        assert 1 in pages and doc.n_pages in pages  # âncoras: início e fim
        assert all(1 <= p <= doc.n_pages for p in pages)


def test_recuperacao_qualitativa_nao_regride():
    # piso calibrado: a versão antiga (corte por nº de página) dava 33% das páginas do gabarito
    s, docs = _docs()
    res = run_quali_eval(docs, s.reference_dir, None)
    assert res["recuperacao_media"] >= 0.6


def test_compare_llm_contra_si_mesmo_e_perfeito():
    s, docs = _docs()
    ref = Qualitativo.model_validate_json((s.reference_dir / "qualitativo" / "light.json").read_text(encoding="utf-8"))
    c = compare_llm(ref, ref)
    assert c["tom_ok"] and c["guidance_flag_ok"] and c["motivo_receita_ok"]
    assert c["categorias_risco_recall"] == 1.0 and c["paginas_citadas_recall"] == 1.0
    assert retrieval_recall(ref, {1})["recall"] < 1.0


def test_quali_out_aceita_lista_em_campos_de_texto():
    from finanalyzer.qualitative import QualiOut

    o = QualiOut.model_validate({"nota_cobertura": ["a", "b"], "tom_justificativa": None})
    assert o.nota_cobertura == "a b" and o.tom_justificativa == ""


def test_relocacao_de_pagina_so_se_trecho_literal_for_unico():
    from finanalyzer.grounding import ground_qualitativo
    from finanalyzer.schema import Evidencia, Item

    s, docs = _docs()
    doc = docs["millet"]
    page = doc.page(27)
    trecho = " ".join(page.text.split()[10:30])  # literal, longo o bastante
    q = Qualitativo.model_validate_json((s.reference_dir / "qualitativo" / "millet.json").read_text(encoding="utf-8"))
    q.eventos_relevantes = [Item(texto="x", evidencias=[Evidencia(documento="millet", pagina=5, trecho=trecho)])]
    q.motivos_resultado, q.riscos, q.guidance, q.motivo_variacao_receita, q.tom_evidencias = [], [], [], None, []
    falhas = ground_qualitativo(doc, q)
    ev = q.eventos_relevantes[0].evidencias[0]
    assert ev.verificada and ev.pagina != 5 and "página corrigida" in (ev.motivo_falha or "")
    assert not falhas
    # trecho inventado continua reprovado
    q.eventos_relevantes = [Item(texto="y", evidencias=[Evidencia(documento="millet", pagina=5, trecho="frase inventada que não existe em nenhuma página do documento financeiro")])]
    assert ground_qualitativo(doc, q)


def test_documento_novo_em_modo_baseline_nao_quebra_e_nao_inventa(tmp_path, monkeypatch):
    import shutil

    from finanalyzer.config import get_settings
    from finanalyzer.pipeline import run_pipeline

    s = get_settings()
    s.input_dir = tmp_path / "in"
    s.input_dir.mkdir()
    for nome in ("light", "millet", "brasal"):
        shutil.copy(get_settings().input_dir / f"{nome}.pdf", s.input_dir / f"{nome}.pdf")
    shutil.copy(get_settings().input_dir / "millet.pdf", s.input_dir / "nova_empresa.pdf")
    s.output_dir = tmp_path / "out"
    s.cache_dir = tmp_path / "cache"
    run = run_pipeline(s, mode="baseline", write=True, with_tables=False)
    q = run.quals["nova_empresa"]
    assert q.riscos == [] and q.confianca_tom == "baixa" and "Rode com --mode llm" in q.nota_cobertura
    md = (s.output_dir / "relatorio.md").read_text(encoding="utf-8")
    assert "Nova Empresa" in md  # o relatório é gerado com 4 empresas sem quebrar
    assert "Light, Millet, Brasal e Nova Empresa" in md
    assert "Nenhuma das quatro empresas" in (s.output_dir / "respostas.md").read_text(encoding="utf-8")
