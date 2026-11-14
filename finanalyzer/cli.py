"""CLI:  python -m finanalyzer <comando>

  run          pipeline completo (ingestão -> extração -> validação -> Q&A -> relatório)
  ingest       só ingestão (gera data/cache/*.pages.json)
  eval         mede a qualidade da extração contra o gabarito (data/reference)
  eval-quali   mini-avaliação do qualitativo (recuperação de páginas + saída llm vs curadoria)
  ask          pergunta livre com citações (padrão: offline, sem LLM; --mode llm usa o modelo configurado)
  smoke-llm    testa suas credenciais/modelo com uma chamada mínima
  serve-mcp    expõe os dados extraídos via servidor MCP (stdio)
  scan         varredura de prompt injection nos PDFs
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from dataclasses import asdict

from .config import get_settings

EXIT_RETRY = 75  # EX_TEMPFAIL: o run_llm_full.sh só repete o passo quando vê este código


def _llm(settings):
    import os

    from .llm.client import CachingLLM, make_client

    client = make_client(settings.llm_provider, settings.llm_model)
    if os.getenv("LLM_CACHE", "1") == "0":
        return client
    return CachingLLM(client, settings.cache_dir / "llm")


def cmd_run(a) -> int:
    from .pipeline import run_pipeline

    s = get_settings()
    llm = _llm(s) if a.mode == "llm" else None
    run = run_pipeline(s, mode=a.mode, llm=llm, force_ingest=a.force_ingest, with_tables=not a.no_tables)
    nf = sum(len(v) for v in run.grounding_failures.values())
    print(f"✔ modo={run.mode} | {len(run.docs)} documentos | grounding: {sum(run.grounding_counts.values())} evidências, {nf} falhas | tempo {run.timings['total_s']}s")
    alerts = sum(1 for d in run.order for c in run.checks[d] if c.status == "alerta" and c.id != "C08")
    print(f"✔ alertas de validação: {alerts} | achados de segurança: {len(run.security_findings)}")
    print(f"✔ saídas em {s.output_dir}/  (relatorio.md, relatorio.html, respostas.md, extracao/*.json, qualitativo/*.json)")
    if run.meter and run.meter.calls:
        print(f"✔ LLM: {run.meter.calls} chamadas ({run.meter.cache_hits} do cache), {run.meter.input_tokens} tokens in / {run.meter.output_tokens} out, ~US$ {run.meter.cost_usd(s.price_in_per_mtok, s.price_out_per_mtok):.3f}")
    return 0


def cmd_ingest(a) -> int:
    from .pipeline import discover_docs

    s = get_settings()
    for d in discover_docs(s, force=True, with_tables=not a.no_tables).values():
        print(f"{d.doc_id}: {d.n_pages} páginas, {sum(len(p.tables) for p in d.pages)} tabelas, {d.ingest_seconds}s, sha256={d.sha256[:12]}")
    return 0


def cmd_eval(a) -> int:
    from .evaluate import evaluate_all
    from .extract import extract_with_llm, load_reference
    from .baseline import extract_baseline
    from .grounding import ground_extraction
    from .llm.client import UsageMeter
    from .pipeline import discover_docs
    from .retrieval import BM25Index

    s = get_settings()
    docs = discover_docs(s)
    refs = {d: load_reference(s, d) for d in docs if (s.reference_dir / "extracao" / f"{d}.json").exists()}
    preds = {}
    meter = UsageMeter()
    if a.mode == "llm":
        llm, idx = _llm(s), BM25Index(list(docs.values()))
    for d in refs:
        if a.mode == "baseline":
            preds[d] = extract_baseline(docs[d])
        else:
            preds[d] = extract_with_llm(docs[d], idx, llm, meter, s)
        ground_extraction(docs[d], preds[d])
    res = evaluate_all(preds, refs)
    res["modo"] = a.mode
    if meter.calls:
        res["uso_llm"] = {"chamadas": meter.calls, "tokens_in": meter.input_tokens, "chamadas_do_cache": meter.cache_hits, "tokens_out": meter.output_tokens, "segundos": round(meter.seconds, 1)}
    out = s.output_dir / f"avaliacao_{a.mode}.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    g = res["global"]
    print(f"Avaliação [{a.mode}] — recall {g['recall']:.1%} | precisão {g['precisao']:.1%} | página correta {g['pagina_correta_entre_corretos']:.1%} | alucinação {g['taxa_alucinacao']:.1%}")
    for e in res["erros"]:
        print("  ✗", e)
    print(f"→ {out}")
    return 0


def cmd_eval_quali(a) -> int:
    from .evaluate_quali import run_quali_eval
    from .pipeline import discover_docs

    s = get_settings()
    llm_dir = Path(a.llm_dir) if a.llm_dir else None
    res = run_quali_eval(discover_docs(s), s.reference_dir, llm_dir)
    print(f"Qualitativo — recuperação (páginas do gabarito que chegam ao prompt, teto {res['max_paginas']}): média {res['recuperacao_media']:.1%}")
    for d, v in res["recuperacao"].items():
        print(f"  {d}: {v['recall']:.1%} ({v['paginas_gabarito'] - len(v['faltando'])}/{v['paginas_gabarito']}) faltando {v['faltando']}")
    if res.get("llm_resumo"):
        print("Qualitativo — saída do LLM vs curadoria:", res["llm_resumo"])
        for d, v in res["llm"].items():
            print(f"  {d}: {v}")
    else:
        print("(sem saída llm em --llm-dir: rode `bash scripts/run_llm_full.sh` e repita com --llm-dir outputs_llm)")
    out = (llm_dir or s.output_dir) / "avaliacao_qualitativo.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"→ {out}")
    return 0


def cmd_ask(a) -> int:
    from .llm.client import UsageMeter
    from .pipeline import discover_docs, run_pipeline
    from .qa import Ctx, ask, ask_offline
    from .retrieval import BM25Index

    s = get_settings()
    docs = discover_docs(s)
    index = BM25Index(list(docs.values()))
    if a.mode == "offline":
        run = run_pipeline(s, mode="reference", write=False)
        res = ask_offline(a.pergunta, docs, index, Ctx(run.exts, run.ders, run.quals, run.checks))
    else:
        res = ask(a.pergunta, docs, index, _llm(s), UsageMeter(), s)
    print(res.resposta)
    print(f"\n[{res.modo}] citações verificadas: {len(res.citacoes_validas)} | descartadas: {len(res.citacoes_descartadas)}")
    for c in res.citacoes_validas[: a.max_citacoes]:
        print(f"  ✓ {c.documento} p.{c.pagina}: “{c.trecho[:110]}”")
    for c in res.citacoes_descartadas:
        print(f"  ✗ DESCARTADA (não confere com a página): {c.documento} p.{c.pagina}")
    return 0


def cmd_smoke(a) -> int:
    from .llm.client import make_client

    s = get_settings()
    llm = make_client(s.llm_provider, s.llm_model)  # sem cache: o teste precisa falar com o modelo de verdade
    # 512 (e não 64): modelos que "pensam" gastam parte do limite raciocinando e cortariam o JSON
    r = llm.complete("Responda apenas com JSON.", 'Devolva {"ok": true}', 512, json_schema={"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]})
    print(f"provedor={s.llm_provider} modelo={s.llm_model} -> {r.data} ({r.input_tokens} in / {r.output_tokens} out, {r.latency_s:.2f}s)")
    ok = bool(r.data and r.data.get("ok"))
    if not ok:
        print(f"✘ resposta não era o JSON esperado. Texto bruto (até 200 caracteres): {r.text[:200]!r}")
    return 0 if ok else 1


def cmd_scan(a) -> int:
    from .pipeline import discover_docs
    from .security import scan_document

    docs = discover_docs(get_settings())
    total = 0
    for d in docs.values():
        f = scan_document(d)
        total += len(f)
        print(f"{d.doc_id}: {len(f)} achados em {d.n_pages} páginas")
        for x in f:
            print("   ", asdict(x))
    return 0


def cmd_mcp(a) -> int:
    from .mcp_server import serve

    serve()
    return 0


def _setup_logging() -> None:
    """Logs legíveis no terminal (stderr). Nível via LOG_LEVEL (padrão WARNING = silencioso).
    O log estruturado completo vai sempre para outputs/logs/run.jsonl."""
    import logging
    import os

    logging.basicConfig(level=os.getenv("LOG_LEVEL", "WARNING").upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main(argv: list[str] | None = None) -> None:
    _setup_logging()
    p = argparse.ArgumentParser(prog="finanalyzer", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="pipeline completo")
    r.add_argument("--mode", choices=["reference", "llm", "baseline"], default="reference")
    r.add_argument("--force-ingest", action="store_true")
    r.add_argument("--no-tables", action="store_true", help="pula extract_tables do pdfplumber (mais rápido)")
    r.set_defaults(fn=cmd_run)
    i = sub.add_parser("ingest")
    i.add_argument("--no-tables", action="store_true")
    i.set_defaults(fn=cmd_ingest)
    e = sub.add_parser("eval", help="avalia extração vs gabarito")
    e.add_argument("--mode", choices=["baseline", "llm"], default="baseline")
    e.set_defaults(fn=cmd_eval)
    eq = sub.add_parser("eval-quali", help="mini-avaliação do qualitativo (recuperação + saída llm vs curadoria)")
    eq.add_argument("--llm-dir", default=None, help="pasta com qualitativo/*.json gerado em modo llm (ex.: outputs_llm)")
    eq.set_defaults(fn=cmd_eval_quali)
    q = sub.add_parser("ask", help="pergunta livre com citações (offline = sem LLM e sem chave)")
    q.add_argument("pergunta")
    q.add_argument("--mode", choices=["offline", "llm"], default="offline")
    q.add_argument("--max-citacoes", type=int, default=8)
    q.set_defaults(fn=cmd_ask)
    sub.add_parser("smoke-llm").set_defaults(fn=cmd_smoke)
    sub.add_parser("scan").set_defaults(fn=cmd_scan)
    sub.add_parser("serve-mcp").set_defaults(fn=cmd_mcp)
    a = p.parse_args(argv)
    from .llm.client import LLMHTTPError

    try:
        sys.exit(a.fn(a))
    except LLMHTTPError as e:  # falha TRANSITÓRIA do provedor (429/503/rede): código 75 = "tente de novo"
        print(f"ERRO (transitório) do provedor de LLM: {str(e)[:400]}", file=sys.stderr)
        sys.exit(EXIT_RETRY)
