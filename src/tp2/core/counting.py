"""Contagem de avaliações num único lugar (enunciado, Seção 3 e Seção 6).

``CountingProblem`` envolve qualquer problema e conta cada avaliação de h:
chamadas a ``h``, cada sucessor produzido por ``sucessores`` e cada
``sucessor_aleatorio``. Quando o orçamento B acaba, a avaliação B + 1 lança
``BudgetExhausted``; os algoritmos não precisam (nem devem) checar o
orçamento por conta própria. O invólucro também guarda a melhor solução vista
e o momento (em avaliações) de cada melhoria, que dá a curva de convergência.
"""

from __future__ import annotations

import math
import random
from collections.abc import Iterator

from tp2.core.interface import Move, Problem, Solution


class BudgetExhausted(Exception):
    """O orçamento de avaliações acabou."""


class CountingProblem:
    def __init__(self, inner: Problem, budget: int):
        if budget <= 0:
            raise ValueError("o orçamento precisa ser positivo")
        self.inner = inner
        self.budget = budget
        self.evals = 0
        self.best_h: float = math.inf
        self.best_s: Solution | None = None
        # (avaliações gastas, melhor h) a cada melhoria do melhor global
        self.improvements: list[tuple[int, int]] = []

    def _contar(self, hv: int, s: Solution | None, mov: Move | None = None) -> int:
        if self.evals >= self.budget:
            raise BudgetExhausted
        self.evals += 1
        if hv < self.best_h:
            self.best_h = hv
            self.best_s = list(s) if mov is None else self.inner.aplicar(s, mov)
            self.improvements.append((self.evals, hv))
        return hv

    @property
    def restantes(self) -> int:
        return self.budget - self.evals

    # --- métodos que avaliam (contam) ---

    def h(self, s: Solution) -> int:
        if self.evals >= self.budget:
            raise BudgetExhausted
        return self._contar(self.inner.h(s), s)

    def sucessores(
        self, s: Solution, h_s: int, rng: random.Random | None = None
    ) -> Iterator[tuple[Move, int]]:
        for mov, hv in self.inner.sucessores(s, h_s, rng):
            self._contar(hv, s, mov)
            yield mov, hv

    def sucessor_aleatorio(self, s: Solution, h_s: int, rng: random.Random) -> tuple[Move, int]:
        if self.evals >= self.budget:
            raise BudgetExhausted
        mov, hv = self.inner.sucessor_aleatorio(s, h_s, rng)
        self._contar(hv, s, mov)
        return mov, hv

    # --- métodos que não avaliam (delegação direta) ---

    def solucao_aleatoria(self, rng: random.Random) -> Solution:
        return self.inner.solucao_aleatoria(rng)

    def aplicar(self, s: Solution, mov: Move) -> Solution:
        return self.inner.aplicar(s, mov)

    def tamanho_vizinhanca(self) -> int:
        return self.inner.tamanho_vizinhanca()

    def cruzamento(
        self, s1: Solution, s2: Solution, rng: random.Random
    ) -> tuple[Solution, Solution]:
        return self.inner.cruzamento(s1, s2, rng)

    def mutacao(self, s: Solution, rng: random.Random) -> Solution:
        return self.inner.mutacao(s, rng)

    def distancia(self, s1: Solution, s2: Solution) -> int:
        return self.inner.distancia(s1, s2)
