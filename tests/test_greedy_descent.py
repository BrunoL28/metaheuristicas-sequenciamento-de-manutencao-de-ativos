import random

import pytest

from tp2.algorithms.greedy_descent import VARIANTES, descida_gulosa
from tp2.core.counting import CountingProblem
from tp2.core.recorder import Recorder, assinatura
from tp2.problem.instance import load_named
from tp2.problem.maintenance import MaintenanceProblem


@pytest.fixture(scope="module")
def pequena():
    return load_named("pequena")


def _rodar(instancia, variante, vizinhanca="swap", budget=3000, seed=0):
    cp = CountingProblem(MaintenanceProblem(instancia, vizinhanca), budget=budget)
    rec = Recorder()
    resumo = descida_gulosa(cp, random.Random(seed), variante, rec=rec)
    return cp, rec, resumo


@pytest.mark.parametrize("variante", VARIANTES)
@pytest.mark.parametrize("vizinhanca", ["swap", "insertion", "2opt"])
def test_gasta_exatamente_o_orcamento(pequena, variante, vizinhanca):
    cp, _, _ = _rodar(pequena, variante, vizinhanca, budget=2345)
    assert cp.evals == 2345
    assert MaintenanceProblem(pequena).h(cp.best_s) == cp.best_h


@pytest.mark.parametrize("variante", ["best", "first"])
def test_descidas_completas_terminam_em_otimo_local(pequena, variante):
    cp, rec, _ = _rodar(pequena, variante)
    puro = MaintenanceProblem(pequena, "swap")
    completas = [r for r in rec.tabelas["otimos_locais"] if r["completa"]]
    assert completas
    # Refaz as descidas com a mesma semente para ter as permutações finais.
    finais = _permutacoes_finais(pequena, variante)
    assert [assinatura(s) for s in finais] == [r["assinatura"] for r in completas]
    for s, r in zip(finais, completas, strict=True):
        h_s = puro.h(s)
        assert h_s == r["h"]
        assert all(hv >= h_s for _, hv in puro.sucessores(s, h_s))


def _permutacoes_finais(instancia, variante):
    """Captura as soluções no fim de cada descida completa, espiando ``aplicar``."""
    cp = CountingProblem(MaintenanceProblem(instancia, "swap"), budget=3000)
    finais = []

    class Espiao(Recorder):
        def __init__(self):
            super().__init__()
            self.atual = None

        def registrar(self, tabela, **campos):
            super().registrar(tabela, **campos)
            if campos["completa"]:
                finais.append(list(self.atual))

    espiao = Espiao()
    aplicar = cp.aplicar
    solucao_aleatoria = cp.solucao_aleatoria

    def aplicar_espiado(s, mov):
        espiao.atual = aplicar(s, mov)
        return espiao.atual

    def aleatoria_espiada(rng):
        espiao.atual = solucao_aleatoria(rng)
        return espiao.atual

    cp.aplicar = aplicar_espiado
    cp.solucao_aleatoria = aleatoria_espiada
    descida_gulosa(cp, random.Random(0), variante, rec=espiao)
    return finais


def test_resumo_bate_com_a_telemetria(pequena):
    _, rec, resumo = _rodar(pequena, "first", budget=5000)
    registros = rec.tabelas["otimos_locais"]
    assert resumo["descidas"] == len(registros)
    assert resumo["passos"] == sum(r["passos"] for r in registros)
    assert resumo["otimos_locais"] == sum(r["completa"] for r in registros)
    assert resumo["otimos_distintos"] == len({r["assinatura"] for r in registros if r["completa"]})
    # Só a última descida pode ter sido cortada pelo orçamento.
    assert all(r["completa"] for r in registros[:-1])


def test_mesma_semente_mesma_execucao(pequena):
    a, _, ra = _rodar(pequena, "first", "insertion", seed=7)
    b, _, rb = _rodar(pequena, "first", "insertion", seed=7)
    assert a.improvements == b.improvements
    assert a.best_s == b.best_s
    assert ra == rb


def test_random_recomeca_depois_de_k_falhas(pequena):
    # Com k_fator minúsculo (K = 1), quase toda descida para no primeiro fracasso.
    cp = CountingProblem(MaintenanceProblem(pequena, "swap"), budget=2000)
    rec = Recorder()
    descida_gulosa(cp, random.Random(3), "random", k_fator=0.001, rec=rec)
    longas = _rodar(pequena, "random", budget=2000, seed=3)[2]
    assert len(rec.tabelas["otimos_locais"]) > longas["descidas"]


def test_supera_o_guloso_construtivo(pequena):
    cp, _, _ = _rodar(pequena, "first", budget=50_000, seed=1)
    assert cp.best_h < 3168


def test_variante_invalida(pequena):
    cp = CountingProblem(MaintenanceProblem(pequena), budget=10)
    with pytest.raises(ValueError):
        descida_gulosa(cp, random.Random(0), "melhor")
