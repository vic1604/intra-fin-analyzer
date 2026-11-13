.PHONY: verify run test eval secrets docker ask llm-full
run:      ; python -m finanalyzer run
test:     ; python -m pytest -q
eval:     ; python -m finanalyzer eval --mode baseline
verify:   ; python scripts/verify_numbers.py
llm-full: ; bash scripts/run_llm_full.sh
ask:      ; python -m finanalyzer ask "Qual empresa tem a maior receita líquida?"
secrets:  ; python scripts/check_secrets.py
docker:   ; docker build -t intra-fin-analyzer . && docker run --rm -v $$PWD/data/input:/app/data/input -v $$PWD/outputs:/app/outputs intra-fin-analyzer run
