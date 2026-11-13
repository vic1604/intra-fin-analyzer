#!/usr/bin/env bash
# Sequência completa com LLM REAL, sem sobrescrever a execução em modo reference:
#   1) smoke-llm   -> confirma servidor/modelo/credencial com 1 chamada mínima
#   2) run --mode llm  -> pipeline completo (extração + qualitativo por LLM, com grounding). É a execução
#                         que mede tokens/tempo/custo de verdade (chamadas novas ao modelo).
#   3) eval --mode llm -> mede recall/precisão/alucinação contra o gabarito. Reaproveita do cache as
#                         respostas idênticas do passo 2 (não gasta cota de novo).
# Camadas gratuitas oscilam (503 "alta demanda", 429 cota). Por isso os passos 2 e 3 são REPETIDOS
# automaticamente (até TENTATIVAS vezes, com pausa de PAUSA s): cada resposta já recebida fica em
# data/cache/llm, então cada nova tentativa continua de onde a anterior caiu — não refaz nem gasta cota
# do que já deu certo. Ajuste: TENTATIVAS=10 PAUSA=120 bash scripts/run_llm_full.sh
# Tudo vai para outputs_llm/ (OUTPUT_DIR). Configure antes o .env (LLM_PROVIDER, LLM_MODEL, ...).
set -uo pipefail
cd "$(dirname "$0")/.."
export OUTPUT_DIR="${OUTPUT_DIR:-outputs_llm}"
export LLM_RETRIES="${LLM_RETRIES:-10}"   # ~4 min de espera por chamada antes de desistir da tentativa
TENTATIVAS="${TENTATIVAS:-8}"
PAUSA="${PAUSA:-90}"

tentar() {  # tentar "<descrição>" comando...
  local desc="$1"; shift
  local n=1
  until "$@"; do
    local rc=$?
    if [ "$rc" -ne 75 ]; then   # 75 = falha transitória do provedor (429/503/rede); outro código = erro real, repetir não adianta
      echo "!! $desc falhou com erro NÃO transitório (código $rc). Não vou repetir: me envie a mensagem acima." >&2
      exit 1
    fi
    if [ "$n" -ge "$TENTATIVAS" ]; then
      echo "!! $desc falhou $n vezes. Espere um pouco (ou troque LLM_MODEL no .env) e rode de novo: o que já deu certo está em cache." >&2
      exit 1
    fi
    echo "!! $desc falhou (tentativa $n/$TENTATIVAS). Aguardando ${PAUSA}s e continuando de onde parou (cache)..." >&2
    sleep "$PAUSA"; n=$((n + 1))
  done
}

echo "== [1/3] smoke-llm"; tentar "smoke-llm" python -m finanalyzer smoke-llm
echo "== [2/3] run --mode llm (pode demorar)"; tentar "run --mode llm" python -m finanalyzer run --mode llm
echo "== [3/3] eval --mode llm (reaproveita o cache)"; tentar "eval --mode llm" python -m finanalyzer eval --mode llm
echo; echo "Pronto. Resultados em $OUTPUT_DIR/ : avaliacao_llm.json, run_manifest.json (tokens/tempo), relatorio.html, logs/run.jsonl"
