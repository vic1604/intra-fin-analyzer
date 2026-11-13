# Guia passo a passo — do zero até a entrega

Cada passo diz **o que abrir, quando e por quê**. Tempo total: ~1h30 (sem LLM) + ~30–60 min para testar um LLM real (local grátis ou chave gratuita).

## Parte A — Preparar o ambiente (15 min)

| # | Abra | Faça | Por quê |
|---|---|---|---|
| A1 | **Terminal** | `python3 --version` (precisa 3.11+) e `pdftotext -v` | O pipeline usa `pdftotext` (pacote poppler-utils) para ler PDF preservando colunas de números. Se faltar: `sudo apt install poppler-utils` ou `brew install poppler`. |
| A2 | **Terminal**, pasta do projeto | `unzip intra-fin-analyzer.zip && cd intra-fin-analyzer` | Seu repositório pronto. |
| A3 | **Terminal** | `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` | Ambiente isolado: não suja o Python do sistema. |
| A4 | **Gerenciador de arquivos** | Copie os 3 PDFs para `data/input/` com os nomes `light.pdf`, `millet.pdf`, `brasal.pdf` | O pipeline descobre os documentos pelo nome do arquivo. |

## Parte B — Rodar e ver funcionando (15 min)

| # | Abra | Faça | O que você deve ver / por quê |
|---|---|---|---|
| B1 | **Terminal** | `python -m pytest -q` | `106 passed`. Prova que o código funciona antes de mexer em qualquer coisa. |
| B2 | **Terminal** | `python -m finanalyzer run` | `3 documentos · 150 evidências, 0 falhas · 19 alertas`. Gera `outputs/` (inclui `ml_tradicional.json` e `logs/run.jsonl`). |
| B3 | **VS Code** (ou editor) → `outputs/relatorio.html` no navegador | Leia as seções 1 a 5 | É o entregável principal. Familiarize-se: você vai apresentá-lo. |
| B4 | **Terminal** | `python -m finanalyzer eval --mode baseline` | Recall 64,3%, precisão 94,7%, 0 alucinação. É o seu "quanto um método simples erra" para comparar com o LLM. |
| B5a | **Terminal** | `python scripts/verify_numbers.py` | `71 valores conferidos direto no PDF; 0 falhas` e 9 derivados `✓`. Prova independente do pipeline. |
| B5 | **Terminal** | `python scripts/check_secrets.py` | `OK: nenhum segredo`. Requisito explícito do teste. |
| B6 | **Terminal** | `python -m finanalyzer ask "Qual empresa tem a maior receita líquida?"` e depois `ask "Quais são os riscos de crédito mencionados?"` e `ask "preço do bitcoin"` | Pergunta livre **sem LLM**: as duas primeiras devolvem linhas dos documentos com `[doc p.N]` e citações `✓` verificadas; a terceira responde **"Sem evidência suficiente"** — é a prova de que ele não inventa. |
| B7 | **Editor** → `outputs/logs/run.jsonl` | Veja 1 linha JSON por etapa (`ingestao`, `extracao`, `validacao`, `ml_tradicional`, `relatorio`) | É o seu log/traço estruturado (diferencial do enunciado). Não há texto de PDF nem chave ali. |
| B8 | **Navegador** → `outputs/relatorio.html`, role até **Anexo B** | Tabela "ML tradicional vs regras/LLM" | Comparação com abordagem sem LLM (diferencial). Entenda a leitura: o ML acha linhas de movimento grande; as regras/LLM explicam — são complementares. |

## Parte C — Conferir os números nos PDFs (30 min) — **não pule**

O gabarito (`data/reference/`) foi montado com ajuda de IA. Cada trecho é verificado por código, mas **você precisa ser capaz de dizer "conferi"**.

1. Abra `outputs/extracao/light.json` no editor e o `light.pdf` no leitor de PDF.
2. Confira **pelo menos estes 8 valores** (página = posição física, 1 = capa; no leitor, a página pode diferir do número impresso no rodapé):
   - Light: receita líquida 13.253.286 e 14.897.920 (p.20); lucro líquido −5.672.203 (p.20); EBITDA "1.180" (p.9); alavancagem 3,32x (p.10).
   - Millet: receita 462.127 vs 199.259 (p.7); EBIT 25.298 (p.7) + D&A 18.248 (p.10) = EBITDA derivado 43,5 mi.
   - Brasal: receita 1,325 bi (p.8); caixa 96.453 e aplicações 78.569 (p.6) e empréstimos 3.417 (p.48) → dívida líquida derivada −171,6 mi.
3. Se algum não bater, **corrija o JSON em `data/reference/extracao/`** (ou o `scripts/build_reference.py`) e rode `python -m finanalyzer run` — o grounding avisa se o trecho não existir na página.

## Parte D — Testar com um LLM de verdade, **sem chave paga** (30–60 min)

O caminho LLM foi testado só com LLM falso e servidor HTTP falso. Rodar com um modelo real é o que o avaliador mais vai querer ver — e você não precisa de cartão. Escolha **uma** opção:

### Opção D1 — Ollama (modelo local, grátis, nada sai do seu computador)
| # | Faça | Por quê |
|---|---|---|
| D1.1 | No **terminal WSL**: `curl -fsSL https://ollama.com/install.sh \| sh` | Instala o servidor local de modelos. |
| D1.2 | `ollama pull qwen2.5:7b-instruct` (~5 GB; se o nome não existir, veja ollama.com/library; alternativa: `llama3.1:8b`) | Baixa o modelo. Leva alguns minutos. |
| D1.3 | `cp .env.example .env` e edite: `LLM_PROVIDER=ollama`, `LLM_MODEL=qwen2.5:7b-instruct`, `OLLAMA_NUM_CTX=32768` | Diz ao pipeline para usar o modelo local. O contexto grande é necessário: cada documento envia ~13–17 mil tokens. |
| D1.4 | `python -m finanalyzer smoke-llm` | 1 chamada mínima. Se falhar, o erro diz o que ajustar (servidor fora do ar, modelo não baixado…). **Rode isto sozinho primeiro.** |
| D1.5 | `bash scripts/run_llm_full.sh` | Roda `smoke-llm` → `run --mode llm` → `eval --mode llm` e grava tudo em **`outputs_llm/`** (não sobrescreve o `outputs/` do modo reference). Pode levar de minutos a mais de uma hora sem GPU: deixe rodando. |
| D1.6 | Abra `outputs_llm/avaliacao_llm.json`, `outputs_llm/run_manifest.json` e `outputs_llm/relatorio.html` | Recall/precisão/alucinação **reais**, tokens e segundos reais, e o relatório gerado pelo modelo. |

Se a máquina travar/ficar sem memória: feche outros programas; no `.env` use `MAX_PAGES=10`; no Windows crie `C:\Users\SEU_USUARIO\.wslconfig` com `[wsl2]` e `memory=12GB` (ajuste ao seu PC) e rode `wsl --shutdown`.

### Opção D2 — Google Gemini (chave gratuita, sem cartão)
| # | Faça | Por quê |
|---|---|---|
| D2.1 | Navegador: https://aistudio.google.com/apikey → **Create API key** | Chave gratuita. **Não cole a chave no chat, no código nem no Git.** |
| D2.2 | No `.env`: `LLM_PROVIDER=gemini`, `GEMINI_API_KEY=<sua chave>`, `LLM_MODEL=<modelo gratuito que o AI Studio listar>` | Os nomes de modelo mudam; use o que aparecer lá. |
| D2.3 | `python -m finanalyzer smoke-llm` e depois `bash scripts/run_llm_full.sh` | Igual à opção 1. Se vier erro 429 é limite da camada gratuita: o cliente tenta de novo sozinho; se persistir, espere um minuto. |

Atenção: na camada gratuita o Google pode usar o conteúdo enviado para melhorar produtos. Os PDFs são demonstrações de companhias abertas, mas **não use esse caminho com documentos confidenciais**.

### Depois de rodar (obrigatório se você rodou)
1. Abra `outputs_llm/avaliacao_llm.json` e anote recall, precisão, alucinação e o custo/tempo do `run_manifest.json`.
2. *(feito)* A coluna "LLM real" da tabela "Avaliação de qualidade" do README já traz os números medidos com `gemini-3.5-flash-lite` em 13/11/2026; se trocar de modelo, atualize-a.
3. **Não esconda um resultado ruim.** Um modelo pequeno pode errar mais que o baseline; o que importa é o grounding ter mantido **alucinação = 0** e você explicar por quê (é um ótimo tópico para a apresentação).
4. Se você **não** rodou: deixe como está — o README já diz com franqueza que não foi executado.

## Parte E — Docker e publicar o repositório (25 min)

**Docker (opcional, mas é diferencial):**
1. Windows: instale o Docker Desktop e ligue *Settings → Resources → WSL integration* para a sua distro Ubuntu. Teste: `docker --version`.
2. `docker build -t intra-fin-analyzer .` (a primeira vez baixa a imagem; alguns minutos).
3. `docker run --rm -v "$PWD/data/input:/app/data/input" -v "$PWD/outputs:/app/outputs" intra-fin-analyzer` → deve imprimir o mesmo resumo do B2.
4. `docker run --rm --entrypoint python intra-fin-analyzer -m pytest -q` → `106 passed` (os testes que dependem dos PDFs usam os de `data/input` copiados na imagem).
5. Se funcionou, troque "não construído" por "construído e executado em <data>" no README (seções de status e Limitações). Se falhou, **me envie o erro** antes de apresentar.

**Git/GitHub:**
1. `git init && git add . && git status` → confirme que **não aparece** `.env` nem `data/cache/`.
2. `python scripts/check_secrets.py` de novo → `git commit -m "Entrega teste prático Intra"`.
3. `gh auth login` (siga o assistente no navegador) → `gh repo create intra-fin-analyzer --private --source=. --push`.
4. Dê acesso ao avaliador: no GitHub, *Settings → Collaborators → Add people* (ou `gh api -X PUT repos/<você>/intra-fin-analyzer/collaborators/<usuario-do-avaliador>`).
5. Os PDFs: se o enunciado permitir, mantenha em `data/input/`; se preferir não versionar, adicione `data/input/*.pdf` ao `.gitignore` e o README já explica onde colocá-los (mas então os testes que dependem deles serão pulados no clone do avaliador — por isso eu recomendo versioná-los se permitido).

## Parte F — Preparar a apresentação (20 min)

Abra `docs/3_ROTEIRO_APRESENTACAO.md`. Deixe **abertas, nesta ordem**, antes de começar: (1) README no GitHub/editor, (2) `outputs/relatorio.html` (com o Anexo B à mão), (3) `outputs/extracao/light.json`, (4) `light.pdf` na página 9, (5) terminal na pasta do projeto (já com `ask` testado), (6) `outputs/avaliacao_baseline.json` (e `avaliacao_llm.json` se você rodou a Parte D), (7) `outputs/logs/run.jsonl`.

## Se algo falhar
| Sintoma | Causa provável | Solução |
|---|---|---|
| `pdftotext: command not found` | poppler ausente | Instalar poppler-utils |
| `Nenhum PDF em data/input` | nomes/pasta errados | `light.pdf`, `millet.pdf`, `brasal.pdf` em `data/input/` |
| Teste pula ("PDFs não estão em data/input") | idem | idem |
| `smoke-llm`: "connection refused" (Ollama) | servidor não está rodando | `ollama serve` em outro terminal e tente de novo |
| `smoke-llm`: "model not found" (Ollama) | modelo não foi baixado / nome diferente | `ollama list` e use o nome exato no `LLM_MODEL` |
| Erro "prompt preencheu todo o contexto" | `OLLAMA_NUM_CTX` pequeno para o prompt | aumente `OLLAMA_NUM_CTX` ou reduza `MAX_PAGES` no `.env` |
| Gemini 429 | cota gratuita daquele modelo esgotada/zerada | troque `LLM_MODEL` por outro da lista (`curl .../v1beta/openai/models`); espere 1–2 min; reduza `MAX_PAGES` |
| Gemini 503 "high demand" | modelo novo sobrecarregado | espere alguns minutos ou troque de modelo; o cliente tenta 7 vezes por chamada (10 no `run_llm_full.sh`, via `LLM_RETRIES`) e o script ainda repete sozinho o passo inteiro até 8 vezes, pausando 90 s entre elas |
| Gemini 404 "no longer available to new users" | modelo antigo | use um nome da lista de modelos da sua conta |
| Execução caiu no meio (503/429) | serviço gratuito instável | o script repete sozinho só falhas transitórias (429/503/rede); se desistir, rode `bash scripts/run_llm_full.sh` de novo: o cache em `data/cache/llm` retoma de onde parou |
| `smoke-llm` fica parado por minutos | `LLM_TIMEOUT` alto (era para modelo local) | no `.env`: `LLM_TIMEOUT=120` para APIs na nuvem |
| "resposta cortada pelo limite de saída" | `LLM_MAX_TOKENS` baixo (modelos que pensam gastam parte dele) | no `.env`: `LLM_MAX_TOKENS=16384` |
| Mudou o `.env` mas o modelo continua o antigo | variável exportada na sessão do terminal | feche o terminal e abra outro (`env \| grep -c '^LLM_'` deve dar 0) |
| `ask` devolve "Sem evidência suficiente" | a pergunta usa termos que não estão nos documentos | é o comportamento correto; reformule com termos do documento ou use `--mode llm` |
| `ModuleNotFoundError: finanalyzer` | executou fora da raiz | `cd` para a raiz do projeto |
| `grounding` acusa falha após você editar o gabarito | trecho não está literalmente na página | copie a linha exata do PDF |
