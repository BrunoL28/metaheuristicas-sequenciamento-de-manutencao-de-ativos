"""Problema de sequenciamento de manutenção (Seções 1.2 e 2).

Implementa a interface ``tp2.core.interface.Problem``. Uma solução é uma
permutação dos ativos 1..n (a ordem de visita).
"""

from __future__ import annotations

import random
from collections.abc import Iterator, Sequence

from tp2.problem.instance import Instance
from tp2.problem.neighborhoods import VIZINHANCAS, Mov
from tp2.problem.operators import CRUZAMENTOS


class MaintenanceProblem:
    """Sequenciamento de manutenção com atraso ponderado total.

    ``vizinhanca`` escolhe o operador usado por ``sucessores`` e
    ``sucessor_aleatorio`` (``swap``, ``insertion`` ou ``2opt``). Com
    ``incremental=True`` os sucessores são avaliados a partir do prefixo
    inalterado da solução corrente; com ``False``, do zero (só para medir o
    ganho de tempo; os valores são idênticos). ``cruzamento`` escolhe o
    operador do AG (``ox`` ou ``pmx``).
    """

    def __init__(
        self,
        instancia: Instance,
        vizinhanca: str = "swap",
        incremental: bool = True,
        cruzamento: str = "ox",
    ):
        self.instancia = instancia
        self.n = instancia.n
        # Listas simples são mais rápidas que tuplas aninhadas no laço de h.
        self._T = [list(linha) for linha in instancia.T]
        self._P = list(instancia.p)
        self._D = list(instancia.d)
        self._W = list(instancia.w)

        self._cruzar = CRUZAMENTOS[cruzamento]
        self.viz = VIZINHANCAS[vizinhanca]
        self.incremental = incremental
        self._movimentos = self.viz.movimentos(self.n)
        self._ordem_aleatoria: list[Mov] | None = None

        # Cache de prefixos da última solução corrente vista.
        self._cache_s: list[int] | None = None
        self._C_pre: list[int] = []
        self._H_pre: list[int] = []

    # --- avaliação ---

    def h(self, s: Sequence[int]) -> int:
        """Equações (2) e (3): soma de w_j · max(0, C_j − d_j) seguindo a ordem s."""
        return self._avaliar_de(s, 0, 0, 0)

    def _avaliar_de(self, trecho: Sequence[int], anterior: int, C: int, total: int) -> int:
        """Continua a avaliação a partir de (último ativo, C, custo acumulado)."""
        T, P, D, W = self._T, self._P, self._D, self._W
        for j in trecho:
            C += T[anterior][j] + P[j]
            anterior = j
            atraso = C - D[j]
            if atraso > 0:
                total += W[j] * atraso
        return total

    def conclusoes(self, s: Sequence[int]) -> list[int]:
        """Instantes de conclusão C_{π_k} na ordem de visita (Equação 2)."""
        T, P = self._T, self._P
        anterior = 0
        C = 0
        saida = []
        for j in s:
            C += T[anterior][j] + P[j]
            anterior = j
            saida.append(C)
        return saida

    def _preparar_cache(self, s: Sequence[int], h_s: int) -> None:
        """Monta C e h acumulados por posição para a solução corrente s.

        É contabilidade interna, não a avaliação de uma solução candidata,
        por isso não conta no orçamento. Confere que h_s é mesmo o custo de s.
        """
        if self._cache_s is not None and self._cache_s == s:
            return
        T, P, D, W = self._T, self._P, self._D, self._W
        C_pre, H_pre = [], []
        anterior = C = total = 0
        for j in s:
            C += T[anterior][j] + P[j]
            anterior = j
            atraso = C - D[j]
            if atraso > 0:
                total += W[j] * atraso
            C_pre.append(C)
            H_pre.append(total)
        if total != h_s:
            raise ValueError(f"h_s = {h_s} não é o custo da solução corrente ({total})")
        self._cache_s = list(s)
        self._C_pre, self._H_pre = C_pre, H_pre

    def _avaliar_movimento(self, s: list[int], mov: Mov) -> int:
        if not self.incremental:
            return self.h(self.viz.aplicar(s, mov))
        a, suf = self.viz.sufixo(s, mov)
        if a == 0:
            return self._avaliar_de(suf, 0, 0, 0)
        return self._avaliar_de(suf, s[a - 1], self._C_pre[a - 1], self._H_pre[a - 1])

    # --- interface Problem ---

    def solucao_aleatoria(self, rng: random.Random) -> list[int]:
        return rng.sample(range(1, self.n + 1), self.n)

    def sucessores(
        self, s: list[int], h_s: int, rng: random.Random | None = None
    ) -> Iterator[tuple[Mov, int]]:
        """Todos os sucessores de s, como pares (movimento, h).

        Sem ``rng``, na ordem canônica. Com ``rng``, a varredura começa num
        ponto sorteado de uma ordem embaralhada uma única vez (evita favorecer
        sempre as primeiras posições sem reembaralhar a lista a cada passo).
        """
        if self.incremental:
            self._preparar_cache(s, h_s)
        if rng is None:
            ordem = self._movimentos
            inicio = 0
        else:
            if self._ordem_aleatoria is None:
                self._ordem_aleatoria = list(self._movimentos)
                rng.shuffle(self._ordem_aleatoria)
            ordem = self._ordem_aleatoria
            inicio = rng.randrange(len(ordem))
        for k in range(len(ordem)):
            mov = ordem[(inicio + k) % len(ordem)]
            yield mov, self._avaliar_movimento(s, mov)

    def sucessor_aleatorio(self, s: list[int], h_s: int, rng: random.Random) -> tuple[Mov, int]:
        if self.incremental:
            self._preparar_cache(s, h_s)
        mov = self._movimentos[rng.randrange(len(self._movimentos))]
        return mov, self._avaliar_movimento(s, mov)

    def aplicar(self, s: Sequence[int], mov: Mov) -> list[int]:
        return self.viz.aplicar(s, mov)

    def tamanho_vizinhanca(self) -> int:
        return self.viz.tamanho(self.n)

    def cruzamento(
        self, s1: Sequence[int], s2: Sequence[int], rng: random.Random
    ) -> tuple[list[int], list[int]]:
        """OX (convenção do slide) ou PMX, conforme o construtor. Não avalia."""
        return self._cruzar(s1, s2, rng)

    def mutacao(self, s: Sequence[int], rng: random.Random) -> list[int]:
        """Aplica um movimento aleatório da vizinhança configurada. Não avalia."""
        return self.viz.aplicar(s, self._movimentos[rng.randrange(len(self._movimentos))])

    def distancia(self, s1: Sequence[int], s2: Sequence[int]) -> int:
        """Número de posições com ativos diferentes (Hamming por posição)."""
        return sum(1 for a, b in zip(s1, s2, strict=True) if a != b)
