from finanalyzer.grounding import verify_absence, verify_evidence
from finanalyzer.schema import Evidencia


def test_evidence_ok(mini_doc):
    ok, _ = verify_evidence(mini_doc, Evidencia(documento="exemplo", pagina=2, trecho="RECEITA LÍQUIDA   1.000.000   800.000"), 1000000)
    assert ok


def test_wrong_page_is_rejected(mini_doc):
    ok, why = verify_evidence(mini_doc, Evidencia(documento="exemplo", pagina=1, trecho="RECEITA LÍQUIDA   1.000.000   800.000"))
    assert not ok and "página" in why


def test_invented_quote_is_rejected(mini_doc):
    ok, _ = verify_evidence(mini_doc, Evidencia(documento="exemplo", pagina=2, trecho="RECEITA LÍQUIDA 9.999.999"))
    assert not ok


def test_number_not_in_quote_is_rejected(mini_doc):
    ok, why = verify_evidence(mini_doc, Evidencia(documento="exemplo", pagina=2, trecho="LUCRO LÍQUIDO   50.000   40.000"), 1000000)
    assert not ok and "valor" in why


def test_page_out_of_range(mini_doc):
    ok, _ = verify_evidence(mini_doc, Evidencia(documento="exemplo", pagina=99, trecho="qualquer coisa"))
    assert not ok


def test_absence_detects_hidden_term(mini_doc):
    assert verify_absence(mini_doc, ["ebitda"])  # existe na p.2 -> "não encontrado" seria falso
    assert not verify_absence(mini_doc, ["guidance"])


# ---- citações "arrumadas" do LLM (rótulo quebrado em 2 linhas no PDF) ----------
from finanalyzer.ingest import Document, Page
from finanalyzer.schema import Evidencia as _Ev
from finanalyzer.grounding import verify_evidence as _verify


def _doc_quebrado():
    txt = "Caixa liquido gerado pelas (consumido nas)\n24.799 (317) (860) (14.293)\natividades operacionais\nOutra linha 5.000"
    return Document("d", "d.pdf", "0" * 64, 1, [Page(1, txt)])


def test_reflow_accepts_label_wrapped_by_pdf_and_replaces_with_real_text():
    ev = _Ev(documento="d", pagina=1, trecho="Caixa liquido gerado pelas (consumido nas) atividades operacionais 24.799 (317) (860) (14.293)")
    ok, why = _verify(_doc_quebrado(), ev, 24799)
    assert ok and why is None
    assert ev.trecho in _doc_quebrado().page(1).text_norm  # passou a ser literal


def test_reflow_still_rejects_wrong_or_invented_numbers_and_words():
    d = _doc_quebrado()
    for q, v in [
        ("Caixa liquido gerado pelas (consumido nas) atividades operacionais 24.798 (317) (860) (14.293)", 24798),
        ("Caixa liquido gerado pelas (consumido nas) atividades operacionais 24.799 (317) (860) (99.999)", 24799),
        ("Caixa liquido gerado pelas (consumido nas) atividades de investimento 24.799 (317) (860) (14.293)", 24799),
    ]:
        assert _verify(d, _Ev(documento="d", pagina=1, trecho=q), v)[0] is False


def test_pipe_joined_quote_keeps_only_the_verified_segment_with_the_value():
    d = Document("d", "d.pdf", "0" * 64, 1, [Page(1, "Lucro A 14.743 5.371\nMinoritarios - - (4.148)")])
    ev = _Ev(documento="d", pagina=1, trecho="Lucro A - - (4.148) | Lucro A 14.743 5.371")
    ok, _ = _verify(d, ev, 14743)
    assert ok and ev.trecho == "Lucro A 14.743 5.371"


def test_scale_converted_by_model_is_rescaled_from_quote_but_wrong_digits_still_fail():
    from finanalyzer.grounding import _check_valor
    from finanalyzer.schema import Valor

    d = Document("d", "d.pdf", "0" * 64, 1, [Page(1, "o EBITDA foi de R$1.180 milhões em 2022")])
    q = "o EBITDA foi de R$1.180 milhões"
    # caso real do Gemini: valor 1.180.000 com escala 'milhoes' (conversão errada) -> reescala para 1180 milhoes
    for valor, escala in [(1_180_000, "milhoes"), (1_180_000, "mil"), (1180, "mil")]:
        v = Valor(valor=valor, escala=escala, evidencia=_Ev(documento="d", pagina=1, trecho=q))
        fails: list = []
        assert _check_valor(d, v, "ebitda.atual", fails) and not fails
        assert (v.valor, v.escala) == (1180, "milhoes")
    # dígitos diferentes (1.190) NÃO são salvos pela reescala
    v = Valor(valor=1_190_000, escala="mil", evidencia=_Ev(documento="d", pagina=1, trecho=q))
    fails = []
    assert _check_valor(d, v, "ebitda.atual", fails) is False and fails
