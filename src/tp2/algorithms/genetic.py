"""(C) Algoritmo genético (enunciado, Seção 2.5; pseudocódigo da aula, Parte 3).

A cada geração:

1. os ``elite`` melhores indivíduos passam direto para a próxima população;
2. o resto é preenchido com filhos: dois pais escolhidos por torneio, cruzados
   com probabilidade ``Pc`` (senão, os filhos são cópias dos pais), e cada
   filho sofre mutação com probabilidade ``Pm``;
3. cada filho é avaliado, inclusive as cópias sem alteração (1 avaliação
   cada). A busca termina só pelo orçamento, que pode cortar a última
   geração no meio.

Seleção por torneio de tamanho ``k`` comparando h diretamente (menor vence).
Como só a ordem importa, não é preciso converter custo em aptidão, e a
seleção não depende da escala de h (que vai de 10³ a 10⁵ entre instâncias).

Variantes (para o experimento extra, "o AG compensa?"):

- ``padrao``: cruzamento entre dois pais da população;
- ``headless``: "headless chicken" (Jones, 1995): o segundo pai é uma
  permutação aleatória nova. Se o resultado empatar com o padrão, o
  cruzamento está agindo como uma macromutação, não combinando blocos bons.

A variante só com mutação é ``padrao`` com ``Pc = 0``. Com ``p_ls > 0`` o AG
vira memético: cada filho, depois de avaliado, desce com probabilidade
``p_ls`` até um ótimo local (first improvement em ordem aleatória, como a
descida gulosa) e volta melhorado para a população (lamarckiano). Cada
sucessor examinado conta 1 avaliação.

Telemetria por geração (tabela ``ag_geracoes``): melhor h e h médio da
população, número de permutações distintas e distância média entre pares
sorteados (diversidade). O tempo gasto nela volta em ``s_telemetria``, para
o runner descontá-lo do tempo de parede.
"""

from __future__ import annotations

import random
import statistics
import time

from tp2.core.counting import BudgetExhausted
from tp2.core.interface import Problem, Solution
from tp2.core.recorder import Recorder

VARIANTES = ("padrao", "headless")
PARES_DIVERSIDADE = 50


def algoritmo_genetico(
    problema: Problem,
    rng: random.Random,
    variante: str = "padrao",
    *,
    N: int,
    Pc: float,
    Pm: float,
    k: int = 3,
    elite: int = 2,
    p_ls: float = 0.0,
    rec: Recorder | None = None,
) -> dict:
    """Roda até o orçamento acabar e devolve o resumo da execução.

    ``problema`` deve ser um ``CountingProblem``.
    """
    if variante not in VARIANTES:
        raise ValueError(f"variante desconhecida: {variante!r}")
    if not 0 <= elite < N:
        raise ValueError("a elite precisa ser menor que a população")
    rec = rec if rec is not None else Recorder()
    # A amostragem da diversidade usa outro gerador para não alterar a busca.
    rng_div = random.Random(rng.random())

    geracao = 0
    avaliacoes = 0
    cruzamentos = mutacoes = descidas = 0
    s_telemetria = 0.0
    pop: list[Solution] = []
    hs: list[int] = []

    def avaliar(s: Solution) -> int:
        nonlocal avaliacoes
        hv = problema.h(s)
        avaliacoes += 1
        return hv

    def descer(s: Solution, hv: int) -> tuple[Solution, int]:
        nonlocal avaliacoes, descidas
        descidas += 1
        melhorou = True
        while melhorou:
            melhorou = False
            for mov, h_viz in problema.sucessores(s, hv, rng):
                avaliacoes += 1
                if h_viz < hv:
                    s, hv = problema.aplicar(s, mov), h_viz
                    melhorou = True
                    break
        return s, hv

    def torneio() -> Solution:
        melhor = min(rng.sample(range(N), k), key=hs.__getitem__)
        return pop[melhor]

    def registrar() -> None:
        nonlocal s_telemetria
        inicio = time.perf_counter()
        pares = [rng_div.sample(range(N), 2) for _ in range(PARES_DIVERSIDADE)]
        rec.registrar(
            "ag_geracoes",
            geracao=geracao,
            avaliacoes=avaliacoes,
            melhor_h=min(hs),
            media_h=statistics.fmean(hs),
            distintos=len({tuple(s) for s in pop}),
            distancia_media=statistics.fmean(problema.distancia(pop[a], pop[b]) for a, b in pares),
        )
        s_telemetria += time.perf_counter() - inicio

    try:
        for _ in range(N):
            s = problema.solucao_aleatoria(rng)
            pop.append(s)
            hs.append(avaliar(s))
        registrar()

        while True:
            ordem = sorted(range(N), key=hs.__getitem__)[:elite]
            nova = [pop[i] for i in ordem]
            nova_h = [hs[i] for i in ordem]
            while len(nova) < N:
                p1 = torneio()
                p2 = problema.solucao_aleatoria(rng) if variante == "headless" else torneio()
                if rng.random() < Pc:
                    filhos = problema.cruzamento(p1, p2, rng)
                    cruzamentos += 1
                else:
                    filhos = (list(p1), list(p2))
                for filho in filhos:
                    if len(nova) == N:
                        break
                    if rng.random() < Pm:
                        filho = problema.mutacao(filho, rng)
                        mutacoes += 1
                    h_filho = avaliar(filho)
                    if p_ls and rng.random() < p_ls:
                        filho, h_filho = descer(filho, h_filho)
                    nova_h.append(h_filho)
                    nova.append(filho)
            pop, hs = nova, nova_h
            geracao += 1
            registrar()
    except BudgetExhausted:
        pass

    return {
        "geracoes": geracao,
        "cruzamentos": cruzamentos,
        "mutacoes": mutacoes,
        "descidas": descidas,
        "avaliacoes": avaliacoes,
        "s_telemetria": s_telemetria,
    }
