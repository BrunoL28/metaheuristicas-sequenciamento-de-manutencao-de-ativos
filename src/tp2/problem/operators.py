"""Operadores do algoritmo genético para permutações (enunciado, Seção 2.5).

Cruzamento OX (order crossover) na convenção do slide da aula (Parte 3):
o filho herda do pai 1 um bloco contíguo, nas mesmas posições, e as posições
livres são preenchidas da esquerda para a direita com os genes que faltam, na
ordem em que aparecem no pai 2. Exemplo do slide, com bloco nas posições 1..3:

    P1 = (1 2 3 4 5), P2 = (5 4 2 1 3)  →  filho = (5 2 3 4 1)

O filho é sempre uma permutação: o bloco não tem repetição e o preenchimento
só usa genes que ainda não estão no filho. O segundo filho troca os papéis
dos pais.

Mutação: um movimento aleatório da vizinhança configurada (ver
``MaintenanceProblem.mutacao``).

Exemplo passo a passo para o relatório:
``uv run python -m tp2.problem.operators --demo --n 8 --seed 15``
"""

from __future__ import annotations

import argparse
import random
from collections.abc import Sequence


def ox(p1: Sequence[int], p2: Sequence[int], a: int, b: int) -> list[int]:
    """Filho do OX com o bloco p1[a..b] (inclusive) mantido no lugar."""
    n = len(p1)
    filho: list[int | None] = [None] * n
    filho[a : b + 1] = p1[a : b + 1]
    no_bloco = set(p1[a : b + 1])
    resto = iter(g for g in p2 if g not in no_bloco)
    for k in range(n):
        if filho[k] is None:
            filho[k] = next(resto)
    return filho  # type: ignore[return-value]


def cortes(n: int, rng: random.Random) -> tuple[int, int]:
    """Dois pontos de corte distintos a < b, sorteados uniformemente."""
    a, b = sorted(rng.sample(range(n), 2))
    return a, b


def cruzamento_ox(
    p1: Sequence[int], p2: Sequence[int], rng: random.Random
) -> tuple[list[int], list[int]]:
    a, b = cortes(len(p1), rng)
    return ox(p1, p2, a, b), ox(p2, p1, a, b)


def demo(n: int, seed: int) -> str:
    """Exemplo numérico passo a passo do OX (texto para o relatório)."""
    rng = random.Random(seed)
    p1 = rng.sample(range(1, n + 1), n)
    p2 = rng.sample(range(1, n + 1), n)
    a, b = cortes(n, rng)
    bloco = p1[a : b + 1]
    ordem_p2 = [g for g in p2 if g not in set(bloco)]
    parcial = ["_"] * n
    parcial[a : b + 1] = map(str, bloco)
    filho = ox(p1, p2, a, b)

    def fmt(s):
        return "(" + " ".join(map(str, s)) + ")"

    linhas = [
        f"Pai 1: {fmt(p1)}",
        f"Pai 2: {fmt(p2)}",
        f"1. Cortes nas posições {a + 1} e {b + 1} (contando de 1): bloco do pai 1 = {fmt(bloco)}",
        f"2. Copia o bloco nas mesmas posições: {fmt(parcial)}",
        f"3. Genes do pai 2 que faltam, na ordem do pai 2: {fmt(ordem_p2)}",
        f"4. Preenche as posições livres da esquerda para a direita: {fmt(filho)}",
        f"Segundo filho (papéis trocados): {fmt(ox(p2, p1, a, b))}",
    ]
    return "\n".join(linhas)


def main() -> None:
    ap = argparse.ArgumentParser(description="Operadores do AG")
    ap.add_argument("--demo", action="store_true", help="exemplo passo a passo do OX")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--seed", type=int, default=15)
    args = ap.parse_args()
    if args.demo:
        print(demo(args.n, args.seed))


if __name__ == "__main__":
    main()
