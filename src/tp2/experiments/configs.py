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


@dataclass(frozen=True)
class Celula:
    """Uma configuração de algoritmo, rodada em todas as instâncias da suíte."""

    algoritmo: str
    variante: str
    vizinhanca: str
    params: dict = field(default_factory=dict, hash=False)


def semente(instancia: str, run: int, base: int = BASE_SEED) -> int:
    return base + 1000 * INSTANCIAS.index(instancia) + run


def celulas(suite: str) -> list[Celula]:
    if suite == "t2":
        # T2: a mesma busca local (first improvement) em cada vizinhança.
        return [Celula("gd", "first", v) for v in VIZINHANCAS]
    raise ValueError(f"suíte desconhecida: {suite!r}")


SUITES = ("t2",)
