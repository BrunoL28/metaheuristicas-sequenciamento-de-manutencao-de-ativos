"""Figuras PDF do relatório: boxplots, convergência, aceitação do SA e diversidade do AG."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from tp2.analysis import dados  # noqa: E402
from tp2.analysis.tabelas import BRACOS_EXTRA, NOME_VIZ, PRINCIPAIS  # noqa: E402
from tp2.experiments import configs  # noqa: E402
from tp2.problem.heuristicas import guloso_menor_acrescimo  # noqa: E402
from tp2.problem.instance import load_named  # noqa: E402
from tp2.problem.maintenance import MaintenanceProblem  # noqa: E402

INSTANCIAS = configs.INSTANCIAS

# Uma cor por algoritmo em todas as figuras.
COR = {
    "GD-random": "#1f77b4",
    "GD-first": "#6baed6",
    "GD-best": "#9ecae1",
    "SA": "#ff7f0e",
    "AG": "#2ca02c",
    "AG-OX": "#2ca02c",
    "AG-PMX": "#98df8a",
    "AG só mutação": "#8c564b",
    "AG headless": "#7f7f7f",
    "AG memético": "#9467bd",
    "Swap": "#d62728",
    "Insertion": "#1f77b4",
    "2-opt": "#bcbd22",
}
COR_INSTANCIA = {"pequena": "#1b9e77", "media": "#d95f02", "grande": "#7570b3"}

plt.rcParams.update(
    {
        "pdf.fonttype": 42,
        "font.size": 8,
        "axes.titlesize": 9,
        "legend.fontsize": 7,
        "figure.dpi": 150,
    }
)

LARGURA = 7.0  # polegadas, largura útil de uma página A4 com margens de 2,5 cm


def _salvar(fig, arquivo: Path) -> None:
    # Sem data de criação, o PDF só muda quando o conteúdo muda.
    fig.savefig(arquivo, metadata={"CreationDate": None})


def _guloso(inst: str) -> int:
    instancia = load_named(inst)
    return MaintenanceProblem(instancia).h(guloso_menor_acrescimo(instancia))


def _boxplots(grupos, ordem, arquivo: Path, log=False, referencias=True, rotulos=None):
    fig, eixos = plt.subplots(1, 3, figsize=(LARGURA, 2.6))
    for ax, inst in zip(eixos, INSTANCIAS, strict=True):
        valores = [grupos[(inst, c)] for c in ordem]
        caixas = ax.boxplot(valores, patch_artist=True, widths=0.6)
        for caixa, c in zip(caixas["boxes"], ordem, strict=True):
            caixa.set_facecolor(COR[c])
            caixa.set_alpha(0.75)
        for mediana in caixas["medians"]:
            mediana.set_color("black")
        ax.set_xticks(range(1, len(ordem) + 1), rotulos or ordem, rotation=30, ha="right")
        ax.set_title(f"{dados.NOME_INSTANCIA[inst]} ($n = {dados.N_INSTANCIA[inst]}$)")
        if log:
            ax.set_yscale("log")
        if referencias:
            ax.axhline(configs.REFERENCIA[inst], color="black", ls="--", lw=0.8, label="referência")
            # O guloso só aparece quando cabe na escala dos dados (senão achata as caixas).
            guloso = _guloso(inst)
            if guloso <= 1.05 * max(max(v) for v in valores):
                ax.axhline(guloso, color="gray", ls=":", lw=0.8, label="guloso")
        ax.grid(axis="y", alpha=0.3)
    eixos[0].set_ylabel("melhor $h$ da execução")
    if referencias:
        # A legenda vai no primeiro painel que mostra as duas linhas, se houver.
        completo = [ax for ax in eixos if len(ax.get_legend_handles_labels()[0]) > 1]
        (completo or eixos)[0].legend(loc="upper left")
    fig.tight_layout()
    _salvar(fig, arquivo)
    plt.close(fig)


def _grupos(linhas):
    # Ordenado para o PDF não depender da ordem em que as execuções terminaram.
    return {
        k: sorted(dados.melhores(g))
        for k, g in dados.agrupar(linhas, "instancia", "config").items()
    }


def boxplots(t3, saida: Path) -> Path:
    arquivo = saida / "boxplots.pdf"
    _boxplots(_grupos(t3), PRINCIPAIS, arquivo)
    return arquivo


def t2(linhas_t2, saida: Path) -> Path:
    for linha in linhas_t2:
        linha["config"] = NOME_VIZ[linha["vizinhanca"]]
    arquivo = saida / "t2_vizinhancas.pdf"
    _boxplots(_grupos(linhas_t2), ["Swap", "Insertion", "2-opt"], arquivo)
    return arquivo


def extra(linhas_extra, saida: Path) -> Path:
    arquivo = saida / "extra.pdf"
    rotulos = [b.removeprefix("AG ").removeprefix("AG-") for b in BRACOS_EXTRA]
    _boxplots(_grupos(linhas_extra), BRACOS_EXTRA, arquivo, log=True, rotulos=rotulos)
    return arquivo


def _faixa(ax, x, matriz, cor, rotulo, estilo="-"):
    mediana = np.nanmedian(matriz, axis=0)
    q1, q3 = np.nanpercentile(matriz, [25, 75], axis=0)
    ax.plot(x, mediana, estilo, color=cor, lw=1.2, label=rotulo)
    ax.fill_between(x, q1, q3, color=cor, alpha=0.2, lw=0)


def convergencia(t3, pasta_t3: Path, saida: Path) -> Path:
    curvas = dados.curvas(pasta_t3)
    geracoes = dados.tabela_telemetria(pasta_t3, "ag_geracoes")
    fig, eixos = plt.subplots(1, 3, figsize=(LARGURA, 2.9))
    for ax, inst in zip(eixos, INSTANCIAS, strict=True):
        B = configs.ORCAMENTO[inst]
        grade = np.linspace(B / 200, B, 200)
        x = grade / 1000
        for alg in PRINCIPAIS:
            ids = [r["run_id"] for r in t3 if r["instancia"] == inst and r["config"] == alg]
            matriz = np.array([dados.em_grade(*curvas[rid], grade) for rid in ids])
            _faixa(ax, x, matriz, COR[alg], alg)
            if alg == "AG":
                media_pop = np.array(
                    [
                        dados.em_grade(
                            np.array([int(g["avaliacoes"]) for g in geracoes[rid]]),
                            np.array([float(g["media_h"]) for g in geracoes[rid]]),
                            grade,
                        )
                        for rid in ids
                    ]
                )
                ax.plot(
                    x,
                    np.nanmedian(media_pop, axis=0),
                    "--",
                    color=COR["AG"],
                    lw=1,
                    label="AG (média da população)",
                )
        ax.axhline(configs.REFERENCIA[inst], color="black", ls=":", lw=0.8, label="referência")
        ax.set_yscale("log")
        ax.set_xlabel("avaliações (mil)")
        ax.set_title(f"{dados.NOME_INSTANCIA[inst]} ($B = {B // 1000}$ mil)")
        ax.grid(alpha=0.3)
    eixos[0].set_ylabel("melhor $h$ (mediana e IQR)")
    alcas, rotulos = eixos[0].get_legend_handles_labels()
    fig.legend(alcas, rotulos, loc="lower center", ncol=5, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    arquivo = saida / "convergencia.pdf"
    _salvar(fig, arquivo)
    plt.close(fig)
    return arquivo


def sa_aceitacao(t3, pasta_t3: Path, saida: Path) -> Path:
    janelas = dados.tabela_telemetria(pasta_t3, "sa_aceitacao")
    fig, ax = plt.subplots(figsize=(LARGURA / 2, 2.4))
    for inst in INSTANCIAS:
        ids = [r["run_id"] for r in t3 if r["instancia"] == inst and r["config"] == "SA"]
        matriz = np.array(
            [[float(j["taxa"]) if j["taxa"] else np.nan for j in janelas[rid]] for rid in ids]
        )
        x = np.arange(1, matriz.shape[1] + 1) / matriz.shape[1]
        _faixa(ax, x, matriz, COR_INSTANCIA[inst], dados.NOME_INSTANCIA[inst])
    ax.set_xlabel("fração do orçamento")
    ax.set_ylabel("aceitação de pioras")
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    arquivo = saida / "sa_aceitacao.pdf"
    _salvar(fig, arquivo)
    plt.close(fig)
    return arquivo


def ag_diversidade(t3, pasta_t3: Path, saida: Path) -> Path:
    geracoes = dados.tabela_telemetria(pasta_t3, "ag_geracoes")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(LARGURA, 2.4))
    grade = np.linspace(0, 1, 101)
    for inst in INSTANCIAS:
        ids = [r["run_id"] for r in t3 if r["instancia"] == inst and r["config"] == "AG"]
        N = next(r for r in t3 if r["run_id"] == ids[0])["params"]["N"]
        n = dados.N_INSTANCIA[inst]
        distintos, distancia = [], []
        for rid in ids:
            serie = geracoes[rid]
            x = np.linspace(0, 1, len(serie))
            distintos.append(np.interp(grade, x, [int(g["distintos"]) / N for g in serie]))
            distancia.append(np.interp(grade, x, [float(g["distancia_media"]) / n for g in serie]))
        cor = COR_INSTANCIA[inst]
        _faixa(ax1, grade, np.array(distintos), cor, dados.NOME_INSTANCIA[inst])
        _faixa(ax2, grade, np.array(distancia), cor, dados.NOME_INSTANCIA[inst])
    ax1.set_ylabel("permutações distintas / $N$")
    ax2.set_ylabel("distância média entre pares / $n$")
    for ax in (ax1, ax2):
        ax.set_xlabel("fração das gerações")
        ax.set_ylim(0, 1.02)
        ax.grid(alpha=0.3)
    ax1.legend()
    fig.tight_layout()
    arquivo = saida / "ag_diversidade.pdf"
    _salvar(fig, arquivo)
    plt.close(fig)
    return arquivo


def gerar(saida: Path) -> list[Path]:
    saida.mkdir(parents=True, exist_ok=True)
    pasta_t3 = dados.pasta_atual("T3")
    t3 = dados.runs(pasta_t3)
    return [
        boxplots(t3, saida),
        convergencia(t3, pasta_t3, saida),
        sa_aceitacao(t3, pasta_t3, saida),
        ag_diversidade(t3, pasta_t3, saida),
        t2(dados.runs(dados.pasta_atual("T2")), saida),
        extra(dados.runs(dados.pasta_atual("EXTRA")), saida),
    ]
