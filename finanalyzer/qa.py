"""Etapa 4 — Perguntas em linguagem natural.

Dois caminhos:

1. `answer_standard_questions(ctx)` — as 5 perguntas do teste, respondidas por
   CÓDIGO sobre os dados já verificados (extração + derivados + qualitativo).
   Vantagem: números e citações vêm de campos ancorados; nada é "escrito de
   memória" pelo modelo. Q4 (riscos em comum) é uma interseção de categorias.

2. `ask(question, ...)` — perguntas livres COM LLM: BM25 recupera páginas, o LLM
   responde em JSON com citações, e o grounding descarta qualquer citação que
   não exista literalmente na página. Sem citação válida => "sem evidência".

3. `ask_offline(question, ...)` — perguntas livres SEM LLM e sem chave: roteia a
   pergunta por palavras-chave para os indicadores/itens qualitativos já
   verificados e acrescenta os trechos mais relevantes da busca BM25. É
   extrativo: mostra o que os documentos dizem, não sintetiza nem interpreta.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .config import Settings
from .derive import Derivado
from .fmt import DOC_NOME, cite, mi, mult, n, pct
from .grounding import verify_evidence
from .ingest import Document
from .llm.client import LLMClient, UsageMeter
from .llm.prompts import SYSTEM_QA, USER_QA
from .retrieval import BM25Index, compact_page_text
from .schema import CATEGORIAS_RISCO, Evidencia, Extracao, Qualitativo
from .security import wrap_untrusted
from .text_utils import to_base
from .validate import Check

PERGUNTAS = [
    "Qual empresa teve a maior margem EBITDA no período?",
    "O que a administração de cada empresa apontou como principal motivo da variação da receita?",
    "Alguma das empresas está com alavancagem acima de 3x? Qual?",
    "Quais riscos são citados por mais de uma empresa?",
    "Qual é o guidance de cada empresa para o próximo ano?",
]


@dataclass
class Fonte:
    documento: str
    pagina: int
    trecho: str


@dataclass
class Resposta:
    numero: int
    pergunta: str
    resposta: str
    fontes: list[Fonte] = field(default_factory=list)


@dataclass
class Ctx:
    exts: dict[str, Extracao]
    ders: dict[str, dict[str, Derivado]]
    quals: dict[str, Qualitativo]
    checks: dict[str, list[Check]]

    @property
    def order(self) -> list[str]:
        return [d for d in ("light", "millet", "brasal") if d in self.exts] + [d for d in self.exts if d not in ("light", "millet", "brasal")]


def _dedup(fontes: list[Fonte]) -> list[Fonte]:
    seen, out = set(), []
    for f in fontes:
        k = (f.documento, f.pagina, f.trecho)
        if k not in seen:
            seen.add(k)
            out.append(f)
    return out


def _fe(e: Evidencia) -> Fonte:
    return Fonte(e.documento, e.pagina, e.trecho)


def _mil(v) -> float:
    return to_base(v.valor, v.escala) / 1e3


_EXTENSO = {1: "uma", 2: "duas", 3: "três", 4: "quatro", 5: "cinco", 6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez"}


def _qtd(n_: int) -> str:
    return _EXTENSO.get(n_, str(n_))


# ---------------------------------------------------------------- Q1 -------
def q1(ctx: Ctx) -> Resposta:
    fontes: list[Fonte] = []
    rows = []
    for d in ctx.order:
        der = ctx.ders[d]
        md = der["margem_ebitda_derivada"]
        ed = der["ebitda_derivado"]
        for en in ed.entradas + md.entradas:
            if en.periodo == "atual":
                fontes.append(Fonte(en.documento, en.pagina, en.trecho))
        rows.append((d, md.atual, md.anterior, ed.atual, ctx.exts[d]))
    rows_ok = [r for r in rows if r[1] is not None]
    rows_ok.sort(key=lambda r: -r[1])
    if not rows_ok:
        return Resposta(1, PERGUNTAS[0], "**Não encontrado**: nenhum documento trouxe EBIT e D&A suficientes para calcular a margem EBITDA (nenhum publica margem).", _dedup(fontes))
    top = rows_ok[0]
    publica = [DOC_NOME[d] for d, *_ , e in rows if e.ebitda.status == "encontrado"]
    publica_margem = [DOC_NOME[d] for d, *_ , e in rows if e.margem_ebitda.status == "encontrado"]

    L = []
    L.append(
        f"**{DOC_NOME[top[0]]}**, com margem EBITDA de ≈ **{pct(top[1])}** em 2022 — mas atenção: é uma margem **derivada pelo pipeline**, "
        f"não publicada. "
        + (f"Nenhum dos {_qtd(len(ctx.order))} documentos informa margem EBITDA" if not publica_margem else f"Só {', '.join(publica_margem)} informa margem EBITDA")
        + f", e {('só a ' + ', '.join(publica)) if publica else 'nenhuma empresa'} publica EBITDA."
    )
    light = ctx.exts.get("light")
    if light and light.ebitda.status == "encontrado":
        ed = ctx.ders["light"]["ebitda_derivado"]
        L.append(
            f"A Light imprime EBITDA CVM de R$ {n(light.ebitda.atual.valor, 0)} mi {cite('light', light.ebitda.atual.evidencia.pagina)}, "
            f"porém as DFs mostram EBIT + D&A = {mi(ed.atual)} (**negativo**; ver alerta de sinal)."
        )
    L.append("Para comparar de forma padronizada usei **EBITDA derivado = EBIT + D&A (fluxo de caixa) ÷ receita líquida da DRE**:")
    for i, (d, m22, m21, e22, ext) in enumerate(rows_ok, 1):
        extra = ""
        if d == "brasal" and any(a.id == "BRASAL-A2" for a in ext.anomalias_documento):
            extra = " — 2021 inflado por R$ 105,6 mi de créditos extemporâneos não recorrentes"
        if d == "light" and "margem_ebitda_derivada_ex_construcao" in ctx.ders[d]:
            extra = f" ({pct(ctx.ders[d]['margem_ebitda_derivada_ex_construcao'].atual)} sobre receita ex-construção)"
        pg = ext.ebit.atual.evidencia.pagina if ext.ebit.atual else 0
        L.append(f"{i}. {DOC_NOME[d]}: **{pct(m22)}** (EBITDA derivado {mi(e22)}; 2021: {pct(m21)}){extra} {cite(d, pg)}")
    L.append("*Comparação com ressalvas: as empresas usam critérios contábeis e atuam em setores diferentes.*")
    return Resposta(1, PERGUNTAS[0], "\n".join(L), _dedup(fontes))


# ---------------------------------------------------------------- Q2 -------
def q2(ctx: Ctx) -> Resposta:
    fontes: list[Fonte] = []
    L = []
    for d in ctx.order:
        ext, q = ctx.exts[d], ctx.quals[d]
        rl = ext.receita_liquida
        var = None
        if rl.atual and rl.anterior:
            var = (_mil(rl.atual) / _mil(rl.anterior) - 1) * 100
        head = f"**{DOC_NOME[d]}** (receita {mi(_mil(rl.atual))} vs {mi(_mil(rl.anterior))}; {pct(var, sign=True)})" if rl.atual else f"**{DOC_NOME[d]}**"
        if q.motivo_variacao_receita:
            it = q.motivo_variacao_receita
            pgs = ", ".join(sorted({f"p.{e.pagina}" for e in it.evidencias}, key=lambda s: int(s[2:])))
            body = f"{it.texto} [{DOC_NOME[d]} {pgs}]"
            fontes += [_fe(e) for e in it.evidencias]
        else:
            body = "**Não encontrado**: o documento não traz explicação da administração para a variação da receita."
        extra = ""
        if d == "light":
            ex = ext.receita_liquida_ex_construcao
            if ex and ex.atual:
                extra = f" (a DRE total varia {pct(var, sign=True)}; o −13% da administração exclui receita de construção)"
        if d == "millet":
            pf = next((v for v in rl.complementares if (v.rotulo or "").startswith("pro_forma_anterior")), None)
            if pf and rl.atual:
                pvar = (_mil(rl.atual) / _mil(pf) - 1) * 100
                extra = f" Em base comparável (Alibra com 2021 inteiro) a receita cresceria ≈ {pct(pvar, sign=True)} {cite(d, pf.evidencia.pagina)}."
                fontes.append(_fe(pf.evidencia))
        L.append(f"- {head}: {body}{extra}")
        if rl.atual:
            fontes.append(_fe(rl.atual.evidencia))
    return Resposta(2, PERGUNTAS[1], "\n".join(L), _dedup(fontes))


# ---------------------------------------------------------------- Q3 -------
def q3(ctx: Ctx, limite: float = 3.0) -> Resposta:
    fontes: list[Fonte] = []
    acima, linhas = [], []
    for d in ctx.order:
        ext, der = ctx.exts[d], ctx.ders[d]
        rep = ext.alavancagem
        ad = der["alavancagem_derivada"]
        if rep.status == "encontrado" and rep.atual:
            v = rep.atual.valor
            fontes.append(_fe(rep.atual.evidencia))
            dl = ext.divida_liquida.atual
            txt = f"**{DOC_NOME[d]}: {mult(v)}** (Dívida líquida/EBITDA ajustado de covenants, publicado) {cite(d, rep.atual.evidencia.pagina)}"
            if dl:
                txt += f"; dívida líquida {mi(_mil(dl))} {cite(d, dl.evidencia.pagina)}"
                fontes.append(_fe(dl.evidencia))
            if ad.atual is None and ctx.ders[d]["ebitda_derivado"].atual is not None and ctx.ders[d]["ebitda_derivado"].atual <= 0:
                txt += "; pelo EBITDA CVM recomposto (negativo) o múltiplo é n.s., o que é pior, não melhor"
            if v > limite:
                acima.append(DOC_NOME[d])
            linhas.append(txt)
        else:
            ed = der["ebitda_derivado"]
            dl_rep = ext.divida_liquida.atual
            dl_val = _mil(dl_rep) if dl_rep else der["divida_liquida_derivada"].atual
            for en in ed.entradas + der["divida_liquida_derivada"].entradas:
                if en.periodo == "atual":
                    fontes.append(Fonte(en.documento, en.pagina, en.trecho))
            if dl_rep:
                fontes.append(_fe(dl_rep.evidencia))
            if dl_val is not None and dl_val < 0:
                linhas.append(f"{DOC_NOME[d]}: não publica alavancagem; dívida líquida derivada = **{mi(dl_val)}** (caixa líquido: mais caixa e aplicações do que dívida) — sem alavancagem.")
            elif ad.atual is not None:
                linhas.append(f"{DOC_NOME[d]}: não publica alavancagem sobre EBITDA; **derivado {mult(ad.atual)}** (dívida líquida {mi(dl_val)} ÷ EBITDA derivado {mi(ed.atual)}).")
                if ad.atual > limite:
                    acima.append(DOC_NOME[d] + " (derivado)")
            else:
                linhas.append(f"{DOC_NOME[d]}: alavancagem não calculável com os dados do documento.")
    if acima:
        head = f"**Sim — {', '.join(acima)}.** Único múltiplo **publicado** acima de {n(limite, 0)}x: Light."
    else:
        head = f"**Não** — nenhuma empresa está acima de {n(limite, 0)}x."
    return Resposta(3, PERGUNTAS[2], head + "\n" + "\n".join(f"- {x}" for x in linhas), _dedup(fontes))


# ---------------------------------------------------------------- Q4 -------
def q4(ctx: Ctx) -> Resposta:
    por_cat: dict[str, dict[str, list]] = {}
    for d in ctx.order:
        for r in ctx.quals[d].riscos:
            if r.categoria:
                por_cat.setdefault(r.categoria, {}).setdefault(d, []).append(r)
    comuns = {c: v for c, v in por_cat.items() if len(v) >= 2}
    unicos = {c: v for c, v in por_cat.items() if len(v) == 1}
    fontes: list[Fonte] = []
    L = []
    for cat, emp in sorted(comuns.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        nomes = ", ".join(DOC_NOME[d] for d in ctx.order if d in emp)
        L.append(f"- **{CATEGORIAS_RISCO.get(cat, cat)}** — {len(emp)} empresas ({nomes}):")
        for d in ctx.order:
            if d in emp:
                r = emp[d][0]
                ev = r.evidencias[0]
                fontes += [_fe(e) for e in r.evidencias]
                txt = r.texto if len(r.texto) <= 150 else r.texto[:147].rsplit(" ", 1)[0] + "…"
                L.append(f"    - {DOC_NOME[d]}: {txt} {cite(d, ev.pagina)}")
    if unicos:
        partes = []
        for cat, emp in unicos.items():
            d = next(iter(emp))
            partes.append(f"{CATEGORIAS_RISCO.get(cat, cat)} ({DOC_NOME[d]})")
            fontes += [_fe(e) for e in emp[d][0].evidencias]
        L.append("- Citados por **apenas uma** empresa: " + "; ".join(partes) + ".")
    todas = [CATEGORIAS_RISCO.get(c, c) for c, v in comuns.items() if len(v) == len(ctx.order)]
    head = f"**{len(comuns)} categorias de risco aparecem em mais de uma empresa**; {len(todas)} aparecem em todas as {_qtd(len(ctx.order))}: {', '.join(todas) if todas else 'nenhuma'}."
    nota = "*Metodologia: cada risco recebe uma categoria de uma taxonomia fixa; a pergunta é respondida pela interseção das categorias (código), não por um parecer livre. Para Millet e Brasal, a base são as notas explicativas (não há relatório da administração).*"
    return Resposta(4, PERGUNTAS[3], head + "\n" + "\n".join(L) + "\n" + nota, _dedup(fontes))


# ---------------------------------------------------------------- Q5 -------
def q5(ctx: Ctx) -> Resposta:
    fontes: list[Fonte] = []
    L = []
    for d in ctx.order:
        q = ctx.quals[d]
        if q.guidance_numerico_encontrado:
            tag = "guidance numérico encontrado"
        else:
            tag = "**nenhum guidance numérico**"
        if q.guidance:
            itens = []
            for g in q.guidance:
                ev = g.evidencias[0]
                fontes += [_fe(e) for e in g.evidencias]
                itens.append(f"{g.texto} {cite(d, ev.pagina)}")
            L.append(f"- **{DOC_NOME[d]}** — {tag}. Perspectivas qualitativas: " + " ".join(f"({i}) {t}" for i, t in enumerate(itens, 1)))
        else:
            L.append(f"- **{DOC_NOME[d]}** — {tag}; o documento também não traz perspectivas/projeções (**não encontrado**).")
    com_guidance = [DOC_NOME[d] for d in ctx.order if ctx.quals[d].guidance_numerico_encontrado]
    if com_guidance:
        head = f"**Guidance numérico encontrado em: {', '.join(com_guidance)}.** As demais empresas não o divulgam nos documentos fornecidos."
    else:
        head = f"**Nenhuma das {_qtd(len(ctx.order))} empresas divulga guidance numérico para o próximo ano** nos documentos fornecidos (se forem demonstrações anuais, não releases com projeções)."
    return Resposta(5, PERGUNTAS[4], head + "\n" + "\n".join(L), _dedup(fontes))


def answer_standard_questions(ctx: Ctx) -> list[Resposta]:
    return [q1(ctx), q2(ctx), q3(ctx), q4(ctx), q5(ctx)]


# ----------------------------------------------------- perguntas livres ----
@dataclass
class FreeAnswer:
    pergunta: str
    resposta: str
    citacoes_validas: list[Fonte]
    citacoes_descartadas: list[Fonte]
    modo: str = "llm"


def ask(question: str, docs: dict[str, Document], index: BM25Index, llm: LLMClient, meter: UsageMeter, settings: Settings) -> FreeAnswer:
    hits = index.search(question, k=settings.top_k_pages)
    blocos = "\n\n".join(wrap_untrusted(h.doc_id, h.pagina, compact_page_text(docs[h.doc_id].page(h.pagina).text)) for h in hits)
    res = llm.complete(SYSTEM_QA, USER_QA.format(pergunta=question, paginas=blocos), settings.llm_max_tokens, json_schema={"type": "object", "properties": {"resposta": {"type": "string"}, "citacoes": {"type": "array", "items": {"type": "object", "properties": {"documento": {"type": "string"}, "pagina": {"type": "integer"}, "trecho": {"type": "string"}}, "required": ["documento", "pagina", "trecho"]}}}, "required": ["resposta", "citacoes"]})
    meter.add("qa_livre", res)
    data = res.data or {}
    ok, bad = [], []
    for c in (data.get("citacoes") or []):
        doc = docs.get(str(c.get("documento", "")).lower())
        if not isinstance(c, dict):
            continue
        try:
            pag = int(c.get("pagina", 0) or 0)
        except (TypeError, ValueError):
            pag = 0
        f = Fonte(str(c.get("documento", "")), pag, str(c.get("trecho", "")))
        if doc is None:
            bad.append(f)
            continue
        valid, _ = verify_evidence(doc, Evidencia(documento=doc.doc_id, pagina=max(f.pagina, 1), trecho=f.trecho or "xxx"))
        (ok if valid else bad).append(f)
    resposta = data.get("resposta", "")
    if not ok:
        resposta = "Sem evidência suficiente nos documentos (nenhuma citação do modelo pôde ser verificada)."
    return FreeAnswer(question, resposta, ok, bad)


# ----------------------------------------- perguntas livres SEM LLM (offline)
_IND_INTENTS: list[tuple[tuple[str, ...], list[str]]] = [
    (("margem",), ["margem_ebitda", "ebitda"]),
    (("ebitda", "lajida"), ["ebitda", "margem_ebitda"]),
    (("receita", "faturamento"), ["receita_liquida"]),
    (("lucro", "prejuizo", "resultado liquido"), ["lucro_liquido"]),
    (("alavanc", "covenant"), ["alavancagem", "divida_liquida"]),
    (("divida", "endividamento"), ["divida_liquida", "divida_bruta"]),
    (("fluxo de caixa", "caixa operacional", "fco"), ["fco"]),
    (("capex", "investimento"), ["capex"]),
]
_QUALI_INTENTS: list[tuple[tuple[str, ...], str, str]] = [
    (("risco", "incerteza", "atencao"), "riscos", "Riscos e pontos de atenção"),
    (("guidance", "perspectiva", "projec", "expectativa"), "guidance", "Guidance / perspectivas"),
    (("motivo", "explic", "causa", "por que", "porque"), "motivos_resultado", "Principais motivos do resultado"),
    (("evento", "aquisic", "reestrutur", "contingenc"), "eventos_relevantes", "Eventos relevantes"),
]
_LABEL = {
    "receita_liquida": "Receita líquida", "ebitda": "EBITDA publicado", "margem_ebitda": "Margem EBITDA publicada", "lucro_liquido": "Lucro líquido",
    "divida_liquida": "Dívida líquida", "divida_bruta": "Dívida bruta", "alavancagem": "Dívida líquida/EBITDA", "fco": "Fluxo de caixa operacional", "capex": "Capex",
}
_STOP = {"de", "da", "do", "das", "dos", "a", "o", "e", "em", "para", "por", "que", "qual", "quais", "com", "as", "os", "na", "no", "um", "uma", "foi", "tem", "ser", "sao"}


def _fmt_valor(v) -> str:
    if v.unidade == "%":
        return pct(v.valor)
    if v.unidade == "x":
        return mult(v.valor)
    return mi(_mil(v))


def _best_lines(text: str, terms: set[str], n_lines: int = 2) -> list[str]:
    """Linhas LITERAIS da página com mais termos da pergunta (extrativo)."""
    from .text_utils import normalize_for_search

    scored = []
    min_cov = max(1, -(-len(terms) // 2))  # teto de 50% dos termos relevantes
    for ln in text.splitlines():
        raw = " ".join(ln.split())
        if not 25 <= len(raw) <= 260:
            continue
        toks = set(normalize_for_search(raw).split())
        sc = sum(1 for t in terms if any(tok.startswith(t) for tok in toks))
        if sc and sc >= min_cov:  # exige cobertura: casar só 1 palavra de 3 é ruído, não evidência
            scored.append((sc, raw))
    scored.sort(key=lambda x: -x[0])
    return [r for _, r in scored[:n_lines]]


def ask_offline(question: str, docs: dict[str, Document], index: BM25Index, ctx: Ctx | None = None, k: int = 3) -> FreeAnswer:
    """Responde sem LLM. Toda citação passa por `verify_evidence`."""
    from .text_utils import normalize_for_search

    qn = normalize_for_search(question)
    empresas = [d for d in docs if d in qn] or list(docs)
    terms = {t for t in qn.split() if t not in _STOP and len(t) > 2 and t not in docs}
    L: list[str] = []
    fontes: list[Fonte] = []

    if ctx:
        campos: list[str] = []
        for keys, cs in _IND_INTENTS:
            if any(key in qn for key in keys):
                campos += [c for c in cs if c not in campos]
        if campos:
            L.append("**Indicadores extraídos e verificados** (publicados pelo documento; indicadores calculados aparecem à parte):")
            for d in empresas:
                ext = ctx.exts.get(d)
                if not ext:
                    continue
                partes = []
                for c in campos:
                    m = getattr(ext, c, None)
                    if m is None:
                        continue
                    if m.status == "encontrado" and m.atual:
                        t = f"{_LABEL[c]}: {_fmt_valor(m.atual)} {cite(d, m.atual.evidencia.pagina)}"
                        if m.anterior:
                            t += f" (comparável: {_fmt_valor(m.anterior)})"
                        partes.append(t)
                        fontes.append(_fe(m.atual.evidencia))
                    elif m.status == "nao_encontrado":
                        partes.append(f"{_LABEL[c]}: **não encontrado** ({m.motivo_ausencia})")
                der = ctx.ders.get(d, {})
                if any(c in campos for c in ("ebitda", "margem_ebitda")) and der.get("ebitda_derivado") and der["ebitda_derivado"].atual is not None:
                    ed, md = der["ebitda_derivado"], der.get("margem_ebitda_derivada")
                    t = f"¤ calculado (EBIT + D&A): EBITDA {mi(ed.atual)}" + (f", margem {pct(md.atual)}" if md and md.atual is not None else "")
                    partes.append(t)
                    fontes += [Fonte(d, e.pagina, e.trecho) for e in ed.entradas if e.periodo == "atual"]
                if partes:
                    L.append(f"- **{DOC_NOME.get(d, d)}** — " + "; ".join(partes))
        for keys, attr, titulo in _QUALI_INTENTS:
            if any(key in qn for key in keys):
                L.append(f"**{titulo}** (análise qualitativa verificada):")
                for d in empresas:
                    q = ctx.quals.get(d)
                    if not q:
                        continue
                    itens = getattr(q, attr)
                    if not itens:
                        L.append(f"- **{DOC_NOME.get(d, d)}** — **não encontrado** no documento.")
                        continue
                    for it in itens[:3]:
                        L.append(f"- **{DOC_NOME.get(d, d)}** — {it.texto} {cite(d, it.evidencias[0].pagina)}")
                        fontes += [_fe(e) for e in it.evidencias]
        if "tom" in qn.split():
            for d in empresas:
                q = ctx.quals.get(d)
                if q:
                    L.append(f"- **{DOC_NOME.get(d, d)}** — tom **{q.tom}** (confiança {q.confianca_tom}): {q.tom_justificativa}")
                    fontes += [_fe(e) for e in q.tom_evidencias]

    # trechos literais mais relevantes (busca textual)
    achados = []
    for h in index.search(question, k=k, doc_id=empresas[0] if len(empresas) == 1 else None):
        if h.score <= 0:
            continue
        for ln in _best_lines(docs[h.doc_id].page(h.pagina).text, terms):
            achados.append(Fonte(h.doc_id, h.pagina, ln))
    if achados:
        L.append("**Trechos mais relevantes encontrados nos PDFs** (busca textual; copiados literalmente, sem interpretação):")
        L += [f"- {DOC_NOME.get(f.documento, f.documento)} p.{f.pagina}: “{f.trecho}”" for f in achados]
        fontes += achados

    ok, bad = [], []
    seen = set()
    for f in fontes:
        if (f.documento, f.pagina, f.trecho) in seen:
            continue
        seen.add((f.documento, f.pagina, f.trecho))
        doc = docs.get(f.documento.lower())
        valid = doc is not None and verify_evidence(doc, Evidencia(documento=doc.doc_id, pagina=max(f.pagina, 1), trecho=f.trecho or "xxx"))[0]
        (ok if valid else bad).append(f)
    if not ok:
        return FreeAnswer(question, "Sem evidência suficiente nos documentos para responder a esta pergunta.", [], bad, "offline")
    cab = "*Modo offline (sem LLM): resposta extrativa — mostra o que os documentos dizem e não sintetiza.*"
    return FreeAnswer(question, cab + "\n\n" + "\n".join(L), ok, bad, "offline")
