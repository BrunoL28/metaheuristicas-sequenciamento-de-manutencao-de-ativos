import random

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tp2.algorithms.genetic import algoritmo_genetico
from tp2.core.counting import CountingProblem
from tp2.core.recorder import Recorder
from tp2.experiments import configs
from tp2.experiments.runner import montar_jobs
from tp2.problem.instance import load_named
from tp2.problem.maintenance import MaintenanceProblem
from tp2.problem.operators import cruzamento_ox, demo, ox

# --- operadores ---


def test_ox_exemplo_do_slide():
    assert ox([1, 2, 3, 4, 5], [5, 4, 2, 1, 3], 1, 3) == [5, 2, 3, 4, 1]


@st.composite
def pais_e_cortes(draw):
    n = draw(st.integers(min_value=2, max_value=40))
    p1 = draw(st.permutations(range(1, n + 1)))
    p2 = draw(st.permutations(range(1, n + 1)))
    a = draw(st.integers(min_value=0, max_value=n - 2))
    b = draw(st.integers(min_value=a + 1, max_value=n - 1))
    return list(p1), list(p2), a, b


@given(pais_e_cortes())
def test_ox_gera_permutacao_e_preserva_o_bloco(dados):
    p1, p2, a, b = dados
    filho = ox(p1, p2, a, b)
    assert sorted(filho) == sorted(p1)
    assert filho[a : b + 1] == p1[a : b + 1]
    # Os genes de fora do bloco aparecem na ordem relativa do pai 2.
    fora = [g for k, g in enumerate(filho) if not a <= k <= b]
    assert fora == [g for g in p2 if g in set(fora)]


@given(st.integers(min_value=2, max_value=40), st.integers(min_value=0, max_value=10**6))
def test_cruzamento_gera_dois_filhos_validos(n, seed):
    rng = random.Random(seed)
    p1 = rng.sample(range(1, n + 1), n)
    p2 = rng.sample(range(1, n + 1), n)
    for f in cruzamento_ox(p1, p2, rng):
        assert sorted(f) == list(range(1, n + 1))


@pytest.mark.parametrize("vizinhanca", ["swap", "insertion", "2opt"])
def test_mutacao_e_um_movimento_da_vizinhanca(vizinhanca):
    prob = MaintenanceProblem(load_named("pequena"), vizinhanca)
    rng = random.Random(4)
    s = prob.solucao_aleatoria(rng)
    vizinhos = {tuple(prob.aplicar(s, mov)) for mov, _ in prob.sucessores(s, prob.h(s))}
    for _ in range(50):
        assert tuple(prob.mutacao(s, rng)) in vizinhos


def test_demo_mostra_o_passo_a_passo():
    texto = demo(8, 15)
    assert "Pai 1: (4 1 5 7 2 6 3 8)" in texto
    assert "(3 8 5 7 2 6 1 4)" in texto


# --- algoritmo ---


@pytest.fixture(scope="module")
def pequena():
    return load_named("pequena")


def _rodar(instancia, budget=2000, seed=0, variante="padrao", **params):
    params = {"N": 20, "Pc": 0.9, "Pm": 0.2, "k": 3, "elite": 2, **params}
    cp = CountingProblem(MaintenanceProblem(instancia, "insertion"), budget=budget)
    rec = Recorder()
    resumo = algoritmo_genetico(cp, random.Random(seed), variante, rec=rec, **params)
    return cp, rec, resumo


@pytest.mark.parametrize("variante", ["padrao", "headless"])
def test_gasta_exatamente_o_orcamento(pequena, variante):
    cp, _, resumo = _rodar(pequena, variante=variante)
    assert cp.evals == 2000 == resumo["avaliacoes"]
    assert MaintenanceProblem(pequena).h(cp.best_s) == cp.best_h


def test_geracoes_e_elitismo(pequena):
    cp, rec, resumo = _rodar(pequena, budget=2000)
    geracoes = rec.tabelas["ag_geracoes"]
    # População inicial (20) + gerações completas de 18 filhos.
    assert [g["avaliacoes"] for g in geracoes] == [20 + 18 * k for k in range(len(geracoes))]
    assert resumo["geracoes"] == len(geracoes) - 1 == (2000 - 20) // 18
    melhores = [g["melhor_h"] for g in geracoes]
    assert melhores == sorted(melhores, reverse=True)
    assert all(1 <= g["distintos"] <= 20 for g in geracoes)


def test_sem_cruzamento_nem_mutacao_so_copia(pequena):
    _, rec, resumo = _rodar(pequena, Pc=0.0, Pm=0.0, budget=500)
    assert resumo["cruzamentos"] == resumo["mutacoes"] == 0
    geracoes = rec.tabelas["ag_geracoes"]
    # Só seleção: a diversidade nunca aumenta.
    distintos = [g["distintos"] for g in geracoes]
    assert distintos == sorted(distintos, reverse=True)


def test_mesma_semente_mesma_execucao(pequena):
    a, ra, _ = _rodar(pequena, seed=9)
    b, rb, _ = _rodar(pequena, seed=9)
    assert a.improvements == b.improvements
    assert ra.tabelas == rb.tabelas


def test_parametros_invalidos(pequena):
    cp = CountingProblem(MaintenanceProblem(pequena), budget=10)
    with pytest.raises(ValueError):
        algoritmo_genetico(cp, random.Random(0), "outro", N=10, Pc=0.9, Pm=0.2)
    with pytest.raises(ValueError):
        algoritmo_genetico(cp, random.Random(0), N=10, Pc=0.9, Pm=0.2, elite=10)


def test_runner_monta_os_parametros_do_ag():
    jobs = montar_jobs("ag_ajuste", ["media"], max_execucoes=2)
    assert len({j["run_id"] for j in jobs}) == len(jobs) == 10
    for job in jobs:
        assert job["params"]["Pc"] == configs.AG["media"]["Pc"]
        assert job["rotulo"] == f"N{job['params']['N']}-Pm{job['params']['Pm']}"
    padrao = montar_jobs("ag_piloto", ["grande"], max_execucoes=1)[0]
    assert padrao["params"] == configs.AG["grande"]
