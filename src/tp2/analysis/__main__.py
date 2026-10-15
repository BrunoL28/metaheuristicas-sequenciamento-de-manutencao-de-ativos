"""Gera todas as tabelas e figuras do relatório a partir de ``results/LATEST_*``.

Uso: ``uv run python -m tp2.analysis [--tabelas DIR] [--figuras DIR]``
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tp2.analysis import figuras, tabelas
from tp2.problem.instance import RAIZ_PROJETO


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tabelas", type=Path, default=RAIZ_PROJETO / "relatorio" / "tabelas")
    ap.add_argument("--figuras", type=Path, default=RAIZ_PROJETO / "relatorio" / "figuras")
    args = ap.parse_args(argv)
    for caminho in tabelas.gerar(args.tabelas) + figuras.gerar(args.figuras):
        print(
            caminho.relative_to(RAIZ_PROJETO) if caminho.is_relative_to(RAIZ_PROJETO) else caminho
        )


if __name__ == "__main__":
    main()
