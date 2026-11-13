"""Clientes de LLM exercitados por HTTP de verdade contra um servidor local falso."""
import re

import pytest

import finanalyzer.llm.client as C
from finanalyzer.llm.client import LLMHTTPError, OllamaClient, OpenAICompatClient, make_client

from fake_llm_server import FakeServer

SCHEMA = {"type": "object", "properties": {"ok": {"type": "boolean"}}}


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(C, "_RETRY_SLEEP_SCALE", 0.0)


def test_ollama_request_and_usage():
    with FakeServer(lambda p, path: {"ok": True}) as s:
        r = OllamaClient("modelo-x", host=s.url, num_ctx=20000).complete("sys", "user", 512, json_schema=SCHEMA)
    req = s.requests[0]
    assert req["path"] == "/api/chat"
    p = req["payload"]
    assert p["model"] == "modelo-x" and p["stream"] is False
    assert p["options"] == {"num_ctx": 20000, "num_predict": 512, "temperature": 0}
    assert p["format"] == SCHEMA  # saída estruturada por schema
    assert [m["role"] for m in p["messages"]] == ["system", "user"]
    assert r.data == {"ok": True} and r.input_tokens == 1234 and r.output_tokens == 56


def test_ollama_detects_context_overflow():
    with FakeServer(lambda p, path: {"ok": True}) as s:
        with pytest.raises(LLMHTTPError, match="num_ctx"):
            OllamaClient("m", host=s.url, num_ctx=1200).complete("s", "u", json_schema=SCHEMA)  # prompt_eval_count=1234 >= 1200


def test_compat_sends_bearer_and_json_mode():
    with FakeServer(lambda p, path: {"ok": True}) as s:
        r = OpenAICompatClient("m", s.url + "/v1", "CHAVE-SECRETA-123").complete("sys", "user", 300, json_schema=SCHEMA)
    q = s.requests[0]
    assert q["path"] == "/v1/chat/completions" and q["auth"] == "Bearer CHAVE-SECRETA-123"
    assert q["payload"]["response_format"] == {"type": "json_object"} and q["payload"]["max_tokens"] == 300
    assert "JSON" in q["payload"]["messages"][0]["content"]
    assert r.data == {"ok": True} and (r.input_tokens, r.output_tokens) == (1234, 56)


def test_retry_on_429_then_success():
    with FakeServer(lambda p, path: {"ok": True}, fail_first=2, fail_code=429) as s:
        r = OllamaClient("m", host=s.url).complete("s", "u", json_schema=SCHEMA)
    assert len(s.requests) == 3 and r.data == {"ok": True}


def test_no_retry_on_400_and_key_not_leaked():
    with FakeServer(fail_first=5, fail_code=400) as s:
        with pytest.raises(LLMHTTPError) as e:
            OpenAICompatClient("m", s.url, "CHAVE-SECRETA-123").complete("s", "u")
    assert len(s.requests) == 1  # erro do cliente não é repetido
    assert "CHAVE-SECRETA-123" not in str(e.value)


def test_gives_up_after_retries(monkeypatch):
    monkeypatch.setenv("LLM_RETRIES", "3")
    with FakeServer(fail_first=10, fail_code=503) as s:
        with pytest.raises(LLMHTTPError, match="503"):
            OllamaClient("m", host=s.url).complete("s", "u")
    assert len(s.requests) == 3


def test_default_retries_is_patient_and_survives_long_503_spike(monkeypatch):
    """Pico de demanda (503) por 6 tentativas seguidas: com o padrão (7) ainda dá certo na 7ª."""
    monkeypatch.delenv("LLM_RETRIES", raising=False)
    assert C._default_retries() == 7
    with FakeServer(fail_first=6, fail_code=503) as s:
        r = OllamaClient("m", host=s.url).complete("s", "u")
    assert len(s.requests) == 7 and r.text


def test_retries_env_invalid_falls_back(monkeypatch):
    monkeypatch.setenv("LLM_RETRIES", "abc")
    assert C._default_retries() == 7


def test_network_failure_message():
    with pytest.raises(LLMHTTPError, match="falha de rede"):
        OllamaClient("m", host="http://127.0.0.1:9", timeout=2).complete("s", "u")


def test_make_client_routing(monkeypatch):
    assert make_client("ollama", "m").name == "ollama"
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        make_client("gemini", "m")
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    g = make_client("gemini", "m")
    assert isinstance(g, OpenAICompatClient) and "generativelanguage.googleapis.com" in g.base_url
    monkeypatch.setenv("LLM_BASE_URL", "http://h/v1")
    assert make_client("openai_compatible", "m").base_url == "http://h/v1"
    with pytest.raises(ValueError, match="inválido"):
        make_client("nao-existe", "m")


# --------------------------------------------------------------------------
# Ponta a ponta do modo `llm` com um "modelo perfeito" atrás do HTTP:
# prova ingestão -> seleção de páginas -> prompt -> HTTP -> parse -> grounding
# -> validação -> relatório, sem depender de serviço externo.
# --------------------------------------------------------------------------
def _perfect_model(settings):
    from finanalyzer.extract import load_reference
    from finanalyzer.llm.prompts import SYSTEM_QUALI
    from finanalyzer.qualitative import load_reference_quali
    from fake_llm_server import extracao_to_llm_json, quali_to_llm_json

    def respond(payload, path):
        msgs = payload["messages"]
        doc = re.search(r'<documento id="(\w+)"', msgs[1]["content"]).group(1)
        if msgs[0]["content"][:50] == SYSTEM_QUALI[:50]:
            return quali_to_llm_json(load_reference_quali(settings, doc))
        return extracao_to_llm_json(load_reference(settings, doc))

    return respond


def test_full_llm_mode_end_to_end_over_http(real_run, settings, tmp_path):
    import dataclasses

    from finanalyzer.pipeline import run_pipeline

    s = dataclasses.replace(settings, output_dir=tmp_path)
    with FakeServer(_perfect_model(settings)) as srv:
        run = run_pipeline(s, mode="llm", llm=OllamaClient("fake", host=srv.url, num_ctx=65536))
    assert run.mode == "llm" and set(run.exts) == {"light", "millet", "brasal"}
    assert sum(len(v) for v in run.grounding_failures.values()) == 0
    assert all(e.modo == "llm" for e in run.exts.values())
    assert run.exts["light"].receita_liquida.atual.evidencia.pagina == 20
    assert run.meter.calls == 6 and run.meter.input_tokens == 6 * 1234  # 2 chamadas por documento
    assert (tmp_path / "relatorio.html").exists() and (tmp_path / "extracao" / "light.json").exists()
    # os prompts enviados ao modelo isolam o PDF em tags e declaram o PDF como não confiável
    first_user = srv.requests[0]["payload"]["messages"][1]["content"]
    assert '<documento id="' in first_user
    assert all(r["payload"]["options"]["num_ctx"] == 65536 for r in srv.requests)


def test_llm_mode_blocks_hallucinating_model_over_http(real_run, settings, tmp_path):
    """Modelo que inventa a receita da Brasal com citação falsa: o grounding barra e o relatório alerta."""
    import dataclasses

    from finanalyzer.pipeline import run_pipeline

    good = _perfect_model(settings)

    def liar(payload, path):
        out = good(payload, path)
        if "campos" in out and '<documento id="brasal"' in payload["messages"][1]["content"]:
            for c in out["campos"]:
                if c["campo"] == "receita_liquida" and c["periodo"] == "atual":
                    c["valor"], c["trecho"] = 9_999_999, "RECEITA LÍQUIDA 9.999.999"
        return out

    s = dataclasses.replace(settings, output_dir=tmp_path)
    with FakeServer(liar) as srv:
        run = run_pipeline(s, mode="llm", llm=OllamaClient("fake", host=srv.url, num_ctx=65536))
    fails = run.grounding_failures["brasal"]
    assert any(f.campo.startswith("receita_liquida") for f in fails)
    assert run.exts["brasal"].receita_liquida.status != "encontrado"
    assert any(c.id == "C00" for c in run.checks["brasal"])  # a falha aparece como alerta
    assert "grounding" in (tmp_path / "relatorio.md").read_text(encoding="utf-8").lower()


def test_truncated_response_raises_clear_error_compat():
    """Modelo que 'pensa' (Gemini 3.x) estoura max_tokens: erro explicativo, nunca JSON pela metade."""
    with FakeServer(lambda p, path: '{"ok": tr', finish_reason="length") as s:
        with pytest.raises(LLMHTTPError, match="LLM_MAX_TOKENS"):
            OpenAICompatClient("m", s.url + "/v1", "k").complete("s", "u", 64, json_schema=SCHEMA)


def test_truncated_response_raises_clear_error_ollama():
    with FakeServer(lambda p, path: '{"ok": tr', finish_reason="length") as s:
        with pytest.raises(LLMHTTPError, match="LLM_MAX_TOKENS"):
            OllamaClient("m", host=s.url).complete("s", "u", 64, json_schema=SCHEMA)


def test_finish_reason_stop_is_fine():
    with FakeServer(lambda p, path: {"ok": True}, finish_reason="stop") as s:
        assert OpenAICompatClient("m", s.url + "/v1", "k").complete("s", "u", 64, json_schema=SCHEMA).data == {"ok": True}


# ------------------------------------------------------------------ cache ---
def test_caching_llm_reuses_identical_calls_and_marks_them(tmp_path):
    from finanalyzer.llm.client import CachingLLM, FakeLLM, UsageMeter

    inner = FakeLLM([{"a": 1}, {"b": 2}])
    llm = CachingLLM(inner, tmp_path / "llm")
    meter = UsageMeter()
    r1 = llm.complete("sys", "user", 100, json_schema=SCHEMA)
    r2 = llm.complete("sys", "user", 100, json_schema=SCHEMA)  # idêntica: cache
    r3 = llm.complete("sys", "OUTRO prompt", 100, json_schema=SCHEMA)  # diferente: chama o modelo
    for i, r in enumerate((r1, r2, r3)):
        meter.add(f"x{i}", r)
    assert len(inner.calls) == 2
    assert (r1.cached, r2.cached, r3.cached) == (False, True, False)
    assert r2.data == {"a": 1} and r2.latency_s == 0.0 and r2.input_tokens == r1.input_tokens
    assert meter.calls == 3 and meter.cache_hits == 1 and meter.log[1]["cache"] is True


def test_caching_llm_survives_new_process_and_corrupt_file(tmp_path):
    from finanalyzer.llm.client import CachingLLM, FakeLLM

    d = tmp_path / "llm"
    CachingLLM(FakeLLM([{"a": 1}]), d).complete("s", "u", 10, json_schema=SCHEMA)
    inner2 = FakeLLM([{"a": 999}])
    assert CachingLLM(inner2, d).complete("s", "u", 10, json_schema=SCHEMA).data == {"a": 1}  # outro "processo", mesmo disco
    assert inner2.calls == []
    for f in d.glob("*.json"):
        f.write_text("{corrompido", encoding="utf-8")
    assert CachingLLM(inner2, d).complete("s", "u", 10, json_schema=SCHEMA).data == {"a": 999}  # refaz a chamada


def test_caching_llm_does_not_cache_errors_or_store_secrets(tmp_path):
    from finanalyzer.llm.client import CachingLLM

    class Quebra:
        name = "q"
        model = "m"

        def complete(self, *a, **k):
            raise LLMHTTPError("503")

    d = tmp_path / "llm"
    with pytest.raises(LLMHTTPError):
        CachingLLM(Quebra(), d).complete("s", "u")
    assert not list(d.glob("*.json")) if d.exists() else True
    # o arquivo de cache guarda só resposta e contagens — nunca o prompt
    with FakeServer(lambda p, path: {"ok": True}) as s:
        c = OpenAICompatClient("m", s.url + "/v1", "CHAVE-SECRETA-123")
        CachingLLM(c, d).complete("PROMPT-SECRETO-XYZ", "u", 50, json_schema=SCHEMA)
    conteudo = "".join(f.read_text(encoding="utf-8") for f in d.glob("*.json"))
    assert "CHAVE-SECRETA" not in conteudo and "PROMPT-SECRETO" not in conteudo
