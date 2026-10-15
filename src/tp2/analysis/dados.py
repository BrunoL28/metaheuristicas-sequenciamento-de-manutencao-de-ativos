"""Leitura das pastas de resultados e nomes de exibição das configurações."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from tp2.problem.instance import RAIZ_PROJETO

RESULTADOS = RAIZ_PROJETO / "results"

NOME_INSTANCIA = {"pequena": "pequena", "media": "média", "grande": "grande"}
N_INSTANCIA = {"pequena": 12, "media": 50, "grande": 150}

# Nomes curtos usados nas tabelas e figuras.
NOME_AG = {
    "ox": "AG-OX",
    "pmx": "AG-PMX",
    "so-mutacao": "AG só mutação",
    "memetico": "AG memético",
}


def pasta_atual(nome: str) -> Path:
    """Pasta apontada por ``results/LATEST_<NOME>``."""
    return RESULTADOS / (RESULTADOS / f"LATEST_{nome}").read_text().strip()


def ler_csv(caminho: Path) -> list[dict]:
    with caminho.open(newline="") as f:
        return list(csv.DictReader(f))


def config(linha: dict) -> str:
    """Nome de exibição da configuração de uma execução."""
    # Pastas anteriores à M5 não têm a coluna "rotulo".
    alg, variante, rotulo = linha["algoritmo"], linha["variante"], linha.get("rotulo", "")
    sufixo = {"2B": " (2B)", "B-calibracao": " (B − calib.)"}.get(rotulo, "")
    if alg == "gd":
        return f"GD-{variante}{sufixo}"
    if alg == "sa":
        return f"SA{sufixo}"
    if variante == "headless":
        return "AG headless"
    return NOME_AG.get(rotulo, "AG") + sufixo


def runs(pasta: Path) -> list[dict]:
    """Execuções ok de uma pasta, com os campos numéricos convertidos."""
    saida = []
    for linha in ler_csv(pasta / "runs.csv"):
        if linha["status"] != "ok":
            continue
        for campo in ("n", "run", "seed", "orcamento", "evals", "best_h", "ref_h"):
            linha[campo] = int(linha[campo])
        linha["wall_s"] = float(linha["wall_s"])
        linha["resumo"] = json.loads(linha["resumo"]) if linha.get("resumo") else {}
        linha["params"] = json.loads(linha["params"])
        linha["config"] = config(linha)
        saida.append(linha)
    return saida


def agrupar(linhas: list[dict], *campos: str) -> dict[tuple, list[dict]]:
    grupos: dict[tuple, list[dict]] = defaultdict(list)
    for linha in linhas:
        grupos[tuple(linha[c] for c in campos)].append(linha)
    return grupos


def melhores(linhas: list[dict]) -> list[int]:
    return [linha["best_h"] for linha in linhas]


def curvas(pasta: Path) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Por execução: avaliações em que o melhor global melhorou e o h nesse ponto."""
    brutas: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for linha in ler_csv(pasta / "curvas.csv"):
        brutas[linha["run_id"]].append((int(linha["evals"]), int(linha["best_h"])))
    return {
        rid: (np.array([e for e, _ in pts]), np.array([h for _, h in pts]))
        for rid, pts in brutas.items()
    }


def em_grade(evals: np.ndarray, valores: np.ndarray, grade: np.ndarray) -> np.ndarray:
    """Função degrau: o último valor registrado até cada ponto da grade (NaN antes do 1º)."""
    idx = np.searchsorted(evals, grade, side="right") - 1
    saida = np.where(idx >= 0, valores[np.clip(idx, 0, None)], np.nan)
    return saida.astype(float)


def tabela_telemetria(pasta: Path, nome: str) -> dict[str, list[dict]]:
    """Linhas de uma tabela de telemetria (ex.: ``ag_geracoes``) por execução."""
    por_run: dict[str, list[dict]] = defaultdict(list)
    caminho = pasta / f"{nome}.csv"
    if caminho.exists():
        for linha in ler_csv(caminho):
            por_run[linha["run_id"]].append(linha)
    return por_run
