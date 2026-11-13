"""Etapa 5 — Validação e consistência (determinística, sem LLM).

Cada verificação devolve um `Check`. Nada é "corrigido em silêncio": o que
não bate vira alerta no relatório, com páginas para o analista conferir.

Checks implementados
  C01  variação % reportada vs recalculada (atual/anterior)
  C02  variação absoluta reportada vs diferença dos valores
  C03  mesma grandeza citada em duas fontes/escalas (texto × DFs) — inclui
       detecção de erro de escala (×1.000 / ×1.000.000)
  C04  EBITDA reportado vs recomposto (EBIT + D&A): módulo e SINAL
  C05  margem EBITDA reportada vs calculada
  C06  dívida líquida reportada vs (bruta − caixa − aplicações)
  C07  receita sem construção: variação reportada vs recalculada
  C08  campos não encontrados / não verificados (cobertura)
  C09  alavancagem reportada vs recalculada
  C10  variações extremas (possível não comparabilidade)
  C11  anomalias lidas no próprio documento (typos, períodos trocados,
       comparativo não auditado...)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .derive import Derivado, derive_all, variation_pct
from .schema import CAMPOS_ENTREGA, Extracao, Metrica, Valor
from .text_utils import to_base


@dataclass
class Check:
    id: str
    doc_id: str
    campo: str
    status: str  # ok | alerta | info
    severidade: str  # alta | media | baixa | info
    mensagem: str
    paginas: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _mil(v: Valor) -> float:
    return to_base(v.valor, v.escala) / 1e3


def _pages(*vals: Valor | None) -> list[int]:
    return sorted({v.evidencia.pagina for v in vals if v is not None})


def _fmt(x: float, nd: int = 1) -> str:
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ------------------------------------------------------------------------
def check_variacao_pct(ext: Extracao) -> list[Check]:
    out: list[Check] = []
    for nome, m in ext.metricas().items():
        rep = m.variacao_reportada_pct
        if rep is None or nome == "receita_liquida_ex_construcao":
            continue
        if not (m.atual and m.anterior):
            continue
        calc = variation_pct(m)
        if calc is None:
            continue
        diff = abs(calc - rep.valor)
        # tolerância = arredondamento do que foi impresso (inteiro => ±0,5 p.p.) + folga p/ escala em milhões
        tol = 1.0
        ok = diff <= tol
        out.append(
            Check(
                "C01", ext.doc_id, nome, "ok" if ok else "alerta", "info" if ok else "media",
                f"Variação reportada {_fmt(rep.valor)}% vs recalculada {_fmt(calc)}% (diferença {_fmt(diff)} p.p.).",
                _pages(m.atual, m.anterior, rep),
            )
        )
    return out


def check_variacao_abs(ext: Extracao, der: dict[str, Derivado]) -> list[Check]:
    out: list[Check] = []
    # lucro líquido
    m = ext.lucro_liquido
    if m.variacao_reportada_abs and m.atual and m.anterior:
        rep = abs(_mil(m.variacao_reportada_abs))
        calc = abs(_mil(m.atual) - _mil(m.anterior))
        tol = 0.5 * to_base(1, m.variacao_reportada_abs.escala) / 1e3  # meia unidade da escala impressa
        ok = abs(rep - calc) <= tol
        out.append(
            Check("C02", ext.doc_id, "lucro_liquido", "ok" if ok else "alerta", "info" if ok else "media",
                  f"Variação absoluta reportada {_fmt(rep / 1e3)} mi vs diferença das DFs {_fmt(calc / 1e3)} mi.",
                  _pages(m.atual, m.anterior, m.variacao_reportada_abs))
        )
    # EBITDA (usa derivado como referência do período anterior)
    e = ext.ebitda
    ed = der.get("ebitda_derivado")
    if e.variacao_reportada_abs and ed and ed.atual is not None and ed.anterior is not None:
        rep = abs(_mil(e.variacao_reportada_abs))
        calc = abs(ed.atual - ed.anterior)
        tol = 0.5 * to_base(1, e.variacao_reportada_abs.escala) / 1e3
        ok = abs(rep - calc) <= tol
        out.append(
            Check("C02", ext.doc_id, "ebitda", "ok" if ok else "alerta", "info" if ok else "media",
                  f"Redução do EBITDA reportada {_fmt(rep / 1e3)} mi vs Δ do EBITDA recomposto (EBIT + D&A) {_fmt(calc / 1e3)} mi — "
                  + ("a recomposição reproduz a variação informada." if ok else "não reproduz."),
                  _pages(e.variacao_reportada_abs) + [en.pagina for en in ed.entradas][:0])
        )
    return out


def check_alternativas(ext: Extracao) -> list[Check]:
    out: list[Check] = []
    for nome, m in ext.metricas().items():
        if not m.alternativas or not m.atual:
            continue
        base = _mil(m.atual)
        for alt in m.alternativas:
            altv = _mil(alt)
            tol = 0.5 * to_base(1, alt.escala) / 1e3
            diff = abs(altv - base)
            # (a) erro de escala?
            if base != 0 and altv != 0:
                ratio = abs(altv / base)
                for k in (1e3, 1e6):
                    if abs(ratio / k - 1) < 0.01 or abs(ratio * k - 1) < 0.01:
                        out.append(Check("C03", ext.doc_id, nome, "alerta", "alta",
                                         f"Possível erro de escala (razão ≈ {k:g}) entre {alt.escala} e {m.atual.escala}.",
                                         _pages(m.atual, alt)))
            if (altv < 0) != (base < 0) and abs(abs(altv) - abs(base)) <= max(tol, 0.01 * abs(base)):
                out.append(Check("C03", ext.doc_id, nome, "alerta", "alta", "Mesmo módulo, sinais diferentes entre as fontes.", _pages(m.atual, alt)))
                continue
            ok = diff <= tol
            rel = diff / abs(base) * 100 if base else 0
            out.append(
                Check("C03", ext.doc_id, nome, "ok" if ok else "alerta", "info" if ok else ("alta" if rel > 1 else "baixa"),
                      f"{alt.rotulo or 'Menção alternativa'}: {_fmt(altv / 1e3, 3)} mi (escala {alt.escala}) vs DFs {_fmt(base / 1e3, 3)} mi "
                      f"— diferença {_fmt(diff / 1e3, 3)} mi ({_fmt(rel, 3)}%)"
                      + ("; dentro do arredondamento." if ok else "; EXCEDE o arredondamento da escala impressa."),
                      _pages(m.atual, alt))
            )
    return out


def check_ebitda_recomposto(ext: Extracao, der: dict[str, Derivado]) -> list[Check]:
    e, ed = ext.ebitda, der.get("ebitda_derivado")
    if e.status != "encontrado" or not e.atual or not ed or ed.atual is None:
        return []
    rep, rec = _mil(e.atual), ed.atual
    same_mag = abs(abs(rep) - abs(rec)) <= max(0.002 * abs(rec), 0.5 * to_base(1, e.atual.escala) / 1e3)
    if same_mag and (rep < 0) != (rec < 0):
        return [Check("C04", ext.doc_id, "ebitda", "alerta", "alta",
                      f"EBITDA reportado no texto = {_fmt(rep / 1e3, 0)} mi (positivo), mas a recomposição pelas DFs (EBIT + D&A) = {_fmt(rec / 1e3, 1)} mi (NEGATIVO). "
                      "Mesmo módulo, sinal oposto: provável omissão do sinal negativo no texto. O pipeline usa o valor recomposto na comparação.",
                      _pages(e.atual))]
    if not same_mag:
        return [Check("C04", ext.doc_id, "ebitda", "alerta", "media",
                      f"EBITDA reportado {_fmt(rep / 1e3, 1)} mi ≠ recomposto {_fmt(rec / 1e3, 1)} mi.", _pages(e.atual))]
    return [Check("C04", ext.doc_id, "ebitda", "ok", "info", "EBITDA reportado confere com EBIT + D&A.", _pages(e.atual))]


def check_margem(ext: Extracao, der: dict[str, Derivado]) -> list[Check]:
    m = ext.margem_ebitda
    if m.status != "encontrado" or not m.atual:
        return []
    md = der.get("margem_ebitda_derivada")
    if not md or md.atual is None:
        return []
    diff = abs(m.atual.valor - md.atual)
    ok = diff <= 0.6
    return [Check("C05", ext.doc_id, "margem_ebitda", "ok" if ok else "alerta", "info" if ok else "media",
                  f"Margem reportada {_fmt(m.atual.valor)}% vs calculada {_fmt(md.atual)}% (Δ {_fmt(diff)} p.p.).", _pages(m.atual))]


def check_divida_liquida(ext: Extracao, der: dict[str, Derivado]) -> list[Check]:
    dl = ext.divida_liquida
    dd = der.get("divida_liquida_derivada")
    if dl.status != "encontrado" or not dd:
        return []
    out = []
    for periodo in ("atual", "anterior"):
        rep, calc = getattr(dl, periodo), getattr(dd, periodo)
        if rep is None or calc is None:
            continue
        diff = abs(_mil(rep) - calc)
        ok = diff <= max(0.001 * abs(calc), 1.0)
        out.append(Check("C06", ext.doc_id, f"divida_liquida[{periodo}]", "ok" if ok else "alerta", "info" if ok else "media",
                         f"Dívida líquida reportada {_fmt(_mil(rep), 0)} mil vs bruta − caixa = {_fmt(calc, 0)} mil.",
                         _pages(rep)))
    return out


def check_ex_construcao(ext: Extracao) -> list[Check]:
    m = ext.receita_liquida_ex_construcao
    if not m or not m.variacao_reportada_pct or not ext.receita_construcao:
        return []
    rl, rc = ext.receita_liquida, ext.receita_construcao
    if not (rl.atual and rl.anterior and rc.atual and rc.anterior):
        return []
    a, b = _mil(rl.atual) - _mil(rc.atual), _mil(rl.anterior) - _mil(rc.anterior)
    calc = (a / b - 1) * 100
    rep = m.variacao_reportada_pct.valor
    ok = abs(calc - rep) <= 1.0
    msgs = [f"Receita ex-construção recalculada (DRE − nota 31): {_fmt(a / 1e3, 0)} mi vs {_fmt(b / 1e3, 0)} mi → {_fmt(calc)}%; reportado {_fmt(rep)}%."]
    chk = [Check("C07", ext.doc_id, "receita_liquida_ex_construcao", "ok" if ok else "alerta", "info" if ok else "media", msgs[0],
                 _pages(rl.atual, rc.atual, m.variacao_reportada_pct))]
    if m.atual:
        diff = abs(_mil(m.atual) - a)
        ok2 = diff <= 0.5 * to_base(1, m.atual.escala) / 1e3
        chk.append(Check("C07", ext.doc_id, "receita_liquida_ex_construcao", "ok" if ok2 else "alerta", "info" if ok2 else "media",
                         f"Receita ex-construção do texto ({_fmt(_mil(m.atual) / 1e3, 0)} mi) vs DRE − construção ({_fmt(a / 1e3, 1)} mi).",
                         _pages(m.atual, rl.atual, rc.atual)))
    # variação da receita total (com construção) — informativo, para não confundir com o -13%
    calc_total = variation_pct(rl)
    if calc_total is not None:
        chk.append(Check("C07", ext.doc_id, "receita_liquida", "info", "info",
                         f"Receita líquida TOTAL da DRE varia {_fmt(calc_total)}%; a administração comenta {_fmt(rep)}% porque exclui a receita de construção (bases diferentes).",
                         _pages(rl.atual, rl.anterior)))
    return chk


def check_cobertura(ext: Extracao) -> list[Check]:
    out = []
    for nome in CAMPOS_ENTREGA:
        m: Metrica = getattr(ext, nome)
        if m.status == "nao_encontrado":
            out.append(Check("C08", ext.doc_id, nome, "alerta", "info", f"Não encontrado no documento. {m.motivo_ausencia or ''}".strip(), []))
        elif m.status == "nao_verificado":
            out.append(Check("C08", ext.doc_id, nome, "alerta", "alta", "Valor NÃO verificado contra o PDF (grounding falhou) — não usar.", []))
    return out


def check_alavancagem(ext: Extracao, der: dict[str, Derivado]) -> list[Check]:
    m = ext.alavancagem
    if m.status != "encontrado" or not m.atual:
        return []
    ad = der.get("alavancagem_derivada")
    if ad and ad.atual is None:
        return [Check("C09", ext.doc_id, "alavancagem", "info", "info",
                      f"Alavancagem reportada {_fmt(m.atual.valor, 2)}x (EBITDA ajustado p/ covenants). Não é replicável com o EBITDA recomposto (≤ 0 → n.s.): "
                      "o EBITDA de covenants exclui provisões e itens não caixa.", _pages(m.atual))]
    if ad and ad.atual is not None:
        diff = abs(ad.atual - m.atual.valor)
        ok = diff <= 0.1
        return [Check("C09", ext.doc_id, "alavancagem", "ok" if ok else "alerta", "info" if ok else "media",
                      f"Alavancagem reportada {_fmt(m.atual.valor, 2)}x vs recalculada {_fmt(ad.atual, 2)}x.", _pages(m.atual))]
    return []


def check_extremos(ext: Extracao) -> list[Check]:
    out = []
    for nome in ("receita_liquida", "lucro_liquido", "fco"):
        m: Metrica = getattr(ext, nome)
        if not (m.atual and m.anterior):
            continue
        a, b = _mil(m.atual), _mil(m.anterior)
        if b <= 0 or a <= 0:
            out.append(Check("C10", ext.doc_id, nome, "info", "info",
                             f"Sinal negativo em um dos períodos ({_fmt(a / 1e3, 1)} mi vs {_fmt(b / 1e3, 1)} mi): variação percentual não significativa (n.s.).", _pages(m.atual, m.anterior)))
            continue
        v = (a / b - 1) * 100
        if abs(v) >= 100:
            out.append(Check("C10", ext.doc_id, nome, "alerta", "media",
                             f"Variação extrema ({_fmt(v)}%): confirme comparabilidade dos períodos (ver anomalias do documento).", _pages(m.atual, m.anterior)))
    return out


def check_anomalias(ext: Extracao) -> list[Check]:
    return [
        Check("C11", ext.doc_id, a.id, "alerta", a.severidade, a.descricao, sorted({e.pagina for e in a.evidencias}))
        for a in ext.anomalias_documento
    ]


def validate_extraction(ext: Extracao) -> tuple[list[Check], dict[str, Derivado]]:
    der = derive_all(ext)
    checks: list[Check] = []
    checks += check_variacao_pct(ext)
    checks += check_variacao_abs(ext, der)
    checks += check_alternativas(ext)
    checks += check_ebitda_recomposto(ext, der)
    checks += check_margem(ext, der)
    checks += check_divida_liquida(ext, der)
    checks += check_ex_construcao(ext)
    checks += check_alavancagem(ext, der)
    checks += check_extremos(ext)
    checks += check_cobertura(ext)
    checks += check_anomalias(ext)
    return checks, der
