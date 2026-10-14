import itertools
from pathlib import Path

import pytest

from tp2.problem.exato import otimo_exato
from tp2.problem.heuristicas import guloso_menor_acrescimo, vizinho_mais_proximo
from tp2.problem.instance import load_instance, load_named
from tp2.problem.maintenance import MaintenanceProblem

TOY = Path(__file__).parent / "fixtures" / "toy4.txt"


@pytest.fixture(scope="module")
def pequena():
    return load_named("pequena")


@pytest.fixture(scope="module")
def toy():
    return load_instance(TOY, "figura1")


def test_identidade_na_pequena_vale_4366(pequena):
    assert MaintenanceProblem(pequena).h(list(range(1, 13))) == 4366


def test_figura1_rota_gulosa_vale_39_com_cronograma_da_figura(toy):
    prob = MaintenanceProblem(toy)
    assert prob.h([1, 4, 2, 3]) == 39
    assert prob.conclusoes([1, 4, 2, 3]) == [7, 16, 27, 38]


def test_figura1_otimo_unico_vale_22(toy):
    prob = MaintenanceProblem(toy)
    custos = sorted((prob.h(list(p)), p) for p in itertools.permutations([1, 2, 3, 4]))
    assert custos[0] == (22, (1, 4, 3, 2))
    assert custos[1][0] > 22


def test_exato_bate_com_forca_bruta_na_figura1(toy):
    assert otimo_exato(toy) == (22, [1, 4, 3, 2])


def test_otimo_exato_da_pequena_vale_1875(pequena):
    h_otimo, rota = otimo_exato(pequena)
    assert h_otimo == 1875
    assert sorted(rota) == list(range(1, 13))
    assert MaintenanceProblem(pequena).h(rota) == 1875


def test_guloso_do_enunciado_vale_3168(pequena):
    assert MaintenanceProblem(pequena).h(guloso_menor_acrescimo(pequena)) == 3168


def test_vizinho_mais_proximo_vale_2590(pequena):
    assert MaintenanceProblem(pequena).h(vizinho_mais_proximo(pequena)) == 2590


def test_h_nao_decrescente_no_prefixo(pequena):
    prob = MaintenanceProblem(pequena)
    rota = guloso_menor_acrescimo(pequena)
    parciais = [prob.h(rota[:k]) for k in range(len(rota) + 1)]
    assert parciais == sorted(parciais)
