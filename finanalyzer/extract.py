"""Etapa 2 — Extração estruturada.

Três modos (mesma saída `Extracao`, mesmo grounding/validação depois):

  reference : lê data/reference/extracao/<doc>.json (curadoria assistida,
              verificada por código). Roda sem chave de API.
  llm       : seleciona páginas por BM25 e pede ao LLM um JSON com
              página + trecho por valor; o grounding barra o que não existir.
  baseline  : regras/regex (ver baseline.py) — ponto de comparação "ML
              tradicional vs LLM".
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator

from .config import KNOWN_DOCS, Settings
from .ingest import Document
from .llm.client import LLMClient, UsageMeter
from .llm.lenient import lenient_validate, warn_all
from .llm.prompts import CAMPOS_EXTRACAO, SYSTEM_EXTRACT, USER_EXTRACT
from .retrieval import FIELD_QUERIES, BM25Index, compact_page_text
from .schema import Escala, Evidencia, Extracao, Metrica, Unidade, Valor
from .security import wrap_untrusted
from .text_utils import parse_ptbr_number

# --------------------------------------------------------------- referência


def load_reference(settings: Settings, doc_id: str) -> Extracao:
    path = settings.reference_dir / "extracao" / f"{doc_id}.json"
    return Extracao.model_validate_json(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------- LLM ---


class LLMCampo(BaseModel):
    campo: str
    periodo: str  # atual | anterior | variacao_pct | variacao_abs | alternativa | complementar
    valor: float
    escala: Escala = "mil"
    unidade: Unidade = "R$"
    rotulo: str | None = None
    pagina: int
    trecho: str

    @field_validator("valor", mode="before")
    @classmethod
    def _valor_texto(cls, v):  # modelos às vezes devolvem "1.234,5" como texto
        if isinstance(v, str):
            try:
                return parse_ptbr_number(v)
            except ValueError:
                return v  # deixa o pydantic rejeitar -> item descartado
        return v


class LLMNaoEncontrado(BaseModel):
    campo: str
    motivo: str = ""
    termos_buscados: list[str] = Field(default_factory=list)


class LLMEvid(BaseModel):
    pagina: int
    trecho: str


class LLMAnomalia(BaseModel):
    id: str = ""  # modelos omitem; o id é gerado em assemble_extracao
    severidade: str = "media"
    descricao: str = ""
    evidencias: list[LLMEvid] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _formato_plano(cls, d):
        """Aceita a variante "plana" {pagina, trecho, ...} (sem lista `evidencias`)."""
        if isinstance(d, dict) and not d.get("evidencias") and "pagina" in d and "trecho" in d:
            d = {**d, "evidencias": [{"pagina": d["pagina"], "trecho": d["trecho"]}]}
        if isinstance(d, dict) and not d.get("descricao"):
            d = {**d, "descricao": d.get("descrição") or d.get("texto") or d.get("trecho") or ""}
        return d


class LLMExtracaoOut(BaseModel):
    empresa: str = ""
    periodo_referencia: str = ""
    tipo_documento: str = ""
    moeda_escala_declarada: str = ""
    campos: list[LLMCampo] = Field(default_factory=list)
    nao_encontrados: list[LLMNaoEncontrado] = Field(default_factory=list)
    anomalias: list[LLMAnomalia] = Field(default_factory=list)


_OBRIGATORIAS = [
    "receita_liquida", "ebitda", "margem_ebitda", "lucro_liquido", "divida_liquida", "alavancagem", "fco", "capex",
    "ebit", "depreciacao_amortizacao", "caixa_equivalentes", "aplicacoes_financeiras", "divida_bruta",
]
_OPCIONAIS = ["receita_liquida_ex_construcao", "receita_construcao"]


def select_pages(doc: Document, index: BM25Index, k: int = 6, max_pages: int = 18) -> list[int]:
    """Páginas candidatas = união dos top-k por consulta numérica + páginas de
    demonstrações (cabeçalho com 'DEMONSTRAÇÕES'/'BALANÇO'). Ordenadas."""
    chosen: set[int] = set()
    for key in ("receita", "ebitda", "lucro", "divida", "fluxo"):
        for h in index.search(FIELD_QUERIES[key], k=k, doc_id=doc.doc_id):
            chosen.add(h.pagina)
    for p in doc.pages:
        head = " ".join(p.text.split("\n")[:6]).upper()
        if any(t in head for t in ("DEMONSTRAÇÕES DE RESULTADOS", "DEMONSTRAÇÕES DOS RESULTADOS", "DEMONSTRAÇÃO DO RESULTADO", "DEMONSTRAÇÕES DO RESULTADO", "FLUXOS DE CAIXA", "BALANÇOS PATRIMONIAIS")):
            chosen.add(p.number)
    ordered = sorted(chosen)
    if len(ordered) > max_pages:  # mantém as de maior score BM25 agregado
        score: dict[int, float] = {}
        for key in ("receita", "ebitda", "lucro", "divida", "fluxo"):
            for h in index.search(FIELD_QUERIES[key], k=30, doc_id=doc.doc_id):
                score[h.pagina] = score.get(h.pagina, 0) + h.score
        ordered = sorted(sorted(ordered, key=lambda n: -score.get(n, 0))[:max_pages])
    return ordered


def build_extract_prompt(doc: Document, pages: list[int]) -> str:
    campos = "\n".join(f"- {k}: {v}" for k, v in CAMPOS_EXTRACAO.items())
    blocos = "\n\n".join(wrap_untrusted(doc.doc_id, n, compact_page_text(doc.page(n).text)) for n in pages)
    return USER_EXTRACT.format(doc_id=doc.doc_id, campos=campos, paginas=blocos)


def assemble_extracao(doc_id: str, out: LLMExtracaoOut) -> Extracao:
    meta = KNOWN_DOCS.get(doc_id, {})
    buckets: dict[str, dict] = {}
    for c in out.campos:
        v = Valor(
            valor=c.valor, escala=c.escala, unidade=c.unidade, rotulo=c.rotulo,
            evidencia=Evidencia(documento=doc_id, pagina=c.pagina, trecho=c.trecho),
        )
        b = buckets.setdefault(c.campo, {"alternativas": [], "complementares": []})
        if c.campo == "capex" and c.periodo in ("atual", "anterior") and v.valor < 0:
            # No fluxo de caixa o capex é uma SAÍDA (vem entre parênteses). Convenção do pipeline:
            # capex em módulo (positivo), igual ao gabarito e às fórmulas derivadas.
            v.valor = abs(v.valor)
            b["observacao"] = "capex normalizado para módulo (saída de caixa impressa entre parênteses/negativa)"
        if c.periodo == "atual":
            b["atual"] = v
        elif c.periodo == "anterior":
            b["anterior"] = v
        elif c.periodo == "variacao_pct":
            b["variacao_reportada_pct"] = v
        elif c.periodo == "variacao_abs":
            b["variacao_reportada_abs"] = v
        elif c.periodo == "alternativa":
            b["alternativas"].append(v)
        elif c.periodo == "complementar":
            b["complementares"].append(v)
    nf = {n.campo: n for n in out.nao_encontrados}

    def metrica(nome: str, obrigatoria: bool) -> Metrica | None:
        b = buckets.get(nome)
        if b and (b.get("atual") or b.get("anterior")):
            return Metrica(status="encontrado", **b)
        if nome in nf or obrigatoria:
            n = nf.get(nome)
            return Metrica(
                status="nao_encontrado",
                motivo_ausencia=(n.motivo if n else "o modelo não retornou o campo nem justificou a ausência"),
                termos_verificados=(n.termos_buscados if n else []),
                complementares=(b or {}).get("complementares", []),
            )
        return None

    kwargs = {n: metrica(n, True) for n in _OBRIGATORIAS}
    kwargs.update({n: metrica(n, False) for n in _OPCIONAIS})
    anomalias = [
        {"id": a.id or f"{doc_id.upper()}-A{n}", "severidade": a.severidade if a.severidade in ("alta", "media", "baixa", "info") else "media",
         "descricao": a.descricao, "evidencias": [{"documento": doc_id, "pagina": e.pagina, "trecho": e.trecho} for e in a.evidencias]}
        for n, a in enumerate((x for x in out.anomalias if x.evidencias), start=1)
    ]
    return Extracao(
        doc_id=doc_id,
        empresa=out.empresa or meta.get("empresa", doc_id),
        periodo_referencia=out.periodo_referencia,
        tipo_documento=out.tipo_documento or meta.get("tipo", ""),
        moeda_escala_declarada=out.moeda_escala_declarada,
        anomalias_documento=anomalias,
        modo="llm",
        **kwargs,
    )


def extract_with_llm(doc: Document, index: BM25Index, llm: LLMClient, meter: UsageMeter, settings: Settings) -> Extracao:
    pages = select_pages(doc, index, k=settings.top_k_pages, max_pages=settings.max_pages)
    user = build_extract_prompt(doc, pages)
    res = llm.complete(SYSTEM_EXTRACT, user, settings.llm_max_tokens, json_schema=LLMExtracaoOut.model_json_schema())
    meter.add(f"extracao:{doc.doc_id}", res)
    if not res.data:
        raise RuntimeError(f"LLM não devolveu JSON para {doc.doc_id}: {res.text[:200]}")
    out, avisos = lenient_validate(LLMExtracaoOut, res.data, f"extracao:{doc.doc_id}")
    warn_all(avisos)
    return assemble_extracao(doc.doc_id, out)
