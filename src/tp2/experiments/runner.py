"""Executa uma suíte de experimentos em paralelo e grava os resultados em CSV.

Cada execução monta o problema, envolve-o no ``CountingProblem`` com o
orçamento B da instância, roda o algoritmo com ``random.Random(seed)`` e, ao
final, confere duas invariantes:

- foram feitas exatamente B avaliações;
- a melhor permutação, reavaliada por um problema novo (sem contador), tem
  o mesmo h registrado e é de fato uma permutação de 1..n.

``wall_s`` é o tempo de parede da execução sem a telemetria que o algoritmo
declara (``s_telemetria`` no resumo, hoje só no AG), para que o tempo
comparado seja o da busca.

Se algo falhar, a linha sai com ``status=error`` e o traceback vai para
``erros.txt``. As linhas são gravadas (com flush) assim que cada execução
termina; ``--resume`` pula as execuções que já têm ``status=ok``.

Arquivos na pasta de saída:

- ``runs.csv``: uma linha por execução;
- ``curvas.csv``: cada melhoria do melhor global (run_id, evals, best_h);
- um CSV por tabela de telemetria do algoritmo (``otimos_locais.csv`` na
  descida gulosa, ``sa_aceitacao.csv`` no SA, ``ag_geracoes.csv`` no AG);
- ``config.json``: parâmetros, commit, versão do Python e máquina.

Uso: ``uv run python -m tp2.experiments.runner --suite t2 --out results/<data>_t2``
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import random
import subprocess
import sys
import time
import traceback
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

from tp2.algorithms.genetic import algoritmo_genetico
from tp2.algorithms.greedy_descent import descida_gulosa
from tp2.algorithms.simulated_annealing import alfa_para_orcamento, simulated_annealing
from tp2.core.counting import CountingProblem
from tp2.core.recorder import Recorder
from tp2.experiments import calibrate_sa, configs
from tp2.problem.instance import RAIZ_PROJETO, load_named
from tp2.problem.maintenance import MaintenanceProblem

ALGORITMOS = {"gd": descida_gulosa, "sa": simulated_annealing, "ag": algoritmo_genetico}

COLUNAS = [
    "run_id",
    "suite",
    "algoritmo",
    "variante",
    "vizinhanca",
    "rotulo",
    "instancia",
    "n",
    "run",
    "seed",
    "orcamento",
    "evals",
    "best_h",
    "ref_h",
    "gap",
    "wall_s",
    "passos",
    "descidas",
    "otimos_locais",
    "otimos_distintos",
    "resumo",
    "params",
    "best_perm",
    "git_commit",
    "status",
]


def run_id(job: dict) -> str:
    partes = [job["algoritmo"], job["variante"], job["vizinhanca"], job["instancia"]]
    if job.get("rotulo"):
        partes.insert(3, job["rotulo"])
    return "-".join(partes) + f"-{job['run']:02d}"


def montar_jobs(
    suite: str,
    instancias: list[str],
    max_execucoes: int | None = None,
    orcamento: int | None = None,
    base_seed: int = configs.BASE_SEED,
) -> list[dict]:
    jobs = []
    for cel in configs.celulas(suite):
        for inst in instancias:
            execucoes = configs.EXECUCOES[inst]
            if max_execucoes is not None:
                execucoes = min(execucoes, max_execucoes)
            orcamento_inst = orcamento or configs.ORCAMENTO[inst]
            params = _parametros(cel, inst, orcamento_inst)
            for run in range(execucoes):
                job = {
                    "suite": suite,
                    "algoritmo": cel.algoritmo,
                    "variante": cel.variante,
                    "vizinhanca": cel.vizinhanca,
                    "rotulo": cel.rotulo,
                    "params": params,
                    "instancia": inst,
                    "run": run,
                    "seed": configs.semente(inst, run, base_seed),
                    "orcamento": orcamento_inst,
                }
                job["run_id"] = run_id(job)
                jobs.append(job)
    # As execuções mais caras primeiro, para equilibrar a carga entre processos.
    jobs.sort(key=lambda j: -j["orcamento"])
    return jobs


def _parametros(cel: configs.Celula, instancia: str, orcamento: int) -> dict:
    """Parâmetros da célula, completados com os que dependem da instância e de B."""
    params = dict(cel.params)
    if cel.algoritmo == "ag":
        # Os parâmetros da célula (ex.: Pc = 0 no experimento extra) têm precedência.
        params = {**configs.AG[instancia], **params}
    if cel.algoritmo == "sa":
        cal = calibrate_sa.carregar(instancia)
        if cal["vizinhanca"] != cel.vizinhanca:
            raise ValueError(
                f"configs/sa_{instancia}.json foi calibrado com {cal['vizinhanca']}, "
                f"não {cel.vizinhanca}; rode make calibrate"
            )
        params.update(
            T0=cal["T0"],
            Tf=cal["Tf"],
            L=cal["L"],
            alfa=alfa_para_orcamento(cal["T0"], cal["Tf"], orcamento, cal["L"]),
            janela=max(1, orcamento // 100),
        )
    return params


def executar(job: dict) -> dict:
    """Roda uma execução e devolve a linha do ``runs.csv`` e a telemetria."""
    inst = load_named(job["instancia"])
    problema = CountingProblem(MaintenanceProblem(inst, job["vizinhanca"]), budget=job["orcamento"])
    rng = random.Random(job["seed"])
    rec = Recorder()
    resumo: dict = {}
    erro = None
    inicio = time.perf_counter()
    try:
        algoritmo = ALGORITMOS[job["algoritmo"]]
        resumo = algoritmo(problema, rng, variante=job["variante"], rec=rec, **job["params"])
    except Exception:
        erro = traceback.format_exc()
    wall = time.perf_counter() - inicio

    best_s = problema.best_s
    if erro is None:
        erro = _conferir(inst, problema, job["orcamento"])

    ref = configs.REFERENCIA[job["instancia"]]
    linha = {
        "run_id": job["run_id"],
        "suite": job["suite"],
        "algoritmo": job["algoritmo"],
        "variante": job["variante"],
        "vizinhanca": job["vizinhanca"],
        "rotulo": job["rotulo"],
        "instancia": job["instancia"],
        "n": inst.n,
        "run": job["run"],
        "seed": job["seed"],
        "orcamento": job["orcamento"],
        "evals": problema.evals,
        "best_h": problema.best_h if best_s is not None else "",
        "ref_h": ref,
        "gap": round((problema.best_h - ref) / ref, 6) if best_s is not None else "",
        "wall_s": round(wall - resumo.get("s_telemetria", 0.0), 3),
        "params": json.dumps(job["params"], sort_keys=True),
        "best_perm": " ".join(map(str, best_s)) if best_s is not None else "",
        "git_commit": job.get("git_commit", ""),
        "status": "ok" if erro is None else "error",
    }
    for chave in ("passos", "descidas", "otimos_locais", "otimos_distintos"):
        linha[chave] = resumo.get(chave, "")
    linha["resumo"] = json.dumps(resumo, sort_keys=True)
    return {
        "linha": linha,
        "curva": problema.improvements,
        "tabelas": dict(rec.tabelas),
        "erro": erro,
    }


def _conferir(inst, problema: CountingProblem, orcamento: int) -> str | None:
    if problema.evals != orcamento:
        return f"evals = {problema.evals}, esperado {orcamento}"
    s = problema.best_s
    if s is None or sorted(s) != list(range(1, inst.n + 1)):
        return f"best_perm não é uma permutação de 1..{inst.n}: {s}"
    h_novo = MaintenanceProblem(inst).h(s)
    if h_novo != problema.best_h:
        return f"h(best_perm) reavaliado = {h_novo}, registrado {problema.best_h}"
    return None


# --- escrita incremental dos resultados ---


class Saida:
    """Grava os resultados à medida que as execuções terminam."""

    def __init__(self, pasta: Path):
        self.pasta = pasta
        self._escritores: dict[str, tuple] = {}

    def _escritor(self, nome: str, colunas: list[str]):
        if nome not in self._escritores:
            caminho = self.pasta / f"{nome}.csv"
            novo = not caminho.exists()
            if not novo:
                with caminho.open(newline="") as f:
                    colunas = next(csv.reader(f))
            arquivo = caminho.open("a", newline="")
            escritor = csv.DictWriter(arquivo, fieldnames=colunas)
            if novo:
                escritor.writeheader()
            self._escritores[nome] = (arquivo, escritor)
        return self._escritores[nome]

    def gravar(self, resultado: dict) -> None:
        rid = resultado["linha"]["run_id"]
        # Telemetria antes da linha principal: se o processo morrer no meio,
        # o --resume descarta a telemetria órfã (sem linha em runs.csv).
        arquivo, escritor = self._escritor("curvas", ["run_id", "evals", "best_h"])
        escritor.writerows({"run_id": rid, "evals": e, "best_h": h} for e, h in resultado["curva"])
        arquivo.flush()
        for tabela, linhas in resultado["tabelas"].items():
            if not linhas:
                continue
            arquivo, escritor = self._escritor(tabela, ["run_id", *linhas[0]])
            escritor.writerows({"run_id": rid, **linha} for linha in linhas)
            arquivo.flush()
        if resultado["erro"]:
            with (self.pasta / "erros.txt").open("a") as f:
                f.write(f"=== {rid}\n{resultado['erro']}\n")
        arquivo, escritor = self._escritor("runs", COLUNAS)
        escritor.writerow(resultado["linha"])
        arquivo.flush()

    def fechar(self) -> None:
        for arquivo, _ in self._escritores.values():
            arquivo.close()


def concluidos(pasta: Path) -> set[str]:
    """Para o --resume: mantém só as execuções ok e a telemetria delas."""
    runs = pasta / "runs.csv"
    if not runs.exists():
        return set()
    with runs.open(newline="") as f:
        linhas = list(csv.DictReader(f))
    ok = {linha["run_id"] for linha in linhas if linha["status"] == "ok"}
    for caminho in pasta.glob("*.csv"):
        with caminho.open(newline="") as f:
            leitor = csv.DictReader(f)
            colunas = leitor.fieldnames or []
            if "run_id" not in colunas:
                continue
            manter = [linha for linha in leitor if linha["run_id"] in ok]
        with caminho.open("w", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=colunas)
            escritor.writeheader()
            escritor.writerows(manter)
    return ok


def commit_atual() -> str:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=RAIZ_PROJETO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        sujo = subprocess.run(
            ["git", "status", "--porcelain", "--", "src", "configs", "pyproject.toml", "uv.lock"],
            cwd=RAIZ_PROJETO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconhecido"
    return f"{commit}-dirty" if sujo else commit


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--suite", choices=configs.SUITES, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--base-seed", type=int, default=configs.BASE_SEED)
    ap.add_argument("--instancias", nargs="+", choices=configs.INSTANCIAS)
    ap.add_argument("--max-execucoes", type=int, help="limita as execuções por instância (pilotos)")
    ap.add_argument("--orcamento", type=int, help="substitui B em todas as instâncias (pilotos)")
    args = ap.parse_args(argv)

    pasta: Path = args.out
    if (pasta / "runs.csv").exists() and not args.resume:
        print(f"{pasta} já tem resultados; use outra pasta ou --resume", file=sys.stderr)
        return 2
    pasta.mkdir(parents=True, exist_ok=True)

    instancias = args.instancias or list(configs.INSTANCIAS)
    jobs = montar_jobs(args.suite, instancias, args.max_execucoes, args.orcamento, args.base_seed)
    commit = commit_atual()
    for job in jobs:
        job["git_commit"] = commit

    feitos = concluidos(pasta) if args.resume else set()
    pendentes = [j for j in jobs if j["run_id"] not in feitos]

    _gravar_config(pasta, args, instancias, commit, len(jobs), len(pendentes))
    print(f"{args.suite}: {len(pendentes)} de {len(jobs)} execuções, {args.jobs} processos")

    saida = Saida(pasta)
    erros = 0
    inicio = time.perf_counter()
    try:
        if args.jobs == 1:
            resultados = map(executar, pendentes)
        else:
            pool = Pool(args.jobs)
            resultados = pool.imap_unordered(executar, pendentes, chunksize=1)
        for k, resultado in enumerate(resultados, 1):
            saida.gravar(resultado)
            linha = resultado["linha"]
            erros += linha["status"] != "ok"
            print(
                f"[{k}/{len(pendentes)}] {linha['run_id']}: h = {linha['best_h']} "
                f"({linha['wall_s']} s) {linha['status']}",
                flush=True,
            )
        if args.jobs != 1:
            pool.close()
            pool.join()
    finally:
        saida.fechar()
    print(f"concluído em {time.perf_counter() - inicio:.1f} s; {erros} erro(s)")
    return 1 if erros else 0


def _gravar_config(pasta, args, instancias, commit, total, pendentes) -> None:
    caminho = pasta / "config.json"
    agora = datetime.now().isoformat(timespec="seconds")
    if caminho.exists():
        config = json.loads(caminho.read_text())
        config.setdefault("retomadas", []).append(
            {"data": agora, "git_commit": commit, "pendentes": pendentes}
        )
    else:
        config = {
            "suite": args.suite,
            "data": agora,
            "git_commit": commit,
            "base_seed": args.base_seed,
            "regra_seed": "base_seed + 1000 * indice_instancia + run",
            "instancias": instancias,
            "orcamento": {i: args.orcamento or configs.ORCAMENTO[i] for i in instancias},
            "execucoes": {
                i: min(configs.EXECUCOES[i], args.max_execucoes or configs.EXECUCOES[i])
                for i in instancias
            },
            "celulas": [
                {
                    "algoritmo": c.algoritmo,
                    "variante": c.variante,
                    "vizinhanca": c.vizinhanca,
                    "rotulo": c.rotulo,
                    "params": c.params,
                }
                for c in configs.celulas(args.suite)
            ],
            "total_execucoes": total,
            "processos": args.jobs,
            "python": sys.version.split()[0],
            "plataforma": platform.platform(),
            "processador": platform.processor() or platform.machine(),
            "cpus": os.cpu_count(),
        }
    caminho.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    sys.exit(main())
