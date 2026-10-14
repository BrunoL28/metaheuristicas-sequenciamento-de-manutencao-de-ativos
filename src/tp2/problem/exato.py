"""Ótimo exato para instâncias pequenas (programação dinâmica com rótulos de Pareto).

Serve só para conferir o h* = 1875 da instância pequena (Seção 1.4). Não é um
dos algoritmos comparados.

Estado: (conjunto de ativos já visitados, último ativo). Dois caminhos que
chegam ao mesmo estado diferem apenas no instante atual C e no custo
acumulado h. Como o custo futuro nunca diminui quando C aumenta, um rótulo
(C, h) com C e h menores ou iguais aos de outro o domina, e o dominado pode
ser descartado. Para n = 12 são 4096 × 12 estados com poucos rótulos cada.
"""

from __future__ import annotations

from tp2.problem.instance import Instance

# rótulo: (C, h, estado_anterior, índice_do_rótulo_anterior)
Rotulo = tuple[int, int, tuple[int, int] | None, int]


def _pareto(rotulos: list[Rotulo]) -> list[Rotulo]:
    rotulos.sort(key=lambda r: (r[0], r[1]))
    frente: list[Rotulo] = []
    melhor_h = None
    for r in rotulos:
        if melhor_h is None or r[1] < melhor_h:
            frente.append(r)
            melhor_h = r[1]
    return frente


def otimo_exato(inst: Instance, n_max: int = 15) -> tuple[int, list[int]]:
    """Devolve (h*, permutação ótima). Recusa instâncias com n > n_max."""
    n = inst.n
    if n > n_max:
        raise ValueError(f"n = {n} grande demais para a enumeração exata (limite {n_max})")
    T, p, d, w = inst.T, inst.p, inst.d, inst.w

    rotulos: dict[tuple[int, int], list[Rotulo]] = {}
    for j in range(1, n + 1):
        C = T[0][j] + p[j]
        rotulos[(1 << (j - 1), j)] = [(C, w[j] * max(0, C - d[j]), None, -1)]

    for mascara in range(1, 1 << n):
        for ultimo in range(1, n + 1):
            estado = (mascara, ultimo)
            if estado not in rotulos:
                continue
            frente = _pareto(rotulos[estado])
            rotulos[estado] = frente
            for k in range(1, n + 1):
                bit = 1 << (k - 1)
                if mascara & bit:
                    continue
                destino = rotulos.setdefault((mascara | bit, k), [])
                for idx, (C, h, _, _) in enumerate(frente):
                    C2 = C + T[ultimo][k] + p[k]
                    destino.append((C2, h + w[k] * max(0, C2 - d[k]), estado, idx))

    completo = (1 << n) - 1
    melhor = None
    for ultimo in range(1, n + 1):
        frente = _pareto(rotulos[(completo, ultimo)])
        rotulos[(completo, ultimo)] = frente
        for idx, r in enumerate(frente):
            if melhor is None or r[1] < melhor[0]:
                melhor = (r[1], (completo, ultimo), idx)

    h_otimo, estado, idx = melhor
    rota = []
    while estado is not None:
        rota.append(estado[1])
        _, _, anterior, idx_anterior = rotulos[estado][idx]
        estado, idx = anterior, idx_anterior
    rota.reverse()
    return h_otimo, rota
