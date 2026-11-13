"""Varre o repositório atrás de padrões de chaves de API. Sai com código 1 se achar."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = {
    "Anthropic": r"sk-ant-[A-Za-z0-9_\-]{20,}",
    "OpenAI": r"sk-(?:proj-)?[A-Za-z0-9_\-]{32,}",
    "Azure/hex-32": r"(?i)(api[_-]?key|secret|token)\s*[=:]\s*['\"]?[A-Fa-f0-9]{32}['\"]?",
    "AWS": r"AKIA[0-9A-Z]{16}",
    "Chave genérica preenchida": r"(?m)^(?:ANTHROPIC|OPENAI|AZURE_OPENAI)_API_KEY[ \t]*=[ \t]*\S+",
}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "cache", ".venv"}
SKIP_SUFFIX = {".pdf", ".pyc", ".zip"}

hits = []
for p in ROOT.rglob("*"):
    if not p.is_file() or SKIP_DIRS & set(p.parts) or p.suffix in SKIP_SUFFIX or p.name == "check_secrets.py":
        continue
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        continue
    for name, pat in PATTERNS.items():
        for m in re.finditer(pat, txt):
            hits.append((p.relative_to(ROOT), name, m.group(0)[:12] + "…"))
if (ROOT / ".env").exists():
    print("⚠ existe .env local (ok, está no .gitignore) — não envie esta pasta sem excluí-lo.")
for h in hits:
    print("✗", *h)
print("OK: nenhum segredo encontrado" if not hits else f"{len(hits)} possível(is) segredo(s)")
sys.exit(1 if hits else 0)
