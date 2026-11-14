"""Recuperação de páginas (BM25 em memória).

Por que BM25 e não embeddings aqui?
  * 3 documentos / ~220 páginas cabem em memória; BM25 é determinístico,
    auditável (dá para explicar POR QUE a página foi escolhida) e não custa
    tokens nem exige serviço de embeddings.
  * Termos financeiros ("EBITDA", "dívida líquida", "Lei 14.385") são muito
    lexicais — BM25 acerta melhor que embeddings genéricos.
  * Em produção (milhares de docs) o caminho é busca híbrida (BM25 + vetor)
    no Azure AI Search — ver README, seção "Caminho para produção".
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from .ingest import Document
from .text_utils import normalize_for_search

_TOKEN = re.compile(r"[a-z0-9]{2,}")

# Consultas por campo: termos que costumam estar nas páginas certas.
FIELD_QUERIES: dict[str, str] = {
    "receita": "receita liquida receita operacional liquida demonstracao do resultado",
    "ebitda": "ebitda lajida margem ebitda depreciacao amortizacao resultado antes do resultado financeiro",
    "lucro": "lucro liquido prejuizo liquido do exercicio demonstracao do resultado",
    "divida": "divida liquida divida bruta emprestimos financiamentos caixa equivalentes alavancagem covenants",
    "fluxo": "fluxo de caixa atividades operacionais investimento aquisicao imobilizado intangivel capex",
    "qualitativo_motivos": "variacao resultado explicada principalmente reducao aumento provisao impairment queda",
    "qualitativo_riscos": "risco riscos incerteza covenants rating contingencias inadimplencia liquidez juros",
    "qualitativo_guidance": "perspectivas expectativa projecao proximos anos guidance meta renovacao",
    "qualitativo_eventos": "evento subsequente aquisicao reestruturacao lei revisao tarifaria mudanca contabil",
    # consultas focadas (itens que o LLM errava/omitia): variação de receita e perspectivas
    "qualitativo_receita": "receita liquida aumento reducao variacao em relacao ao exercicio anterior devido consolidacao mercado volume tarifa",
    "qualitativo_perspectivas": "perspectivas expectativa projecoes estimativas investimentos previstos plano de negocios proximo exercicio meta",
}


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(normalize_for_search(text))


@dataclass
class Hit:
    doc_id: str
    pagina: int
    score: float


class BM25Index:
    def __init__(self, docs: list[Document], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.keys: list[tuple[str, int]] = []
        self.tf: list[Counter] = []
        self.len: list[int] = []
        df: Counter = Counter()
        for d in docs:
            for p in d.pages:
                toks = tokenize(p.text)
                c = Counter(toks)
                self.keys.append((d.doc_id, p.number))
                self.tf.append(c)
                self.len.append(len(toks))
                df.update(c.keys())
        self.N = len(self.keys)
        self.avgdl = (sum(self.len) / self.N) if self.N else 0.0
        self.idf = {t: math.log(1 + (self.N - n + 0.5) / (n + 0.5)) for t, n in df.items()}

    def search(self, query: str, k: int = 6, doc_id: str | None = None) -> list[Hit]:
        q = tokenize(query)
        scores: list[tuple[float, int]] = []
        for i, c in enumerate(self.tf):
            if doc_id and self.keys[i][0] != doc_id:
                continue
            s = 0.0
            dl = self.len[i] or 1
            for t in q:
                f = c.get(t, 0)
                if not f:
                    continue
                s += self.idf.get(t, 0.0) * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
            if s > 0:
                scores.append((s, i))
        scores.sort(reverse=True)
        return [Hit(self.keys[i][0], self.keys[i][1], s) for s, i in scores[:k]]


def compact_page_text(text: str) -> str:
    """Colapsa espaços DENTRO de cada linha (preserva quebras de linha).
    Reduz tokens sem perder a ordem das colunas das tabelas."""
    lines = (re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n"))
    return "\n".join(ln for ln in lines if ln)
