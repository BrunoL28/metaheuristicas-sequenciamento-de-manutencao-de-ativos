import math
import random

import pytest

from tp2.algorithms.simulated_annealing import alfa_para_orcamento, simulated_annealing
from tp2.core.counting import CountingProblem
from tp2.core.recorder import Recorder
from tp2.experiments import calibrate_sa, configs
from tp2.experiments.runner import _parametros
from tp2.problem.instance import load_named
from tp2.problem.maintenance import MaintenanceProblem


@pytest.fixture(scope="module")
def pequena():
    return load_named("pequena")


def _rodar(instancia, budget=3001, seed=0, T0=500.0, Tf=5.0, L=50, janela=300):
    cp = CountingProblem(MaintenanceProblem(instancia, "insertion"), budget=budget)
    rec = Recorder()
    alfa = alfa_para_orcamento(T0, Tf, budget, L)
    resumo = simulated_annealing(
        cp, random.Random(seed), T0=T0, Tf=Tf, alfa=alfa, L=L, janela=janela, rec=rec
    )
    return cp, rec, resumo


@pytest.mark.parametrize(("B", "L"), [(50_000, 100), (150_000, 300), (300_000, 1000), (1001, 7)])
def test_alfa_leva_t0_a_tf_no_ultimo_patamar(B, L):
    T0, Tf = 5000.0, 10.0
    alfa = alfa_para_orcamento(T0, Tf, B, L)
    patamares = math.ceil((B - 1) / L)
    assert T0 * alfa ** (patamares - 1) == pytest.approx(Tf)


def test_gasta_exatamente_o_orcamento(pequena):
    cp, _, resumo = _rodar(pequena)
    assert cp.evals == 3001
    assert resumo["passos"] == 3000
    assert MaintenanceProblem(pequena).h(cp.best_s) == cp.best_h


def test_temperatura_termina_em_tf(pequena):
    _, rec, resumo = _rodar(pequena, budget=3001, L=50, janela=300)
    janelas = rec.tabelas["sa_aceitacao"]
    assert janelas[-1]["passos"] == 3000
    assert [j["passos"] for j in janelas] == list(range(300, 3001, 300))
    assert janelas[-1]["T"] == pytest.approx(5.0)
    temperaturas = [j["T"] for j in janelas]
    assert temperaturas == sorted(temperaturas, reverse=True)
    assert resumo["T_final"] == pytest.approx(5.0)


def test_temperatura_quase_zero_vira_descida(pequena):
    _, rec, resumo = _rodar(pequena, T0=1e-9, Tf=1e-9)
    assert resumo["piores_aceitos"] == 0
    h = [j["h_corrente"] for j in rec.tabelas["sa_aceitacao"]]
    assert h == sorted(h, reverse=True)


def test_temperatura_enorme_aceita_quase_tudo(pequena):
    _, rec, _ = _rodar(pequena, T0=1e12, Tf=1e12)
    propostos = sum(j["piores_propostos"] for j in rec.tabelas["sa_aceitacao"])
    aceitos = sum(j["piores_aceitos"] for j in rec.tabelas["sa_aceitacao"])
    assert aceitos == propostos > 0


def test_mesma_semente_mesma_execucao(pequena):
    a, ra, _ = _rodar(pequena, seed=5)
    b, rb, _ = _rodar(pequena, seed=5)
    assert a.improvements == b.improvements
    assert ra.tabelas == rb.tabelas


def test_calibracao_segue_as_formulas():
    c = calibrate_sa.calibrar("pequena")
    assert c["T0"] == pytest.approx(-c["mediana_piora"] / math.log(0.9))
    assert c["Tf"] == pytest.approx(-c["q10_piora"] / math.log(1e-3))
    assert 0 < c["Tf"] < c["T0"]
    assert c["avaliacoes_calibracao"] == 2 * calibrate_sa.AMOSTRAS
    assert c["alfa"] == pytest.approx(alfa_para_orcamento(c["T0"], c["Tf"], 50_000, c["L"]))


def test_runner_usa_a_calibracao_versionada():
    cel = configs.celulas("sa_piloto")[0]
    for inst in configs.INSTANCIAS:
        cal = calibrate_sa.carregar(inst)
        params = _parametros(cel, inst, configs.ORCAMENTO[inst])
        assert params["T0"] == cal["T0"] and params["Tf"] == cal["Tf"]
        assert params["alfa"] == pytest.approx(cal["alfa"])
        assert params["janela"] == configs.ORCAMENTO[inst] // 100
