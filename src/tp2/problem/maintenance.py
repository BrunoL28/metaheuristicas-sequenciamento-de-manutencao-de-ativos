"""Problema de sequenciamento de manutenção: função de avaliação h (Seção 1.2)."""

from __future__ import annotations

from collections.abc import Sequence

from tp2.problem.instance import Instance


class MaintenanceProblem:
    """Sequenciamento de manutenção com atraso ponderado total.

    Uma solução é uma permutação dos ativos 1..n (a ordem de visita). A
    interface completa usada pelos algoritmos (sucessores, cruzamento, ...)
    é adicionada junto com as vizinhanças.
    """

    def __init__(self, instancia: Instance):
        self.instancia = instancia
        self.n = instancia.n
        # Listas simples são mais rápidas que tuplas aninhadas no laço de h.
        self._T = [list(linha) for linha in instancia.T]
        self._P = list(instancia.p)
        self._D = list(instancia.d)
        self._W = list(instancia.w)

    def h(self, s: Sequence[int]) -> int:
        """Equações (2) e (3): soma de w_j · max(0, C_j − d_j) seguindo a ordem s."""
        T, P, D, W = self._T, self._P, self._D, self._W
        anterior = 0
        C = 0
        total = 0
        for j in s:
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
