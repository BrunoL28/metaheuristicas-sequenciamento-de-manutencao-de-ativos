import math

import pytest

from tp2.problem.instance import load_named, tempo_deslocamento


@pytest.mark.parametrize(
    ("nome", "n", "soma_p"),
    [("pequena", 12, 55), ("media", 50, 239), ("grande", 150, 684)],
)
def test_instancias_batem_com_o_enunciado(nome, n, soma_p):
    inst = load_named(nome)
    assert inst.n == n
    assert sum(inst.p) == soma_p
    assert inst.xy[0] == (50, 50)
    assert inst.p[0] == 0
    assert len(inst.T) == n + 1 and all(len(linha) == n + 1 for linha in inst.T)


@pytest.mark.parametrize("nome", ["pequena", "media", "grande"])
def test_matriz_de_tempos_simetrica_e_sem_empate_em_meio(nome):
    inst = load_named(nome)
    for i, a in enumerate(inst.xy):
        assert inst.T[i][i] == 0
        for j, b in enumerate(inst.xy):
            assert inst.T[i][j] == inst.T[j][i]
            distancia = math.hypot(a[0] - b[0], a[1] - b[1])
            # nenhuma distância termina em ,5: o tipo de arredondamento não importa
            assert abs((distancia % 1) - 0.5) > 1e-9


def test_tempo_deslocamento_arredonda():
    assert tempo_deslocamento((0, 0), (3, 4)) == 5
    assert tempo_deslocamento((0, 0), (1, 1)) == 1  # 1,414
    assert tempo_deslocamento((0, 0), (1, 2)) == 2  # 2,236
    assert tempo_deslocamento((0, 0), (2, 2)) == 3  # 2,828
