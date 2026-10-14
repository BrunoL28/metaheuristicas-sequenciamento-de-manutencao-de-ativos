"""Heurísticas construtivas usadas como referência (linhas de base nos gráficos).

Não fazem parte dos três algoritmos comparados; servem para validar a
implementação contra o valor citado no enunciado (Seção 1.4) e para dar
uma escala aos resultados.
"""

from __future__ import annotations

from tp2.problem.instance import Instance


def guloso_menor_acrescimo(inst: Instance) -> list[int]:
    """Escolhe sempre o ativo que gera o menor acréscimo imediato de atraso.

    No começo da rota quase todo ativo acrescenta atraso zero, então o
    critério de desempate decide a solução. O enunciado não diz qual é; o
    valor 3168 da instância pequena só é reproduzido desempatando pelo menor
    tempo de deslocamento a partir da posição atual (e depois pelo menor
    índice).
    """
    restantes = set(range(1, inst.n + 1))
    atual, C = 0, 0
    rota = []
    while restantes:
        # (acréscimo de atraso, deslocamento, índice) de cada candidato
        _, _, j = min(
            (
                inst.w[k] * max(0, C + inst.T[atual][k] + inst.p[k] - inst.d[k]),
                inst.T[atual][k],
                k,
            )
            for k in restantes
        )
        C += inst.T[atual][j] + inst.p[j]
        atual = j
        rota.append(j)
        restantes.remove(j)
    return rota


def vizinho_mais_proximo(inst: Instance) -> list[int]:
    """Vai sempre ao ativo mais próximo ainda não visitado (desempate: menor índice)."""
    restantes = set(range(1, inst.n + 1))
    atual = 0
    rota = []
    while restantes:
        j = min(restantes, key=lambda k: (inst.T[atual][k], k))
        atual = j
        rota.append(j)
        restantes.remove(j)
    return rota
