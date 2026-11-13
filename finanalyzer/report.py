"""Etapa 6 — Relatório consolidado (Markdown + HTML).

O relatório é montado por CÓDIGO a partir de dados já verificados (o "agente
redator" é determinístico por padrão): nenhum número novo é introduzido na
redação. Todo alerta de validação/grounding/segurança aparece no corpo do
documento — nada é corrigido em silêncio.
"""

from __future__ import annotations

import re
from datetime import datetime

import markdown as md_lib

from .derive import variation_pct
from .fmt import DOC_NOME, cite, mi, mult, n, pct
from .qa import Resposta
from .schema import CATEGORIAS_RISCO, CAMPOS_ENTREGA, Extracao
from .text_utils import to_base

SEV_ORD = {"alta": 0, "media": 1, "baixa": 2, "info": 3}
SEV_ICON = {"alta": "🔴 alta", "media": "🟠 média", "baixa": "🟡 baixa", "info": "⚪ info"}



def _first_sentence(txt: str) -> str:
    """Primeira frase, sem cortar números como 'R$1.180' ou 'R$199.3'."""
    m = re.search(r"\.(?=\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ])", txt)
    out = txt[: m.start() + 1] if m else txt
    return out if out.endswith((".", "!", "?")) else out + "."

def _clip(txt: str, limit: int) -> str:
    """Corta em fronteira de palavra (nunca no meio de um número) e acrescenta '…'."""
    txt = " ".join(txt.split())
    if len(txt) <= limit:
        return txt
    cut = txt[:limit]
    for sep in ("; ", " — ", ": ", ", ", " "):
        i = cut.rfind(sep)
        if i >= limit * 0.5:
            cut = cut[:i]
            break
    return cut.rstrip(" ,;:—-.") + "…"


MAX_LINHA_RESUMO = 150  # caracteres visíveis por linha do resumo executivo (testado)


def _mil(v) -> float:
    return to_base(v.valor, v.escala) / 1e3


def _pg(v) -> int:
    return v.evidencia.pagina


# ------------------------------------------------------------- resumo ------
def exec_summary(run, d: str) -> list[str]:
    ext: Extracao = run.exts[d]
    der = run.ders[d]
    q = run.quals[d]
    L: list[str] = []
    rl = ext.receita_liquida
    var = variation_pct(rl)
    flag = ""
    if any(a.id == "MILLET-A1" for a in ext.anomalias_documento):
        flag = " (⚠ 2021 parcial: Alibra só desde jun/21)"
    L.append(f"Receita líquida de **{mi(_mil(rl.atual))}** em 2022 ({pct(var, sign=True)} vs 2021){flag} {cite(d, _pg(rl.atual))}.")
    ed, md_ = der["ebitda_derivado"], der["margem_ebitda_derivada"]
    if ext.ebitda.status == "encontrado":
        L.append(
            f"EBITDA: texto cita R$ {n(ext.ebitda.atual.valor, 0)} mi, mas **recomposto pelas DFs = {mi(ed.atual)}** — diverge, ver alertas {cite(d, _pg(ext.ebitda.atual))}."
        )
    else:
        L.append(f"EBITDA **não publicado**; derivado (EBIT + D&A) = {mi(ed.atual)}, margem ≈ {pct(md_.atual)} (calculado ¤) {cite(d, _pg(ext.ebit.atual))}.")
    ll = ext.lucro_liquido
    lv = variation_pct(ll)
    lv_txt = f"{pct(lv, sign=True)} vs 2021" if lv is not None else f"vs {mi(_mil(ll.anterior))} em 2021 (variação % n.s.)"
    L.append(f"Lucro líquido de **{mi(_mil(ll.atual))}** ({lv_txt}) {cite(d, _pg(ll.atual))}.")
    if ext.divida_liquida.status == "encontrado":
        alav = ext.alavancagem.atual.valor if ext.alavancagem.status == "encontrado" else None
        L.append(f"Dívida líquida de **{mi(_mil(ext.divida_liquida.atual))}**" + (f"; alavancagem de covenants **{mult(alav)}**" if alav else "") + f" {cite(d, _pg(ext.divida_liquida.atual))}.")
    else:
        dd = der["divida_liquida_derivada"].atual
        L.append(f"Dívida líquida **não publicada**; derivada = **{mi(dd)}** (caixa líquido; calculado ¤) {cite(d, _pg(ext.divida_bruta.atual))}.")
    top = sorted([a for a in ext.anomalias_documento if a.severidade == "alta"], key=lambda a: a.id)
    tom = f"Tom: **{q.tom}** (confiança {q.confianca_tom})."
    if top:
        L.append(f"{tom} Alerta: {_clip(_first_sentence(top[0].descricao), 85)} {cite(d, top[0].evidencias[0].pagina)}")
    else:
        L.append(tom)
    return L[:5]


# ---------------------------------------------------------- tabela ---------
def _cell_money(m, periodo="atual", scale_note: str = "") -> str:
    v = getattr(m, periodo) if m and m.status == "encontrado" else None
    if v is None:
        return "não encontrado"
    return f"{n(_mil(v) / 1e3, 1)} · p.{_pg(v)}"


def comparative_table(run) -> str:
    docs = run.order
    hdr = "| Indicador (R$ milhões, salvo indicação) | " + " | ".join(DOC_NOME[d] for d in docs) + " |"
    sep = "|---|" + "---|" * len(docs)
    rows = [hdr, sep]

    def row(label, fn):
        rows.append(f"| {label} | " + " | ".join(fn(d) for d in docs) + " |")

    def var_cell(d, nome="receita_liquida"):
        m = getattr(run.exts[d], nome)
        v = variation_pct(m)
        mark = ""
        if nome == "receita_liquida":
            if d == "millet":
                mark = " ⚠¹"
            if d == "brasal":
                mark = " ⚠²"
        return (pct(v, sign=True) if v is not None else "n.s.") + mark

    row("**Período**", lambda d: "FY2022 vs FY2021")
    row("Receita líquida 2022", lambda d: _cell_money(run.exts[d].receita_liquida))
    row("Receita líquida 2021", lambda d: _cell_money(run.exts[d].receita_liquida, "anterior"))
    row("Variação da receita (calculada)", var_cell)

    def ebitda_pub(d):
        m = run.exts[d].ebitda
        if m.status != "encontrado":
            return "não encontrado"
        return f"{n(m.atual.valor, 0)} (texto, sem sinal) ⚠³ · p.{_pg(m.atual)}"

    row("EBITDA publicado", ebitda_pub)
    row("EBITDA derivado (EBIT + D&A)¤", lambda d: f"{n(run.ders[d]['ebitda_derivado'].atual / 1e3, 1)}" if run.ders[d]["ebitda_derivado"].atual is not None else "n/d")
    row("Margem EBITDA publicada", lambda d: "não encontrado" if run.exts[d].margem_ebitda.status != "encontrado" else pct(run.exts[d].margem_ebitda.atual.valor))
    row("Margem EBITDA derivada¤ (2022 / 2021)", lambda d: f"{pct(run.ders[d]['margem_ebitda_derivada'].atual)} / {pct(run.ders[d]['margem_ebitda_derivada'].anterior)}")
    row("Lucro líquido 2022", lambda d: _cell_money(run.exts[d].lucro_liquido))
    row("Lucro líquido 2021", lambda d: _cell_money(run.exts[d].lucro_liquido, "anterior"))
    row("Variação do lucro (calculada)", lambda d: var_cell(d, "lucro_liquido"))

    def dl(d):
        m = run.exts[d].divida_liquida
        if m.status == "encontrado":
            return f"{n(_mil(m.atual) / 1e3, 1)} · p.{_pg(m.atual)}"
        return f"não encontrado (derivada¤: {n(run.ders[d]['divida_liquida_derivada'].atual / 1e3, 1)})"

    row("Dívida líquida 2022", dl)

    def lev(d):
        m = run.exts[d].alavancagem
        if m.status == "encontrado":
            return f"**{mult(m.atual.valor)}** (covenants) · p.{_pg(m.atual)}"
        a = run.ders[d]["alavancagem_derivada"].atual
        dd = run.ders[d]["divida_liquida_derivada"].atual
        if dd is not None and dd < 0:
            return "não encontrado (caixa líquido¤)"
        return f"não encontrado (derivada¤: {mult(a)})"

    row("Dívida líquida / EBITDA", lev)
    row("Fluxo de caixa operacional 2022", lambda d: _cell_money(run.exts[d].fco))

    def cap(d):
        m = run.exts[d].capex
        if m.status == "encontrado":
            return f"{n(_mil(m.atual) / 1e3, 1)} · p.{_pg(m.atual)}"
        cd = run.ders[d].get("capex_caixa_derivado")
        return f"não encontrado (soma das linhas de caixa¤: {n(cd.atual / 1e3, 1)})" if cd else "não encontrado"

    row("Capex 2022", cap)
    notes = [
        "",
        "¤ **Calculado pelo pipeline** a partir de linhas do documento (fórmulas na seção *Anexo A*); não é número publicado pela empresa.",
        "¹ Millet: a Alibra foi consolidada só a partir de 18/06/2021; a variação não é comparável (base comparável ≈ +45%).",
        "² Brasal: coluna 2021 marcada como *não auditada* pelo auditor.",
        "³ Light: o texto imprime R$ 1.180 mi **sem sinal**; as DFs (EBIT + D&A) dão −R$ 1.179,6 mi. Light capex: 'investimentos' da administração (competência); capex de caixa = soma das duas linhas do DFC.",
        "Células com `· p.N` indicam a página do PDF (1 = capa) onde o valor foi encontrado e verificado.",
    ]
    return "\n".join(rows + notes)


# ---------------------------------------------------------- qualitativo ----
def _items_md(d: str, items) -> list[str]:
    out = []
    for it in items:
        pgs = ", ".join(f"p.{p}" for p in sorted({e.pagina for e in it.evidencias}))
        out.append(f"- {it.texto} *[{DOC_NOME[d]} {pgs}]*")
    return out


def qualitative_section(run) -> str:
    L = []
    for d in run.order:
        q = run.quals[d]
        L.append(f"### {DOC_NOME[d]}")
        L.append(f"*Fonte da análise:* {q.fonte_qualitativa}. {q.nota_cobertura}")
        L.append("\n**Principais motivos do resultado**")
        L += _items_md(d, q.motivos_resultado) or ["- Não encontrado."]
        L.append("\n**Motivo da variação da receita**")
        L += _items_md(d, [q.motivo_variacao_receita]) if q.motivo_variacao_receita else ["- Não encontrado no documento."]
        L.append("\n**Riscos e pontos de atenção**")
        for r in q.riscos:
            pgs = ", ".join(f"p.{p}" for p in sorted({e.pagina for e in r.evidencias}))
            cat = f"`{CATEGORIAS_RISCO.get(r.categoria, r.categoria)}` " if r.categoria else ""
            L.append(f"- {cat}{r.texto} *[{DOC_NOME[d]} {pgs}]*")
        L.append("\n**Guidance / perspectivas**")
        if not q.guidance_numerico_encontrado:
            L.append("- **Guidance numérico: não encontrado.**")
        L += _items_md(d, q.guidance)
        L.append("\n**Eventos relevantes** (aquisições, reestruturações, contingências, mudanças contábeis)")
        L += _items_md(d, q.eventos_relevantes) or ["- Nenhum encontrado."]
        pgs = ", ".join(f"p.{p}" for p in sorted({e.pagina for e in q.tom_evidencias}))
        L.append(f"\n**Tom geral da administração: {q.tom.upper()}** (confiança {q.confianca_tom}) — {q.tom_justificativa} *[{DOC_NOME[d]} {pgs}]*\n")
    return "\n".join(L)


# ---------------------------------------------------------------- alertas --
def alerts_section(run) -> str:
    L = []
    L.append("### Inconsistências e alertas de validação\n")
    L.append("| Sev. | Empresa | Check | Campo | Descrição | Págs. |")
    L.append("|---|---|---|---|---|---|")
    rows = []
    for d in run.order:
        for c in run.checks[d]:
            if c.status == "alerta" and c.id != "C08":
                rows.append((SEV_ORD.get(c.severidade, 9), d, c))
    rows.sort(key=lambda r: (r[0], run.order.index(r[1])))
    for _, d, c in rows:
        pgs = ", ".join(map(str, c.paginas)) or "—"
        L.append(f"| {SEV_ICON.get(c.severidade, c.severidade)} | {DOC_NOME[d]} | {c.id} | `{c.campo}` | {c.mensagem} | {pgs} |")
    ok_n = sum(1 for d in run.order for c in run.checks[d] if c.status == "ok")
    info = [(d, c) for d in run.order for c in run.checks[d] if c.status == "info"]
    L.append(f"\n**{ok_n} verificações passaram** (variações, margem, dívida líquida = bruta − caixa, reconciliação com notas). Notas informativas:")
    for d, c in info:
        L.append(f"- *{DOC_NOME[d]} · {c.id} · {c.campo}:* {c.mensagem}")

    L.append("\n### Informações não encontradas nos documentos\n")
    L.append("| Empresa | Campo | Motivo | Ausência re-verificada por busca no PDF |")
    L.append("|---|---|---|---|")
    for d in run.order:
        ext = run.exts[d]
        for nome in CAMPOS_ENTREGA:
            m = getattr(ext, nome)
            if m.status == "nao_encontrado":
                termos = ", ".join(f"“{t}”" for t in m.termos_verificados) if m.termos_verificados else "—"
                L.append(f"| {DOC_NOME[d]} | `{nome}` | {m.motivo_ausencia or ''} | {termos} |")
    L.append("\n*Campos 'não encontrado' **não foram estimados**. Quando útil à comparação, o relatório mostra um indicador derivado, sempre rotulado como calculado (¤).*")

    L.append("\n### Verificação de ancoragem (grounding)\n")
    tot = sum(run.grounding_counts[d] for d in run.order)
    fails = [f for d in run.order for f in run.grounding_failures[d]]
    if not fails:
        L.append(f"✅ **{tot} evidências verificadas, 0 falhas**: todo trecho citado existe literalmente na página indicada e contém o número extraído.")
    else:
        L.append(f"⚠️ **{len(fails)} falhas de ancoragem de {tot} evidências** — os itens abaixo foram marcados como *não verificado* e NÃO entram nas conclusões:")
        for f in fails:
            L.append(f"- {DOC_NOME.get(f.doc_id, f.doc_id)} p.{f.pagina} · `{f.campo}` · {f.motivo}")

    L.append("\n### Segurança do conteúdo (varredura de prompt injection)\n")
    sf = run.security_findings
    if not sf:
        L.append(f"✅ Nenhum padrão suspeito em {sum(run.docs[d].n_pages for d in run.order)} páginas.")
    else:
        L.append(f"⚠️ {len(sf)} achados — o conteúdo é tratado como dado e nunca como instrução:")
        for f in sf[:20]:
            L.append(f"- {DOC_NOME.get(f.doc_id, f.doc_id)} p.{f.pagina}: {f.tipo} — “{f.trecho}”")
    return "\n".join(L)


def annex_derivations(run) -> str:
    L = ["Cada indicador **derivado** lista fórmula e as entradas (página + trecho do PDF).\n"]
    for d in run.order:
        L.append(f"**{DOC_NOME[d]}**\n")
        for nome, dv in run.ders[d].items():
            fmtv = (lambda x: pct(x)) if dv.unidade == "%" else (lambda x: mult(x)) if dv.unidade == "x" else (lambda x: mi(x))
            L.append(f"- `{nome}` = {dv.formula}: 2022 = **{fmtv(dv.atual)}**, 2021 = {fmtv(dv.anterior)}" + (f". {dv.nota}" if dv.nota else ""))
            for e in [x for x in dv.entradas if x.periodo == "atual"]:
                L.append(f"    - {e.campo}: {mi(e.valor_mil)} — {cite(d, e.pagina)} “{e.trecho[:110]}{'…' if len(e.trecho) > 110 else ''}”")
        L.append("")
    return "\n".join(L)



def annex_ml(run) -> str:
    ml = getattr(run, "ml", None)
    if not ml:
        return "_Não executado._"
    an, tom = ml["anomalias"], ml["tom"]
    L = [
        "Comparação entre a abordagem **estatística / ML clássico** (sem LLM, sem rótulos) e as **regras + leitura do documento** usadas no restante do relatório. "
        "O detector olha as linhas das demonstrações (DRE, balanço, fluxo de caixa) e procura variações atípicas **dentro de cada documento**: "
        f"z-score robusto ({an['metodo']['zscore_robusto']}) e Isolation Forest. Ele **não explica** nada e **não vê texto**; serve para gerar candidatos a revisão.\n",
        "| Documento | Linhas pontuadas | Sinalizadas (z-score) | Sinalizadas (Isolation Forest) | Ambos | Coincidem com alerta existente¹ | Inversões de sinal² |",
        "|---|---|---|---|---|---|---|",
    ]
    for d in run.order:
        v = an["documentos"][d]
        L.append(f"| {DOC_NOME[d]} | {v['linhas_pontuadas']} | {v['sinalizadas_zscore']} | {v['sinalizadas_iforest'] if v['sinalizadas_iforest'] is not None else 'n/d (scikit-learn ausente)'} | {v['sinalizadas_ambos']} | {v['sinalizadas_que_coincidem_com_alerta_existente']} | {v['inversoes_de_sinal']} |")
    L.append("")
    for d in run.order:
        top = an["documentos"][d]["top"][:5]
        if not top:
            continue
        L.append(f"**{DOC_NOME[d]} — maiores desvios**")
        for t in top:
            marca = "já coberto por alerta" if t["coincide_com_alerta_existente"] else "candidato novo"
            L.append(f"- {t['rotulo']}: {n(t['atual'], 0)} vs {n(t['anterior'], 0)} (R$ mil), z = {t['z_robusto']:+.1f} {cite(d, t['pagina'])} — _{marca}_")
        L.append("")
    L.append("**Tom da administração: léxico (sem ML) vs classificação**\n")
    L.append("| Documento | Classificado | Léxico | Score léxico | Concorda |")
    L.append("|---|---|---|---|---|")
    for d in run.order:
        t = tom[d]
        L.append(f"| {DOC_NOME[d]} | {t['tom_classificado']} | {t['tom_lexico']} | {t['score_lexico']:+.2f} | {'sim' if t['concorda'] else 'não'} |")
    L.append("")
    L.append(
        "_Leitura honesta:_ (1) coincidência por palavras do rótulo, heurística imperfeita; (2) linhas que mudam de sinal não têm razão logarítmica e ficam fora da pontuação. "
        "Um classificador de tom **supervisionado não foi treinado**: com 3 documentos não há corpus rotulado, e o léxico (n = 3) é só um sanity-check — não prova nada. "
        "O detector estatístico acerta números atípicos que as regras não procuram, mas gera ruído e não distingue efeito contábil legítimo de erro; as regras e a leitura do texto dão o *porquê*. "
        "A comparação com o **LLM** só é possível rodando `--mode llm` (veja o README)."
    )
    return "\n".join(L)

def annex_method(run) -> str:
    L = []
    L.append(f"- **Modo de extração:** `{run.mode}` " + {
        "reference": "(extração curada + verificada por código; não usa LLM nesta execução)",
        "llm": "(LLM com saída estruturada; cada valor passa por grounding)",
        "baseline": "(regras/regex; sem LLM)",
    }.get(run.mode, ""))
    L.append("- **Documentos** (SHA-256 abreviado · páginas · tempo de ingestão):")
    for d in run.order:
        doc = run.docs[d]
        L.append(f"    - {DOC_NOME[d]}: `{doc.path}` · `{doc.sha256[:12]}` · {doc.n_pages} págs · {doc.ingest_seconds}s ({doc.extractor})")
    if run.meter and run.meter.calls:
        cost = run.meter.cost_usd(run.settings.price_in_per_mtok, run.settings.price_out_per_mtok)
        L.append(f"- **LLM:** {run.settings.llm_provider}/{run.settings.llm_model} · {run.meter.calls} chamadas · {run.meter.input_tokens:,} tokens de entrada · {run.meter.output_tokens:,} de saída · {run.meter.seconds:.1f}s · custo estimado US$ {cost:.3f} (preços configuráveis em .env).")
    L.append("- **Convenção de páginas:** posição física no PDF (1 = capa); pode diferir do número impresso no rodapé.")
    L.append("- **Premissa de escopo:** os PDFs são demonstrações financeiras **anuais de 2022** (não releases trimestrais). 'Período de referência' = exercício 2022 vs 2021.")
    return "\n".join(L)


# ------------------------------------------------------------------ main ---

_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\S")


def _blank_before_lists(md: str) -> str:
    """Garante linha em branco antes de uma lista que segue um parágrafo.
    Sem isso, o Markdown (python-markdown) funde a lista no parágrafo anterior."""
    out: list[str] = []
    for line in md.split("\n"):
        if _LIST_ITEM.match(line) and out and out[-1].strip() and not _LIST_ITEM.match(out[-1]) and not out[-1].startswith((" ", "\t")):
            out.append("")
        out.append(line)
    return "\n".join(out)

def build_report_md(run, respostas: list[Resposta]) -> str:
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    L: list[str] = []
    L.append("# Relatório de Análise Financeira — Light, Millet e Brasal\n")
    L.append(f"*Gerado em {now} · modo `{run.mode}` · exercício 2022 vs 2021 · valores em R$ (conforme indicado)*\n")
    L.append("> **Leia primeiro:** os 3 PDFs são demonstrações financeiras anuais, não releases trimestrais. Só a Light inclui Relatório da Administração; "
             "Millet e Brasal têm apenas DFs e notas explicativas — por isso EBITDA, margem EBITDA, dívida líquida e guidance estão frequentemente *não encontrados*. "
             "Indicadores marcados com ¤ são **calculados** pelo pipeline, nunca extraídos.\n")

    L.append("## 1. Resumo executivo\n")
    for d in run.order:
        L.append(f"### {run.exts[d].empresa}")
        L += [f"{i}. {t}" for i, t in enumerate(exec_summary(run, d), 1)]
        L.append("")

    L.append("## 2. Tabela comparativa\n")
    L.append(comparative_table(run))
    L.append("\n## 3. Análise qualitativa do comentário da administração\n")
    L.append(qualitative_section(run))

    L.append("\n## 4. Respostas às 5 perguntas\n")
    for r in respostas:
        L.append(f"### {r.numero}. {r.pergunta}\n")
        L.append(r.resposta)
        L.append("\n<details><summary>Fontes (documento · página · trecho)</summary>\n")
        for f in r.fontes:
            t = f.trecho if len(f.trecho) <= 140 else f.trecho[:137] + "…"
            L.append(f"- **{DOC_NOME.get(f.documento, f.documento)} p.{f.pagina}** — “{t}”")
        L.append("\n</details>\n")

    L.append("## 5. Alertas de inconsistência e de informações não encontradas\n")
    L.append(alerts_section(run))
    L.append("\n## Anexo A — Indicadores derivados (fórmulas e insumos)\n")
    L.append(annex_derivations(run))
    L.append("\n## Anexo B — Abordagem tradicional (estatística / ML clássico) vs regras e LLM\n")
    L.append(annex_ml(run))
    L.append("\n## Anexo C — Metodologia desta execução\n")
    L.append(annex_method(run))
    return _blank_before_lists("\n".join(L) + "\n")


CSS = """
body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;max-width:1180px;margin:2rem auto;padding:0 1.2rem;color:#1b1f24;line-height:1.5}
h1{border-bottom:3px solid #0b5fff;padding-bottom:.3rem} h2{margin-top:2.2rem;border-bottom:1px solid #d0d7de;padding-bottom:.2rem}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.88rem} th,td{border:1px solid #d0d7de;padding:.4rem .55rem;vertical-align:top}
th{background:#f3f6fa} tr:nth-child(even) td{background:#fafbfc} code{background:#eef1f5;padding:.05rem .3rem;border-radius:4px;font-size:.85em}
blockquote{border-left:4px solid #f0ad00;background:#fff8e6;margin:1rem 0;padding:.6rem 1rem} details{margin:.4rem 0 1.2rem;font-size:.88rem}
summary{cursor:pointer;color:#0b5fff} em{color:#444}
"""


def build_report_html(md_text: str) -> str:
    body = md_lib.markdown(md_text, extensions=["tables", "sane_lists"])
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Relatório de Análise Financeira</title><style>{CSS}</style></head><body>{body}</body></html>'
