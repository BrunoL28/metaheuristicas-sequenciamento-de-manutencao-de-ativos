"""Telemetria dos algoritmos, separada da contagem de avaliações.

Os algoritmos registram eventos (ótimos locais da descida, janelas de
aceitação do SA, gerações do AG) num ``Recorder``. O runner depois grava cada
tabela num CSV próprio. Registrar não avalia nada e não gasta orçamento.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Sequence


def assinatura(s: Sequence[int]) -> str:
    """Identificador curto e estável de uma permutação (para contar ótimos distintos)."""
    return hashlib.blake2b(",".join(map(str, s)).encode(), digest_size=8).hexdigest()


class Recorder:
    def __init__(self) -> None:
        self.tabelas: dict[str, list[dict]] = defaultdict(list)

    def registrar(self, tabela: str, **campos) -> None:
        self.tabelas[tabela].append(campos)
