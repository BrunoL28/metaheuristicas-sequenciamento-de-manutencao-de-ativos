"""Parâmetros do protocolo experimental (enunciado, Seção 3) e das suítes.

Toda execução usa ``seed = BASE_SEED + 1000 · índice da instância + run``.
O mesmo par (instância, run) recebe a mesma semente em todos os algoritmos e
vizinhanças.
"""

from __future__ import annotations

from dataclasses import dataclass, field

BASE_SEED = 20261014

INSTANCIAS = ("pequena", "media", "grande")
ORCAMENTO = {"pequena": 50_000, "media": 150_000, "grande": 300_000}
EXECUCOES = {"pequena": 30, "media": 30, "grande": 10}
# Valores de referência da Tabela 1 (ótimo global só na pequena).
REFERENCIA = {"pequena": 1875, "media": 16332, "grande": 60417}

VIZINHANCAS = ("swap", "insertion", "2opt")
# Escolhida no T2 (results/2026-10-15_t2): melhor mediana na média e na grande,
# ótimo em 30/30 na pequena e custo por movimento igual ao das outras.
# Vale para a descida gulosa e o SA no T3, e é o movimento da mutação do AG.
VIZINHANCA = "insertion"

# Algoritmo genético: torneio k = 3, Pc por par, Pm por filho (1 movimento
# da vizinhança escolhida), elitismo de 2. Parada só pelo orçamento.
AG = {
    "pequena": {"N": 50, "Pc": 0.9, "Pm": 0.2, "k": 3, "elite": 2},
    "media": {"N": 100, "Pc": 0.9, "Pm": 0.2, "k": 3, "elite": 2},
    "grande": {"N": 100, "Pc": 0.9, "Pm": 0.2, "k": 3, "elite": 2},
}
# AG memético (experimento extra): cada filho desce até um ótimo local com
# probabilidade P_LS. Escolhido no piloto make memetico-ajuste.
P_LS = 0.1


@dataclass(frozen=True)
class Celula:
    """Uma configuração de algoritmo, rodada em todas as instâncias da suíte."""

    algoritmo: str
    variante: str
    vizinhanca: str
    params: dict = field(default_factory=dict, hash=False)
    # Distingue células do mesmo algoritmo e variante com parâmetros diferentes.
    rotulo: str = ""
    # Opções do MaintenanceProblem além da vizinhança (ex.: cruzamento PMX).
    problema: dict = field(default_factory=dict, hash=False)
    # Orçamento da célula = B · fator_orcamento, menos as avaliações da
    # calibração do SA se descontar_calibracao.
    fator_orcamento: float = 1.0
    descontar_calibracao: bool = False
    # Restringe a célula a algumas instâncias (None = todas as da suíte).
    instancias: tuple[str, ...] | None = None


def semente(instancia: str, run: int, base: int = BASE_SEED) -> int:
    return base + 1000 * INSTANCIAS.index(instancia) + run


def celulas(suite: str) -> list[Celula]:
    if suite == "t2":
        # T2: a mesma busca local (first improvement) em cada vizinhança.
        return [Celula("gd", "first", v) for v in VIZINHANCAS]
    if suite == "sa_piloto":
        # Confere o perfil de aceitação do SA calibrado (configs/sa_*.json).
        return [Celula("sa", "geometrico", VIZINHANCA)]
    if suite == "ag_piloto":
        # Confere a configuração padrão do AG (convergência e diversidade).
        return [Celula("ag", "padrao", VIZINHANCA)]
    if suite == "ag_ajuste":
        # Piloto de parâmetros do AG na média, com sementes fora do protocolo
        # (make ag-ajuste usa outra base de sementes).
        return [
            Celula("ag", "padrao", VIZINHANCA, {"N": N, "Pm": Pm}, f"N{N}-Pm{Pm}")
            for N, Pm in ((100, 0.2), (100, 0.5), (100, 1.0), (50, 0.2), (200, 0.2))
        ]
    if suite == "memetico_ajuste":
        # Piloto da probabilidade de busca local do AG memético (sementes fora
        # do protocolo).
        return [
            Celula("ag", "padrao", VIZINHANCA, {"p_ls": p}, f"memetico-pls{p}")
            for p in (0.02, 0.1, 0.5)
        ]
    if suite in ("t3", "tempos"):
        # T3: os três algoritmos com o protocolo da Seção 3. A descida gulosa
        # roda nas três variantes. "tempos" repete as mesmas células em um
        # processo só, para medir o tempo de parede sem carga paralela.
        return [Celula("gd", v, VIZINHANCA) for v in ("best", "first", "random")] + [
            Celula("sa", "geometrico", VIZINHANCA),
            Celula("ag", "padrao", VIZINHANCA),
        ]
    if suite == "extra":
        # Experimento extra: o cruzamento ajuda? OX (padrão), só mutação,
        # headless chicken, PMX e AG memético.
        return [
            Celula("ag", "padrao", VIZINHANCA, rotulo="ox"),
            Celula("ag", "padrao", VIZINHANCA, {"Pc": 0.0}, "so-mutacao"),
            Celula("ag", "headless", VIZINHANCA),
            Celula("ag", "padrao", VIZINHANCA, rotulo="pmx", problema={"cruzamento": "pmx"}),
            Celula("ag", "padrao", VIZINHANCA, {"p_ls": P_LS}, "memetico"),
        ]
    if suite == "robustez":
        # (1) SA descontando do orçamento as avaliações gastas na calibração;
        # (2) os três algoritmos com o dobro do orçamento na média e na grande.
        maiores = ("media", "grande")
        return [
            Celula(
                "sa", "geometrico", VIZINHANCA, rotulo="B-calibracao", descontar_calibracao=True
            ),
            *(
                Celula("gd", v, VIZINHANCA, rotulo="2B", fator_orcamento=2, instancias=maiores)
                for v in ("best", "first", "random")
            ),
            Celula(
                "sa", "geometrico", VIZINHANCA, rotulo="2B", fator_orcamento=2, instancias=maiores
            ),
            Celula("ag", "padrao", VIZINHANCA, rotulo="2B", fator_orcamento=2, instancias=maiores),
        ]
    raise ValueError(f"suíte desconhecida: {suite!r}")


SUITES = (
    "t2",
    "sa_piloto",
    "ag_piloto",
    "ag_ajuste",
    "memetico_ajuste",
    "t3",
    "tempos",
    "extra",
    "robustez",
)
