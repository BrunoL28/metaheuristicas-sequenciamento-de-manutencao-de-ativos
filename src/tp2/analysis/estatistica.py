"""Estatística descritiva e testes não paramétricos (enunciado, Seção 3).

- Mann–Whitney bilateral entre duas configurações (amostras independentes).
- Correção de Holm sobre a família de comparações de cada instância.
- Tamanho de efeito A12 de Vargha e Delaney: a probabilidade de uma execução
  de X ter h menor (melhor) que uma de Y, contando empates como meio.
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence

from scipy.stats import mannwhitneyu

ALFA = 0.05


def descrever(valores: Sequence[float]) -> dict:
    return {
        "n": len(valores),
        "media": statistics.fmean(valores),
        "dp": statistics.stdev(valores) if len(valores) > 1 else 0.0,
        "min": min(valores),
        "mediana": statistics.median(valores),
        "max": max(valores),
    }


def mann_whitney(x: Sequence[float], y: Sequence[float]) -> tuple[float, float]:
    """Estatística U de x e p-valor bilateral.

    Se todos os valores das duas amostras são iguais (ex.: todas as execuções
    acharam o ótimo), não há diferença a testar e p = 1.
    """
    if len(set(x) | set(y)) == 1:
        return len(x) * len(y) / 2, 1.0
    r = mannwhitneyu(x, y, alternative="two-sided", method="auto")
    return float(r.statistic), float(r.pvalue)


def holm(pvalores: Sequence[float]) -> list[float]:
    """p-valores ajustados por Holm (step-down), na ordem original."""
    m = len(pvalores)
    ordem = sorted(range(m), key=lambda i: pvalores[i])
    ajustados = [0.0] * m
    corrente = 0.0
    for posicao, i in enumerate(ordem):
        corrente = max(corrente, min(1.0, (m - posicao) * pvalores[i]))
        ajustados[i] = corrente
    return ajustados


def a12(x: Sequence[float], y: Sequence[float]) -> float:
    """P(h de X < h de Y) + 0,5 · P(empate). 0,5 = sem diferença; > 0,5 = X melhor."""
    vitorias = sum((a < b) + 0.5 * (a == b) for a in x for b in y)
    return vitorias / (len(x) * len(y))


def comparar(grupos: dict[str, Sequence[float]], pares: list[tuple[str, str]]) -> list[dict]:
    """Testa cada par e corrige por Holm dentro da família ``pares``."""
    linhas = []
    for a, b in pares:
        u, p = mann_whitney(grupos[a], grupos[b])
        linhas.append({"a": a, "b": b, "U": u, "p": p, "A12": a12(grupos[a], grupos[b])})
    for linha, p_holm in zip(linhas, holm([lin["p"] for lin in linhas]), strict=True):
        linha["p_holm"] = p_holm
        if p_holm >= ALFA:
            linha["melhor"] = None
        else:
            linha["melhor"] = linha["a"] if linha["A12"] > 0.5 else linha["b"]
    return linhas
