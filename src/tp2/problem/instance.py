"""Leitura das instâncias ``manutencao_*.txt`` (enunciado, Seção 1.3)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[3]
PASTA_INSTANCIAS = RAIZ_PROJETO / "INPUTS"

INSTANCIAS = {
    "pequena": PASTA_INSTANCIAS / "manutencao_pequena.txt",
    "media": PASTA_INSTANCIAS / "manutencao_media.txt",
    "grande": PASTA_INSTANCIAS / "manutencao_grande.txt",
}


@dataclass(frozen=True)
class Instance:
    """Dados de uma instância. O índice 0 é a base; os ativos vão de 1 a n.

    ``p``, ``d`` e ``w`` têm n + 1 posições, com a base valendo 0 (p_0 = 0).
    ``T[i][j]`` é o tempo de deslocamento arredondado da Equação (1).
    """

    nome: str
    n: int
    xy: tuple[tuple[int, int], ...]
    p: tuple[int, ...]
    d: tuple[int, ...]
    w: tuple[int, ...]
    T: tuple[tuple[int, ...], ...]


def tempo_deslocamento(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Equação (1): distância euclidiana arredondada para o inteiro mais próximo.

    Com coordenadas inteiras, sqrt(k) nunca termina exatamente em 0,5
    (seria k = m² + m + 1/4, que não é inteiro). Por isso o ``round`` do
    Python, que desempata para o par, dá o mesmo resultado que arredondar
    meio para cima.
    """
    return round(math.hypot(a[0] - b[0], a[1] - b[1]))


def load_instance(caminho: str | Path, nome: str | None = None) -> Instance:
    """Lê um arquivo no formato da Seção 1.3 e pré-computa a matriz de tempos."""
    caminho = Path(caminho)
    tokens = caminho.read_text().split()
    n = int(tokens[0])
    if len(tokens) != 3 + 5 * n:
        raise ValueError(
            f"{caminho}: esperava {3 + 5 * n} números para n = {n}, encontrei {len(tokens)}"
        )
    valores = [int(t) for t in tokens]

    xy = [(valores[1], valores[2])]
    p, d, w = [0], [0], [0]
    for i in range(n):
        x, y, pj, dj, wj = valores[3 + 5 * i : 8 + 5 * i]
        xy.append((x, y))
        p.append(pj)
        d.append(dj)
        w.append(wj)

    T = tuple(tuple(tempo_deslocamento(a, b) for b in xy) for a in xy)
    return Instance(
        nome=nome or caminho.stem.removeprefix("manutencao_"),
        n=n,
        xy=tuple(xy),
        p=tuple(p),
        d=tuple(d),
        w=tuple(w),
        T=T,
    )


def load_named(nome: str) -> Instance:
    """Atalho para as três instâncias do enunciado: ``pequena``, ``media`` ou ``grande``."""
    return load_instance(INSTANCIAS[nome], nome)
