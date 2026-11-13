"""Orquestração ponta a ponta com três papéis explícitos ("agentes"):

  ExtractorAgent  -> produz Extracao + Qualitativo (reference | llm | baseline)
  ValidatorAgent  -> grounding + validações determinísticas + derivados
  WriterAgent     -> respostas às perguntas + relatório (determinístico)

Por que um orquestrador simples em vez de LangGraph/AutoGen? O fluxo é linear
(extrai -> valida -> escreve), cada etapa é testável isoladamente e o fluxo
determinístico facilita auditoria. Se houvesse laços (ex.: "re-extrair campos
que falharam no grounding"), a migração natural é LangGraph ou o Azure AI
Foundry Agent Service — ver README.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .config import KNOWN_DOCS, Settings
from .derive import Derivado
from .export import to_deliverable
from .extract import extract_with_llm, load_reference
from .baseline import extract_baseline
from .grounding import GroundingFailure, drop_unverified_items, ground_extraction, ground_qualitativo
from .ingest import Document, load_or_ingest
from .llm.client import LLMClient, UsageMeter
from .ml_baseline import analisar as analisar_ml, comparar_tom
from .obs import NullTracer, Tracer
from .qa import Ctx, Resposta, answer_standard_questions
from .qualitative import analyze_with_llm, load_reference_quali
from .report import build_report_html, build_report_md
from .retrieval import BM25Index
from .schema import Evidencia, Extracao, Qualitativo
from .security import SecurityFinding, scan_document
from .validate import Check, validate_extraction


@dataclass
class RunResult:
    settings: Settings
    mode: str
    docs: dict[str, Document]
    exts: dict[str, Extracao] = field(default_factory=dict)
    quals: dict[str, Qualitativo] = field(default_factory=dict)
    ders: dict[str, dict[str, Derivado]] = field(default_factory=dict)
    checks: dict[str, list[Check]] = field(default_factory=dict)
    grounding_failures: dict[str, list[GroundingFailure]] = field(default_factory=dict)
    grounding_counts: dict[str, int] = field(default_factory=dict)
    security_findings: list[SecurityFinding] = field(default_factory=list)
    answers: list[Resposta] = field(default_factory=list)
    meter: UsageMeter | None = None
    timings: dict[str, float] = field(default_factory=dict)
    ml: dict | None = None
    trace: Tracer | None = None

    @property
    def order(self) -> list[str]:
        known = [d for d in ("light", "millet", "brasal") if d in self.docs]
        return known + [d for d in self.docs if d not in known]


def discover_docs(settings: Settings, force: bool = False, with_tables: bool = True) -> dict[str, Document]:
    pdfs = sorted(settings.input_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"Nenhum PDF em {settings.input_dir}. Copie light.pdf, millet.pdf e brasal.pdf para essa pasta.")
    return {p.stem.lower(): load_or_ingest(p, settings.cache_dir, with_tables=with_tables, force=force) for p in pdfs}


def _count_evidences(ext: Extracao | None = None, q: Qualitativo | None = None) -> int:
    n = 0
    if ext:
        for m in ext.metricas().values():
            for v in [m.atual, m.anterior, m.variacao_reportada_pct, m.variacao_reportada_abs, *m.alternativas, *m.complementares]:
                n += 1 if v is not None else 0
        n += sum(len(a.evidencias) for a in ext.anomalias_documento)
    if q:
        for it in [*q.motivos_resultado, *q.riscos, *q.guidance, *q.eventos_relevantes, *([q.motivo_variacao_receita] if q.motivo_variacao_receita else [])]:
            n += len(it.evidencias)
        n += len(q.tom_evidencias)
    return n


class ExtractorAgent:
    def __init__(self, settings: Settings, mode: str, llm: LLMClient | None, meter: UsageMeter, index: BM25Index | None):
        self.s, self.mode, self.llm, self.meter, self.index = settings, mode, llm, meter, index

    def extract(self, doc: Document) -> Extracao:
        if self.mode == "reference":
            return load_reference(self.s, doc.doc_id)
        if self.mode == "baseline":
            return extract_baseline(doc)
        if self.mode == "llm":
            assert self.llm and self.index
            return extract_with_llm(doc, self.index, self.llm, self.meter, self.s)
        raise ValueError(f"modo desconhecido: {self.mode}")

    def qualitative(self, doc: Document) -> Qualitativo:
        if self.mode in ("reference", "baseline"):
            return load_reference_quali(self.s, doc.doc_id)
        assert self.llm and self.index
        return analyze_with_llm(doc, self.index, self.llm, self.meter, self.s)


class ValidatorAgent:
    def validate(self, doc: Document, ext: Extracao, q: Qualitativo):
        f1 = ground_extraction(doc, ext)
        f2 = ground_qualitativo(doc, q)
        checks, ders = validate_extraction(ext)
        if f1:
            checks.append(Check("C00", doc.doc_id, "grounding", "alerta", "alta", f"{len(f1)} evidência(s) da extração falharam no grounding.", sorted({f.pagina for f in f1})))
        q = drop_unverified_items(q)
        return checks, ders, f1 + f2, q


class WriterAgent:
    def write(self, run: RunResult) -> tuple[list[Resposta], str, str]:
        ctx = Ctx(run.exts, run.ders, run.quals, run.checks)
        answers = answer_standard_questions(ctx)
        md = build_report_md(run, answers)
        return answers, md, build_report_html(md)


def run_pipeline(settings: Settings, mode: str = "reference", llm: LLMClient | None = None, force_ingest: bool = False, with_tables: bool = True, write: bool = True, tracer: Tracer | None = None) -> RunResult:
    t0 = time.perf_counter()
    tr = tracer or (Tracer(settings.output_dir / "logs" / "run.jsonl") if write else NullTracer())
    tr.event("run_inicio", modo=mode, provedor=(settings.llm_provider if mode == "llm" else None), modelo=(settings.llm_model if mode == "llm" else None))
    try:
        with tr.span("ingestao") as ex:
            docs = discover_docs(settings, force=force_ingest, with_tables=with_tables)
            ex.update(documentos=len(docs), paginas=sum(d.n_pages for d in docs.values()))
        run = RunResult(settings=settings, mode=mode, docs=docs, meter=UsageMeter(), trace=tr)
        run.timings["ingestao_s"] = round(time.perf_counter() - t0, 2)

        with tr.span("seguranca_scan") as ex:  # segurança antes de qualquer LLM
            for d in docs.values():
                run.security_findings += scan_document(d)
            ex.update(achados=len(run.security_findings))

        index = BM25Index(list(docs.values())) if mode == "llm" else None
        extractor, validator, writer = ExtractorAgent(settings, mode, llm, run.meter, index), ValidatorAgent(), WriterAgent()
        for doc_id in run.order:
            doc = docs[doc_id]
            if doc_id not in KNOWN_DOCS and mode == "reference":
                continue  # sem gabarito para documentos desconhecidos
            t1 = time.perf_counter()
            n_calls = len(run.meter.log)
            with tr.span("extracao", doc=doc_id, modo=mode) as ex:
                ext = extractor.extract(doc)
                ex.update(campos_encontrados=sum(1 for m in ext.metricas().values() if m.status == "encontrado"))
            with tr.span("qualitativo", doc=doc_id, modo=mode):
                q = extractor.qualitative(doc)
            for c in run.meter.log[n_calls:]:  # uma linha por chamada de LLM (sem prompt/resposta)
                tr.event("llm_chamada", doc=doc_id, **c)
            with tr.span("validacao", doc=doc_id) as ex:
                checks, ders, fails, q = validator.validate(doc, ext, q)
                ex.update(alertas=sum(1 for c in checks if c.status == "alerta"), falhas_grounding=len(fails))
            run.exts[doc_id], run.quals[doc_id], run.ders[doc_id], run.checks[doc_id] = ext, q, ders, checks
            run.grounding_failures[doc_id] = fails
            run.grounding_counts[doc_id] = _count_evidences(ext, q)
            run.timings[f"extracao_validacao_{doc_id}_s"] = round(time.perf_counter() - t1, 2)
        run.docs = {k: v for k, v in docs.items() if k in run.exts}

        t2 = time.perf_counter()
        with tr.span("ml_tradicional") as ex:
            textos = {d: [c.mensagem for c in run.checks[d] if c.status == "alerta"] + [a.descricao for a in run.exts[d].anomalias_documento] for d in run.order}
            run.ml = {"anomalias": analisar_ml({d: run.docs[d] for d in run.order}, textos), "tom": comparar_tom(run.quals)}
        run.timings["ml_tradicional_s"] = round(time.perf_counter() - t2, 2)

        with tr.span("relatorio") as ex:
            run.answers, md, html = writer.write(run)
            ex.update(respostas=len(run.answers), tamanho_md=len(md))
        run.timings["total_s"] = round(time.perf_counter() - t0, 2)
        if write:
            write_outputs(run, md, html)
        tr.event("run_fim", status="ok", total_s=run.timings["total_s"], chamadas_llm=run.meter.calls,
                 tokens_in=run.meter.input_tokens, tokens_out=run.meter.output_tokens)
        return run
    except Exception as exc:
        tr.event("run_fim", status="erro", erro_tipo=type(exc).__name__)
        raise
    finally:
        tr.close()


def write_outputs(run: RunResult, md: str, html: str) -> None:
    out = run.settings.output_dir
    (out / "extracao").mkdir(parents=True, exist_ok=True)
    (out / "qualitativo").mkdir(parents=True, exist_ok=True)
    for d in run.order:
        (out / "extracao" / f"{d}.json").write_text(json.dumps(to_deliverable(run.exts[d], run.ders[d], run.checks[d]), ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "qualitativo" / f"{d}.json").write_text(run.quals[d].model_dump_json(indent=2, exclude_none=True), encoding="utf-8")
    (out / "respostas.json").write_text(json.dumps([asdict(a) for a in run.answers], ensure_ascii=False, indent=2), encoding="utf-8")
    respostas_md = "# Respostas às 5 perguntas\n\n" + "\n\n".join(
        f"## {a.numero}. {a.pergunta}\n\n{a.resposta}\n\n**Fontes:** " + "; ".join(f"{f.documento} p.{f.pagina}" for f in a.fontes) for a in run.answers
    )
    (out / "respostas.md").write_text(respostas_md + "\n", encoding="utf-8")
    (out / "relatorio.md").write_text(md, encoding="utf-8")
    (out / "relatorio.html").write_text(html, encoding="utf-8")
    manifest = {
        "modo": run.mode,
        "documentos": {d: {"arquivo": run.docs[d].path, "sha256": run.docs[d].sha256, "paginas": run.docs[d].n_pages, "ingestao_s": run.docs[d].ingest_seconds} for d in run.order},
        "tempos_s": run.timings,
        "grounding": {d: {"evidencias": run.grounding_counts[d], "falhas": len(run.grounding_failures[d])} for d in run.order},
        "seguranca_achados": len(run.security_findings),
        "llm": None if not (run.meter and run.meter.calls) else {
            "provedor": run.settings.llm_provider, "modelo": run.settings.llm_model, "chamadas": run.meter.calls, "chamadas_do_cache": run.meter.cache_hits,
            "tokens_in": run.meter.input_tokens, "tokens_out": run.meter.output_tokens, "segundos": round(run.meter.seconds, 1),
            "custo_usd_estimado": round(run.meter.cost_usd(run.settings.price_in_per_mtok, run.settings.price_out_per_mtok), 4), "log": run.meter.log,
        },
    }
    if run.ml:
        (out / "ml_tradicional.json").write_text(json.dumps(run.ml, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
