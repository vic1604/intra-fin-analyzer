"""Baseline sem LLM: regras + regex sobre o texto com layout.

Para quê? (1) mostrar objetivamente o ganho do LLM; (2) funcionar como
"ML/abordagem tradicional" na comparação pedida nos diferenciais; (3) ser uma
checagem independente: se baseline e LLM concordam num número, a confiança
sobe.

Limites conhecidos (aparecem na avaliação):
  * rótulos quebrados em várias linhas (Millet) → perde o número;
  * mesma linha em escopo diferente (EBITDA da distribuidora vs consolidado);
  * não entende texto livre nem escala (milhões x mil).
"""

from __future__ import annotations

import re

from .config import KNOWN_DOCS
from .ingest import Document
from .schema import Evidencia, Extracao, Metrica, Valor
from .text_utils import extract_numbers, normalize_text

_HEAD_RESULT = re.compile(r"DEMONSTRA[ÇC][ÕO]ES? D[OE]S? RESULTADOS?", re.I)
_HEAD_DFC = re.compile(r"FLUXOS? DE CAIXA", re.I)


def _pages_with_head(doc: Document, rx: re.Pattern) -> list[int]:
    out = []
    for p in doc.pages:
        head = " ".join(p.text.split("\n")[:8])
        if rx.search(head) and "ÍNDICE" not in head.upper():
            out.append(p.number)
    return out


def _last_two(line: str) -> tuple[float, float] | None:
    nums = extract_numbers(line)
    # remove números de nota explicativa (inteiros pequenos logo após o rótulo)
    big = [n for n in nums if abs(n) >= 100 or "," in line]
    if len(big) < 2:
        return None
    return big[-2], big[-1]


def _valor(doc_id: str, pagina: int, line: str, v: float, escala="mil", unidade="R$") -> Valor:
    return Valor(valor=v, escala=escala, unidade=unidade, evidencia=Evidencia(documento=doc_id, pagina=pagina, trecho=normalize_text(line)))


def _find_line(doc: Document, pages: list[int], rx: str, join_next: int = 0):
    for n in pages:
        rows = doc.page(n).text.split("\n")
        for i, r in enumerate(rows):
            if re.search(rx, r, flags=re.I):
                return n, " ".join(rows[i : i + 1 + join_next])
    return None


def _metric_from_line(doc: Document, pages: list[int], rx: str, join_next: int = 0) -> Metrica | None:
    hit = _find_line(doc, pages, rx, join_next)
    if not hit:
        return None
    n, line = hit
    pair = _last_two(line)
    if not pair:
        return None
    a, b = pair
    return Metrica(status="encontrado", atual=_valor(doc.doc_id, n, line, a), anterior=_valor(doc.doc_id, n, line, b))


def _nf(msg: str = "fora do alcance das regras do baseline") -> Metrica:
    return Metrica(status="nao_encontrado", motivo_ausencia=msg)


def extract_baseline(doc: Document) -> Extracao:
    res_pages = _pages_with_head(doc, _HEAD_RESULT)
    dfc_pages = _pages_with_head(doc, _HEAD_DFC)
    all_pages = [p.number for p in doc.pages]

    receita = _metric_from_line(doc, res_pages, r"^\s*(RECEITA L[ÍI]QUIDA|Receita operacional l[íi]quida|Receita l[íi]quida)\b")
    lucro = _metric_from_line(doc, res_pages, r"^\s*(LUCRO \(PREJU[ÍI]ZO\) L[ÍI]QUIDO DO EXERC[ÍI]CIO|Lucro l[íi]quido do exerc[íi]cio)")
    fco = _metric_from_line(doc, dfc_pages, r"(Caixa l[íi]quido gerado|Caixa liquido gerado).*atividades operacionais")

    # EBITDA: primeira frase "EBITDA ... R$ X milhões" do documento
    ebitda = None
    for n in all_pages:
        t = normalize_text(doc.page(n).text)
        m = re.search(r"EBITDA[^.]{0,60}?R\$\s?([\d.]+)\s*milh", t)
        if m:
            val = float(m.group(1).replace(".", ""))
            trecho = t[max(0, m.start()) : m.end() + 5]
            ebitda = Metrica(status="encontrado", atual=Valor(valor=val, escala="milhoes", evidencia=Evidencia(documento=doc.doc_id, pagina=n, trecho=trecho)))
            break

    # dívida líquida: primeira linha "Dívida líquida" com número
    dl = None
    for n in all_pages:
        for r in doc.page(n).text.split("\n"):
            if re.search(r"d[íi]vida l[íi]quida", r, flags=re.I):
                nums = [x for x in extract_numbers(r) if abs(x) >= 100]
                if nums:
                    esc = "milhoes" if re.search(r"milh", r, flags=re.I) else "mil"
                    dl = Metrica(status="encontrado", atual=_valor(doc.doc_id, n, r, nums[0] if esc == "mil" else nums[-1], esc))
                    break
        if dl:
            break

    meta = KNOWN_DOCS.get(doc.doc_id, {})
    return Extracao(
        doc_id=doc.doc_id,
        empresa=meta.get("empresa", doc.doc_id),
        periodo_referencia="(baseline não infere período)",
        tipo_documento=meta.get("tipo", ""),
        moeda_escala_declarada="(não inferida)",
        receita_liquida=receita or _nf("regra não casou"),
        ebitda=ebitda or _nf("regra não casou"),
        margem_ebitda=_nf(),
        lucro_liquido=lucro or _nf("regra não casou"),
        divida_liquida=dl or _nf("regra não casou"),
        alavancagem=_nf(),
        fco=fco or _nf("regra não casou"),
        capex=_nf(),
        ebit=_nf(),
        depreciacao_amortizacao=_nf(),
        caixa_equivalentes=_nf(),
        aplicacoes_financeiras=_nf(),
        divida_bruta=_nf(),
        modo="baseline",
    )
