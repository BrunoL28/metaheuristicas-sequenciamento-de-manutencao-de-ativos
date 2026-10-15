"""(A) Greedy descent com random restart (enunciado, Seção 2.3).

Desce até um ótimo local, recomeça de uma permutação aleatória e repete até o
orçamento acabar. O melhor global fica com o ``CountingProblem``; aqui só se
contam passos de melhoria e ótimos locais.

Variantes de escolha do sucessor:

- ``best``: avalia a vizinhança inteira e fica com o melhor sucessor (empate:
  o primeiro na ordem canônica). Se nenhum melhora, é ótimo local.
- ``first``: percorre a vizinhança em ordem aleatória e aceita o primeiro
  sucessor que melhora. Se a varredura completa não melhora, é ótimo local.
- ``random``: sorteia um sucessor por vez e aceita se melhorar. Sem varredura
  não há teste exato de ótimo local, então recomeça depois de K sorteios
  seguidos sem melhoria, com K = ``k_fator`` · |N|. Com K = |N| e sorteio com
  reposição, a chance de nunca sortear um dado movimento de melhoria é
  (1 − 1/|N|)^|N| ≈ e⁻¹ ≈ 37%.

O h da solução corrente nunca é recalculado: ele vem do sucessor aceito.
Cada recomeço custa exatamente 1 avaliação (a da nova solução aleatória).
"""

from __future__ import annotations

import random

from tp2.core.counting import BudgetExhausted
from tp2.core.interface import Problem
from tp2.core.recorder import Recorder, assinatura

VARIANTES = ("best", "first", "random")


def descida_gulosa(
    problema: Problem,
    rng: random.Random,
    variante: str = "first",
    k_fator: float = 1.0,
    rec: Recorder | None = None,
) -> dict:
    """Roda até o orçamento acabar e devolve o resumo da execução.

    ``problema`` deve ser um ``CountingProblem``: é ele que encerra a busca
    lançando ``BudgetExhausted`` na avaliação B + 1.

    Para cada descida, registra em ``rec`` (tabela ``otimos_locais``) o h
    final, a assinatura da permutação, os passos de melhoria e se a descida
    terminou (``completa``) ou foi cortada pelo orçamento.
    """
    if variante not in VARIANTES:
        raise ValueError(f"variante desconhecida: {variante!r}")
    rec = rec if rec is not None else Recorder()
    k_max = max(1, round(k_fator * problema.tamanho_vizinhanca()))

    passos_total = 0
    descidas = 0
    completas = 0
    otimos: set[str] = set()
    s: list[int] = []
    hs = 0
    passos = 0

    def registrar(completa: bool) -> None:
        nonlocal passos_total, completas
        passos_total += passos
        if completa:
            completas += 1
            otimos.add(assinatura(s))
        rec.registrar(
            "otimos_locais",
            descida=descidas,
            h=hs,
            assinatura=assinatura(s),
            passos=passos,
            completa=int(completa),
        )

    try:
        while True:
            # Recomeço. Se o orçamento acabar já aqui, não há descida para registrar.
            s = problema.solucao_aleatoria(rng)
            hs = problema.h(s)
            descidas += 1
            passos = 0
            try:
                while True:
                    mov = _escolher(problema, s, hs, rng, variante, k_max)
                    if mov is None:
                        break
                    s, hs = problema.aplicar(s, mov[0]), mov[1]
                    passos += 1
            except BudgetExhausted:
                registrar(completa=False)
                raise
            registrar(completa=True)
    except BudgetExhausted:
        pass

    return {
        "passos": passos_total,
        "descidas": descidas,
        "otimos_locais": completas,
        "otimos_distintos": len(otimos),
    }


def _escolher(problema, s, hs, rng, variante, k_max):
    """Devolve (movimento, h) de um sucessor que melhora, ou None num ótimo local."""
    if variante == "best":
        melhor = None
        for mov, hv in problema.sucessores(s, hs):
            if hv < hs and (melhor is None or hv < melhor[1]):
                melhor = (mov, hv)
        return melhor
    if variante == "first":
        for mov, hv in problema.sucessores(s, hs, rng):
            if hv < hs:
                return mov, hv
        return None
    for _ in range(k_max):
        mov, hv = problema.sucessor_aleatorio(s, hs, rng)
        if hv < hs:
            return mov, hv
    return None
