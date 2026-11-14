"""Etapa 3 — Análise qualitativa (motivos, riscos, guidance, eventos, tom).

reference : data/reference/qualitativo/<doc>.json (curadoria + grounding)
llm       : prompt estruturado sobre páginas recuperadas por BM25; itens sem
            evidência verificada são DESCARTADOS (drop_unverified_items).

Comparação "LLM vs ML tradicional" para o TOM: implementada em
`tone_baseline()` — um léxico simples (palavras positivas/negativas) usado só
como sanity-check do tom classificado; não substitui a leitura do contexto.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator, model_validator

from .config import Settings
from .ingest import Document
from .llm.client import LLMClient, UsageMeter
from .llm.lenient import lenient_validate, warn_all
from .llm.prompts import SYSTEM_QUALI, USER_QUALI
from .retrieval import FIELD_QUERIES, BM25Index, compact_page_text
from .schema import CATEGORIAS_RISCO, Evidencia, Item, Qualitativo
from .security import wrap_untrusted
from .text_utils import normalize_for_search


def load_reference_quali(settings: Settings, doc_id: str) -> Qualitativo:
    path = settings.reference_dir / "qualitativo" / f"{doc_id}.json"
    return Qualitativo.model_validate_json(path.read_text(encoding="utf-8"))


class _QEvid(BaseModel):
    pagina: int
    trecho: str


class _QItem(BaseModel):
    texto: str
    categoria: str | None = None
    evidencias: list[_QEvid] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _tolerante(cls, d):
        if isinstance(d, str):  # item devolvido como texto puro (sem evidência -> será descartado depois)
            return {"texto": d}
        if isinstance(d, dict) and not d.get("evidencias") and "pagina" in d and "trecho" in d:
            d = {**d, "evidencias": [{"pagina": d["pagina"], "trecho": d["trecho"]}]}
        return d


def _as_text(v):
    if isinstance(v, list):
        return " ".join(str(x) for x in v)
    return "" if v is None else (v if isinstance(v, str) else str(v))


class QualiOut(BaseModel):
    fonte_qualitativa: str = ""
    nota_cobertura: str = ""
    motivos_resultado: list[_QItem] = Field(default_factory=list)
    motivo_variacao_receita: _QItem | None = None
    riscos: list[_QItem] = Field(default_factory=list)
    guidance: list[_QItem] = Field(default_factory=list)
    guidance_numerico_encontrado: bool = False
    eventos_relevantes: list[_QItem] = Field(default_factory=list)
    tom: str = "neutro"
    tom_justificativa: str = ""
    tom_evidencias: list[_QEvid] = Field(default_factory=list)
    confianca_tom: str = "media"

    @field_validator("fonte_qualitativa", "nota_cobertura", "tom_justificativa", mode="before")
    @classmethod
    def _texto(cls, v):  # o modelo às vezes devolve lista no lugar de texto
        return _as_text(v)


def _item(doc_id: str, it: _QItem, risco: bool = False) -> Item:
    cat = it.categoria if (risco and it.categoria in CATEGORIAS_RISCO) else None
    return Item(texto=it.texto, categoria=cat, evidencias=[Evidencia(documento=doc_id, pagina=e.pagina, trecho=e.trecho) for e in it.evidencias])


QUALI_MAX_PAGES = 24  # teto próprio do qualitativo (calibrado pela mini-avaliação de recuperação)
QUALI_QUERY_KEYS = (
    "qualitativo_motivos",
    "qualitativo_receita",
    "qualitativo_riscos",
    "qualitativo_guidance",
    "qualitativo_perspectivas",
    "qualitativo_eventos",
)


def select_quali_pages(doc: Document, index: BM25Index, k: int = 8, max_pages: int = 24) -> list[int]:
    """Escolhe as páginas do prompt qualitativo.

    Round-robin entre as consultas (cada tema — motivos, receita, riscos,
    guidance, perspectivas, eventos — garante suas melhores páginas) e, se
    estourar `max_pages`, o corte é por POSIÇÃO NO RANKING, não por número de
    página (a versão anterior cortava as páginas finais do PDF, onde ficam
    notas explicativas e eventos subsequentes).
    """
    ranked = [[h.pagina for h in index.search(FIELD_QUERIES[key], k=k, doc_id=doc.doc_id)] for key in QUALI_QUERY_KEYS]
    # âncoras estruturais: início (sumário/relatório/mensagem) e fim (eventos subsequentes, aprovação)
    anchors = [n for n in (*range(1, 4), *range(doc.n_pages - 1, doc.n_pages + 1)) if 1 <= n <= doc.n_pages]
    chosen: list[int] = list(dict.fromkeys(anchors))[:max_pages]
    for rank in range(k):
        for lst in ranked:
            if rank < len(lst) and lst[rank] not in chosen:
                chosen.append(lst[rank])
                if len(chosen) >= max_pages:
                    return sorted(chosen)
    return sorted(chosen)


def analyze_with_llm(doc: Document, index: BM25Index, llm: LLMClient, meter: UsageMeter, settings: Settings) -> Qualitativo:
    pages = select_quali_pages(doc, index, k=max(settings.top_k_pages, 8), max_pages=QUALI_MAX_PAGES)
    blocos = "\n\n".join(wrap_untrusted(doc.doc_id, n, compact_page_text(doc.page(n).text)) for n in pages)
    system = SYSTEM_QUALI.format(categorias=", ".join(CATEGORIAS_RISCO))
    res = llm.complete(system, USER_QUALI.format(doc_id=doc.doc_id, paginas=blocos), settings.llm_max_tokens, json_schema=QualiOut.model_json_schema())
    meter.add(f"qualitativo:{doc.doc_id}", res)
    if not res.data:
        raise RuntimeError(f"LLM não devolveu JSON qualitativo para {doc.doc_id}")
    o, avisos = lenient_validate(QualiOut, res.data, f"qualitativo:{doc.doc_id}")
    warn_all(avisos)
    tom = o.tom if o.tom in ("positivo", "neutro", "negativo") else "neutro"
    return Qualitativo(
        doc_id=doc.doc_id,
        empresa=doc.doc_id,
        fonte_qualitativa=o.fonte_qualitativa,
        nota_cobertura=o.nota_cobertura,
        motivos_resultado=[_item(doc.doc_id, i) for i in o.motivos_resultado],
        motivo_variacao_receita=_item(doc.doc_id, o.motivo_variacao_receita) if o.motivo_variacao_receita else None,
        riscos=[_item(doc.doc_id, i, True) for i in o.riscos],
        guidance=[_item(doc.doc_id, i) for i in o.guidance],
        guidance_numerico_encontrado=o.guidance_numerico_encontrado,
        eventos_relevantes=[_item(doc.doc_id, i) for i in o.eventos_relevantes],
        tom=tom,
        tom_justificativa=o.tom_justificativa,
        tom_evidencias=[Evidencia(documento=doc.doc_id, pagina=e.pagina, trecho=e.trecho) for e in o.tom_evidencias],
        confianca_tom=o.confianca_tom if o.confianca_tom in ("alta", "media", "baixa") else "media",
        modo="llm",
    )


# ------------------------------------------------- baseline "tradicional" --
_POS = {"crescimento", "aumento", "melhora", "melhor", "recorde", "superou", "atendeu", "expansao", "ganho", "eficiencia", "lucro", "robusto", "solido"}
_NEG = {"prejuizo", "queda", "reducao", "piora", "incerteza", "risco", "inadimplencia", "perdas", "provisao", "impairment", "rebaixamento", "descumprimento", "dificuldade", "agravad", "agravou", "furto", "contingencia", "contingencias"}


def tone_baseline(texts: list[str]) -> dict:
    """Léxico simples: (#pos − #neg) / (#pos + #neg). Serve de sanity-check."""
    pos = neg = 0
    for t in texts:
        for tok in re.findall(r"[a-z]+", normalize_for_search(t)):
            if tok in _POS:
                pos += 1
            elif any(tok.startswith(w) for w in _NEG):
                neg += 1
    tot = pos + neg
    score = (pos - neg) / tot if tot else 0.0
    label = "positivo" if score > 0.2 else "negativo" if score < -0.2 else "neutro"
    return {"pos": pos, "neg": neg, "score": round(score, 2), "tom": label}
