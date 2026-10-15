import random

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tp2.problem.instance import criar_instancia, load_named
from tp2.problem.maintenance import MaintenanceProblem
from tp2.problem.neighborhoods import VIZINHANCAS

NOMES = ["swap", "insertion", "2opt"]


@pytest.mark.parametrize(
    ("nome", "n", "esperado"),
    [
        ("swap", 12, 66),
        ("swap", 50, 1225),
        ("swap", 150, 11175),
        ("2opt", 12, 66),
        ("2opt", 50, 1225),
        ("2opt", 150, 11175),
        ("insertion", 12, 121),
        ("insertion", 50, 2401),
        ("insertion", 150, 22201),
    ],
)
def test_tamanho_da_vizinhanca(nome, n, esperado):
    viz = VIZINHANCAS[nome]
    assert viz.tamanho(n) == esperado
    assert len(viz.movimentos(n)) == esperado


@pytest.mark.parametrize("nome", NOMES)
@pytest.mark.parametrize("n", [2, 3, 5, 12])
def test_sucessores_distintos_e_diferentes_de_s(nome, n):
    viz = VIZINHANCAS[nome]
    s = random.Random(n).sample(range(1, n + 1), n)
    vizinhos = [tuple(viz.aplicar(s, m)) for m in viz.movimentos(n)]
    assert len(set(vizinhos)) == len(vizinhos) == viz.tamanho(n)
    assert tuple(s) not in vizinhos
    assert all(sorted(v) == sorted(s) for v in vizinhos)


def test_exemplos_da_figura_3():
    s = [3, 7, 1, 5, 2, 8]
    assert VIZINHANCAS["swap"].aplicar(s, (1, 4)) == [3, 2, 1, 5, 7, 8]
    assert VIZINHANCAS["insertion"].aplicar(s, (1, 4)) == [3, 1, 5, 2, 7, 8]
    assert VIZINHANCAS["2opt"].aplicar(s, (1, 4)) == [3, 2, 5, 1, 7, 8]


@pytest.mark.parametrize("nome", NOMES)
def test_sufixo_reconstroi_o_sucessor(nome):
    viz = VIZINHANCAS[nome]
    s = random.Random(1).sample(range(1, 13), 12)
    for m in viz.movimentos(12):
        a, suf = viz.sufixo(s, m)
        t = viz.aplicar(s, m)
        assert t[:a] == s[:a]
        assert t[a:] == suf


@st.composite
def instancias(draw):
    n = draw(st.integers(min_value=2, max_value=30))
    coord = st.integers(min_value=0, max_value=99)
    ativos = [
        (
            draw(coord),
            draw(coord),
            draw(st.integers(1, 8)),
            draw(st.integers(0, 400)),
            draw(st.integers(1, 5)),
        )
        for _ in range(n)
    ]
    return criar_instancia("aleatoria", (draw(coord), draw(coord)), ativos)


@settings(max_examples=150, deadline=None)
@given(instancias(), st.sampled_from(NOMES), st.randoms(use_true_random=False))
def test_avaliacao_incremental_igual_a_completa(inst, nome, rng):
    prob = MaintenanceProblem(inst, vizinhanca=nome, incremental=True)
    s = prob.solucao_aleatoria(rng)
    h_s = prob.h(s)
    for mov, hv in prob.sucessores(s, h_s):
        assert hv == prob.h(prob.aplicar(s, mov))


@pytest.mark.parametrize("nome", NOMES)
@pytest.mark.parametrize("instancia", ["pequena", "media"])
def test_incremental_igual_a_completa_nas_instancias(nome, instancia):
    inst = load_named(instancia)
    inc = MaintenanceProblem(inst, vizinhanca=nome, incremental=True)
    completa = MaintenanceProblem(inst, vizinhanca=nome, incremental=False)
    rng = random.Random(7)
    for _ in range(5):
        s = inc.solucao_aleatoria(rng)
        h_s = inc.h(s)
        assert list(inc.sucessores(s, h_s)) == list(completa.sucessores(s, h_s))


def test_sucessor_aleatorio_e_ordem_aleatoria():
    prob = MaintenanceProblem(load_named("pequena"), vizinhanca="swap")
    rng = random.Random(3)
    s = prob.solucao_aleatoria(rng)
    h_s = prob.h(s)
    for _ in range(200):
        mov, hv = prob.sucessor_aleatorio(s, h_s, rng)
        assert hv == prob.h(prob.aplicar(s, mov))
    ordem = [m for m, _ in prob.sucessores(s, h_s, rng)]
    assert sorted(ordem) == sorted(m for m, _ in prob.sucessores(s, h_s))


def test_h_s_errado_e_detectado():
    prob = MaintenanceProblem(load_named("pequena"))
    s = list(range(1, 13))
    with pytest.raises(ValueError):
        next(prob.sucessores(s, 1234))


def test_distancia_hamming():
    prob = MaintenanceProblem(load_named("pequena"))
    s = list(range(1, 13))
    assert prob.distancia(s, s) == 0
    assert prob.distancia(s, prob.aplicar(s, (0, 5))) == 2
