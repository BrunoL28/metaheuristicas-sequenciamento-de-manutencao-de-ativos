"""Operadores de vizinhança sobre permutações (enunciado, Seção 2.2, Figura 3).

Posições são 0-based. Cada operador sabe:

- listar todos os seus movimentos distintos para um dado n;
- aplicar um movimento (devolvendo uma nova lista);
- produzir só o sufixo alterado da permutação, a partir da primeira posição
  tocada ``a``. A avaliação incremental parte do prefixo já conhecido
  (posições 0..a−1 não mudam) e percorre apenas esse sufixo.

Tamanhos das vizinhanças (sucessores distintos):

- swap:      n(n−1)/2  — troca as posições i < j;
- insertion: (n−1)²    — retira o elemento da posição i e o reinsere na
  posição j. Mover i para i+1 dá a mesma permutação que mover i+1 para i,
  então os n(n−1) pares (i, j) têm n−1 repetições; excluímos j = i−1;
- 2-opt:     n(n−1)/2  — inverte o trecho s[i..j], i < j.

Swap e 2-opt coincidem quando j = i + 1 (as duas trocam vizinhos): as
vizinhanças se sobrepõem em n−1 elementos, mas não são equivalentes.
"""

from __future__ import annotations

from collections.abc import Sequence

Mov = tuple[int, int]


class Vizinhanca:
    nome: str

    def tamanho(self, n: int) -> int:
        raise NotImplementedError

    def movimentos(self, n: int) -> list[Mov]:
        raise NotImplementedError

    def aplicar(self, s: Sequence[int], mov: Mov) -> list[int]:
        raise NotImplementedError

    def sufixo(self, s: Sequence[int], mov: Mov) -> tuple[int, list[int]]:
        """(a, s'[a:]): primeira posição alterada e o novo sufixo a partir dela."""
        raise NotImplementedError


class Swap(Vizinhanca):
    nome = "swap"

    def tamanho(self, n: int) -> int:
        return n * (n - 1) // 2

    def movimentos(self, n: int) -> list[Mov]:
        return [(i, j) for i in range(n) for j in range(i + 1, n)]

    def aplicar(self, s, mov):
        i, j = mov
        t = list(s)
        t[i], t[j] = t[j], t[i]
        return t

    def sufixo(self, s, mov):
        i, j = mov
        suf = s[i:]
        suf[0], suf[j - i] = s[j], s[i]
        return i, suf


class Insertion(Vizinhanca):
    nome = "insertion"

    def tamanho(self, n: int) -> int:
        return (n - 1) ** 2

    def movimentos(self, n: int) -> list[Mov]:
        return [(i, j) for i in range(n) for j in range(n) if j != i and j != i - 1]

    def aplicar(self, s, mov):
        i, j = mov
        t = list(s)
        t.insert(j, t.pop(i))
        return t

    def sufixo(self, s, mov):
        i, j = mov
        if i < j:
            return i, s[i + 1 : j + 1] + [s[i]] + s[j + 1 :]
        return j, [s[i]] + s[j:i] + s[i + 1 :]


class DoisOpt(Vizinhanca):
    nome = "2opt"

    def tamanho(self, n: int) -> int:
        return n * (n - 1) // 2

    def movimentos(self, n: int) -> list[Mov]:
        return [(i, j) for i in range(n) for j in range(i + 1, n)]

    def aplicar(self, s, mov):
        i, j = mov
        t = list(s)
        t[i : j + 1] = t[i : j + 1][::-1]
        return t

    def sufixo(self, s, mov):
        i, j = mov
        return i, s[i : j + 1][::-1] + s[j + 1 :]


VIZINHANCAS: dict[str, Vizinhanca] = {v.nome: v for v in (Swap(), Insertion(), DoisOpt())}
