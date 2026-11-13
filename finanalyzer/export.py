"""JSON de entrega por documento (formato pedido no teste): cada valor com
origem (página + trecho); ausência explícita; derivados separados."""

from __future__ import annotations

from .derive import Derivado, variation_pct
from .schema import Extracao, Metrica, Valor
from .validate import Check

_UNID = {"mil": "R$ mil", "milhoes": "R$ milhões", "bilhoes": "R$ bilhões", "unidade": "R$"}


def _unidade(v: Valor) -> str:
    return v.unidade if v.unidade != "R$" else _UNID[v.escala]


def _val(v: Valor | None) -> dict | None:
    if v is None:
        return None
    return {
        "valor": v.valor,
        "unidade": _unidade(v),
        **({"rotulo": v.rotulo} if v.rotulo else {}),
        "origem": {"documento": v.evidencia.documento, "pagina": v.evidencia.pagina, "trecho": v.evidencia.trecho, "verificada": v.evidencia.verificada},
    }


def _metrica(m: Metrica) -> dict:
    if m.status == "nao_encontrado":
        out = {"status": "não encontrado", "motivo": m.motivo_ausencia}
        if m.termos_verificados:
            out["termos_buscados_no_pdf"] = m.termos_verificados
        if m.complementares:
            out["complementares"] = [_val(v) for v in m.complementares]
        return out
    out = {
        "status": {"encontrado": "encontrado", "nao_verificado": "não verificado (falhou no grounding)"}[m.status],
        "valor_periodo_atual": _val(m.atual),
        "valor_periodo_comparavel": _val(m.anterior),
        "variacao_pct_calculada": None if variation_pct(m) is None else round(variation_pct(m), 2),
        "variacao_pct_reportada": _val(m.variacao_reportada_pct),
        "variacao_absoluta_reportada": _val(m.variacao_reportada_abs),
    }
    if m.alternativas:
        out["outras_mencoes"] = [_val(v) for v in m.alternativas]
    if m.complementares:
        out["complementares"] = [_val(v) for v in m.complementares]
    if m.observacao:
        out["observacao"] = m.observacao
    return {k: v for k, v in out.items() if v not in (None, [])}


def to_deliverable(ext: Extracao, ders: dict[str, Derivado], checks: list[Check]) -> dict:
    campos = ["receita_liquida", "receita_liquida_ex_construcao", "ebitda", "margem_ebitda", "lucro_liquido", "divida_liquida", "alavancagem", "fco", "capex"]
    ind = {c: _metrica(getattr(ext, c)) for c in campos if getattr(ext, c) is not None}
    return {
        "empresa": ext.empresa,
        "periodo_referencia": ext.periodo_referencia,
        "documento": f"{ext.doc_id}.pdf",
        "tipo_documento": ext.tipo_documento,
        "escala_declarada": ext.moeda_escala_declarada,
        "modo_extracao": ext.modo,
        "indicadores": ind,
        "insumos_para_derivados": {c: _metrica(getattr(ext, c)) for c in ("ebit", "depreciacao_amortizacao", "caixa_equivalentes", "aplicacoes_financeiras", "divida_bruta", "receita_construcao") if getattr(ext, c) is not None},
        "indicadores_derivados_calculados_pelo_pipeline": {
            k: {
                "formula": d.formula,
                "unidade": d.unidade,
                "periodo_atual": None if d.atual is None else round(d.atual, 4),
                "periodo_comparavel": None if d.anterior is None else round(d.anterior, 4),
                "entradas": [{"campo": e.campo, "valor_R$_mil": e.valor_mil, "pagina": e.pagina, "trecho": e.trecho} for e in d.entradas if e.periodo == "atual"],
                "nota": d.nota,
            }
            for k, d in ders.items()
        },
        "anomalias_no_documento": [
            {"id": a.id, "severidade": a.severidade, "descricao": a.descricao, "evidencias": [{"pagina": e.pagina, "trecho": e.trecho, "verificada": e.verificada} for e in a.evidencias]}
            for a in ext.anomalias_documento
        ],
        "validacoes": [c.to_dict() for c in checks],
    }
