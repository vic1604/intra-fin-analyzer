"""Abordagem "tradicional" (estatística / ML clássico) — comparada com regras e LLM.

O que existe aqui e por quê
---------------------------
1. DETECÇÃO DE ANOMALIAS (não supervisionada) nas linhas das demonstrações:
   para cada linha "rótulo ... 2022 2021" calculamos a variação log(|2022|/|2021|)
   e procuramos linhas atípicas DENTRO do próprio documento com
     (a) z-score robusto (mediana/MAD, limiar 3,5 — Iglewicz & Hoaglin) e
     (b) Isolation Forest (scikit-learn, opcional) sobre [variação, magnitude].
   Não precisa de rótulos nem de LLM, custa ~0 e é determinístico. Em troca, só
   enxerga "número atípico": não sabe POR QUÊ (isso as regras e o LLM explicam)
   e ignora anomalias de texto (ex.: ano repetido, ações divergentes).
   É um gerador de candidatos a revisão, não um veredito.

2. TOM DA ADMINISTRAÇÃO: só existe o léxico (`qualitative.tone_baseline`). Um
   classificador SUPERVISIONADO (TF-IDF + regressão logística) NÃO foi treinado
   porque não há corpus rotulado — são 3 documentos. Treinar com 3 exemplos
   seria teatro. Em produção: rotular algumas centenas de trechos de comentário
   da administração e treinar/avaliar com validação cruzada.

Limitações assumidas: a extração de linhas é textual e heurística (pega os dois
últimos números da linha como "período atual / comparável"); linhas com sinais
opostos entre períodos são listadas à parte (log-razão indefinido).
"""

from __future__ import annotations

import math
import re
import statistics
from dataclasses import asdict, dataclass

from .ingest import Document
from .text_utils import normalize_for_search, parse_ptbr_number

_TOKEN = re.compile(r"^\(?-?[\d.]+(?:,\d+)?\)?$|^[-–—]$")
_SKIP_PAGE = ("MUTAÇÕES", "MUTACOES", "VALOR ADICIONADO")
# só as demonstrações primárias (DRE, balanço, fluxo de caixa): notas explicativas têm colunas que não são "atual/comparável"
_STATEMENT = (
    "DEMONSTRAÇÕES DOS RESULTADOS", "DEMONSTRAÇÕES DE RESULTADOS", "DEMONSTRAÇÃO DO RESULTADO", "DEMONSTRAÇÕES DO RESULTADO",
    "BALANÇO PATRIMONIAL", "BALANÇOS PATRIMONIAIS", "FLUXO DE CAIXA", "FLUXOS DE CAIXA",
)
MAD_THRESHOLD = 3.5


@dataclass
class Linha:
    documento: str
    pagina: int
    rotulo: str
    atual: float
    anterior: float
    trecho: str
    log_razao: float | None = None
    z_robusto: float | None = None
    anomalia_zscore: bool = False
    anomalia_iforest: bool | None = None
    inversao_de_sinal: bool = False


def _num(tok: str) -> float | None:
    if tok in ("-", "–", "—"):
        return 0.0
    try:
        return parse_ptbr_number(tok)
    except ValueError:
        return None


def extrair_linhas(doc: Document) -> list[Linha]:
    """Linhas das demonstrações com ao menos dois números no fim: (atual, comparável)."""
    out, seen = [], set()
    for p in doc.pages:
        titulos = [" ".join(l.split()).upper() for l in p.text.split("\n")[:10] if l.strip() and len(l.strip()) <= 90 and "," not in l]  # título curto, não frase de nota
        if not any(h in t for t in titulos for h in _STATEMENT) or any(s in t for t in titulos for s in _SKIP_PAGE):
            continue
        for ln in p.text.splitlines():
            raw = " ".join(ln.split())
            toks = raw.split(" ")
            if len(toks) < 3 or not _TOKEN.match(toks[-1]) or not _TOKEN.match(toks[-2]):
                continue
            a, b = _num(toks[-2]), _num(toks[-1])
            if a is None or b is None:
                continue
            label_toks = []
            for t in toks[:-2]:
                if _TOKEN.match(t) and re.search(r"\d", t):
                    continue  # número de nota / valores da controladora no meio da linha
                label_toks.append(t)
            label = " ".join(label_toks).lstrip("# ").strip(" -")
            if len(re.findall(r"[A-Za-zÀ-ÿ]", label)) < 4 or max(abs(a), abs(b)) < 1000:
                continue
            key = (label, a, b)
            if key in seen:
                continue
            seen.add(key)
            out.append(Linha(doc.doc_id, p.number, label, a, b, raw))
    return out


def _robust_z(values: list[float]) -> tuple[float, float]:
    med = statistics.median(values)
    mad = statistics.median(abs(v - med) for v in values) or 1e-9
    return med, 1.4826 * mad


def detectar_anomalias(linhas: list[Linha], usar_iforest: bool = True) -> list[Linha]:
    pontos = []
    for l in linhas:
        if l.atual == 0 or l.anterior == 0:
            continue
        if l.atual * l.anterior < 0:
            l.inversao_de_sinal = True
            continue
        l.log_razao = math.log(abs(l.atual) / abs(l.anterior))
        pontos.append(l)
    if len(pontos) < 8:  # poucos dados: não há distribuição para comparar
        return linhas
    med, escala = _robust_z([l.log_razao for l in pontos])
    for l in pontos:
        l.z_robusto = (l.log_razao - med) / escala
        l.anomalia_zscore = abs(l.z_robusto) >= MAD_THRESHOLD
    if usar_iforest:
        try:
            from sklearn.ensemble import IsolationForest
        except ImportError:  # scikit-learn é opcional
            return linhas
        X = [[l.log_razao, math.log(max(abs(l.atual), abs(l.anterior)))] for l in pontos]
        pred = IsolationForest(n_estimators=200, contamination=0.05, random_state=0).fit_predict(X)
        for l, y in zip(pontos, pred):
            l.anomalia_iforest = bool(y == -1)
    return linhas


def _fmt_milhar(v: float) -> str:
    return f"{abs(v):,.0f}".replace(",", ".")


def _cobertura(l: Linha, textos: list[str]) -> bool:
    """Heurística: algum alerta/anomalia JÁ existente descreve esta linha?
    Vale (a) o número impresso (ex.: '105.633') aparecer no alerta, ou (b) >=3 palavras do rótulo
    (e >=60% delas) aparecerem no MESMO alerta. Casar palavras soltas em texto concatenado dá falso positivo."""
    stop = {"de", "da", "do", "das", "dos", "e", "a", "o", "em", "por", "com", "para", "liquido", "liquida", "total", "ativo", "passivo"}
    pal = [w for w in normalize_for_search(l.rotulo).split() if len(w) > 3 and w not in stop and not w.isdigit()]
    nums = {_fmt_milhar(v) for v in (l.atual, l.anterior) if abs(v) >= 1000}
    for t in textos:
        if any(x in t for x in nums):
            return True
        tn = normalize_for_search(t)
        achou = [w for w in pal if w in tn]
        if len(achou) >= 3 and len(achou) / max(len(pal), 1) >= 0.6:
            return True
    return False


def analisar(docs: dict[str, Document], textos_alertas: dict[str, list[str]] | None = None, top: int = 10) -> dict:
    textos_alertas = textos_alertas or {}
    res: dict = {"metodo": {"zscore_robusto": f"|z| >= {MAD_THRESHOLD} (mediana/MAD)", "isolation_forest": "contamination=0.05, random_state=0 (se scikit-learn instalado)"}, "documentos": {}}
    for d, doc in docs.items():
        linhas = detectar_anomalias(extrair_linhas(doc))
        ptos = [l for l in linhas if l.log_razao is not None]
        flag_all = sorted((l for l in ptos if l.anomalia_zscore or l.anomalia_iforest), key=lambda l: -abs(l.z_robusto or 0))
        flag, vistos = [], set()
        for l in flag_all:  # a mesma linha costuma aparecer na DRE e no fluxo de caixa: conta uma vez
            k = (round(l.atual), round(l.anterior))
            if k not in vistos:
                vistos.add(k)
                flag.append(l)
        cobertas = [l for l in flag if _cobertura(l, textos_alertas.get(d, []))]
        res["documentos"][d] = {
            "linhas_extraidas": len(linhas),
            "linhas_pontuadas": len(ptos),
            "inversoes_de_sinal": sum(1 for l in linhas if l.inversao_de_sinal),
            "sinalizadas_zscore": sum(1 for l in flag if l.anomalia_zscore),
            "sinalizadas_iforest": sum(1 for l in flag if l.anomalia_iforest) if any(l.anomalia_iforest is not None for l in ptos) else None,
            "sinalizadas_ambos": sum(1 for l in flag if l.anomalia_zscore and l.anomalia_iforest),
            "sinalizadas_que_coincidem_com_alerta_existente": len(cobertas),
            "top": [asdict(l) | {"coincide_com_alerta_existente": l in cobertas} for l in flag[:top]],
        }
    return res


def comparar_tom(quals: dict) -> dict:
    """Léxico (baseline sem ML) vs tom classificado (gabarito/LLM). n = nº de documentos: NÃO é estatística, é sanity-check."""
    from .qualitative import tone_baseline

    out = {}
    for d, q in quals.items():
        textos = [i.texto for i in (*q.motivos_resultado, *q.riscos, *q.eventos_relevantes, *q.guidance)]
        lex = tone_baseline(textos)
        out[d] = {"tom_classificado": q.tom, "tom_lexico": lex["tom"], "score_lexico": lex["score"], "pos": lex["pos"], "neg": lex["neg"], "concorda": lex["tom"] == q.tom}
    out["_resumo"] = {"documentos": len(quals), "concordancias": sum(1 for d, v in out.items() if d != "_resumo" and v["concorda"])}
    return out
