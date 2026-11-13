"""Abordagem tradicional: detector de anomalias (z-score robusto + Isolation Forest) e comparação de tom."""
import pytest

from finanalyzer.ingest import Document, Page
from finanalyzer.ml_baseline import analisar, comparar_tom, detectar_anomalias, extrair_linhas


def _doc(linhas: list[str], titulo="Demonstrações dos resultados") -> Document:
    txt = f"Empresa X\n{titulo}\n(Valores em milhares de reais)\n\n" + "\n".join(linhas)
    return Document("x", "x.pdf", "0" * 64, 1, [Page(1, txt)])


NORMAIS = [f"Conta numero {chr(65 + i)}{chr(97 + i)}rotulo   {1000 + 100 * i:,}   {900 + 90 * i:,}".replace(",", ".") for i in range(14)]


def test_extracts_label_and_last_two_numbers():
    ls = extrair_linhas(_doc(["Receita operacional líquida   21   -   -   1.325.059   1.061.410"]))
    assert len(ls) == 1 and ls[0].rotulo == "Receita operacional líquida" and (ls[0].atual, ls[0].anterior) == (1325059, 1061410)


def test_negative_in_parentheses_and_dash_zero():
    ls = extrair_linhas(_doc(["Custos dos produtos vendidos   (839.903)   (672.960)", "Equivalência patrimonial   -   -"]))
    assert [(l.atual, l.anterior) for l in ls] == [(-839903, -672960)]  # linha só com '-' é ignorada


def test_notes_pages_are_ignored():
    d = _doc(["Provisao para contingencias   5.000   4.000"], titulo="Nota 12 - provisões")
    assert extrair_linhas(d) == []


def test_sentence_mentioning_statement_is_not_a_title():
    d = Document("x", "x.pdf", "0" * 64, 1, [Page(1, "Os valores reconhecidos na demonstração do resultado, nos grupos de custos, são como segue:\nConta Z de teste   140   32.972")])
    assert extrair_linhas(d) == []


def test_outlier_is_flagged_by_zscore():
    d = _doc(NORMAIS + ["Outras receitas operacionais liquidas   2.182   105.328"])
    ls = detectar_anomalias(extrair_linhas(d), usar_iforest=False)
    flagged = [l for l in ls if l.anomalia_zscore]
    assert [l.rotulo for l in flagged] == ["Outras receitas operacionais liquidas"] and abs(flagged[0].z_robusto) > 3.5


def test_iforest_runs_when_sklearn_available():
    pytest.importorskip("sklearn")
    d = _doc(NORMAIS + ["Outras receitas operacionais liquidas   2.182   105.328"])
    ls = detectar_anomalias(extrair_linhas(d), usar_iforest=True)
    assert any(l.anomalia_iforest for l in ls if l.rotulo.startswith("Outras"))


def test_sign_flip_is_listed_not_scored():
    d = _doc(NORMAIS + ["Lucro do exercicio total   (5.000)   4.000"])
    ls = detectar_anomalias(extrair_linhas(d), usar_iforest=False)
    flip = [l for l in ls if l.inversao_de_sinal]
    assert len(flip) == 1 and flip[0].log_razao is None


def test_too_few_rows_gives_no_flags():
    ls = detectar_anomalias(extrair_linhas(_doc(NORMAIS[:3])), usar_iforest=False)
    assert not any(l.anomalia_zscore for l in ls)


def test_real_docs_find_known_brasal_anomaly(real_run):
    res = real_run.ml["anomalias"]["documentos"]["brasal"]
    marcadas = [t for t in res["top"] if t["coincide_com_alerta_existente"]]
    assert any("ICMS" in t["rotulo"] and t["pagina"] == 11 for t in marcadas)  # os R$ 105.633 mil de créditos extemporâneos
    assert all(t["pagina"] >= 1 and t["trecho"] for t in res["top"])


def test_tone_comparison_is_reported_honestly(real_run):
    t = real_run.ml["tom"]
    assert set(t) == {"light", "millet", "brasal", "_resumo"} and t["_resumo"]["documentos"] == 3
    assert t["millet"]["concorda"] is False  # discordância não é escondida


def test_ml_outputs_written(real_run, tmp_path):
    import dataclasses
    from finanalyzer.pipeline import run_pipeline

    r = run_pipeline(dataclasses.replace(real_run.settings, output_dir=tmp_path), mode="reference")
    assert (tmp_path / "ml_tradicional.json").exists()
    assert "Anexo B" in (tmp_path / "relatorio.md").read_text(encoding="utf-8")


def test_works_without_sklearn(monkeypatch):
    """scikit-learn é opcional: sem ele o z-score continua funcionando e o IF simplesmente não roda."""
    import sys

    monkeypatch.setitem(sys.modules, "sklearn", None)
    monkeypatch.setitem(sys.modules, "sklearn.ensemble", None)
    d = _doc(NORMAIS + ["Outras receitas operacionais liquidas   2.182   105.328"])
    ls = detectar_anomalias(extrair_linhas(d), usar_iforest=True)
    assert any(l.anomalia_zscore for l in ls)
    assert not any(l.anomalia_iforest for l in ls)
