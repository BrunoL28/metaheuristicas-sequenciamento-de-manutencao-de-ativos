.PHONY: setup test lint verify t2

export MPLBACKEND = Agg

DATA := $(shell date +%F)
T2_OUT ?= results/$(DATA)_t2
# JOBS=n limita os processos; RESUME=1 retoma uma pasta interrompida.
OPCOES = $(if $(JOBS),--jobs $(JOBS)) $(if $(RESUME),--resume)

setup:
	@echo "Criando o ambiente e instalando as dependências com uv..."
	uv sync

test:
	@echo "Executando a suíte de testes..."
	uv run pytest -q

lint:
	@echo "Verificando estilo com ruff..."
	uv run ruff check src tests
	uv run ruff format --check src tests

verify:
	@echo "Validando a função de avaliação (T1)..."
	@mkdir -p results
	uv run python -m tp2.verify | tee results/verify.txt

t2: verify
	@echo "T2: comparando swap, insertion e 2-opt com greedy descent (first improvement)..."
	uv run python -m tp2.experiments.runner --suite t2 --out $(T2_OUT) $(OPCOES)
	uv run python -m tp2.experiments.tempo_movimentos --out $(T2_OUT)/tempo_movimentos.csv
	uv run python -m tp2.experiments.resumo $(T2_OUT) | tee $(T2_OUT)/resumo.txt
	@echo $(notdir $(T2_OUT)) > results/LATEST_T2
