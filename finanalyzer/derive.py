"""Indicadores DERIVADOS (calculados pelo pipeline, nunca "extraídos").

Quando um documento não publica um indicador (ex.: EBITDA no Millet/Brasal),
o campo extraído permanece `nao_encontrado`. Para permitir a comparação entre
empresas (pergunta 1 e 3 do teste), o pipeline calcula um indicador PADRONIZADO
a partir de linhas que existem no documento — e mostra, para cada derivado,
a fórmula e as páginas/trechos de cada entrada.

Convenções (todas documentadas no README):
  * EBITDA derivado   = EBIT (resultado antes do resultado financeiro e dos
                        impostos) + Depreciação e Amortização do fluxo de caixa.
                        Segue a lógica da ICVM 527/2012 usada pela Light (e
                        confirmada por reconciliação, ver validate.py).
  * Margem derivada   = EBITDA derivado / Receita líquida da DRE.
  * Dívida líquida    = Dívida bruta − Caixa − Aplicações financeiras (só
                        quando o documento não informa a dívida líquida).
  * Alavancagem deriv.= Dívida líquida / EBITDA derivado. Quando EBITDA <= 0 o
                        múltiplo não tem significado ("n.s.").
  * Capex de caixa    = soma das linhas de aquisição de imobilizado/intangível.
Todos os valores em R$ mil.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .schema import Extracao, Metrica, Valor
from .text_utils import to_base


@dataclass
class Entrada:
    campo: str
    periodo: str
    valor_mil: float
    documento: str
    pagina: int
    trecho: str


@dataclass
class Derivado:
    nome: str
    formula: str
    unidade: str  # "R$ mil" | "%" | "x"
    atual: float | None
    anterior: float | None
    entradas: list[Entrada] = field(default_factory=list)
    nota: str = ""


def _mil(v: Valor) -> float:
    return to_base(v.valor, v.escala) / 1e3


def _get(m: Metrica | None, periodo: str) -> Valor | None:
    if m is None or m.status == "nao_encontrado":
        return None
    return getattr(m, periodo)


def _entrada(campo: str, periodo: str, v: Valor) -> Entrada:
    return Entrada(campo, periodo, _mil(v), v.evidencia.documento, v.evidencia.pagina, v.evidencia.trecho)


def _combine(ext: Extracao, nome: str, formula: str, unidade: str, parts: list[tuple[str, float]], fn, nota: str = "") -> Derivado:
    """parts: lista de (campo, sinal) -> aplica fn sobre os valores em R$ mil."""
    out = {}
    entradas: list[Entrada] = []
    for periodo in ("atual", "anterior"):
        vals = []
        ok = True
        for campo, _ in parts:
            v = _get(getattr(ext, campo, None), periodo)
            if v is None:
                ok = False
                break
            vals.append(_mil(v))
            entradas.append(_entrada(campo, periodo, v))
        out[periodo] = fn(*vals) if ok else None
    return Derivado(nome, formula, unidade, out["atual"], out["anterior"], entradas, nota)


def derive_all(ext: Extracao) -> dict[str, Derivado]:
    d: dict[str, Derivado] = {}

    # --- EBITDA derivado -------------------------------------------------
    ebitda = _combine(
        ext, "ebitda_derivado", "EBIT + Depreciação e Amortização (fluxo de caixa)", "R$ mil",
        [("ebit", 1), ("depreciacao_amortizacao", 1)], lambda a, b: a + b,
    )
    d["ebitda_derivado"] = ebitda

    # --- margem derivada -------------------------------------------------
    rec_atual = _get(ext.receita_liquida, "atual")
    rec_ant = _get(ext.receita_liquida, "anterior")

    def _margem(e: float | None, r: Valor | None) -> float | None:
        if e is None or r is None or _mil(r) == 0:
            return None
        return e / _mil(r) * 100.0

    m = Derivado(
        "margem_ebitda_derivada", "EBITDA derivado / Receita líquida (DRE)", "%",
        _margem(ebitda.atual, rec_atual), _margem(ebitda.anterior, rec_ant), [],
        "Receita líquida consolidada da DRE.",
    )
    if rec_atual and rec_ant:
        m.entradas = [_entrada("receita_liquida", "atual", rec_atual), _entrada("receita_liquida", "anterior", rec_ant)]
    d["margem_ebitda_derivada"] = m

    # margem sobre receita ex-construção (distribuidoras): padrão do setor elétrico
    if ext.receita_construcao and ext.receita_construcao.status == "encontrado" and rec_atual and rec_ant:
        c_at, c_an = _get(ext.receita_construcao, "atual"), _get(ext.receita_construcao, "anterior")
        if c_at and c_an:
            r_at, r_an = _mil(rec_atual) - _mil(c_at), _mil(rec_ant) - _mil(c_an)
            d["margem_ebitda_derivada_ex_construcao"] = Derivado(
                "margem_ebitda_derivada_ex_construcao", "EBITDA derivado / (Receita líquida − receita de construção)", "%",
                ebitda.atual / r_at * 100 if ebitda.atual is not None and r_at else None,
                ebitda.anterior / r_an * 100 if ebitda.anterior is not None and r_an else None,
                [_entrada("receita_liquida", "atual", rec_atual), _entrada("receita_construcao", "atual", c_at)],
                "Base de receita usada pela administração da Light no texto.",
            )

    # --- dívida líquida derivada ----------------------------------------
    def _dl(periodo: str):
        bruta = _get(ext.divida_bruta, periodo)
        caixa = _get(ext.caixa_equivalentes, periodo)
        if bruta is None or caixa is None:
            return None, []
        apl = _get(ext.aplicacoes_financeiras, periodo)
        ent = [_entrada("divida_bruta", periodo, bruta), _entrada("caixa_equivalentes", periodo, caixa)]
        total = _mil(bruta) - _mil(caixa)
        if apl is not None:
            total -= _mil(apl)
            ent.append(_entrada("aplicacoes_financeiras", periodo, apl))
        return total, ent

    dl_at, e1 = _dl("atual")
    dl_an, e2 = _dl("anterior")
    d["divida_liquida_derivada"] = Derivado(
        "divida_liquida_derivada", "Dívida bruta − Caixa − Aplicações financeiras", "R$ mil", dl_at, dl_an, e1 + e2,
        "Valor negativo = caixa líquido (empresa com mais caixa do que dívida).",
    )

    # --- alavancagem derivada -------------------------------------------
    dl_rep_at = _get(ext.divida_liquida, "atual")
    dl_rep_an = _get(ext.divida_liquida, "anterior")
    dl_use_at = _mil(dl_rep_at) if dl_rep_at else dl_at
    dl_use_an = _mil(dl_rep_an) if dl_rep_an else dl_an

    def _lev(dl: float | None, e: float | None) -> float | None:
        if dl is None or e is None or e <= 0:
            return None  # n.s.
        return dl / e

    d["alavancagem_derivada"] = Derivado(
        "alavancagem_derivada", "Dívida líquida / EBITDA derivado", "x",
        _lev(dl_use_at, ebitda.atual), _lev(dl_use_an, ebitda.anterior), [],
        "n.s. (não significativo) quando o EBITDA é negativo. Dívida líquida = valor reportado, se existir; senão derivada.",
    )

    # --- capex de caixa --------------------------------------------------
    comps = [v for v in (ext.capex.complementares if ext.capex else []) if (v.rotulo or "").startswith("capex_componente")]
    if comps:
        d["capex_caixa_derivado"] = Derivado(
            "capex_caixa_derivado", "Σ aquisições de imobilizado e intangível (fluxo de caixa)", "R$ mil",
            sum(_mil(v) for v in comps), None, [_entrada("capex", "atual", v) for v in comps],
        )
    return d


def variation_pct(m: Metrica | None) -> float | None:
    """Variação % calculada atual vs anterior (None se indisponível ou base <= 0)."""
    if m is None or m.status == "nao_encontrado" or not m.atual or not m.anterior:
        return None
    a, b = to_base(m.atual.valor, m.atual.escala), to_base(m.anterior.valor, m.anterior.escala)
    if b <= 0:
        return None
    return (a / b - 1) * 100
