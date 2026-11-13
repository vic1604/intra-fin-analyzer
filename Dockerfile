# Imagem para rodar o pipeline sem instalar nada na máquina.
#   docker build -t intra-fin-analyzer .
#   docker run --rm -v "$PWD/data/input:/app/data/input" -v "$PWD/outputs:/app/outputs" intra-fin-analyzer          # reference (sem LLM)
#   docker run --rm --env-file .env -v ... intra-fin-analyzer run --mode llm                                         # com LLM
#   docker run --rm --entrypoint python intra-fin-analyzer -m pytest -q                                                           # testes
# Chaves NUNCA entram na imagem: só por --env-file / -e em tempo de execução.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# poppler-utils = pdftotext (ingestão); sem ele o pipeline cai para pdfplumber e perde o layout das tabelas
RUN apt-get update && apt-get install -y --no-install-recommends poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
# anthropic/openai: SDKs dos provedores pagos; Ollama/Gemini usam urllib (nada a instalar)
RUN pip install -r requirements.txt anthropic openai

COPY . .
RUN useradd -m app && mkdir -p /app/outputs /app/data/cache && chown -R app /app
USER app

ENTRYPOINT ["python", "-m", "finanalyzer"]
CMD ["run"]
