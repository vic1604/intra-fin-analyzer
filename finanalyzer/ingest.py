"""Etapa 1 — Ingestão: PDF -> páginas com texto e tabelas.

Decisão (ver README, "Decisões e trade-offs"):
  * texto  : `pdftotext -layout` (poppler) preserva as colunas das
             demonstrações financeiras, o que é crítico para ler tabelas como
             linhas "RÓTULO  2022  2021". Fallback: pdfplumber.
  * tabelas: pdfplumber `extract_tables` (estruturado, usado para auditoria e
             como segunda opinião quando o layout de texto é ambíguo).
  * cache  : JSON por documento, chaveado pelo SHA-256 do PDF — reprocessar é
             grátis e o hash prova qual arquivo gerou a extração.

A numeração de páginas é SEMPRE a posição física no PDF (1 = capa). O número
impresso no rodapé pode diferir (ex.: Light mistura relatório da administração,
DFs e relatório do auditor, cada um com numeração própria).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .text_utils import normalize_text


@dataclass
class Page:
    number: int  # 1-based, posição física no PDF
    text: str  # texto com layout preservado (colunas alinhadas)
    tables: list[list[list[str | None]]] = field(default_factory=list)

    @property
    def text_norm(self) -> str:
        return normalize_text(self.text)


@dataclass
class Document:
    doc_id: str
    path: str
    sha256: str
    n_pages: int
    pages: list[Page]
    extractor: str = "pdftotext"
    ingest_seconds: float = 0.0

    def page(self, n: int) -> Page:
        if not 1 <= n <= self.n_pages:
            raise IndexError(f"{self.doc_id}: página {n} fora do intervalo 1..{self.n_pages}")
        return self.pages[n - 1]

    def to_json(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "path": self.path,
            "sha256": self.sha256,
            "n_pages": self.n_pages,
            "extractor": self.extractor,
            "ingest_seconds": self.ingest_seconds,
            "pages": [asdict(p) for p in self.pages],
        }

    @classmethod
    def from_json(cls, d: dict) -> "Document":
        return cls(
            doc_id=d["doc_id"],
            path=d["path"],
            sha256=d["sha256"],
            n_pages=d["n_pages"],
            extractor=d.get("extractor", "pdftotext"),
            ingest_seconds=d.get("ingest_seconds", 0.0),
            pages=[Page(**p) for p in d["pages"]],
        )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _text_pdftotext(path: Path) -> list[str]:
    out = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout
    pages = out.split("\f")
    if pages and not pages[-1].strip():  # pdftotext termina com \f
        pages = pages[:-1]
    return pages


def _text_pdfplumber(path: Path) -> list[str]:
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        return [(p.extract_text(layout=True) or "") for p in pdf.pages]


def _tables_pdfplumber(path: Path, n_pages: int) -> list[list[list[list[str | None]]]]:
    import pdfplumber

    out: list[list[list[list[str | None]]]] = []
    with pdfplumber.open(path) as pdf:
        for i in range(n_pages):
            try:
                tables = pdf.pages[i].extract_tables()
            except Exception:  # página corrompida não derruba o pipeline
                tables = []
            out.append(tables or [])
    return out


def ingest_pdf(path: Path, with_tables: bool = True) -> Document:
    t0 = time.perf_counter()
    path = Path(path)
    extractor = "pdftotext"
    if shutil.which("pdftotext"):
        texts = _text_pdftotext(path)
    else:  # pragma: no cover - ambiente sem poppler
        texts = _text_pdfplumber(path)
        extractor = "pdfplumber"
    tables = _tables_pdfplumber(path, len(texts)) if with_tables else [[] for _ in texts]
    pages = [Page(number=i + 1, text=t, tables=tb) for i, (t, tb) in enumerate(zip(texts, tables))]
    return Document(
        doc_id=path.stem.lower(),
        path=str(path.name),
        sha256=sha256_file(path),
        n_pages=len(pages),
        pages=pages,
        extractor=extractor,
        ingest_seconds=round(time.perf_counter() - t0, 2),
    )


def load_or_ingest(path: Path, cache_dir: Path, with_tables: bool = True, force: bool = False) -> Document:
    """Usa o cache se o hash do PDF bater; senão reprocessa."""
    path = Path(path)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{path.stem.lower()}.pages.json"
    if cache_file.exists() and not force:
        try:
            doc = Document.from_json(json.loads(cache_file.read_text(encoding="utf-8")))
            if doc.sha256 == sha256_file(path):
                return doc
        except Exception:  # cache inválido -> reprocessa
            pass
    doc = ingest_pdf(path, with_tables=with_tables)
    cache_file.write_text(json.dumps(doc.to_json(), ensure_ascii=False), encoding="utf-8")
    return doc
