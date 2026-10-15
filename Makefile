.PHONY: setup test lint verify t2 calibrate sa-piloto ag-piloto ag-ajuste ox-demo memetico-ajuste experiments extra robustez tempos analysis tables figures report overleaf-zip

export MPLBACKEND = Agg

DATA := $(shell date +%F)
T2_OUT ?= results/$(DATA)_t2
SA_PILOTO_OUT ?= results/$(DATA)_sa_piloto
AG_PILOTO_OUT ?= results/$(DATA)_ag_piloto
AG_AJUSTE_OUT ?= results/$(DATA)_ag_ajuste
MEMETICO_AJUSTE_OUT ?= results/$(DATA)_memetico_ajuste
T3_OUT ?= results/$(DATA)_t3
EXTRA_OUT ?= results/$(DATA)_extra
ROBUSTEZ_OUT ?= results/$(DATA)_robustez
TEMPOS_OUT ?= results/$(DATA)_tempos
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

memetico-ajuste: verify
	@echo "Ajuste do AG memético: probabilidade de busca local, sementes fora do protocolo..."
	uv run python -m tp2.experiments.runner --suite memetico_ajuste --instancias media grande --max-execucoes 10 --base-seed 990000 --out $(MEMETICO_AJUSTE_OUT) $(OPCOES)
	uv run python -m tp2.experiments.resumo $(MEMETICO_AJUSTE_OUT) | tee $(MEMETICO_AJUSTE_OUT)/resumo.txt

experiments: verify
	@echo "T3: descida gulosa (3 variantes), SA e AG nas três instâncias (30/30/10 execuções)..."
	uv run python -m tp2.experiments.runner --suite t3 --out $(T3_OUT) $(OPCOES)
	uv run python -m tp2.experiments.resumo $(T3_OUT) | tee $(T3_OUT)/resumo.txt
	@echo $(notdir $(T3_OUT)) > results/LATEST_T3

extra: verify
	@echo "Experimento extra: AG com OX, só mutação, headless chicken, PMX e memético..."
	uv run python -m tp2.experiments.runner --suite extra --out $(EXTRA_OUT) $(OPCOES)
	uv run python -m tp2.experiments.resumo $(EXTRA_OUT) | tee $(EXTRA_OUT)/resumo.txt
	@echo $(notdir $(EXTRA_OUT)) > results/LATEST_EXTRA

robustez: verify
	@echo "Robustez: SA sem as avaliações da calibração e os três algoritmos com 2B..."
	uv run python -m tp2.experiments.runner --suite robustez --out $(ROBUSTEZ_OUT) $(OPCOES)
	uv run python -m tp2.experiments.resumo $(ROBUSTEZ_OUT) | tee $(ROBUSTEZ_OUT)/resumo.txt
	@echo $(notdir $(ROBUSTEZ_OUT)) > results/LATEST_ROBUSTEZ

tempos: verify
	@echo "Tempos sem carga paralela: células do T3, 3 execuções por instância, 1 processo..."
	uv run python -m tp2.experiments.runner --suite tempos --max-execucoes 3 --jobs 1 --out $(TEMPOS_OUT)
	uv run python -m tp2.experiments.resumo $(TEMPOS_OUT) | tee $(TEMPOS_OUT)/resumo.txt
	@echo $(notdir $(TEMPOS_OUT)) > results/LATEST_TEMPOS

analysis:
	@echo "Gerando tabelas e figuras do relatório a partir de results/LATEST_*..."
	uv run python -m tp2.analysis

tables figures: analysis

report:
	@echo "Compilando o relatório (pdfLaTeX)..."
	cd relatorio && latexmk -pdf main.tex

overleaf-zip:
	@echo "Empacotando relatorio/ para upload no Overleaf (só arquivos versionados)..."
	@mkdir -p tmp
	git archive --format=zip -o tmp/relatorio-overleaf.zip HEAD:relatorio
	@echo "tmp/relatorio-overleaf.zip"

ox-demo:
	@echo "Exemplo passo a passo do cruzamento OX (para o relatório)..."
	@mkdir -p results
	uv run python -m tp2.problem.operators --demo --n 8 --seed 15 | tee results/ox_demo.txt
