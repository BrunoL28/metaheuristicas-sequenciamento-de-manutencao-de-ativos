"""Tabelas LaTeX do relatório (só o ``tabular``; legenda e rótulo ficam no .tex)."""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from tp2.analysis import dados
from tp2.analysis.estatistica import comparar, descrever
from tp2.analysis.formato import gravar, num, pct, pvalor, tabular
from tp2.experiments import configs
from tp2.problem.instance import RAIZ_PROJETO, load_named
from tp2.problem.maintenance import MaintenanceProblem

# Algoritmo (A) da tabela principal: a variante com a melhor mediana na média
# no T3 (CONTEXT §8). As três variantes aparecem em gd_variantes.tex.
ALGORITMO_A = "GD-random"
PRINCIPAIS = (ALGORITMO_A, "SA", "AG")
VARIANTES_GD = ("GD-best", "GD-first", "GD-random")
BRACOS_EXTRA = ("AG-OX", "AG-PMX", "AG só mutação", "AG headless", "AG memético")
INSTANCIAS = configs.INSTANCIAS


def _por_config(linhas: list[dict]) -> dict[tuple[str, str], list[int]]:
    return {
        chave: dados.melhores(grupo)
        for chave, grupo in dados.agrupar(linhas, "instancia", "config").items()
    }


def _media_dp(valores) -> str:
    d = descrever(valores)
    return f"{num(d['media'])} $\\pm$ {num(d['dp'])}"


def _mediana(valores) -> str:
    m = statistics.median(valores)
    return num(m, 1 if m % 1 else 0)


def _melhor(linha: dict) -> str:
    return linha["melhor"] if linha["melhor"] else "--"


def principal(t3: list[dict], tempos: list[dict]) -> str:
    h = _por_config(t3)
    t = {
        k: [r["wall_s"] for r in g] for k, g in dados.agrupar(tempos, "instancia", "config").items()
    }
    linhas, grupos = [], []
    for inst in INSTANCIAS:
        grupos.append(len(linhas))
        ref = configs.REFERENCIA[inst]
        for alg in PRINCIPAIS:
            v = h[(inst, alg)]
            d = descrever(v)
            linhas.append(
                [
                    dados.NOME_INSTANCIA[inst] if alg == PRINCIPAIS[0] else "",
                    alg,
                    _media_dp(v),
                    _mediana(v),
                    num(d["min"]),
                    pct((d["mediana"] - ref) / ref),
                    f"{sum(x <= ref for x in v)}/{len(v)}",
                    num(statistics.median(t[(inst, alg)]), 1),
                ]
            )
    return tabular(
        "llrrrrrr",
        [
            "Instância",
            "Algoritmo",
            "Média $\\pm$ dp",
            "Mediana",
            "Mínimo",
            "Gap (mediana)",
            "$h \\le h_{\\mathrm{ref}}$",
            "Tempo (s)",
        ],
        linhas,
        grupos,
    )


def _tabela_testes(familias: list[tuple[str, list[dict]]]) -> str:
    linhas, grupos = [], []
    for inst, testes in familias:
        grupos.append(len(linhas))
        for k, t in enumerate(testes):
            linhas.append(
                [
                    dados.NOME_INSTANCIA[inst] if k == 0 else "",
                    f"{t['a']} $\\times$ {t['b']}",
                    num(t["U"], 1 if t["U"] % 1 else 0),
                    pvalor(t["p"]),
                    pvalor(t["p_holm"]),
                    num(t["A12"], 2),
                    _melhor(t),
                ]
            )
    return tabular(
        "llrrrrl",
        ["Instância", "Comparação", "$U$", "$p$", "$p$ (Holm)", "$A_{12}$", "Melhor"],
        linhas,
        grupos,
    )


def testes(t3: list[dict]) -> str:
    h = _por_config(t3)
    a, sa, ag = PRINCIPAIS
    familias = []
    for inst in INSTANCIAS:
        grupos = {c: h[(inst, c)] for c in PRINCIPAIS}
        familias.append((inst, comparar(grupos, [(a, sa), (a, ag), (sa, ag)])))
    return _tabela_testes(familias)


def gd_variantes(t3: list[dict]) -> str:
    por = dados.agrupar(t3, "instancia", "config")
    h = _por_config(t3)
    linhas, grupos = [], []
    for inst in INSTANCIAS:
        grupos.append(len(linhas))
        testes_ = comparar(
            {c: h[(inst, c)] for c in VARIANTES_GD},
            [("GD-best", ALGORITMO_A), ("GD-first", ALGORITMO_A)],
        )
        p_holm = {t["a"]: t["p_holm"] for t in testes_}
        for var in VARIANTES_GD:
            grupo = por[(inst, var)]

            def media(campo, grupo=grupo):
                return statistics.fmean(r["resumo"][campo] for r in grupo)

            linhas.append(
                [
                    dados.NOME_INSTANCIA[inst] if var == VARIANTES_GD[0] else "",
                    var.removeprefix("GD-"),
                    num(media("passos"), 1),
                    num(media("descidas"), 1),
                    num(media("otimos_locais"), 1),
                    _mediana(h[(inst, var)]),
                    pvalor(p_holm[var]) if var in p_holm else "--",
                ]
            )
    return tabular(
        "llrrrrr",
        [
            "Instância",
            "Variante",
            "Passos de melhoria",
            "Descidas",
            "Ótimos locais",
            "Mediana de $h$",
            f"$p$ (Holm) vs.\\ {ALGORITMO_A.removeprefix('GD-')}",
        ],
        linhas,
        grupos,
    )


TAMANHO_FORMULA = {"swap": "$n(n-1)/2$", "insertion": "$(n-1)^2$", "2opt": "$n(n-1)/2$"}
TAMANHO = {
    "swap": lambda n: n * (n - 1) // 2,
    "insertion": lambda n: (n - 1) ** 2,
    "2opt": lambda n: n * (n - 1) // 2,
}
NOME_VIZ = {"swap": "Swap", "insertion": "Insertion", "2opt": "2-opt"}


def t2_vizinhancas(t2: list[dict], tempos_mov: list[dict]) -> str:
    h = {k: dados.melhores(g) for k, g in dados.agrupar(t2, "instancia", "vizinhanca").items()}
    tempo = {(r["instancia"], r["vizinhanca"]): r for r in tempos_mov}
    linhas = []
    for viz in configs.VIZINHANCAS:
        g = tempo[("grande", viz)]
        linhas.append(
            [
                NOME_VIZ[viz],
                TAMANHO_FORMULA[viz],
                " / ".join(num(TAMANHO[viz](n)) for n in (12, 50, 150)),
                *(_mediana(h[(inst, viz)]) for inst in INSTANCIAS),
                f"{num(float(g['us_completa']), 1)} $\\to$ {num(float(g['us_incremental']), 1)}",
                num(float(g["ganho"]), 2) + "$\\times$",
            ]
        )
    return tabular(
        "llrrrrrr",
        [
            "Vizinhança",
            "$|N(s)|$",
            "$n = 12 / 50 / 150$",
            "Pequena",
            "Média",
            "Grande",
            "µs/aval. ($n=150$)",
            "Ganho",
        ],
        linhas,
    )


def t2_testes(t2: list[dict]) -> str:
    h = {k: dados.melhores(g) for k, g in dados.agrupar(t2, "instancia", "vizinhanca").items()}
    familias = []
    for inst in INSTANCIAS:
        grupos = {NOME_VIZ[v]: h[(inst, v)] for v in configs.VIZINHANCAS}
        familias.append((inst, comparar(grupos, [("Insertion", "2-opt"), ("Insertion", "Swap")])))
    return _tabela_testes(familias)


def sa_calibracao() -> str:
    linhas = []
    for inst in INSTANCIAS:
        c = json.loads((RAIZ_PROJETO / "configs" / f"sa_{inst}.json").read_text())
        linhas.append(
            [
                dados.NOME_INSTANCIA[inst],
                num(c["mediana_piora"], 1),
                num(c["q10_piora"], 1),
                num(c["T0"], 0),
                num(c["Tf"], 1),
                num(c["L"]),
                num(c["alfa"], 5),
                f"{num(c['avaliacoes_calibracao'])} ({pct(c['fracao_do_orcamento'])})",
            ]
        )
    return tabular(
        "lrrrrrrr",
        [
            "Instância",
            "Mediana $\\Delta^+$",
            "$q_{10}$ $\\Delta^+$",
            "$T_0$",
            "$T_f$",
            "$L$",
            "$\\alpha$",
            "Avaliações (\\% de $B$)",
        ],
        linhas,
    )


def ag_parametros(t3: list[dict], pasta_t3: Path) -> str:
    por = dados.agrupar([r for r in t3 if r["config"] == "AG"], "instancia")
    geracoes = dados.tabela_telemetria(pasta_t3, "ag_geracoes")
    linhas = []
    for inst in INSTANCIAS:
        grupo = por[(inst,)]
        p = grupo[0]["params"]
        finais = [int(geracoes[r["run_id"]][-1]["distintos"]) for r in grupo]
        linhas.append(
            [
                dados.NOME_INSTANCIA[inst],
                num(p["N"]),
                num(p["k"]),
                num(p["Pc"], 1),
                num(p["Pm"], 1),
                num(p["elite"]),
                num(statistics.median(r["resumo"]["geracoes"] for r in grupo)),
                f"{num(statistics.median(finais))}/{num(p['N'])}",
            ]
        )
    return tabular(
        "lrrrrrrr",
        [
            "Instância",
            "$N$",
            "$k$",
            "$P_c$",
            "$P_m$",
            "Elite",
            "Gerações",
            "Distintos no fim",
        ],
        linhas,
    )


def otimos_locais(t3: list[dict], pasta_t3: Path) -> str:
    """Pequena: ótimos locais da descida gulosa e execuções que acharam h*."""
    ref = configs.REFERENCIA["pequena"]
    pequena = [r for r in t3 if r["instancia"] == "pequena"]
    otimos = dados.tabela_telemetria(pasta_t3, "otimos_locais")
    linhas = []
    por_config = dados.agrupar(pequena, "config")
    for cfg in (*VARIANTES_GD, "SA", "AG"):
        grupo = por_config[(cfg,)]
        acertos = f"{sum(r['best_h'] <= ref for r in grupo)}/{len(grupo)}"
        if cfg.startswith("GD"):
            completas = [o for r in grupo for o in otimos[r["run_id"]] if o["completa"] == "1"]
            distintos = {o["assinatura"] for o in completas}
            no_otimo = sum(int(o["h"]) == ref for o in completas)
            linhas.append(
                [
                    cfg,
                    num(len(completas) / len(grupo), 1),
                    num(statistics.fmean(r["resumo"]["otimos_distintos"] for r in grupo), 1),
                    num(len(distintos)),
                    pct(no_otimo / len(completas)),
                    acertos,
                ]
            )
        else:
            linhas.append([cfg, "--", "--", "--", "--", acertos])
    return tabular(
        "lrrrrr",
        [
            "Algoritmo",
            "Ótimos locais/exec.",
            "Distintos/exec.",
            "Distintos (30 exec.)",
            "Descidas em $h^*$",
            "Execuções com $h^*$",
        ],
        linhas,
    )


def extra(linhas_extra: list[dict]) -> str:
    h = _por_config(linhas_extra)
    linhas, grupos = [], []
    for inst in INSTANCIAS:
        grupos.append(len(linhas))
        pares = [(b, "AG-OX") for b in BRACOS_EXTRA if b != "AG-OX"]
        testes_ = {t["a"]: t for t in comparar({b: h[(inst, b)] for b in BRACOS_EXTRA}, pares)}
        for braco in BRACOS_EXTRA:
            v = h[(inst, braco)]
            d = descrever(v)
            t = testes_.get(braco)
            linhas.append(
                [
                    dados.NOME_INSTANCIA[inst] if braco == BRACOS_EXTRA[0] else "",
                    braco,
                    _media_dp(v),
                    _mediana(v),
                    num(d["min"]),
                    pvalor(t["p_holm"]) if t else "--",
                    num(t["A12"], 2) if t else "--",
                ]
            )
    return tabular(
        "llrrrrr",
        [
            "Instância",
            "Variante",
            "Média $\\pm$ dp",
            "Mediana",
            "Mínimo",
            "$p$ (Holm) vs.\\ AG-OX",
            "$A_{12}$ vs.\\ AG-OX",
        ],
        linhas,
        grupos,
    )


def robustez(t3: list[dict], rob: list[dict]) -> str:
    """SA sem as avaliações da calibração e os algoritmos com o dobro do orçamento."""
    h = {**_por_config(t3), **_por_config(rob)}
    linhas, grupos = [], []
    for inst in INSTANCIAS:
        grupos.append(len(linhas))
        algs = ["SA"] if inst == "pequena" else [*VARIANTES_GD, "SA", "AG"]
        for k, alg in enumerate(algs):
            base = h[(inst, alg)]
            menos = h.get((inst, f"{alg} (B − calib.)"))
            dobro = h.get((inst, f"{alg} (2B)"))
            if menos is not None:
                t = comparar({"B": base, "B-c": menos}, [("B", "B-c")])[0]
                p_menos = pvalor(t["p"])
            else:
                p_menos = "--"
            linhas.append(
                [
                    dados.NOME_INSTANCIA[inst] if k == 0 else "",
                    alg,
                    _mediana(base),
                    _mediana(menos) if menos else "--",
                    p_menos,
                    _mediana(dobro) if dobro else "--",
                ]
            )
    return tabular(
        "llrrrr",
        [
            "Instância",
            "Algoritmo",
            "Mediana com $B$",
            "Com $B - $ calibração",
            "$p$",
            "Com $2B$",
        ],
        linhas,
        grupos,
    )


def melhores_solucoes(pastas: dict[str, list[dict]]) -> tuple[str, str]:
    """Melhor permutação encontrada por instância em todas as suítes, reavaliada do zero.

    Devolve a tabela LaTeX e um texto com as permutações (para conferência).
    """
    linhas, texto = [], []
    for inst in INSTANCIAS:
        candidatas = [(r["best_h"], suite, r) for suite, rs in pastas.items() for r in rs]
        candidatas = [c for c in candidatas if c[2]["instancia"] == inst]
        h, suite, r = min(candidatas, key=lambda c: (c[0], c[1], c[2]["run_id"]))
        perm = [int(x) for x in r["best_perm"].split()]
        reavaliado = MaintenanceProblem(load_named(inst)).h(perm)
        if reavaliado != h or sorted(perm) != list(range(1, len(perm) + 1)):
            raise ValueError(f"{r['run_id']}: h reavaliado {reavaliado} difere de {h}")
        ref = configs.REFERENCIA[inst]
        linhas.append(
            [
                dados.NOME_INSTANCIA[inst],
                num(ref),
                num(h),
                pct((h - ref) / ref),
                f"{r['config']} ({suite})",
            ]
        )
        texto.append(f"{inst}: h = {h} ({r['run_id']}, {suite}); reavaliado = {reavaliado}")
        texto.append("  " + " ".join(map(str, perm)))
    tabela = tabular(
        "lrrrl",
        ["Instância", "$h_{\\mathrm{ref}}$", "Melhor $h$", "Diferença", "Encontrado por"],
        linhas,
    )
    return tabela, "\n".join(texto) + "\n"


def gerar(saida: Path) -> list[Path]:
    pasta_t3 = dados.pasta_atual("T3")
    pasta_t2 = dados.pasta_atual("T2")
    t3 = dados.runs(pasta_t3)
    t2 = dados.runs(pasta_t2)
    tempos = dados.runs(dados.pasta_atual("TEMPOS"))
    extra_ = dados.runs(dados.pasta_atual("EXTRA"))
    rob = dados.runs(dados.pasta_atual("ROBUSTEZ"))
    tempos_mov = dados.ler_csv(pasta_t2 / "tempo_movimentos.csv")
    conteudos = {
        "principal.tex": principal(t3, tempos),
        "testes.tex": testes(t3),
        "gd_variantes.tex": gd_variantes(t3),
        "t2_vizinhancas.tex": t2_vizinhancas(t2, tempos_mov),
        "t2_testes.tex": t2_testes(t2),
        "sa_calibracao.tex": sa_calibracao(),
        "ag_parametros.tex": ag_parametros(t3, pasta_t3),
        "otimos_locais.tex": otimos_locais(t3, pasta_t3),
        "extra.tex": extra(extra_),
        "robustez.tex": robustez(t3, rob),
    }
    tabela, permutacoes = melhores_solucoes({"T2": t2, "T3": t3, "extra": extra_, "robustez": rob})
    conteudos["melhores.tex"] = tabela
    arquivos = [gravar(saida, nome, texto) for nome, texto in conteudos.items()]
    caminho = saida.parent / "melhores_solucoes.txt"
    caminho.write_text(permutacoes)
    return [*arquivos, caminho]
