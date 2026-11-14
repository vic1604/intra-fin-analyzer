"""Mini-avaliação da camada QUALITATIVA (offline, sem LLM, sem chave).

Mede duas coisas contra a curadoria em data/reference/qualitativo:

1. RECUPERAÇÃO — as páginas que o gabarito cita estão entre as enviadas ao
   LLM (`select_quali_pages`)? Se a página certa nem chega ao prompt, nenhum
   modelo acerta. É determinístico e reproduzível.
2. SAÍDA DO LLM (se existir `outputs_llm/qualitativo/*.json`) — tom, flag de
   guidance numérico, recall de categorias de risco, motivo da variação de
   receita (página) e recall de páginas citadas.

Limite honesto: o gabarito qualitativo é curadoria de UMA pessoa; mede
cobertura/concordância, não "verdade absoluta". A saída do modo `reference`
NÃO deve ser avaliada aqui (seria comparar o gabarito com ele mesmo).
"""

from __future__ import annotations

from pathlib import Path

from .qualitative import QUALI_MAX_PAGES, select_quali_pages
from .retrieval import BM25Index
from .schema import Qualitativo


def _pages(q: Qualitativo) -> set[int]:
    out: set[int] = set()
    groups = [q.motivos_resultado, q.riscos, q.guidance, q.eventos_relevantes, [q.motivo_variacao_receita] if q.motivo_variacao_receita else []]
    for g in groups:
        for it in g:
            out.update(e.pagina for e in it.evidencias)
    out.update(e.pagina for e in q.tom_evidencias)
    return out


def _cats(q: Qualitativo) -> set[str]:
    return {r.categoria for r in q.riscos if r.categoria}


def retrieval_recall(ref: Qualitativo, selected: set[int]) -> dict:
    pg = _pages(ref)
    return {"paginas_gabarito": len(pg), "paginas_enviadas": len(selected), "recall": round(len(pg & selected) / len(pg), 3) if pg else 1.0, "faltando": sorted(pg - selected)}


def compare_llm(ref: Qualitativo, pred: Qualitativo) -> dict:
    rc, pc = _cats(ref), _cats(pred)
    rp, pp = _pages(ref), _pages(pred)
    rev_ref = {e.pagina for e in ref.motivo_variacao_receita.evidencias} if ref.motivo_variacao_receita else set()
    rev_pred = {e.pagina for e in pred.motivo_variacao_receita.evidencias} if pred.motivo_variacao_receita else set()
    return {
        "tom_ok": ref.tom == pred.tom,
        "guidance_flag_ok": ref.guidance_numerico_encontrado == pred.guidance_numerico_encontrado,
        "categorias_risco_recall": round(len(rc & pc) / len(rc), 3) if rc else 1.0,
        "motivo_receita_ok": (bool(rev_ref & rev_pred) if rev_ref else not rev_pred),
        "paginas_citadas_recall": round(len(rp & pp) / len(rp), 3) if rp else 1.0,
        "n_itens": {"ref": [len(ref.motivos_resultado), len(ref.riscos), len(ref.guidance), len(ref.eventos_relevantes)], "llm": [len(pred.motivos_resultado), len(pred.riscos), len(pred.guidance), len(pred.eventos_relevantes)]},
    }


def run_quali_eval(docs: dict, ref_dir: Path, llm_dir: Path | None, k: int = 8) -> dict:
    index = BM25Index(list(docs.values()))
    res: dict = {"max_paginas": QUALI_MAX_PAGES, "recuperacao": {}, "llm": {}}
    for d, doc in docs.items():
        rp = ref_dir / "qualitativo" / f"{d}.json"
        if not rp.exists():
            continue
        ref = Qualitativo.model_validate_json(rp.read_text(encoding="utf-8"))
        res["recuperacao"][d] = retrieval_recall(ref, set(select_quali_pages(doc, index, k=k, max_pages=QUALI_MAX_PAGES)))
        lp = (llm_dir / "qualitativo" / f"{d}.json") if llm_dir else None
        if lp and lp.exists():
            pred = Qualitativo.model_validate_json(lp.read_text(encoding="utf-8"))
            if pred.modo == "llm":
                res["llm"][d] = compare_llm(ref, pred)
    rec = [v["recall"] for v in res["recuperacao"].values()]
    res["recuperacao_media"] = round(sum(rec) / len(rec), 3) if rec else None
    if res["llm"]:
        n = len(res["llm"])
        res["llm_resumo"] = {
            "tom_ok": f"{sum(v['tom_ok'] for v in res['llm'].values())}/{n}",
            "guidance_flag_ok": f"{sum(v['guidance_flag_ok'] for v in res['llm'].values())}/{n}",
            "motivo_receita_ok": f"{sum(v['motivo_receita_ok'] for v in res['llm'].values())}/{n}",
            "categorias_risco_recall_media": round(sum(v["categorias_risco_recall"] for v in res["llm"].values()) / n, 3),
            "paginas_citadas_recall_media": round(sum(v["paginas_citadas_recall"] for v in res["llm"].values()) / n, 3),
        }
    return res
