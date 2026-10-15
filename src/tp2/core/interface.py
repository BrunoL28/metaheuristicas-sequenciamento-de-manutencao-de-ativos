"""Interface comum entre os algoritmos e o problema (enunciado, Seção 2.1).

Os algoritmos só conhecem este protocolo. Em relação à sugestão mínima do
enunciado há três extensões, todas para permitir a avaliação incremental sem
que o algoritmo saiba o que é um movimento:

- ``sucessores`` e ``sucessor_aleatorio`` devolvem pares (movimento, h do
  sucessor), em vez da permutação pronta. O movimento é opaco para o
  algoritmo; ele só o devolve a ``aplicar`` quando decide aceitar.
- Os dois recebem ``h_s``, o custo já conhecido da solução corrente, para o
  problema montar o cache de prefixos sem uma avaliação extra.
- ``aplicar(s, mov)`` constrói o sucessor aceito (não é uma avaliação).
"""

from __future__ import annotations

import random
from collections.abc import Hashable, Iterator
from typing import Protocol

Solution = list[int]
Move = Hashable


class Problem(Protocol):
    def solucao_aleatoria(self, rng: random.Random) -> Solution:
        """Gera um ponto de partida (uma permutação aleatória)."""
        ...

    def h(self, s: Solution) -> int:
        """Função de avaliação, sempre de minimização. Conta 1 avaliação."""
        ...

    def sucessores(
        self, s: Solution, h_s: int, rng: random.Random | None = None
    ) -> Iterator[tuple[Move, int]]:
        """Itera sobre todos os sucessores de s. Cada item conta 1 avaliação.

        Com ``rng``, a ordem de varredura é aleatória (usada no first improvement).
        """
        ...

    def sucessor_aleatorio(self, s: Solution, h_s: int, rng: random.Random) -> tuple[Move, int]:
        """Sorteia um único sucessor de s. Conta 1 avaliação."""
        ...

    def aplicar(self, s: Solution, mov: Move) -> Solution:
        """Devolve o sucessor de s gerado por ``mov`` (não avalia)."""
        ...

    def tamanho_vizinhanca(self) -> int:
        """Número de sucessores distintos de qualquer solução."""
        ...

    def cruzamento(
        self, s1: Solution, s2: Solution, rng: random.Random
    ) -> tuple[Solution, Solution]:
        """Operador de recombinação (não avalia)."""
        ...

    def mutacao(self, s: Solution, rng: random.Random) -> Solution:
        """Operador de mutação (não avalia)."""
        ...

    def distancia(self, s1: Solution, s2: Solution) -> int:
        """Distância entre soluções, para medir a diversidade (não avalia)."""
        ...
