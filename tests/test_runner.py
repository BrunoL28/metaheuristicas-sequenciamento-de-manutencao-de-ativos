import csv
import json

from tp2.experiments import configs
from tp2.experiments.runner import COLUNAS, executar, main, montar_jobs


def _ler(caminho):
    with caminho.open(newline="") as f:
        return list(csv.DictReader(f))


def test_sementes_seguem_a_regra():
    jobs = montar_jobs("t2", list(configs.INSTANCIAS))
    assert len(jobs) == 3 * (30 + 30 + 10)
    for job in jobs:
        indice = configs.INSTANCIAS.index(job["instancia"])
        assert job["seed"] == configs.BASE_SEED + 1000 * indice + job["run"]
        assert job["orcamento"] == configs.ORCAMENTO[job["instancia"]]
    assert len({j["run_id"] for j in jobs}) == len(jobs)


def test_executar_confere_as_invariantes():
    job = montar_jobs("t2", ["pequena"], max_execucoes=1, orcamento=800)[0]
    resultado = executar(job)
    linha = resultado["linha"]
    assert resultado["erro"] is None
    assert linha["status"] == "ok"
    assert linha["evals"] == 800
    assert set(COLUNAS) == set(linha)
    assert resultado["curva"][-1][1] == linha["best_h"]
    assert resultado["tabelas"]["otimos_locais"]


def test_fim_a_fim_com_resume(tmp_path):
    pasta = tmp_path / "t2"
    args = ["--suite", "t2", "--out", str(pasta), "--instancias", "pequena"]
    args += ["--max-execucoes", "2", "--orcamento", "500", "--jobs", "1"]
    assert main(args) == 0
    runs = _ler(pasta / "runs.csv")
    assert len(runs) == 6
    assert all(r["status"] == "ok" and r["evals"] == "500" for r in runs)

    # Sem --resume, a pasta não é sobrescrita.
    assert main(args) == 2

    # Simula uma interrupção: some a última linha e sobra telemetria órfã.
    with (pasta / "runs.csv").open("w", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(runs[:-1])
    assert main([*args, "--resume"]) == 0

    refeitos = _ler(pasta / "runs.csv")
    assert sorted(r["run_id"] for r in refeitos) == sorted(r["run_id"] for r in runs)
    perdido = runs[-1]
    novo = next(r for r in refeitos if r["run_id"] == perdido["run_id"])
    assert novo["best_h"] == perdido["best_h"]
    assert novo["best_perm"] == perdido["best_perm"]

    # A telemetria da execução refeita aparece uma vez só.
    curvas = _ler(pasta / "curvas.csv")
    da_refeita = [c for c in curvas if c["run_id"] == perdido["run_id"]]
    assert da_refeita[-1]["best_h"] == perdido["best_h"]
    assert len({c["evals"] for c in da_refeita}) == len(da_refeita)

    config = json.loads((pasta / "config.json").read_text())
    assert config["orcamento"] == {"pequena": 500}
    assert len(config["retomadas"]) == 1
