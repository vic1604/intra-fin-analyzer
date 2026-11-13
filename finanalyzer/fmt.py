"""Formatação pt-BR."""

from __future__ import annotations

DOC_NOME = {"light": "Light", "millet": "Millet", "brasal": "Brasal"}


def n(x: float | None, nd: int = 1) -> str:
    if x is None:
        return "n/d"
    s = f"{abs(x):,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return ("−" + s) if x < 0 and float(f"{abs(x):.{nd}f}") != 0 else s


def mi(mil: float | None, nd: int = 1) -> str:
    """Recebe valor em R$ mil -> 'R$ X mi' (ou 'R$ X bi' se >= 1 bi)."""
    if mil is None:
        return "n/d"
    v = mil / 1e3
    sg = "−" if v < 0 else ""
    v = abs(v)
    if v >= 1000:
        return f"{sg}R$ {n(v / 1e3, 2)} bi"
    return f"{sg}R$ {n(v, nd)} mi"


def pct(x: float | None, nd: int = 1, sign: bool = False) -> str:
    if x is None:
        return "n.s."
    s = n(x, nd) + "%"
    return ("+" + s) if sign and x > 0 else s


def mult(x: float | None, nd: int = 2) -> str:
    return "n.s." if x is None else f"{n(x, nd)}x"


def cite(doc: str, page: int) -> str:
    return f"[{DOC_NOME.get(doc, doc)} p.{page}]"
