"""Perguntas livres sem LLM: roteamento, citações verificadas e recusa quando não há evidência."""
import pytest

from finanalyzer.grounding import verify_evidence
from finanalyzer.qa import Ctx, ask_offline
from finanalyzer.retrieval import BM25Index
from finanalyzer.schema import Evidencia


@pytest.fixture(scope="module")
def env(real_run):
    docs = real_run.docs
    return docs, BM25Index(list(docs.values())), Ctx(real_run.exts, real_run.ders, real_run.quals, real_run.checks)


def _ask(env, q):
    docs, idx, ctx = env
    return ask_offline(q, docs, idx, ctx)


def test_margin_question_returns_derived_and_flags_missing(env):
    r = _ask(env, "Qual a margem EBITDA da Brasal?")
    assert r.modo == "offline" and "não encontrado" in r.resposta and "16,7%" in r.resposta and "calculado" in r.resposta
    assert "Light" not in r.resposta.split("Brasal")[0]  # filtrou pela empresa citada


def test_leverage_question_cites_page_10(env):
    r = _ask(env, "Qual a alavancagem da Light?")
    assert "3,32x" in r.resposta and any(c.documento == "light" and c.pagina == 10 for c in r.citacoes_validas)


def test_qualitative_routing(env):
    r = _ask(env, "Quais os riscos da Millet?")
    assert "Riscos e pontos de atenção" in r.resposta and any(c.pagina == 40 for c in r.citacoes_validas)


def test_out_of_domain_question_is_refused(env):
    r = _ask(env, "Qual o preço do bitcoin hoje?")
    assert "Sem evidência suficiente" in r.resposta and r.citacoes_validas == []


def test_every_citation_is_literal_in_its_page(env):
    docs, _, _ = env
    for q in ("Qual a margem EBITDA da Brasal?", "Quais os riscos da Millet?", "Houve aquisição na Millet?", "Qual o incentivo fiscal da Brasal?"):
        r = _ask(env, q)
        assert r.citacoes_validas, q
        assert not r.citacoes_descartadas, q
        for c in r.citacoes_validas:  # re-verifica de forma independente
            assert verify_evidence(docs[c.documento], Evidencia(documento=c.documento, pagina=c.pagina, trecho=c.trecho))[0]
