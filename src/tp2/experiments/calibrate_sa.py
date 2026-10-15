"""Calibração do simulated annealing por instância (T0, Tf, L e α).

O Δh típico cresce com n (dezenas na pequena, milhares na grande), então uma
temperatura fixa não serve para as três instâncias. Aqui o que se mantém
constante é o perfil de aceitação:

- sorteia pares (permutação aleatória, sucessor aleatório) e guarda os
  Δ > 0 (as pioras);
- T0 = −mediana / ln(χ0), com χ0 = 0,9: uma piora típica é aceita com
  probabilidade 0,9 no início;
- Tf = −q10 / ln(χf), com χf = 10⁻³: até as pioras pequenas (10º percentil)
  quase nunca são aceitas no fim. Perto de ótimos locais as pioras são
  maiores que essas, então lá a aceitação final é ainda menor;
- L fixo por instância; α sai de T0, Tf, L e do orçamento B.

Uma versão anterior tirava o q10 de sucessores de ótimos locais. Isso exigia
descidas completas (mais de 150 mil avaliações por ótimo na grande) e, num
piloto com sementes fora do protocolo, não melhorou o SA (decisão em
CONTEXT §8). A calibração é ajuste de hiperparâmetro feito uma vez, fora das
execuções: as avaliações gastas aqui não entram no orçamento das execuções e
ficam registradas no JSON para o relatório declarar o custo.

Uso: ``uv run python -m tp2.experiments.calibrate_sa`` → ``configs/sa_<instância>.json``
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from pathlib import Path

from tp2.algorithms.simulated_annealing import alfa_para_orcamento
from tp2.core.counting import CountingProblem
from tp2.experiments import configs
from tp2.problem.instance import RAIZ_PROJETO, load_named
from tp2.problem.maintenance import MaintenanceProblem

CHI0 = 0.9
CHIF = 1e-3
PATAMAR = {"pequena": 100, "media": 300, "grande": 1000}
AMOSTRAS = 2000
SEED = configs.BASE_SEED + 777
PASTA = RAIZ_PROJETO / "configs"


def _quantil(valores, q):
    return statistics.quantiles(valores, n=100, method="inclusive")[round(q * 100) - 1]


def calibrar(instancia: str, seed: int = SEED) -> dict:
    inst = load_named(instancia)
    # Orçamento "infinito": o invólucro aqui serve só para contar o custo.
    problema = CountingProblem(MaintenanceProblem(inst, configs.VIZINHANCA), budget=10**12)
    rng = random.Random(seed)

    pioras = []
    for _ in range(AMOSTRAS):
        s = problema.solucao_aleatoria(rng)
        hs = problema.h(s)
        _, hv = problema.sucessor_aleatorio(s, hs, rng)
        if hv > hs:
            pioras.append(hv - hs)
    mediana = statistics.median(pioras)
    q10 = _quantil(pioras, 0.10)
    T0 = -mediana / math.log(CHI0)
    Tf = -q10 / math.log(CHIF)

    L = PATAMAR[instancia]
    orcamento = configs.ORCAMENTO[instancia]
    return {
        "instancia": instancia,
        "vizinhanca": configs.VIZINHANCA,
        "T0": T0,
        "Tf": Tf,
        "L": L,
        "alfa": alfa_para_orcamento(T0, Tf, orcamento, L),
        "orcamento": orcamento,
        "chi0": CHI0,
        "chif": CHIF,
        "mediana_piora": mediana,
        "q10_piora": q10,
        "pares_sorteados": AMOSTRAS,
        "pioras": len(pioras),
        "avaliacoes_calibracao": problema.evals,
        "fracao_do_orcamento": problema.evals / orcamento,
        "seed": seed,
    }


def carregar(instancia: str, pasta: Path = PASTA) -> dict:
    return json.loads((pasta / f"sa_{instancia}.json").read_text())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--instancias", nargs="+", default=list(configs.INSTANCIAS))
    ap.add_argument("--pasta", type=Path, default=PASTA)
    args = ap.parse_args()
    args.pasta.mkdir(parents=True, exist_ok=True)
    print(
        f"{'instância':<9} {'mediana Δ+':>11} {'T0':>10} {'q10 Δ+':>8} {'Tf':>9} "
        f"{'L':>5} {'α':>10} {'avaliações':>11}"
    )
    for inst in args.instancias:
        c = calibrar(inst)
        (args.pasta / f"sa_{inst}.json").write_text(json.dumps(c, indent=2) + "\n")
        print(
            f"{inst:<9} {c['mediana_piora']:>11.1f} {c['T0']:>10.1f} "
            f"{c['q10_piora']:>8.1f} {c['Tf']:>9.2f} {c['L']:>5} {c['alfa']:>10.6f} "
            f"{c['avaliacoes_calibracao']:>11}"
        )


if __name__ == "__main__":
    main()
