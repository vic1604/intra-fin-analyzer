"""Utilitários de texto e números no formato pt-BR.

Tudo o que o resto do pipeline precisa para comparar "o que o modelo disse"
com "o que está na página" passa por aqui: normalização de texto, parsing de
números (13.253.286 / (5.672.203) / 3,32x / 13,4%) e conversão de escala.
"""

from __future__ import annotations

import re
import unicodedata

# ---------------------------------------------------------------- texto ----

_DASHES = dict.fromkeys(map(ord, "‐‑‒–—−"), "-")
_QUOTES = {
    ord("“"): '"',
    ord("”"): '"',
    ord("‘"): "'",
    ord("’"): "'",
    ord(" "): " ",
}
_ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿"), None)


def normalize_text(text: str) -> str:
    """Normaliza texto para comparação: NFKC, hífens/aspas unificados,
    espaços colapsados. NÃO altera maiúsculas/minúsculas nem números."""
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_DASHES).translate(_QUOTES).translate(_ZERO_WIDTH)
    return re.sub(r"\s+", " ", text).strip()


def normalize_for_search(text: str) -> str:
    """Versão minúscula e sem acentos, usada apenas em busca/BM25."""
    t = normalize_text(text).lower()
    t = unicodedata.normalize("NFD", t)
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


# --------------------------------------------------------------- números ---

# Aceita: 13.253.286 | (5.672.203) | -1.234,56 | 3,32 | 13% | 0,08
_NUM_RE = re.compile(
    r"""(?<![\w.,])
        (?P<neg>\(|-|−)?\s?
        (?P<num>\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+\.\d+|\d+(?:,\d+)?)
        [xX%]?\)?
        (?![\w])""",
    re.VERBOSE,
)

SCALE_FACTOR = {"unidade": 1.0, "mil": 1e3, "milhoes": 1e6, "bilhoes": 1e9}


def parse_ptbr_number(token: str) -> float:
    """'13.253.286' -> 13253286.0 ; '3,32' -> 3.32 ; '(5.672.203)' -> -5672203.0"""
    t = token.strip()
    neg = t.startswith("(") and t.endswith(")") or t.startswith(("-", "−"))
    t = t.strip("()-−+ ").replace("%", "").replace("x", "").replace("X", "")
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", t):  # 1.180 -> 1180 (milhar pt-BR)
        t = t.replace(".", "")
    value = float(t)
    return -value if neg else value


def extract_numbers(text: str) -> list[float]:
    """Todos os números do trecho, já parseados (sinal preservado quando há
    parênteses ou hífen imediatamente antes)."""
    out: list[float] = []
    for m in _NUM_RE.finditer(text):
        raw = m.group(0)
        try:
            val = parse_ptbr_number(raw)
        except ValueError:
            continue
        if m.group("neg") and val > 0:
            val = -val
        out.append(val)
    return out


def number_in_text(value: float, text: str, rel_tol: float = 1e-9) -> bool:
    """O valor (em módulo) aparece em `text`? Compara por módulo porque o
    sinal em demonstrações costuma vir entre parênteses ou implícito no rótulo
    (ex.: 'Custos' com valor positivo)."""
    target = abs(value)
    for n in extract_numbers(text):
        if abs(abs(n) - target) <= max(rel_tol * target, 1e-9):
            return True
    return False


_NUM_ESCALA_RE = re.compile(r"(\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+)\s*(mil|milhao|milhoes|bilhao|bilhoes)\b")
_PALAVRA_ESCALA = {"mil": "mil", "milhao": "milhoes", "milhoes": "milhoes", "bilhao": "bilhoes", "bilhoes": "bilhoes"}


def rescale_from_quote(value: float, text: str) -> tuple[float, str] | None:
    """O modelo às vezes converte a escala (texto 'R$1.180 milhões' vira 1.180.000). Se o trecho
    traz literalmente 'N <mil|milhões|bilhões>' e o valor devolvido difere de N só por uma potência
    de 1000, o TRECHO manda: devolve (N, escala impressa) com o sinal do valor. Sem 'N + palavra de
    escala' no trecho, ou com dígitos diferentes, devolve None (e o grounding reprova)."""
    sign = -1.0 if value < 0 else 1.0
    v = abs(value)
    for m in _NUM_ESCALA_RE.finditer(normalize_for_search(text)):
        try:
            n = parse_ptbr_number(m.group(1))
        except ValueError:
            continue
        if n <= 0 or v <= 0:
            continue
        for k in (1, 1e3, 1e6, 1e9):
            if abs(v - n * k) <= 1e-9 * v or abs(v * k - n) <= 1e-9 * n:
                return sign * n, _PALAVRA_ESCALA[m.group(2)]
    return None


def to_base(value: float, scale: str) -> float:
    """Converte um valor para R$ (unidade)."""
    return value * SCALE_FACTOR[scale]


def pct_change(current: float, previous: float) -> float | None:
    """Variação percentual (current/previous - 1) * 100. None se previous == 0.
    Quando previous < 0 a leitura de 'variação %' perde sentido; o chamador
    decide se mostra como 'n.s.' (não significativo)."""
    if previous == 0:
        return None
    return (current / previous - 1.0) * 100.0
