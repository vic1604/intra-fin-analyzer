"""Avaliação de qualidade da extração contra o gabarito (data/reference).

Métricas (por campo e global):
  * recall       = valores corretos / valores esperados (esperados = campos que o
                   gabarito marca como encontrados, para atual e anterior)
  * precisão     = valores corretos / valores que o extrator preencheu
  * alucinação   = campos que o gabarito diz "não encontrado" mas o extrator
                   preencheu (o erro mais perigoso para um analista)
  * página       = % dos valores corretos cuja página citada confere
  * ancorado     = % dos valores preenchidos cuja evidência passou no grounding
Um valor é "correto" se, em R$ (ou na mesma unidade), o erro relativo ≤ 0,5 %
(tolera arredondamento de "R$ X milhões" vs "R$ X mil") e o sinal é igual.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .schema import CAMPOS_ENTREGA, Extracao, Metrica, Valor
from .text_utils import to_base


@dataclass
class FieldScore:
    esperados: int = 0
    preenchidos: int = 0
    corretos: int = 0
    pagina_ok: int = 0
    ancorados: int = 0
    alucinacoes: int = 0  # preencheu onde o gabarito diz "não encontrado"
    ausentes_corretos: int = 0  # disse "não encontrado" e o gabarito concorda
    detalhes: list[str] = field(default_factory=list)


def _base(v: Valor) -> float:
    if v.unidade == "R$":
        return to_base(v.valor, v.escala)
    return v.valor


def _match(pred: Valor, ref: Valor, rel_tol: float = 0.005) -> bool:
    p, r = _base(pred), _base(ref)
    if r == 0:
        return abs(p) < 1e-9
    if (p < 0) != (r < 0):
        return False
    return abs(abs(p) - abs(r)) / abs(r) <= rel_tol


def evaluate(pred: Extracao, ref: Extracao, campos: list[str] | None = None) -> dict[str, FieldScore]:
    campos = campos or CAMPOS_ENTREGA
    out: dict[str, FieldScore] = {}
    for nome in campos:
        mp: Metrica = getattr(pred, nome)
        mr: Metrica = getattr(ref, nome)
        s = FieldScore()
        ref_found = mr.status == "encontrado"
        pred_found = mp.status in ("encontrado",)  # nao_verificado conta como não preenchido
        if not ref_found:
            if pred_found:
                s.alucinacoes += 1
                s.detalhes.append(f"{pred.doc_id}.{nome}: preencheu, mas gabarito = não encontrado")
            else:
                s.ausentes_corretos += 1
            out[nome] = s
            continue
        for periodo in ("atual", "anterior"):
            rv, pv = getattr(mr, periodo), getattr(mp, periodo) if pred_found else None
            if rv is None:
                continue
            s.esperados += 1
            if pv is None:
                s.detalhes.append(f"{pred.doc_id}.{nome}.{periodo}: ausente")
                continue
            s.preenchidos += 1
            if pv.evidencia.verificada:
                s.ancorados += 1
            if _match(pv, rv):
                s.corretos += 1
                if pv.evidencia.pagina == rv.evidencia.pagina:
                    s.pagina_ok += 1
            else:
                s.detalhes.append(f"{pred.doc_id}.{nome}.{periodo}: previsto {pv.valor} ({pv.escala}) vs esperado {rv.valor} ({rv.escala})")
        out[nome] = s
    return out


def aggregate(scores: dict[str, FieldScore]) -> dict[str, float | int]:
    tot = FieldScore()
    for s in scores.values():
        for a in ("esperados", "preenchidos", "corretos", "pagina_ok", "ancorados", "alucinacoes", "ausentes_corretos"):
            setattr(tot, a, getattr(tot, a) + getattr(s, a))
    nf_total = tot.alucinacoes + tot.ausentes_corretos
    return {
        "esperados": tot.esperados,
        "preenchidos": tot.preenchidos,
        "corretos": tot.corretos,
        "recall": round(tot.corretos / tot.esperados, 3) if tot.esperados else 0.0,
        "precisao": round(tot.corretos / tot.preenchidos, 3) if tot.preenchidos else 0.0,
        "pagina_correta_entre_corretos": round(tot.pagina_ok / tot.corretos, 3) if tot.corretos else 0.0,
        "ancorados_entre_preenchidos": round(tot.ancorados / tot.preenchidos, 3) if tot.preenchidos else 0.0,
        "campos_nao_encontrados_no_gabarito": nf_total,
        "alucinacoes": tot.alucinacoes,
        "taxa_alucinacao": round(tot.alucinacoes / nf_total, 3) if nf_total else 0.0,
    }


def evaluate_all(preds: dict[str, Extracao], refs: dict[str, Extracao]) -> dict:
    per_doc, per_field_acc = {}, {}
    grand: dict[str, FieldScore] = {}
    for doc_id, ref in refs.items():
        if doc_id not in preds:
            continue
        sc = evaluate(preds[doc_id], ref)
        per_doc[doc_id] = aggregate(sc)
        for nome, s in sc.items():
            g = grand.setdefault(nome, FieldScore())
            for a in ("esperados", "preenchidos", "corretos", "pagina_ok", "ancorados", "alucinacoes", "ausentes_corretos"):
                setattr(g, a, getattr(g, a) + getattr(s, a))
            g.detalhes += s.detalhes
    for nome, g in grand.items():
        per_field_acc[nome] = {
            "esperados": g.esperados, "corretos": g.corretos,
            "recall": round(g.corretos / g.esperados, 3) if g.esperados else None,
            "alucinacoes": g.alucinacoes,
        }
    return {
        "global": aggregate(grand),
        "por_documento": per_doc,
        "por_campo": per_field_acc,
        "erros": [d for g in grand.values() for d in g.detalhes],
    }
