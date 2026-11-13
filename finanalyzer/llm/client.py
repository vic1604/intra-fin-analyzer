"""Cliente LLM mínimo e agnóstico de provedor.

Provedores (variável LLM_PROVIDER):
  anthropic | openai | azure_openai   -> SDKs oficiais (exigem chave paga)
  ollama                              -> modelo open source LOCAL, sem conta e sem chave
  openai_compatible | gemini          -> qualquer API compatível com /chat/completions
                                         (inclui camadas gratuitas); chave via LLM_API_KEY / GEMINI_API_KEY

O restante do código só conhece `LLMClient.complete(...)`, então trocar de
modelo/provedor é configuração, não refatoração.

Os clientes `ollama` e `openai_compatible` usam apenas a biblioteca padrão
(urllib) e têm testes automatizados contra um servidor HTTP local falso
(tests/test_llm_http.py): o formato de requisição/resposta, os cabeçalhos, o
mapeamento de tokens e o *retry* são exercitados de verdade. O que NÃO foi
verificado é o comportamento de serviços reais de terceiros — para isso use
`python -m finanalyzer smoke-llm`.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass
class LLMResult:
    text: str
    data: dict | None
    input_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0
    cached: bool = False  # True = veio do cache em disco (tokens são os medidos na chamada original; latência 0)


@dataclass
class UsageMeter:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0
    cache_hits: int = 0
    log: list[dict] = field(default_factory=list)

    def add(self, label: str, r: LLMResult) -> None:
        self.calls += 1
        self.cache_hits += int(r.cached)
        self.input_tokens += r.input_tokens
        self.output_tokens += r.output_tokens
        self.seconds += r.latency_s
        self.log.append({"etapa": label, "in": r.input_tokens, "out": r.output_tokens, "s": round(r.latency_s, 2), "cache": r.cached})

    def cost_usd(self, price_in: float, price_out: float) -> float:
        return self.input_tokens / 1e6 * price_in + self.output_tokens / 1e6 * price_out


class LLMClient(Protocol):
    name: str

    def complete(self, system: str, user: str, max_tokens: int = 4096, json_schema: dict | None = None) -> LLMResult: ...


def parse_json_loose(text: str) -> dict | None:
    """Extrai o primeiro objeto JSON de um texto (tolera ```json ... ```)."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
    return None


class AnthropicClient:
    name = "anthropic"

    def __init__(self, model: str):
        import anthropic  # import tardio: só exigido no modo llm

        self.model = model
        self.client = anthropic.Anthropic()  # lê ANTHROPIC_API_KEY do ambiente

    def complete(self, system, user, max_tokens=4096, json_schema=None) -> LLMResult:
        t0 = time.perf_counter()
        kwargs = dict(model=self.model, max_tokens=max_tokens, system=system, messages=[{"role": "user", "content": user}])
        if json_schema:  # saída estruturada via "tool use" forçado
            kwargs["tools"] = [{"name": "registrar_resultado", "description": "Registra o resultado estruturado.", "input_schema": json_schema}]
            kwargs["tool_choice"] = {"type": "tool", "name": "registrar_resultado"}
        resp = self.client.messages.create(**kwargs)
        data, text = None, ""
        for block in resp.content:
            if getattr(block, "type", "") == "tool_use":
                data = block.input
            elif getattr(block, "type", "") == "text":
                text += block.text
        if data is None and text:
            data = parse_json_loose(text)
        return LLMResult(text or json.dumps(data or {}), data, resp.usage.input_tokens, resp.usage.output_tokens, time.perf_counter() - t0)


class OpenAIClient:
    name = "openai"

    def __init__(self, model: str, azure: bool = False):
        import openai

        self.model = model
        if azure:
            self.client = openai.AzureOpenAI(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
            )
            self.name = "azure_openai"
        else:
            self.client = openai.OpenAI()  # lê OPENAI_API_KEY

    def complete(self, system, user, max_tokens=4096, json_schema=None) -> LLMResult:
        t0 = time.perf_counter()
        sys_msg = system + ("\n\nResponda SOMENTE com um objeto JSON válido." if json_schema else "")
        resp = self.client.chat.completions.create(
            model=self.model,  # no Azure: nome do *deployment*
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": user}],
            response_format={"type": "json_object"} if json_schema else None,
            max_completion_tokens=max_tokens,
        )
        text = resp.choices[0].message.content or ""
        return LLMResult(text, parse_json_loose(text) if json_schema else None, resp.usage.prompt_tokens, resp.usage.completion_tokens, time.perf_counter() - t0)


class LLMHTTPError(RuntimeError):
    pass


_MSG_TRUNCADA = (
    "resposta cortada pelo limite de saída (max_tokens={max_tokens}): o JSON ficaria incompleto. "
    "Aumente LLM_MAX_TOKENS no .env (modelos que 'pensam', como o Gemini 3.x, gastam parte do limite raciocinando; "
    "use 16384 ou mais)."
)


def _default_retries() -> int:
    try:
        return max(1, int(os.getenv("LLM_RETRIES", "7")))
    except ValueError:
        return 7


def _post_json(url: str, payload: dict, headers: dict[str, str], timeout: float, retries: int | None = None) -> dict:
    """POST JSON com *retry* e *backoff* em 429/5xx e erros de rede.
    Picos de demanda (503) em camadas gratuitas duram minutos: por padrão são 7 tentativas
    com espera de 2, 4, 8, 16, 32 e 45 s (≈ 107 s no total) — ajuste com LLM_RETRIES.
    Nunca inclui cabeçalhos (chave de API) nas mensagens de erro."""
    retries = _default_retries() if retries is None else retries
    body = json.dumps(payload).encode("utf-8")
    last: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", **headers}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (URL vem de configuração do usuário)
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            last = LLMHTTPError(f"HTTP {e.code} em {url}: {detail}")
            if e.code not in (408, 429, 500, 502, 503, 504):
                raise last from None
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = LLMHTTPError(f"falha de rede em {url}: {getattr(e, 'reason', e)}")
        if attempt < retries - 1:
            time.sleep(min(2 ** (attempt + 1), 45) * _RETRY_SLEEP_SCALE)
    raise last  # type: ignore[misc]


_RETRY_SLEEP_SCALE = 1.0  # os testes zeram para não esperar


class OllamaClient:
    """Modelo open source local via Ollama (https://ollama.com). Sem chave, sem conta.

    Usa a API nativa `/api/chat` porque ela permite fixar `num_ctx` por requisição:
    o padrão do Ollama (2–4 mil tokens) TRUNCARIA em silêncio os ~15 mil tokens
    de contexto que enviamos, e o modelo responderia sem ter visto as páginas.
    """

    name = "ollama"

    def __init__(self, model: str, host: str | None = None, num_ctx: int | None = None, timeout: float | None = None):
        self.model = model
        self.host = (host or os.getenv("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")
        if not self.host.startswith("http"):
            self.host = "http://" + self.host
        self.num_ctx = int(num_ctx or os.getenv("OLLAMA_NUM_CTX", "32768"))
        self.timeout = float(timeout or os.getenv("LLM_TIMEOUT", "1800"))  # CPU é lenta: 30 min por chamada

    def complete(self, system, user, max_tokens=4096, json_schema=None) -> LLMResult:
        t0 = time.perf_counter()
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "options": {"num_ctx": self.num_ctx, "num_predict": max_tokens, "temperature": 0},
        }
        if json_schema:
            payload["format"] = json_schema  # saída estruturada por schema (Ollama >= 0.5); versões antigas ignoram e o parse tolerante cobre
        data = _post_json(f"{self.host}/api/chat", payload, {}, self.timeout)
        text = (data.get("message") or {}).get("content", "") or ""
        if data.get("done_reason") == "length":
            raise LLMHTTPError(_MSG_TRUNCADA.format(max_tokens=max_tokens))
        in_tok, out_tok = int(data.get("prompt_eval_count") or 0), int(data.get("eval_count") or 0)
        if in_tok and in_tok >= self.num_ctx - 8:  # contexto estourou: o modelo não viu tudo
            raise LLMHTTPError(f"prompt ({in_tok} tokens) preencheu todo o contexto num_ctx={self.num_ctx}; aumente OLLAMA_NUM_CTX ou reduza TOP_K_PAGES/MAX_PAGES")
        return LLMResult(text, parse_json_loose(text) if json_schema else None, in_tok, out_tok, time.perf_counter() - t0)


class OpenAICompatClient:
    """Qualquer API compatível com `POST {base_url}/chat/completions`
    (Gemini via endpoint OpenAI-compatível, Groq, OpenRouter, vLLM, LM Studio, GitHub Models...)."""

    name = "openai_compatible"

    def __init__(self, model: str, base_url: str, api_key: str | None, timeout: float | None = None):
        if not base_url:
            raise ValueError("defina LLM_BASE_URL (ex.: a URL base da API compatível com OpenAI)")
        self.model, self.base_url = model, base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = float(timeout or os.getenv("LLM_TIMEOUT", "300"))

    def complete(self, system, user, max_tokens=4096, json_schema=None) -> LLMResult:
        t0 = time.perf_counter()
        sys_msg = system + ("\n\nResponda SOMENTE com um objeto JSON válido." if json_schema else "")
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": user}],
            "max_tokens": max_tokens,
            "temperature": 0,
        }
        if json_schema:
            payload["response_format"] = {"type": "json_object"}
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        data = _post_json(f"{self.base_url}/chat/completions", payload, headers, self.timeout)
        choices = data.get("choices") or []
        text = ((choices[0].get("message") or {}).get("content") if choices else "") or ""
        if choices and choices[0].get("finish_reason") == "length":
            raise LLMHTTPError(_MSG_TRUNCADA.format(max_tokens=max_tokens))
        usage = data.get("usage") or {}
        return LLMResult(text, parse_json_loose(text) if json_schema else None, int(usage.get("prompt_tokens") or 0), int(usage.get("completion_tokens") or 0), time.perf_counter() - t0)



class CachingLLM:
    """Cache em disco das respostas do modelo (chave = hash de provedor+modelo+prompt+schema+max_tokens).

    Para que serve: camadas gratuitas oscilam (503/429). Se a execução cair no meio, a próxima
    continua de onde parou, e `eval` reaproveita a extração do `run` sem gastar cota de novo.
    Só respostas bem-sucedidas são guardadas (truncadas/erros lançam exceção antes). O arquivo
    guarda apenas a resposta do modelo e as contagens de tokens — nunca chaves nem o prompt.
    Honestidade nas métricas: em acerto de cache os tokens reportados são os da chamada original,
    a latência é 0 e a chamada é marcada `cache=true` (o manifesto informa quantas vieram do cache).
    Desligue com LLM_CACHE=0 para medir tempo/custo do zero."""

    def __init__(self, inner, cache_dir: Path):
        self.inner = inner
        self.cache_dir = Path(cache_dir)
        self.name = getattr(inner, "name", "llm")

    def _key(self, system, user, max_tokens, json_schema) -> str:
        ident = [self.name, getattr(self.inner, "model", ""), system, user, max_tokens, json_schema]
        return hashlib.sha256(json.dumps(ident, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    def complete(self, system, user, max_tokens=4096, json_schema=None) -> LLMResult:
        path = self.cache_dir / f"{self._key(system, user, max_tokens, json_schema)}.json"
        if path.exists():
            try:
                c = json.loads(path.read_text(encoding="utf-8"))
                text = c["text"]
                return LLMResult(text, parse_json_loose(text) if json_schema else None, int(c["in"]), int(c["out"]), 0.0, cached=True)
            except (OSError, ValueError, KeyError):
                pass  # cache corrompido: ignora e refaz a chamada
        r = self.inner.complete(system, user, max_tokens, json_schema)
        if r.text.strip():
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"text": r.text, "in": r.input_tokens, "out": r.output_tokens, "s": round(r.latency_s, 2)}, ensure_ascii=False), encoding="utf-8")
        return r


class FakeLLM:
    """LLM de mentira para testes: devolve respostas pré-definidas."""

    name = "fake"

    def __init__(self, responses: list[dict | str]):
        self.responses = list(responses)
        self.calls: list[dict] = []

    def complete(self, system, user, max_tokens=4096, json_schema=None) -> LLMResult:
        self.calls.append({"system": system, "user": user, "schema": bool(json_schema)})
        r = self.responses.pop(0) if self.responses else {}
        text = r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)
        return LLMResult(text, r if isinstance(r, dict) else parse_json_loose(text), len(user) // 4, len(text) // 4, 0.0)


GEMINI_OPENAI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai"


def make_client(provider: str, model: str) -> LLMClient:
    provider = provider.lower()
    if provider == "anthropic":
        return AnthropicClient(model)
    if provider == "openai":
        return OpenAIClient(model)
    if provider in ("azure", "azure_openai"):
        return OpenAIClient(model, azure=True)
    if provider == "ollama":
        return OllamaClient(model)
    if provider == "gemini":
        key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        if not key:
            raise ValueError("defina GEMINI_API_KEY (chave gratuita do Google AI Studio)")
        return OpenAICompatClient(model, os.getenv("LLM_BASE_URL") or GEMINI_OPENAI_BASE, key)
    if provider in ("openai_compatible", "compat"):
        return OpenAICompatClient(model, os.getenv("LLM_BASE_URL", ""), os.getenv("LLM_API_KEY"))
    raise ValueError(f"LLM_PROVIDER inválido: {provider} (use anthropic | openai | azure_openai | ollama | gemini | openai_compatible)")
