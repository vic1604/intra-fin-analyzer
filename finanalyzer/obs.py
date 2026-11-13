"""Observabilidade leve: logs estruturados (JSONL) + spans por etapa.

Cada execução grava `outputs/logs/run.jsonl` — uma linha JSON por evento:

    {"run_id": "...", "seq": 3, "ts": "...", "evento": "span", "etapa": "extracao_validacao",
     "doc": "light", "duracao_s": 0.42, "status": "ok", ...}

O que entra: nome da etapa, documento, duração, contagens (páginas, evidências,
alertas, chamadas/tokens de LLM). O que NUNCA entra: texto de PDF, prompts,
respostas do modelo, chaves ou cabeçalhos HTTP — o log é seguro para anexar a
um ticket. (Há teste automatizado para isso.)

Por que não OpenTelemetry/Application Insights já? Para um teste local, JSONL
é legível e dispensa infraestrutura. Os campos (run_id, etapa, duração) são os
mesmos de um span OTel; em produção na Azure basta trocar `Tracer._emit` por
um exporter do Azure Monitor OpenTelemetry (ver README, seção Azure).
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

log = logging.getLogger("finanalyzer")


class Tracer:
    def __init__(self, path: Path | None = None, run_id: str | None = None):
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self.path = path
        self.events: list[dict] = []
        self._seq = 0
        self._fh = None
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            self._fh = path.open("w", encoding="utf-8")  # um arquivo por execução (sobrescreve)

    # -- núcleo -----------------------------------------------------------
    def _emit(self, evento: str, **campos) -> dict:
        self._seq += 1
        rec = {
            "run_id": self.run_id,
            "seq": self._seq,
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "evento": evento,
            **campos,
        }
        self.events.append(rec)
        if self._fh is not None:
            self._fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            self._fh.flush()  # sobrevive a um crash no meio do pipeline
        log.info("%s %s", evento, {k: v for k, v in campos.items() if k in ("etapa", "doc", "duracao_s", "status")})
        return rec

    def event(self, evento: str, **campos) -> dict:
        return self._emit(evento, **campos)

    @contextmanager
    def span(self, etapa: str, **attrs) -> Iterator[dict]:
        """Mede uma etapa. O bloco pode preencher `extra` para adicionar contagens ao registro final."""
        extra: dict = {}
        t0 = time.perf_counter()
        status = "ok"
        try:
            yield extra
        except Exception as exc:  # registra e propaga: o log nunca engole erro
            status = "erro"
            extra["erro_tipo"] = type(exc).__name__
            raise
        finally:
            self._emit("span", etapa=etapa, duracao_s=round(time.perf_counter() - t0, 3), status=status, **attrs, **extra)

    def close(self) -> None:
        if self._fh is not None:
            self._fh.close()
            self._fh = None


class NullTracer(Tracer):
    """Mesma interface, sem arquivo (testes e `write=False`)."""

    def __init__(self) -> None:
        super().__init__(path=None)
