"""Etapa 3 — Grounding (combate à alucinação).

Regra de ouro: **nenhum número entra no relatório sem passar por aqui.**

Para cada `Evidencia` (+ valor associado) verificamos, de forma determinística
(sem LLM):

  1. a página existe no PDF;
  2. o `trecho` é uma subsequência contígua do texto REAL daquela página
     (após normalizar espaços/hífens/aspas) — ou, quando o PDF quebra um rótulo em
     duas linhas, todas as palavras/números da citação estão juntos numa janela curta
     (e a citação é trocada pelo texto real da página);
  3. o número extraído aparece (em módulo) dentro do trecho.

Se qualquer verificação falhar, a evidência é marcada `verificada=False`, a
métrica vira `nao_verificado` e o problema aparece como alerta no relatório.
Um LLM que "inventa" um número (ou uma página) é, portanto, barrado por código.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .ingest import Document
from .schema import Evidencia, Extracao, Metrica, Qualitativo, Valor
from .text_utils import normalize_text, number_in_text, rescale_from_quote


@dataclass
class GroundingFailure:
    doc_id: str
    campo: str
    pagina: int
    motivo: str
    trecho: str


_REFLOW_SLACK = 3  # palavras extras toleradas no meio da citação (rótulo que quebra de linha no PDF)
_REFLOW_MIN_TOKENS = 3


def _reflow(page_tokens: list[str], quote: str) -> str | None:
    """PDFs quebram rótulos longos em 2 linhas ('...atividades' desce depois dos números) e o
    modelo cita o rótulo 'arrumado'. Aceitamos se TODAS as palavras/números da citação (com
    multiplicidade) aparecem juntos numa janela curta da página; devolvemos o texto REAL da
    página (literal) para substituir a citação. Número ou palavra ausente => None."""
    q = quote.split()
    n = len(q)
    if n < _REFLOW_MIN_TOKENS:
        return None
    need = Counter(q)
    w = n + _REFLOW_SLACK
    for i in range(0, max(len(page_tokens) - n + 1, 0)):
        win = page_tokens[i : i + w]
        if need - Counter(win):
            continue
        cnt, lo, hi = Counter(win), 0, len(win)
        while lo < hi and cnt[win[lo]] > need.get(win[lo], 0):
            cnt[win[lo]] -= 1
            lo += 1
        while hi > lo and cnt[win[hi - 1]] > need.get(win[hi - 1], 0):
            cnt[win[hi - 1]] -= 1
            hi -= 1
        return " ".join(win[lo:hi])
    return None


def verify_evidence(doc: Document, ev: Evidencia, valor: float | None = None) -> tuple[bool, str | None]:
    """Valida a evidência. Se ela passar, `ev.trecho` passa a ser (quando necessário) o texto
    LITERAL da página: citações com ' | ' unindo linhas distintas são reduzidas ao segmento
    verificado que contém o valor; citações 'arrumadas' são trocadas pelo trecho real."""
    if ev.documento.lower() != doc.doc_id:
        return False, f"documento '{ev.documento}' diferente de '{doc.doc_id}'"
    if not 1 <= ev.pagina <= doc.n_pages:
        return False, f"página {ev.pagina} fora do intervalo 1..{doc.n_pages}"
    page_text = doc.page(ev.pagina).text_norm
    page_tokens = page_text.split()
    quote = normalize_text(ev.trecho)
    segments = [normalize_text(x) for x in quote.split(" | ")] if " | " in quote else [quote]
    segments = [x for x in segments if x]
    literal = [x for x in segments if x in page_text]  # literais têm preferência sobre reflow
    verified = literal + [r for x in segments if x not in page_text and (r := _reflow(page_tokens, x))]
    if not verified:
        return False, "trecho não encontrado literalmente na página citada"
    for fixed in verified:
        if valor is None:
            ok_num = True
        else:
            ok_num = number_in_text(valor, fixed)
        if ok_num:
            if len(fixed) >= 3:
                ev.trecho = fixed
            return True, None
    return False, f"valor {valor} não aparece no trecho citado"


def _check_valor(doc: Document, v: Valor, campo: str, failures: list[GroundingFailure]) -> bool:
    if v.unidade == "R$":
        # o modelo às vezes converte a escala ("R$1.180 milhões" -> 1.180.000 ou 1180 'mil'): o TRECHO manda.
        r = rescale_from_quote(v.valor, v.evidencia.trecho)
        if r is not None:
            v.valor, v.escala = r
    ok, why = verify_evidence(doc, v.evidencia, v.valor)
    v.evidencia.verificada = ok
    v.evidencia.motivo_falha = why
    if not ok:
        failures.append(GroundingFailure(doc.doc_id, campo, v.evidencia.pagina, why or "", v.evidencia.trecho))
    return ok


def _iter_valores(m: Metrica):
    for nome in ("atual", "anterior", "variacao_reportada_pct", "variacao_reportada_abs"):
        v = getattr(m, nome)
        if v is not None:
            yield nome, v
    for i, v in enumerate(m.alternativas):
        yield f"alternativa[{i}]", v
    for i, v in enumerate(m.complementares):
        yield f"complementar[{i}]", v


def verify_absence(doc: Document, termos: list[str]) -> list[tuple[str, int]]:
    """Retorna (termo, página) para cada termo que APARECE no documento.
    Usado para auditar o status `nao_encontrado`: se o termo existe, o
    'não encontrado' está errado."""
    hits: list[tuple[str, int]] = []
    for t in termos:
        t_norm = normalize_text(t).lower()
        for p in doc.pages:
            if t_norm in p.text_norm.lower():
                hits.append((t, p.number))
                break
    return hits


def ground_extraction(doc: Document, ext: Extracao) -> list[GroundingFailure]:
    failures: list[GroundingFailure] = []
    for nome, m in ext.metricas().items():
        if m.status == "nao_encontrado":
            for termo, pag in verify_absence(doc, m.termos_verificados):
                failures.append(
                    GroundingFailure(doc.doc_id, f"{nome}.ausencia", pag, f"marcado 'não encontrado', mas o termo '{termo}' aparece no documento", termo)
                )
            # complementares (ex.: componentes de capex) continuam exigindo evidência
            for i, v in enumerate(m.complementares):
                _check_valor(doc, v, f"{nome}.complementar[{i}]", failures)
            continue
        all_ok = True
        for sub, v in _iter_valores(m):
            all_ok &= _check_valor(doc, v, f"{nome}.{sub}", failures)
        if not all_ok:
            m.status = "nao_verificado"
    for a in ext.anomalias_documento:
        for i, ev in enumerate(a.evidencias):
            ok, why = verify_evidence(doc, ev)
            ev.verificada, ev.motivo_falha = ok, why
            if not ok:
                failures.append(GroundingFailure(doc.doc_id, f"anomalia:{a.id}[{i}]", ev.pagina, why or "", ev.trecho))
    return failures


MIN_RELOCATE_CHARS = 40


def _relocate_page(doc: Document, ev: Evidencia) -> tuple[bool, str | None]:
    """Modelos às vezes citam o número IMPRESSO no rodapé (ex.: 90) em vez da posição física (107).
    Se o trecho — LITERAL, com pelo menos 40 caracteres — existe em exatamente UMA outra página,
    a evidência é realocada para ela e a correção fica registrada em `motivo_falha`
    (nunca silenciosa). Se houver 0 ou 2+ páginas candidatas, continua reprovada."""
    quote = normalize_text(ev.trecho)
    if len(quote) < MIN_RELOCATE_CHARS:
        return False, "trecho não encontrado literalmente na página citada"
    cands = [p.number for p in doc.pages if p.number != ev.pagina and quote in p.text_norm]
    if len(cands) != 1:
        return False, "trecho não encontrado literalmente na página citada"
    old, ev.pagina = ev.pagina, cands[0]
    ok, why = verify_evidence(doc, ev)
    return (True, f"página corrigida de {old} para {ev.pagina} (trecho literal só existe nela)") if ok else (False, why)


def ground_qualitativo(doc: Document, q: Qualitativo) -> list[GroundingFailure]:
    failures: list[GroundingFailure] = []

    def check(ev: Evidencia, campo: str) -> None:
        ok, why = verify_evidence(doc, ev)
        if not ok and why and why.startswith("trecho não encontrado"):
            ok, why = _relocate_page(doc, ev)
        ev.verificada, ev.motivo_falha = ok, why
        if not ok:
            failures.append(GroundingFailure(doc.doc_id, campo, ev.pagina, why or "", ev.trecho))

    groups = {
        "motivos": q.motivos_resultado,
        "riscos": q.riscos,
        "guidance": q.guidance,
        "eventos": q.eventos_relevantes,
    }
    for gname, items in groups.items():
        for i, it in enumerate(items):
            for ev in it.evidencias:
                check(ev, f"{gname}[{i}]")
    if q.motivo_variacao_receita:
        for ev in q.motivo_variacao_receita.evidencias:
            check(ev, "motivo_variacao_receita")
    for ev in q.tom_evidencias:
        check(ev, "tom")
    return failures


def drop_unverified_items(q: Qualitativo) -> Qualitativo:
    """Remove itens cujas evidências NÃO passaram (em vez de exibi-los)."""

    def keep(it) -> bool:
        return bool(it.evidencias) and all(e.verificada for e in it.evidencias)

    q.motivos_resultado = [i for i in q.motivos_resultado if keep(i)]
    q.riscos = [i for i in q.riscos if keep(i)]
    q.guidance = [i for i in q.guidance if keep(i)]
    q.eventos_relevantes = [i for i in q.eventos_relevantes if keep(i)]
    if q.motivo_variacao_receita and not keep(q.motivo_variacao_receita):
        q.motivo_variacao_receita = None
    return q
