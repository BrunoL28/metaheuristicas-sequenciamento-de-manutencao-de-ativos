"""PMX, AG memético e as suítes do T3, do experimento extra e de robustez."""

import random

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tp2.algorithms.genetic import algoritmo_genetico
from tp2.core.counting import CountingProblem
from tp2.core.recorder import Recorder
from tp2.experiments import calibrate_sa, configs
from tp2.experiments.runner import executar, montar_jobs
from tp2.problem.instance import load_named
from tp2.problem.maintenance import MaintenanceProblem
from tp2.problem.operators import cortes, ox, pmx

# --- PMX ---


def test_pmx_exemplo_classico():
    # Exemplo de Goldberg e Lingle reproduzido na literatura: bloco nas posições 3..7.
    p1 = [8, 4, 7, 3, 6, 2, 5, 1, 9, 0]
    p2 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert pmx(p1, p2, 3, 7) == [0, 7, 4, 3, 6, 2, 5, 1, 8, 9]


@given(st.data())
def test_pmx_gera_permutacao_e_preserva_posicoes(data):
    n = data.draw(st.integers(min_value=2, max_value=40))
    p1 = list(data.draw(st.permutations(range(1, n + 1))))
    p2 = list(data.draw(st.permutations(range(1, n + 1))))
    a = data.draw(st.integers(min_value=0, max_value=n - 2))
    b = data.draw(st.integers(min_value=a + 1, max_value=n - 1))
    filho = pmx(p1, p2, a, b)
    assert sorted(filho) == list(range(1, n + 1))
    assert filho[a : b + 1] == p1[a : b + 1]
    # Fora do bloco, todo gene do pai 2 que não conflita fica na mesma posição.
    bloco = set(p1[a : b + 1])
    for k in range(n):
        if not a <= k <= b and p2[k] not in bloco:
            assert filho[k] == p2[k]


def test_problema_usa_o_cruzamento_escolhido():
    inst = load_named("pequena")
    p1 = list(range(1, 13))
    p2 = [3, 7, 12, 1, 9, 5, 11, 2, 8, 10, 4, 6]
    a, b = cortes(12, random.Random(3))
    assert ox(p1, p2, a, b) != pmx(p1, p2, a, b)
    for nome, operador in (("ox", ox), ("pmx", pmx)):
        problema = MaintenanceProblem(inst, cruzamento=nome)
        a, b = cortes(12, random.Random(3))
        esperado = (operador(p1, p2, a, b), operador(p2, p1, a, b))
        assert problema.cruzamento(p1, p2, random.Random(3)) == esperado
    with pytest.raises(KeyError):
        MaintenanceProblem(inst, cruzamento="erx")


# --- AG memético ---


def test_memetico_gasta_exatamente_o_orcamento_e_desce():
    inst = load_named("pequena")
    cp = CountingProblem(MaintenanceProblem(inst, "insertion"), budget=3000)
    rec = Recorder()
    resumo = algoritmo_genetico(cp, random.Random(2), N=20, Pc=0.9, Pm=0.2, p_ls=0.5, rec=rec)
    assert cp.evals == 3000 == resumo["avaliacoes"]
    assert resumo["descidas"] > 0
    assert MaintenanceProblem(inst).h(cp.best_s) == cp.best_h
    melhores = [g["melhor_h"] for g in rec.tabelas["ag_geracoes"]]
    assert melhores == sorted(melhores, reverse=True)


# --- suítes ---


def test_t3_tem_os_tres_algoritmos_e_as_variantes():
    jobs = montar_jobs("t3", list(configs.INSTANCIAS))
    celulas = {(j["algoritmo"], j["variante"]) for j in jobs}
    assert celulas == {
        ("gd", "best"),
        ("gd", "first"),
        ("gd", "random"),
        ("sa", "geometrico"),
        ("ag", "padrao"),
    }
    assert len(jobs) == 5 * (30 + 30 + 10)
    assert all(j["orcamento"] == configs.ORCAMENTO[j["instancia"]] for j in jobs)


def test_extra_configura_os_cinco_bracos():
    jobs = montar_jobs("extra", ["media"], max_execucoes=1)
    por_rotulo = {(j["variante"], j["rotulo"]): j for j in jobs}
    assert por_rotulo[("padrao", "so-mutacao")]["params"]["Pc"] == 0.0
    assert por_rotulo[("padrao", "pmx")]["problema"] == {"cruzamento": "pmx"}
    assert por_rotulo[("padrao", "memetico")]["params"]["p_ls"] == configs.P_LS
    assert ("headless", "") in por_rotulo
    assert por_rotulo[("padrao", "ox")]["params"] == configs.AG["media"]
    assert len({j["run_id"] for j in jobs}) == 5


def test_robustez_ajusta_os_orcamentos():
    jobs = montar_jobs("robustez", list(configs.INSTANCIAS), max_execucoes=1)
    for j in jobs:
        B = configs.ORCAMENTO[j["instancia"]]
        if j["rotulo"] == "2B":
            assert j["instancia"] in ("media", "grande")
            assert j["orcamento"] == 2 * B
        else:
            cal = calibrate_sa.carregar(j["instancia"])
            assert j["orcamento"] == B - cal["avaliacoes_calibracao"]
            # α recalculado para o orçamento menor: T ainda chega a Tf no fim.
            assert j["params"]["alfa"] < cal["alfa"]
    assert len(jobs) == 3 + 5 * 2


def test_execucao_com_pmx_e_orcamento_reduzido():
    job = next(
        j
        for j in montar_jobs("extra", ["pequena"], max_execucoes=1, orcamento=600)
        if j["rotulo"] == "pmx"
    )
    resultado = executar(job)
    assert resultado["erro"] is None
    assert resultado["linha"]["evals"] == 600
