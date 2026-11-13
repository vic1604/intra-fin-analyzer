"""Servidor HTTP local que imita Ollama (/api/chat) e APIs compatíveis com OpenAI
(/chat/completions). Registra as requisições e responde com conteúdo canned ou
com um 'modelo perfeito' que devolve o gabarito no formato esperado pelo pipeline."""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class FakeServer:
    def __init__(self, responder=None, fail_first: int = 0, fail_code: int = 429, finish_reason: str | None = None):
        self.requests: list[dict] = []
        self.responder = responder or (lambda payload, path: {"ok": True})
        self.fail_first, self.fail_code = fail_first, fail_code
        self.finish_reason = finish_reason
        outer = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):  # silencioso
                pass

            def do_POST(self):
                n = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(n) or b"{}")
                outer.requests.append({"path": self.path, "payload": payload, "auth": self.headers.get("Authorization")})
                if outer.fail_first > 0:
                    outer.fail_first -= 1
                    self.send_response(outer.fail_code)
                    self.end_headers()
                    self.wfile.write(b'{"error":"limite"}')
                    return
                content = outer.responder(payload, self.path)
                text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
                if self.path.endswith("/api/chat"):
                    body = {"message": {"role": "assistant", "content": text}, "prompt_eval_count": 1234, "eval_count": 56}
                    if outer.finish_reason:
                        body["done_reason"] = outer.finish_reason
                else:
                    body = {"choices": [{"message": {"role": "assistant", "content": text}}], "usage": {"prompt_tokens": 1234, "completion_tokens": 56}}
                    if outer.finish_reason:
                        body["choices"][0]["finish_reason"] = outer.finish_reason
                raw = json.dumps(body).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        self.httpd = HTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *a):
        self.httpd.shutdown()
        self.httpd.server_close()


# ---- "modelo perfeito": converte o gabarito para o formato que o pipeline pede ----
def valor_to_campo(campo: str, periodo: str, v) -> dict:
    return {"campo": campo, "periodo": periodo, "valor": v.valor, "escala": v.escala, "unidade": v.unidade, "rotulo": v.rotulo,
            "pagina": v.evidencia.pagina, "trecho": v.evidencia.trecho}


def extracao_to_llm_json(ext) -> dict:
    campos, nao = [], []
    for nome, m in ext.metricas().items():
        if m.status == "nao_encontrado":
            nao.append({"campo": nome, "motivo": m.motivo_ausencia or "não consta", "termos_buscados": m.termos_verificados})
        for per, v in (("atual", m.atual), ("anterior", m.anterior), ("variacao_pct", m.variacao_reportada_pct), ("variacao_abs", m.variacao_reportada_abs)):
            if v is not None:
                campos.append(valor_to_campo(nome, per, v))
        campos += [valor_to_campo(nome, "alternativa", v) for v in m.alternativas]
        campos += [valor_to_campo(nome, "complementar", v) for v in m.complementares]
    return {
        "empresa": ext.empresa, "periodo_referencia": ext.periodo_referencia, "tipo_documento": ext.tipo_documento,
        "moeda_escala_declarada": ext.moeda_escala_declarada, "campos": campos, "nao_encontrados": nao,
        "anomalias": [{"id": a.id, "severidade": a.severidade, "descricao": a.descricao,
                       "evidencias": [{"pagina": e.pagina, "trecho": e.trecho} for e in a.evidencias]} for a in ext.anomalias_documento],
    }


def quali_to_llm_json(q) -> dict:
    def it(i):
        return {"texto": i.texto, "categoria": i.categoria, "evidencias": [{"pagina": e.pagina, "trecho": e.trecho} for e in i.evidencias]}
    return {
        "fonte_qualitativa": q.fonte_qualitativa, "nota_cobertura": q.nota_cobertura,
        "motivos_resultado": [it(i) for i in q.motivos_resultado],
        "motivo_variacao_receita": it(q.motivo_variacao_receita) if q.motivo_variacao_receita else None,
        "riscos": [it(i) for i in q.riscos], "guidance": [it(i) for i in q.guidance],
        "guidance_numerico_encontrado": q.guidance_numerico_encontrado,
        "eventos_relevantes": [it(i) for i in q.eventos_relevantes], "tom": q.tom, "tom_justificativa": q.tom_justificativa,
        "tom_evidencias": [{"pagina": e.pagina, "trecho": e.trecho} for e in q.tom_evidencias], "confianca_tom": q.confianca_tom,
    }
