.PHONY: setup test lint verify t2 calibrate sa-piloto ag-piloto ag-ajuste ox-demo

export MPLBACKEND = Agg

DATA := $(shell date +%F)
T2_OUT ?= results/$(DATA)_t2
SA_PILOTO_OUT ?= results/$(DATA)_sa_piloto
AG_PILOTO_OUT ?= results/$(DATA)_ag_piloto
AG_AJUSTE_OUT ?= results/$(DATA)_ag_ajuste
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

calibrate:
	@echo "Calibrando T0, Tf, L e alfa do simulated annealing por instância..."
	uv run python -m tp2.experiments.calibrate_sa | tee configs/sa_calibracao.txt

sa-piloto: verify
	@echo "Piloto do SA calibrado: perfil de aceitação de pioras (3 execuções por instância)..."
	uv run python -m tp2.experiments.runner --suite sa_piloto --max-execucoes 3 --out $(SA_PILOTO_OUT) $(OPCOES)
	uv run python -m tp2.experiments.resumo $(SA_PILOTO_OUT) | tee $(SA_PILOTO_OUT)/resumo.txt

ag-piloto: verify
	@echo "Piloto do AG: convergência e diversidade (3 execuções por instância)..."
	uv run python -m tp2.experiments.runner --suite ag_piloto --max-execucoes 3 --out $(AG_PILOTO_OUT) $(OPCOES)
	uv run python -m tp2.experiments.resumo $(AG_PILOTO_OUT) | tee $(AG_PILOTO_OUT)/resumo.txt

ag-ajuste: verify
	@echo "Ajuste do AG na média: N e Pm, 10 execuções com sementes fora do protocolo..."
	uv run python -m tp2.experiments.runner --suite ag_ajuste --instancias media --max-execucoes 10 --base-seed 990000 --out $(AG_AJUSTE_OUT) $(OPCOES)
	uv run python -m tp2.experiments.resumo $(AG_AJUSTE_OUT) | tee $(AG_AJUSTE_OUT)/resumo.txt

ox-demo:
	@echo "Exemplo passo a passo do cruzamento OX (para o relatório)..."
	@mkdir -p results
	uv run python -m tp2.problem.operators --demo --n 8 --seed 15 | tee results/ox_demo.txt
