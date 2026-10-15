"""Tempo por avaliação de sucessor: completa × incremental (enunciado, Seção 3).

Para cada instância e vizinhança, sorteia soluções e movimentos e mede o tempo
médio de avaliar um sucessor (a) do zero e (b) a partir do prefixo inalterado.
A contagem de avaliações é a mesma nos dois casos; muda só o tempo de parede.

Uso: ``uv run python -m tp2.experiments.tempo_movimentos --out <arquivo.csv>``
"""

from __future__ import annotations

import argparse
import csv
import random
import time
from pathlib import Path

from tp2.problem.instance import load_named
from tp2.problem.maintenance import MaintenanceProblem

INSTANCIAS = ("pequena", "media", "grande")
VIZINHANCAS = ("swap", "insertion", "2opt")


def medir(
    instancia: str, vizinhanca: str, incremental: bool, n_solucoes: int, n_movs: int, seed: int
) -> float:
    """Microssegundos médios por avaliação de sucessor."""
    prob = MaintenanceProblem(load_named(instancia), vizinhanca, incremental=incremental)
    rng = random.Random(seed)
    total_ns = 0
    for _ in range(n_solucoes):
        s = prob.solucao_aleatoria(rng)
        h_s = prob.h(s)
        movs = [prob._movimentos[rng.randrange(len(prob._movimentos))] for _ in range(n_movs)]
        if incremental:
            prob._preparar_cache(s, h_s)
        inicio = time.perf_counter_ns()
        for mov in movs:
            prob._avaliar_movimento(s, mov)
        total_ns += time.perf_counter_ns() - inicio
    return total_ns / (n_solucoes * n_movs) / 1000


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--solucoes", type=int, default=20)
    ap.add_argument("--movimentos", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=20261014)
    args = ap.parse_args()

    linhas = []
    for inst in INSTANCIAS:
        for viz in VIZINHANCAS:
            completa = medir(inst, viz, False, args.solucoes, args.movimentos, args.seed)
            incremental = medir(inst, viz, True, args.solucoes, args.movimentos, args.seed)
            linhas.append(
                {
                    "instancia": inst,
                    "vizinhanca": viz,
                    "us_completa": round(completa, 3),
                    "us_incremental": round(incremental, 3),
                    "ganho": round(completa / incremental, 2),
                }
            )
            print(
                f"{inst:<8} {viz:<10} completa {completa:7.2f} µs  "
                f"incremental {incremental:7.2f} µs  ganho {completa / incremental:4.2f}x"
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    main()
