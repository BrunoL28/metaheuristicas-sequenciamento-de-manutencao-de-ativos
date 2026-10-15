import pytest

from tp2.analysis import dados
from tp2.analysis.__main__ import main
from tp2.analysis.estatistica import a12, comparar, holm, mann_whitney
from tp2.analysis.formato import num, pvalor


def test_holm_exemplo_classico():
    # p = (0,01; 0,04; 0,03) → ajustados (0,03; 0,06; 0,06).
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert holm([0.5, 0.9]) == pytest.approx([1.0, 1.0])


def test_a12_e_mann_whitney():
    assert a12([1, 2, 3], [4, 5, 6]) == 1.0
    assert a12([4, 5, 6], [1, 2, 3]) == 0.0
    assert a12([1, 1], [1, 1]) == 0.5
    assert mann_whitney([1875] * 30, [1875] * 30) == (450.0, 1.0)
    u, p = mann_whitney(list(range(30)), list(range(100, 130)))
    assert u == 0 and p < 1e-9


def test_comparar_aponta_o_melhor_so_quando_significativo():
    grupos = {"A": list(range(20)), "B": list(range(100, 120)), "C": list(range(1, 21))}
    linhas = {(t["a"], t["b"]): t for t in comparar(grupos, [("A", "B"), ("A", "C")])}
    assert linhas[("A", "B")]["melhor"] == "A"
    assert linhas[("A", "C")]["melhor"] is None


def test_formato_portugues():
    assert num(1234567.25, 1) == "1\\,234\\,567,2"
    assert num(1875) == "1\\,875"
    assert num(-0.6, 1) == "$-$0,6"
    assert num(-0.01, 1) == "0,0"
    assert pvalor(0.0451) == "0,045"
    assert pvalor(2.5e-6) == "$2,5\\times10^{-6}$"


def test_nomes_das_configuracoes():
    base = {"algoritmo": "ag", "variante": "padrao", "rotulo": ""}
    assert dados.config(base) == "AG"
    assert dados.config({**base, "rotulo": "pmx"}) == "AG-PMX"
    assert dados.config({**base, "variante": "headless"}) == "AG headless"
    assert dados.config({**base, "algoritmo": "sa", "rotulo": "2B"}) == "SA (2B)"
    assert dados.config({"algoritmo": "gd", "variante": "first"}) == "GD-first"


def test_gera_todas_as_tabelas_e_figuras(tmp_path):
    main(["--tabelas", str(tmp_path / "tab"), "--figuras", str(tmp_path / "fig")])
    tabelas = sorted(p.name for p in (tmp_path / "tab").iterdir())
    figuras = sorted(p.name for p in (tmp_path / "fig").iterdir())
    assert len(tabelas) == 11 and len(figuras) == 6
    assert (tmp_path / "melhores_solucoes.txt").exists()
    principal = (tmp_path / "tab" / "principal.tex").read_text()
    assert "\\begin{tabular}" in principal and "30/30" in principal
