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
        chave = (
            linha["instancia"],
            linha["algoritmo"],
            linha["variante"],
            linha["vizinhanca"],
            linha.get("rotulo", ""),
        )
        grupos[chave].append(linha)

    ordem_inst = {nome: k for k, nome in enumerate(configs.INSTANCIAS)}
    saida = []
    cabecalho = (
        f"{'instância':<9} {'config':<34} {'exec':>4} {'mín':>7} {'mediana':>9} "
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

        config = "/".join(c for c in chave[1:] if c)
        saida.append(
            f"{chave[0]:<9} {config:<34} {len(hs):>4} {min(hs):>7} "
            f"{statistics.median(hs):>9.1f} {statistics.fmean(hs):>9.1f} {max(hs):>7} "
            f"{sum(h <= ref for h in hs):>5} {media('passos'):>8} {media('otimos_locais'):>7} "
            f"{media('otimos_distintos'):>9} {media('wall_s'):>7}"
        )
    saida.append("")
    saida.append(
        "≤ ref: execuções que atingiram ou superaram o valor de referência da Tabela 1. "
        "passos, ót.loc, distintos e s/exec são médias por execução."
    )
    por_id = {linha["run_id"]: linha for linha in linhas}
    if (pasta / "sa_aceitacao.csv").exists():
        saida += ["", *_aceitacao_sa(pasta, por_id)]
    if (pasta / "ag_geracoes.csv").exists():
        saida += ["", *_diversidade_ag(pasta, por_id)]
    return "\n".join(saida)


FRACOES_AG = (0.0, 0.01, 0.1, 0.25, 0.5, 1.0)


def _diversidade_ag(pasta: Path, runs: dict[str, dict]) -> list[str]:
    """Mediana entre execuções da diversidade em frações do total de gerações."""
    series: dict[str, list[dict]] = defaultdict(list)
    with (pasta / "ag_geracoes.csv").open(newline="") as f:
        for linha in csv.DictReader(f):
            if linha["run_id"] in runs:
                series[linha["run_id"]].append(linha)
    saida = []
    for campo, titulo in (
        ("distintos", "AG: permutações distintas na população"),
        ("distancia_media", "AG: distância média entre pares (posições)"),
        ("media_h", "AG: h médio da população"),
    ):
        cabecalho = f"{titulo + ' (mediana)':<52}" + "".join(
            f"{f'{fr:.0%}':>9}" for fr in FRACOES_AG
        )
        saida += [cabecalho, "-" * len(cabecalho)]
        for inst in configs.INSTANCIAS:
            ids = [rid for rid in series if runs[rid]["instancia"] == inst]
            if not ids:
                continue
            valores = []
            for fr in FRACOES_AG:
                pontos = []
                for rid in ids:
                    serie = series[rid]
                    pontos.append(float(serie[round(fr * (len(serie) - 1))][campo]))
                valores.append(f"{statistics.median(pontos):>9.1f}")
            saida.append(f"{inst:<52}" + "".join(valores))
        saida.append("")
    saida.append("Colunas: fração das gerações completadas (0% = população inicial).")
    return saida


JANELAS_MOSTRADAS = (1, 10, 25, 50, 75, 90, 100)


def _aceitacao_sa(pasta: Path, runs: dict[str, dict]) -> list[str]:
    """Mediana entre execuções da taxa de aceitação de pioras em algumas janelas."""
    taxas: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    contador: dict[str, int] = defaultdict(int)
    with (pasta / "sa_aceitacao.csv").open(newline="") as f:
        for linha in csv.DictReader(f):
            rid = linha["run_id"]
            if rid not in runs:
                continue
            contador[rid] += 1
            if linha["taxa"] != "":
                taxas[runs[rid]["instancia"]][contador[rid]].append(float(linha["taxa"]))
    cabecalho = f"{'SA: aceitação de pioras (mediana) na janela':<45}" + "".join(
        f"{k:>7}" for k in JANELAS_MOSTRADAS
    )
    saida = [cabecalho, "-" * len(cabecalho)]
    for inst in configs.INSTANCIAS:
        if inst not in taxas:
            continue
        valores = [
            f"{statistics.median(taxas[inst][k]):>7.3f}" if taxas[inst][k] else f"{'-':>7}"
            for k in JANELAS_MOSTRADAS
        ]
        saida.append(f"{inst:<45}" + "".join(valores))
    saida.append("Cada janela tem B/100 passos; a janela 1 é o início da execução e a 100, o fim.")
    return saida


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pasta", type=Path)
    args = ap.parse_args()
    print(resumir(args.pasta))


if __name__ == "__main__":
    main()
