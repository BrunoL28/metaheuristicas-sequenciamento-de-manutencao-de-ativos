"""(B) Simulated annealing (enunciado, Seção 2.4).

A cada passo sorteia um sucessor. Se ele não piora, é aceito. Se piora em
Δ > 0, é aceito com probabilidade e^(−Δ/T) (critério de Gibbs, como na aula).

Resfriamento geométrico em patamares: L passos com a mesma temperatura, depois
T ← α·T. O α é escolhido para que T saia de T0 e chegue a Tf exatamente no fim
do orçamento (``alfa_para_orcamento``). A busca termina só pelo orçamento.

A telemetria agrupa os passos em janelas de tamanho fixo e registra, em cada
uma, quantos sucessores piores foram propostos e quantos foram aceitos. Uma
execução bem calibrada começa com taxa perto de 0,9 (quase um passeio
aleatório) e termina perto de 0 (quase uma descida gulosa).
"""

from __future__ import annotations

import math
import random

from tp2.core.counting import BudgetExhausted
from tp2.core.interface import Problem
from tp2.core.recorder import Recorder


def alfa_para_orcamento(T0: float, Tf: float, orcamento: int, L: int) -> float:
    """α tal que o último patamar (dentro de B avaliações) tenha temperatura Tf.

    A primeira avaliação é a da solução inicial; sobram B − 1 passos, que dão
    M = ⌈(B − 1) / L⌉ patamares. Do primeiro (T0) ao último há M − 1 reduções.
    """
    patamares = math.ceil((orcamento - 1) / L)
    if patamares < 2:
        return 1.0
    return (Tf / T0) ** (1 / (patamares - 1))


def simulated_annealing(
    problema: Problem,
    rng: random.Random,
    variante: str = "geometrico",
    *,
    T0: float,
    Tf: float,
    alfa: float,
    L: int,
    janela: int = 1000,
    rec: Recorder | None = None,
) -> dict:
    """Roda até o orçamento acabar e devolve o resumo da execução.

    ``problema`` deve ser um ``CountingProblem``. ``janela`` é o número de
    passos por linha da tabela ``sa_aceitacao`` em ``rec``.
    """
    if variante != "geometrico":
        raise ValueError(f"variante desconhecida: {variante!r}")
    rec = rec if rec is not None else Recorder()

    passos = aceitos = piores_aceitos = 0
    janela_propostos = janela_aceitos = 0
    T = T0
    s: list[int] = []
    hs = 0

    def fechar_janela() -> None:
        nonlocal janela_propostos, janela_aceitos
        rec.registrar(
            "sa_aceitacao",
            passos=passos,
            T=T,
            h_corrente=hs,
            piores_propostos=janela_propostos,
            piores_aceitos=janela_aceitos,
            taxa=janela_aceitos / janela_propostos if janela_propostos else "",
        )
        janela_propostos = janela_aceitos = 0

    try:
        s = problema.solucao_aleatoria(rng)
        hs = problema.h(s)
        while True:
            for _ in range(L):
                mov, hv = problema.sucessor_aleatorio(s, hs, rng)
                passos += 1
                delta = hv - hs
                if delta <= 0:
                    aceita = True
                else:
                    janela_propostos += 1
                    aceita = rng.random() < math.exp(-delta / T)
                    if aceita:
                        janela_aceitos += 1
                        piores_aceitos += 1
                if aceita:
                    s, hs = problema.aplicar(s, mov), hv
                    aceitos += 1
                if passos % janela == 0:
                    fechar_janela()
            T = max(T * alfa, Tf)
    except BudgetExhausted:
        if passos % janela:
            fechar_janela()

    return {
        "passos": passos,
        "aceitos": aceitos,
        "piores_aceitos": piores_aceitos,
        "T_final": T,
        "h_final": hs,
    }
