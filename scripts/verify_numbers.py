"""Verificação INDEPENDENTE do pipeline: não usa finanalyzer.ingest nem o cache.
Para cada `origem` dos JSONs de saída, extrai a página direto com `pdftotext -layout`
e confere (1) trecho literal na página e (2) número dentro do trecho.
Depois recalcula à mão os indicadores derivados. Sai com código 1 se algo divergir."""
import json, re, subprocess, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
norm = lambda s: re.sub(r"\s+", " ", unicodedata.normalize("NFC", s.replace(" ", " "))).strip()

def page_text(pdf, n):
    return norm(subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), str(pdf), "-"], capture_output=True, text=True, check=True).stdout)

def nums(t):
    out = []
    for m in re.finditer(r"\(?-?\d{1,3}(?:\.\d{3})+(?:,\d+)?\)?|\(?-?\d+(?:,\d+)?\)?", t):
        s = m.group(0); neg = s.startswith("(") or s.startswith("-")
        s = s.strip("()-").replace(".", "").replace(",", ".")
        try: out.append(float(s))
        except ValueError: pass
    return out

def walk(o):
    if isinstance(o, dict):
        if "origem" in o and "valor" in o: yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)

fails = checked = 0
cache = {}
for doc in ("light", "millet", "brasal"):
    j = json.loads((ROOT / "outputs/extracao" / f"{doc}.json").read_text(encoding="utf-8"))
    pdf = ROOT / "data/input" / f"{doc}.pdf"
    for v in walk(j):
        o = v["origem"]; key = (doc, o["pagina"])
        cache.setdefault(key, page_text(pdf, o["pagina"]))
        checked += 1
        ok_q = norm(o["trecho"]) in cache[key]
        base = abs(v["valor"]); un = v["unidade"]
        cand = {base, base / 1000, base * 1000}  # trecho pode estar na escala do documento
        ok_n = any(abs(abs(x) - c) < 1e-6 or (abs(x) > 0 and abs(abs(x) - c) / max(c, 1e-9) < 0.0006) for x in nums(o["trecho"]) for c in cand)
        if not (ok_q and ok_n):
            fails += 1; print("✗", doc, "p", o["pagina"], v["valor"], un, "trecho_ok" if ok_q else "TRECHO AUSENTE", "num_ok" if ok_n else "NÚMERO FORA DO TRECHO")
print(f"{checked} valores com origem conferidos direto no PDF; {fails} falhas")

def der(doc, k):
    j = json.loads((ROOT / "outputs/extracao" / f"{doc}.json").read_text(encoding="utf-8"))
    return j["indicadores_derivados_calculados_pelo_pipeline"][k]["periodo_atual"]

def ins(doc, k):
    j = json.loads((ROOT / "outputs/extracao" / f"{doc}.json").read_text(encoding="utf-8"))
    m = j["insumos_para_derivados"][k].get("valor_periodo_atual")
    if m is None: return 0.0  # insumo não publicado separadamente (ex.: Light: caixa já inclui TVM)
    return m["valor"] * {"R$ mil": 1, "R$ milhões": 1000}.get(m["unidade"], 1)

def rec(doc):
    j = json.loads((ROOT / "outputs/extracao" / f"{doc}.json").read_text(encoding="utf-8"))
    m = j["indicadores"]["receita_liquida"]["valor_periodo_atual"]; return m["valor"] * {"R$ mil": 1, "R$ milhões": 1000}.get(m["unidade"], 1)

bad = 0
for doc in ("light", "millet", "brasal"):
    ebitda = ins(doc, "ebit") + ins(doc, "depreciacao_amortizacao")
    esp = {"ebitda_derivado": ebitda, "margem_ebitda_derivada": 100 * ebitda / rec(doc),
           "divida_liquida_derivada": ins(doc, "divida_bruta") - ins(doc, "caixa_equivalentes") - ins(doc, "aplicacoes_financeiras")}
    for k, e in esp.items():
        got = der(doc, k)
        ok = got is not None and abs(got - e) <= 1e-3 * max(1, abs(e)) + 1e-6
        print(("✓" if ok else "✗"), doc, k, "pipeline=", round(got, 4) if got is not None else None, "recalculado=", round(e, 4))
        bad += 0 if ok else 1
sys.exit(1 if fails or bad else 0)
