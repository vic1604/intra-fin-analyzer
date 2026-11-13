"""Servidor MCP (diferencial): expõe os dados JÁ extraídos e verificados para
qualquer cliente MCP (Claude Desktop, VS Code, Azure AI Foundry agents).

Somente leitura; não executa LLM, não recebe texto do usuário que vire comando
e só lê de outputs/ e data/cache/. Rode:  python -m finanalyzer serve-mcp
(Antes: python -m finanalyzer run)
"""

from __future__ import annotations

import json
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from .config import get_settings
from .ingest import Document
from .pipeline import discover_docs
from .retrieval import BM25Index

server = MCPServer("intra-fin-analyzer")
_state: dict = {}


def _out() -> Path:
    return get_settings().output_dir


def _load(rel: str):
    p = _out() / rel
    if not p.exists():
        raise FileNotFoundError(f"{rel} não existe. Rode primeiro: python -m finanalyzer run")
    return json.loads(p.read_text(encoding="utf-8"))


def _company(c: str) -> str:
    c = c.strip().lower()
    if c not in {"light", "millet", "brasal"} and not (_out() / "extracao" / f"{c}.json").exists():
        raise ValueError("empresa desconhecida; use list_companies")
    return c


def _index() -> tuple[dict[str, Document], BM25Index]:
    if "idx" not in _state:
        docs = discover_docs(get_settings())
        _state["docs"], _state["idx"] = docs, BM25Index(list(docs.values()))
    return _state["docs"], _state["idx"]


@server.tool()
def list_companies() -> list[str]:
    """Empresas com extração disponível."""
    return sorted(p.stem for p in (_out() / "extracao").glob("*.json"))


@server.tool()
def get_indicators(company: str) -> dict:
    """JSON de entrega da empresa: indicadores com página+trecho, derivados rotulados, validações."""
    return _load(f"extracao/{_company(company)}.json")


@server.tool()
def get_alerts(company: str, min_severity: str = "media") -> list[dict]:
    """Alertas de validação (nunca corrigidos em silêncio) a partir de uma severidade mínima: alta|media|baixa|info."""
    ordem = {"alta": 0, "media": 1, "baixa": 2, "info": 3}
    lim = ordem.get(min_severity, 1)
    d = _load(f"extracao/{_company(company)}.json")
    return [c for c in d["validacoes"] if c.get("status") == "alerta" and ordem.get(c.get("severidade"), 3) <= lim]


@server.tool()
def get_qualitative(company: str) -> dict:
    """Análise qualitativa (motivos, riscos, guidance, eventos, tom) com evidências."""
    return _load(f"qualitativo/{_company(company)}.json")


@server.tool()
def get_answers() -> list[dict]:
    """As 5 respostas padrão com citações documento+página."""
    return _load("respostas.json")


@server.tool()
def search_pages(query: str, company: str = "", k: int = 5) -> list[dict]:
    """Busca BM25 nas páginas dos PDFs; devolve página e prévia (para o cliente conferir a fonte)."""
    docs, idx = _index()
    k = max(1, min(int(k), 10))
    hits = idx.search(query[:300], k=k, doc_id=_company(company) if company else None)
    return [{"documento": h.doc_id, "pagina": h.pagina, "score": round(h.score, 2), "previa": " ".join(docs[h.doc_id].pages[h.pagina - 1].text.split())[:300]} for h in hits]


def serve() -> None:
    server.run("stdio")
