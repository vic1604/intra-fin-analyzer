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
