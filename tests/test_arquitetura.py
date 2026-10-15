"""Seção 2.1 do enunciado: o algoritmo não pode conhecer o problema."""

import ast
from pathlib import Path

PASTA_ALGORITMOS = Path(__file__).resolve().parents[1] / "src" / "tp2" / "algorithms"


def _imports(arquivo: Path) -> set[str]:
    modulos = set()
    for no in ast.walk(ast.parse(arquivo.read_text())):
        if isinstance(no, ast.Import):
            modulos.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            modulos.add(no.module)
    return modulos


def test_algoritmos_nao_importam_o_problema():
    arquivos = sorted(PASTA_ALGORITMOS.glob("*.py"))
    assert arquivos, "pasta de algoritmos vazia"
    for arquivo in arquivos:
        proibidos = {
            m for m in _imports(arquivo) if m == "tp2.problem" or m.startswith("tp2.problem.")
        }
        assert not proibidos, f"{arquivo.name} importa {proibidos}"
