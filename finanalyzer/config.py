"""Configuração central. Nenhuma credencial fica no código: tudo vem do
ambiente (.env, que está no .gitignore). Veja .env.example."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:  # python-dotenv é opcional em runtime
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass

ROOT = Path(__file__).resolve().parent.parent

# Metadados dos três documentos do teste. O doc_id é o nome do arquivo sem
# extensão (data/input/<doc_id>.pdf).
KNOWN_DOCS = {
    "light": {"empresa": "Light S.A.", "ticker": "LIGT3", "tipo": "DFs anuais + Relatório da Administração"},
    "millet": {"empresa": "Millet Participações S.A.", "ticker": None, "tipo": "DFs anuais + notas explicativas"},
    "brasal": {"empresa": "Brasal Brasília Holding S.A.", "ticker": None, "tipo": "DFs anuais + notas explicativas"},
}


@dataclass
class Settings:
    input_dir: Path = ROOT / "data" / "input"
    cache_dir: Path = ROOT / "data" / "cache"
    reference_dir: Path = ROOT / "data" / "reference"
    # OUTPUT_DIR (relativo à raiz do projeto ou absoluto) permite guardar execuções diferentes lado a lado
    output_dir: Path = field(default_factory=lambda: ROOT / (os.getenv("OUTPUT_DIR") or "outputs"))

    # --- LLM (somente modo `llm`) ---
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "anthropic"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "claude-sonnet-5-5"))
    llm_max_tokens: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "8192")))
    # preços em USD por 1M de tokens — SEMPRE confira na página oficial do provedor
    price_in_per_mtok: float = field(default_factory=lambda: float(os.getenv("PRICE_IN_PER_MTOK", "3.0")))
    price_out_per_mtok: float = field(default_factory=lambda: float(os.getenv("PRICE_OUT_PER_MTOK", "15.0")))

    # --- recuperação de páginas ---
    top_k_pages: int = field(default_factory=lambda: int(os.getenv("TOP_K_PAGES", "6")))
    max_pages: int = field(default_factory=lambda: int(os.getenv("MAX_PAGES", "18")))  # teto de páginas por chamada de LLM

    def ensure_dirs(self) -> None:
        for d in (self.cache_dir, self.output_dir):
            d.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    s = Settings()
    s.ensure_dirs()
    return s
