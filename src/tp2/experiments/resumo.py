"""Resumo textual de uma pasta de resultados (por instância e configuração).

Não substitui as tabelas do relatório (``tp2.analysis``); serve para conferir
uma suíte logo depois de rodar e para justificar decisões intermediárias, como
a escolha da vizinhança no T2.

Uso: ``uv run python -m tp2.experiments.resumo results/<pasta>``
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

from tp2.experiments import configs


def _num(valor: str) -> float | None:
    return float(valor) if valor not in ("", None) else None


def resumir(pasta: Path) -> str:
    with (pasta / "runs.csv").open(newline="") as f:
        linhas = [linha for linha in csv.DictReader(f) if linha["status"] == "ok"]

    grupos: dict[tuple, list[dict]] = defaultdict(list)
    for linha in linhas:
        chave = (linha["instancia"], linha["algoritmo"], linha["variante"], linha["vizinhanca"])
        grupos[chave].append(linha)

    ordem_inst = {nome: k for k, nome in enumerate(configs.INSTANCIAS)}
    saida = []
    cabecalho = (
        f"{'instância':<9} {'config':<20} {'exec':>4} {'mín':>7} {'mediana':>9} "
        f"{'média':>9} {'máx':>7} {'≤ ref':>5} {'passos':>8} {'ót.loc':>7} "
        f"{'distintos':>9} {'s/exec':>7}"
    )
    saida.append(cabecalho)
    saida.append("-" * len(cabecalho))
    for chave in sorted(grupos, key=lambda c: (ordem_inst[c[0]], c[1:])):
        grupo = grupos[chave]
        hs = [int(linha["best_h"]) for linha in grupo]
        ref = int(grupo[0]["ref_h"])

        def media(campo: str, grupo=grupo) -> str:
            valores = [v for linha in grupo if (v := _num(linha[campo])) is not None]
            return f"{statistics.fmean(valores):.1f}" if valores else "-"

        config = "/".join(chave[1:])
        saida.append(
            f"{chave[0]:<9} {config:<20} {len(hs):>4} {min(hs):>7} "
            f"{statistics.median(hs):>9.1f} {statistics.fmean(hs):>9.1f} {max(hs):>7} "
            f"{sum(h <= ref for h in hs):>5} {media('passos'):>8} {media('otimos_locais'):>7} "
            f"{media('otimos_distintos'):>9} {media('wall_s'):>7}"
        )
    saida.append("")
    saida.append(
        "≤ ref: execuções que atingiram ou superaram o valor de referência da Tabela 1. "
        "passos, ót.loc, distintos e s/exec são médias por execução."
    )
    return "\n".join(saida)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pasta", type=Path)
    args = ap.parse_args()
    print(resumir(args.pasta))


if __name__ == "__main__":
    main()
