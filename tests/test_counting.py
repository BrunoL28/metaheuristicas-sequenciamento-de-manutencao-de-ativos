import random

import pytest

from tp2.core.counting import BudgetExhausted, CountingProblem
from tp2.problem.instance import load_named
from tp2.problem.maintenance import MaintenanceProblem


@pytest.fixture
def problema():
    return MaintenanceProblem(load_named("pequena"), vizinhanca="swap")


def test_exatamente_b_avaliacoes(problema):
    cp = CountingProblem(problema, budget=100)
    rng = random.Random(0)
    feitas = 0
    with pytest.raises(BudgetExhausted):
        for _ in range(110):
            cp.h(cp.solucao_aleatoria(rng))
            feitas += 1
    assert feitas == 100
    assert cp.evals == 100


def test_sucessores_param_no_meio_da_varredura(problema):
    cp = CountingProblem(problema, budget=10)
    s = list(range(1, 13))
    h_s = cp.h(s)
    vistos = []
    with pytest.raises(BudgetExhausted):
        for mov, _ in cp.sucessores(s, h_s):
            vistos.append(mov)
    assert len(vistos) == 9  # 1 avaliação em h(s) + 9 sucessores
    assert cp.evals == 10


def test_sucessor_aleatorio_conta_e_respeita_o_orcamento(problema):
    cp = CountingProblem(problema, budget=5)
    rng = random.Random(1)
    s = cp.solucao_aleatoria(rng)
    h_s = cp.h(s)
    for _ in range(4):
        cp.sucessor_aleatorio(s, h_s, rng)
    assert cp.evals == 5
    with pytest.raises(BudgetExhausted):
        cp.sucessor_aleatorio(s, h_s, rng)


def test_melhor_solucao_e_trilha_de_melhorias(problema):
    cp = CountingProblem(problema, budget=500)
    rng = random.Random(2)
    s = cp.solucao_aleatoria(rng)
    h_s = cp.h(s)
    for mov, hv in cp.sucessores(s, h_s):
        if hv < h_s:
            s, h_s = cp.aplicar(s, mov), hv
            break
    assert problema.h(cp.best_s) == cp.best_h
    melhores = [h for _, h in cp.improvements]
    assert melhores == sorted(melhores, reverse=True)
    assert cp.improvements[-1][1] == cp.best_h


def test_metodos_sem_avaliacao_nao_contam(problema):
    cp = CountingProblem(problema, budget=1)
    rng = random.Random(3)
    s = cp.solucao_aleatoria(rng)
    t = cp.aplicar(s, (0, 1))
    cp.distancia(s, t)
    cp.tamanho_vizinhanca()
    assert cp.evals == 0
