.PHONY: setup test lint verify

export MPLBACKEND = Agg

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
