"""Tarefa T1: valida a função de avaliação contra os valores do enunciado.

Uso: ``uv run python -m tp2.verify`` (ou ``make verify``). A saída é colada
no relatório. Sai com código 1 se algum valor não bater.
"""

from __future__ import annotations

import sys

from tp2.problem.exato import otimo_exato
from tp2.problem.heuristicas import guloso_menor_acrescimo, vizinho_mais_proximo
from tp2.problem.instance import RAIZ_PROJETO, load_instance, load_named
from tp2.problem.maintenance import MaintenanceProblem

TOY = RAIZ_PROJETO / "tests" / "fixtures" / "toy4.txt"


def _linha(rotulo: str, obtido: int, esperado: int | None) -> bool:
    if esperado is None:
        print(f"  {rotulo} = {obtido}")
        return True
    ok = obtido == esperado
    marca = "OK" if ok else f"ERRO (esperado {esperado})"
    print(f"  {rotulo} = {obtido}  [{marca}]")
    return ok


def main() -> int:
    ok = True
    print("Verificação da função de avaliação h\n")

    print("Instâncias (Seção 1.3):")
    esperado_soma_p = {"pequena": 55, "media": 239, "grande": 684}
    esperado_n = {"pequena": 12, "media": 50, "grande": 150}
    for nome in ("pequena", "media", "grande"):
        inst = load_named(nome)
        ok &= inst.n == esperado_n[nome]
        ok &= _linha(f"{nome:<8} n = {inst.n:<4} soma de p_j", sum(inst.p), esperado_soma_p[nome])

    pequena = load_named("pequena")
    prob = MaintenanceProblem(pequena)
    print("\nInstância pequena (Seção 1.4):")
    identidade = list(range(1, pequena.n + 1))
    ok &= _linha("h(1, 2, ..., 12)", prob.h(identidade), 4366)
    h_otimo, rota_otima = otimo_exato(pequena)
    ok &= _linha("h* (programação dinâmica exata)", h_otimo, 1875)
    ok &= _linha("h(rota ótima), reavaliada", prob.h(rota_otima), 1875)
    print(f"  rota ótima = {tuple(rota_otima)}")
    ok &= _linha(
        "guloso de menor acréscimo (desempate: deslocamento)",
        prob.h(guloso_menor_acrescimo(pequena)),
        3168,
    )
    _linha("vizinho mais próximo (referência)", prob.h(vizinho_mais_proximo(pequena)), None)

    toy = MaintenanceProblem(load_instance(TOY, "figura1"))
    print("\nExemplo da Figura 1 (n = 4):")
    ok &= _linha("h(1, 4, 2, 3)", toy.h([1, 4, 2, 3]), 39)
    ok &= _linha("h(1, 4, 3, 2)", toy.h([1, 4, 3, 2]), 22)

    print("\nResultado:", "todos os valores conferem." if ok else "HÁ DIVERGÊNCIAS.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
