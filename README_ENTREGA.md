# TP2 — Busca local e algoritmo genético no sequenciamento de manutenção de ativos

Trabalho Prático 2 de Fundamentos de Inteligência Artificial (UFMG, DEE, 2026).
Profs. Cristiano Leite de Castro e João Pedro Campos.

| Integrante | Matrícula |
|---|---|
| Arthur Fernandes | 2020026800 |
| Bruno Lima | 2022055785 |

O código compara três metaheurísticas no problema de sequenciamento de manutenção do enunciado: descida gulosa com reinício aleatório (três variantes), *simulated annealing* e algoritmo genético. Todas rodam com o mesmo orçamento de avaliações de *h*. O relatório está em `relatorio/main.pdf`.

## Requisitos

- Python 3.12 ou mais novo.
- [`uv`](https://docs.astral.sh/uv/), que instala as dependências fixadas em `uv.lock` (scipy, matplotlib e, para os testes, pytest, hypothesis e ruff).
- `make`. Sem `make` (por exemplo, no Windows), cada alvo corresponde a um comando `uv run python -m ...`, listado na seção [Sem make](#sem-make).
- Para recompilar o relatório: TeX Live com `latexmk` (pacotes `texlive-latex-extra`, `texlive-lang-portuguese` e `texlive-science`).

## Primeiros passos

```bash
make setup    # cria o ambiente e instala as dependências (uv sync)
make test     # 114 testes automáticos
make verify   # T1: confere h(identidade) = 4366, h* = 1875 e o exemplo da Figura 1
```

O `make verify` grava a saída em `results/verify.txt`, a mesma que aparece na Seção 3 do relatório.

## Como reproduzir cada tabela e figura do relatório

Os resultados brutos ficam em pastas `results/<data>_<suíte>/`, com um CSV por tabela de dados e um `config.json` com os parâmetros, a versão do Python e a máquina. Uma pasta existente nunca é sobrescrita: rodar uma suíte de novo cria uma pasta com a data do dia, e o arquivo `results/LATEST_<SUÍTE>` passa a apontar para ela. O `make analysis` lê as pastas apontadas por esses arquivos e gera todas as tabelas (`relatorio/tabelas/*.tex`) e figuras (`relatorio/figuras/*.pdf`) do relatório. Ele não roda nenhum algoritmo.

Os resultados usados no relatório estão incluídos neste pacote. Para regenerar só as tabelas e as figuras a partir deles, basta `make analysis`.

| No relatório | Arquivo gerado | Dados (comando) | Tabela ou figura (comando) |
|---|---|---|---|
| Seção 3 (saída do T1) | `results/verify.txt` | `make verify` | — |
| Tabela 2 (exemplo do OX) | `relatorio/tabelas/ox_exemplo.tex` | — | `make analysis` (ou `make ox-demo` para a versão em texto) |
| Tabela 3 (T2: vizinhanças) | `relatorio/tabelas/t2_vizinhancas.tex` | `make t2` | `make analysis` |
| Tabela 4 (resultados principais) | `relatorio/tabelas/principal.tex` | `make experiments` e `make tempos` | `make analysis` |
| Tabela 5 (testes entre algoritmos) | `relatorio/tabelas/testes.tex` | `make experiments` | `make analysis` |
| Tabela 6 (ótimos locais na pequena) | `relatorio/tabelas/otimos_locais.tex` | `make experiments` | `make analysis` |
| Tabela 7 (variantes da descida gulosa) | `relatorio/tabelas/gd_variantes.tex` | `make experiments` | `make analysis` |
| Tabela 8 (experimento extra) | `relatorio/tabelas/extra.tex` | `make extra` | `make analysis` |
| Tabela 9 (calibração do SA) | `relatorio/tabelas/sa_calibracao.tex` | `make calibrate` | `make analysis` |
| Tabela 10 (testes do T2) | `relatorio/tabelas/t2_testes.tex` | `make t2` | `make analysis` |
| Tabela 11 (AG memético × buscas locais) | `relatorio/tabelas/extra_vs_buscas.tex` | `make experiments` e `make extra` | `make analysis` |
| Tabela 12 (robustez) | `relatorio/tabelas/robustez.tex` | `make experiments` e `make robustez` | `make analysis` |
| Tabela 13 (parâmetros do AG) | `relatorio/tabelas/ag_parametros.tex` | `make experiments` | `make analysis` |
| Tabela 14 (melhores soluções) | `relatorio/tabelas/melhores.tex` e `relatorio/melhores_solucoes.txt` | `make t2`, `make experiments`, `make extra` e `make robustez` | `make analysis` |
| Figura 1 (boxplots) | `relatorio/figuras/boxplots.pdf` | `make experiments` | `make analysis` |
| Figura 2 (convergência) | `relatorio/figuras/convergencia.pdf` | `make experiments` | `make analysis` |
| Figura 3 (aceitação do SA e diversidade do AG) | `relatorio/figuras/sa_aceitacao.pdf` e `relatorio/figuras/ag_diversidade.pdf` | `make experiments` | `make analysis` |
| Figura 4 (T2: boxplots por vizinhança) | `relatorio/figuras/t2_vizinhancas.pdf` | `make t2` | `make analysis` |
| Figura 5 (experimento extra) | `relatorio/figuras/extra.pdf` | `make extra` | `make analysis` |
| O relatório inteiro | `relatorio/main.pdf` | — | `make report` |

As Tabelas 1 (instâncias) e 15 (comandos) são texto fixo do relatório.

Também estão incluídos os pilotos citados no texto, que não alimentam nenhuma tabela: `make sa-piloto` (perfil de aceitação do SA), `make ag-piloto`, `make ag-ajuste` (escolha de N e P_m) e `make memetico-ajuste` (escolha de p_ls). Os dois ajustes usam sementes fora das do protocolo.

### Ordem para refazer tudo do zero

```bash
make setup test verify
make calibrate        # opcional: os configs/sa_*.json incluídos são exatamente o que ele gera
make t2 experiments extra robustez tempos
make analysis report
```

Numa máquina com 16 núcleos, as suítes levam cerca de 6 minutos no total (cerca de 1h30 de CPU). Por padrão o runner usa todos os núcleos menos um. `make <alvo> JOBS=4` limita o número de processos, e `make <alvo> RESUME=1` retoma uma pasta interrompida.

## Reprodutibilidade

- Cada execução usa `random.Random(semente)`, com `semente = 20261014 + 1000 · índice da instância + execução` (índices 0, 1 e 2 para pequena, média e grande). A semente vai para a coluna `seed` do `runs.csv`, e as execuções de mesmo índice usam a mesma semente em todos os algoritmos.
- Com as mesmas sementes, as execuções dão exatamente os mesmos `best_h` e `best_perm`. Os tempos de parede (`wall_s`) variam com a máquina.
- No fim de cada execução, o runner confere que foram feitas exatamente B avaliações e reavalia a melhor permutação num problema sem contador. Se alguma das duas checagens falhar, a linha sai com `status=error`.
- A Tabela 4 usa os tempos de `make tempos`, que roda 3 execuções por configuração num único processo, sem carga paralela.

## Organização do código

```
src/tp2/
├── core/          interface comum (interface.py), contador de avaliações (counting.py), telemetria (recorder.py)
├── problem/       instâncias, função h, vizinhanças com avaliação incremental, OX e PMX, guloso e solução exata da pequena
├── algorithms/    descida gulosa, simulated annealing e algoritmo genético; não importam nada de problem/
├── experiments/   configuração do protocolo, runner paralelo, calibração do SA, medição de tempo por movimento
├── analysis/      tabelas LaTeX, figuras e testes estatísticos a partir dos CSVs
└── verify.py      T1
tests/             testes automáticos (pytest + hypothesis)
configs/           parâmetros calibrados do SA por instância
INPUTS/            as três instâncias do enunciado
results/           resultados brutos usados no relatório
relatorio/         fonte LaTeX, tabelas e figuras geradas, e o PDF
```

Algumas decisões que o relatório detalha:

- **Algoritmo separado do problema:** os algoritmos só conhecem o protocolo `Problem` de `core/interface.py`. O teste `tests/test_arquitetura.py` falha se algum arquivo de `algorithms/` importar `tp2.problem`.
- **Contagem num único lugar:** `CountingProblem` conta toda avaliação e lança `BudgetExhausted` na avaliação B + 1. Os algoritmos nunca checam o orçamento por conta própria.
- **Avaliação incremental:** está em `MaintenanceProblem._avaliar_movimento`. Os testes de `tests/test_neighborhoods.py` comparam o valor incremental com a avaliação completa.

## Sem make

| Alvo | Comando equivalente |
|---|---|
| `setup` | `uv sync` |
| `test` | `uv run pytest -q` |
| `verify` | `uv run python -m tp2.verify` |
| `t2` | `uv run python -m tp2.experiments.runner --suite t2 --out results/<data>_t2`, depois `uv run python -m tp2.experiments.tempo_movimentos --out results/<data>_t2/tempo_movimentos.csv` |
| `calibrate` | `uv run python -m tp2.experiments.calibrate_sa` |
| `experiments` | `uv run python -m tp2.experiments.runner --suite t3 --out results/<data>_t3` |
| `extra` | `uv run python -m tp2.experiments.runner --suite extra --out results/<data>_extra` |
| `robustez` | `uv run python -m tp2.experiments.runner --suite robustez --out results/<data>_robustez` |
| `tempos` | `uv run python -m tp2.experiments.runner --suite tempos --max-execucoes 3 --jobs 1 --out results/<data>_tempos` |
| `analysis` | `uv run python -m tp2.analysis` |
| `report` | `cd relatorio && latexmk -pdf main.tex` |

Sem `make`, depois de rodar uma suíte é preciso atualizar à mão o arquivo `results/LATEST_<SUÍTE>` com o nome da pasta nova antes do `analysis`. Os alvos do `make` fazem isso sozinhos. Para ver um resumo de qualquer pasta de resultados: `uv run python -m tp2.experiments.resumo results/<pasta>`.
