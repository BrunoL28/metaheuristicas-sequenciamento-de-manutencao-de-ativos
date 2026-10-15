"""Formatação de números e tabelas LaTeX (convenções do português)."""

from __future__ import annotations

import math
from pathlib import Path


def num(x: float, casas: int = 0) -> str:
    """1234567.8 → '1\\,234\\,567,8' (espaço fino nos milhares, vírgula decimal)."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "--"
    texto = f"{abs(x):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", "\\,")
    negativo = x < 0 and texto.strip("0,\\") != ""
    return f"$-${texto}" if negativo else texto


def pct(x: float, casas: int = 1) -> str:
    return num(100 * x, casas) + "\\%"


def pvalor(p: float) -> str:
    if p >= 0.001:
        return num(p, 3)
    expoente = math.floor(math.log10(p))
    mantissa = p / 10**expoente
    return f"${num(mantissa, 1)}\\times10^{{{expoente}}}$"


def tabular(colunas: str, cabecalho: list[str], linhas: list[list[str]], grupos=None) -> str:
    """Um ``tabular`` com booktabs. ``grupos`` = índices de linha antes dos quais vai um midrule."""
    grupos = set(grupos or [])
    saida = [f"\\begin{{tabular}}{{{colunas}}}", "\\toprule", " & ".join(cabecalho) + " \\\\"]
    saida.append("\\midrule")
    for k, linha in enumerate(linhas):
        if k in grupos and k > 0:
            saida.append("\\midrule")
        saida.append(" & ".join(linha) + " \\\\")
    saida += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(saida)


def gravar(pasta: Path, nome: str, conteudo: str) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / nome
    cabecalho = "% Gerado por `make analysis` (tp2.analysis). Não editar à mão.\n"
    caminho.write_text(cabecalho + conteudo)
    return caminho
