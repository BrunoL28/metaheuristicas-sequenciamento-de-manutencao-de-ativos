# IMPLEMENTATION PLAN — tp2-fundia

**Revision:** 1 · **Date:** 2026-10-14 · **Previous revisions:** `archive/` (none yet) · **Delivery deadline:** **2026-10-18**

> Small changes (bug fixed, component done, sub-task added) → edit in place. Big changes (architecture, scope, restructure) → move this file to `archive/IMPLEMENTATION_PLAN_rev<N>_<YYYY-MM-DD>.md` and write rev N+1.
>
> Source of truth for requirements: `INPUTS/_FundIA__TP2_BuscaLocal_GAs.pdf` (distilled in `CONTEXT.md` §3–§4). Section references like "§2.3" below refer to the **statement**; "C7" refers to components in §9 of this plan.

---

## 1. Current Implementation Status

**Phase:** Phase 1 — build. Plan rev 1 and the delivery schedule (§11) approved 2026-10-14. M0–M2 merged 2026-10-14; M3 (greedy descent + runner + T2) in review (PR #4); M4 (SA) in review (PR #5, stacked on #4); M3–M5 merged 2026-10-15. M0–M7 merged by 2026-10-15. M8 (report draft) in review; M9 pending.

| # | Component | Status | Tested? | Notes |
|---|---|---|---|---|
| C0 | Project scaffolding (`pyproject.toml`, `uv.lock`, `Makefile`, package layout) | 🟡 In progress | `uv sync --locked`, ruff, pytest green; CI workflow `.github/workflows/ci.yml` | M1: hatchling backend (local uv 0.6.12 predates `uv_build`); Makefile has `setup test lint verify t2 calibrate sa-piloto ag-piloto ag-ajuste ox-demo memetico-ajuste experiments extra robustez tempos analysis report overleaf`, the other targets land with their missions |
| C1 | `Problem` interface + `Move` type | ✅ Done (M2) | Exercised through C2/C5 tests | `src/tp2/core/interface.py`; AST test `tests/test_arquitetura.py` forbids `tp2.problem` imports in `tp2/algorithms` (checked to fail on a planted import) |
| C2 | `CountingProblem` (budget, counter, best-so-far trace) | ✅ Done (M2) | B calls succeed and B+1 raises; mid-scan stop; `best_s` re-evaluates to `best_h`; non-evaluating methods don't count (`tests/test_counting.py`) | Stores only improvement events `(evals, best_h)`; the runner writes them to `curvas.csv`; any fixed grid (e.g. 201 points) is derived in C11 |
| C3 | Instance loader | ✅ Done (M1) | n, Σp, base, symmetric T, no .5 ties (`tests/test_instance.py`) | `src/tp2/problem/instance.py` |
| C4 | `MaintenanceProblem` — full fitness h | ✅ Done (M1) | 4366, toy 39/22 + C_j of Fig. 1, unique optimum 22, prefix monotonicity (`tests/test_fitness.py`) | `src/tp2/problem/maintenance.py`; baselines in `heuristicas.py` (greedy 3168, NN 2590); exact DP in `exato.py` |
| C5 | Neighborhoods: swap / insertion / 2-opt (+ incremental evaluation) | ✅ Done (M2) | Sizes, distinctness, Fig. 3 examples, hypothesis property incremental == full (150 random instances n ≤ 30), equality on pequena/media (`tests/test_neighborhoods.py`) | Incremental = rebuild only the suffix from the first touched position + evaluate from the cached prefix. Measured gain 1.1–1.4× (≤ 1.5× theoretical, since E[min(i,j)] ≈ n/3): see below |
| C6 | Crossover (OX; PMX deferred) + mutation operators | ✅ Done (M5) | Slide example (5,2,3,4,1); hypothesis: child is a permutation, keeps the block, fills in P2's relative order; mutation is one move of the neighborhood (`tests/test_genetic.py`) | `src/tp2/problem/operators.py`; `make ox-demo` → `results/ox_demo.txt` (step-by-step example for the report, n = 8, seed 15). Mutation = one random **insertion** move (CONTEXT §8) |
| C7 | Greedy descent + random restart (3 variants) | ✅ Done (M3) | Exact budget for 3 variants × 3 neighborhoods; every complete `best`/`first` descent re-checked as a true local optimum; same seed → same trace; summary == telemetry (`tests/test_greedy_descent.py`) | `src/tp2/algorithms/greedy_descent.py`; per-descent telemetry (h, permutation signature, steps, complete or cut by budget) through `core/recorder.py` |
| C8 | Simulated annealing + SA calibration script | ✅ Done (M4) | α takes T0 to Tf on the last level; exact budget; windows and T monotone; T → 0 gives no accepted worsening, T → ∞ accepts all; same seed → same run; calibration formulas; runner reads the versioned calibration (`tests/test_simulated_annealing.py`) | `src/tp2/algorithms/simulated_annealing.py`, `src/tp2/experiments/calibrate_sa.py` → `configs/sa_*.json` + `configs/sa_calibracao.txt`. Pilot `results/2026-10-15_sa_piloto/` (3 runs/instance): worsening acceptance ≈ 0.87 in the first window → 0.002–0.006 in the last |
| C9 | Genetic algorithm (+ diversity logging) | ✅ Done (M5) | Exact budget (both variants); evaluations per generation = N + g(N − e); best h never worsens (elitism); Pc = Pm = 0 never increases diversity; same seed → same run (`tests/test_genetic.py`) | `src/tp2/algorithms/genetic.py`; variants `padrao` and `headless` (extra experiment); mutation-only = `padrao` with Pc = 0. Diversity sampled on 50 pairs/generation with its own RNG; telemetry time excluded from `wall_s`. Pilot `results/2026-10-15_ag_piloto/`; parameter pilot `results/2026-10-15_ag_ajuste/` kept the defaults |
| C10 | Experiment runner (parallel, seeded, CSV) | ✅ Done (M3–M6) | Seed rule, invariants, end-to-end run with interrupted `--resume` (`tests/test_runner.py`); suite composition and budgets (`tests/test_suites.py`) | `src/tp2/experiments/{runner,configs,resumo}.py`. Cells carry a label, problem options (crossover), a budget factor, an optional SA-calibration discount and an instance filter. Suites: `t2`, `sa_piloto`, `ag_piloto`, `ag_ajuste`, `memetico_ajuste`, `t3`, `extra`, `robustez`, `tempos` |
| C11 | Analysis: stats tables, boxplots, convergence, acceptance, diversity | ✅ Done (M7) | Holm worked example, A12, Mann–Whitney edge case (all equal → p = 1), PT-BR number format, end-to-end generation (`tests/test_analise.py`) | `src/tp2/analysis/{dados,estatistica,formato,tabelas,figuras}.py`; `make analysis` → 11 tables in `relatorio/tabelas/` (only the `tabular`; caption and label live in the report), 6 three-panel figures in `relatorio/figuras/` (deterministic PDFs), `relatorio/melhores_solucoes.txt`. scipy + matplotlib, no pandas |
| C12 | `verify` command (T1 output for the report) | ✅ Done (M1) | `make verify` exits 0; output in `results/verify.txt` | Computes h* = 1875 by exact DP instead of only quoting it |
| C13 | Extra experiment: does crossover help? | ✅ Run (M6) | PMX worked example + hypothesis properties; memetic GA exact budget (`tests/test_suites.py`) | `make extra` → `results/2026-10-15_extra/`: GA-OX, mutation-only (Pc = 0), headless chicken, GA-PMX and memetic GA (p_ls = 0.1). Statistical tests in M7 |
| C14 | Report (`relatorio/`, LaTeX) | 🟡 Draft done (M8), group review | Compiles with TeX Live 2023 (`make report`): 0 undefined refs/citations, one 0.9 pt overfull line | `relatorio/main.tex` + `secoes/*.tex` (one sentence per line) + `referencias.bib` (10 entries, none invented) + `apalike-pt.bst` (apalike with PT connectors). 10 pt, 2 cm margins: body ≈ 7 pages + references + appendices (11 pages total). Every number comes from `relatorio/tabelas/` or the plan §1 facts; prose checked with humanize-text `ai_tells.py`. Overleaf: `make overleaf` → upload |
| C15 | Delivery packaging (README reproduction table, zip) | ⬜ Not started | — | |

**Facts already verified (scratch scripts, 2026-10-14, not yet in the repo):**
- h(identity) on `manutencao_pequena.txt` = **4366** ✅ (matches statement §1.4).
- Σp = 55 / 239 / 684 ✅ (matches statement §1.3 table).
- Fig. 1 toy instance reconstructed: base (0,0), 1=(3,4), 2=(6,0), 3=(0,8), 4=(6,8) (p, d, w from the figure). h(1,4,2,3) = **39**, unique optimum (1,4,3,2) = **22** ✅.
- Statement's greedy value **3168** is reproduced only with the rule "min immediate tardiness increment; tie → min travel time; tie → lowest index". Nearest-neighbour gives **2590**.
- **Statistics (M7, `make analysis`; Mann–Whitney two-sided, Holm within each instance, A12):**
  - GD-random × SA: no significant difference on any instance (p_Holm = 1.000 / 0.145 / 0.910). Both beat the GA everywhere (p_Holm ≤ 0.015, A12 ≥ 0.80). The report must not say "SA wins": it has the lowest median on media and grande, without significance.
  - GD variants: `first` ≈ `random` (p_Holm 0.55 / 0.62); `best` worse on media (7·10⁻⁹) and grande (3.7·10⁻⁴).
  - T2: insertion beats 2-opt and swap on media and grande (p_Holm ≤ 0.009); all tie on pequena.
  - Extra (vs GA-OX, Holm over 4): memetic better everywhere (3.3·10⁻⁶ / 5.6·10⁻⁶ / 0.011); headless worse on media/grande (1.2·10⁻¹⁰ / 7.3·10⁻⁴); PMX and mutation-only not different (p ≥ 0.275).
  - SA with B − calibration vs B: p = 0.515 (media), 0.345 (grande): the calibration cost doesn't change the result.
  - Pequena local optima: `best`/`first` find 19 distinct local optima over 30 runs, and 11% / 15.5% of their descents end at h*. (`random` "optima" are K-failure stops, not verified local optima: 491 distinct.)
  - Best solutions (`relatorio/melhores_solucoes.txt`, re-evaluated): pequena 1 875; media **16 234 (−0.6% vs the 16 332 reference, memetic GA)**; grande 68 986 (+14.2%, SA with 2B).
- **T3 + extra + robustness (M6, commit `7bd25eb`, every run ok; T3 63 s, extra 110 s, robustness 131 s on 15 processes):** medians of best h.
  - T3 pequena: GD (all 3 variants) and SA reach 1 875 in 30/30; GA 12/30 (median 1 937).
  - T3 media: SA 17 047 · GD-random 17 366 · GD-first 17 457.5 · GA 19 378 · GD-best 20 054.5.
  - T3 grande: SA 80 832.5 · GD-random 80 906.5 · GD-first 82 796.5 · GA 94 252 · GD-best 818 369.5 (only 13 improvement steps: one step costs 22 201 evaluations).
  - **Below the media reference 16 332:** SA 16 269, memetic GA 16 234, GD-random 16 306 (independently re-evaluated).
  - Extra, media: memetic 17 125 · OX 19 378 · PMX 19 522.5 · mutation-only 20 409 · headless 47 168.5; grande: memetic 81 773.5 · mutation-only 91 014 · OX 94 252 · PMX 96 107 · headless 515 206.5. Headless keeps both OX children of (selected parent, random permutation), so half of each child comes from noise.
  - Robustness: SA with B − 4 000: media 17 113, grande 82 246 (vs 17 047 / 80 832.5 with B). 2B, media: GD-first 16 645 · SA 16 778.5 · GD-random 16 903 · GD-best 18 516.5 · GA 19 378 (identical to B: no GA run improves after evaluation 149 783); grande: SA 76 488.5 · GD-first 77 827.5 · GD-random 80 906.5 · GA 87 624 · GD-best 575 848.
  - Sequential timing (`results/2026-10-15_tempos/`, s/run at n = 150): GD 3.4–3.9, SA 6.0, GA 8.4.
- **GA pilots (M5):** default GA (N = 50/100/100, Pc = 0.9, Pm = 0.2, k = 3, e = 2), 3 runs: median 1 937 / 18 610 / 97 014, the weakest of the three algorithms in the pilots. Diversity collapses early: distinct permutations at 10% of the generations = 11 / 42 / 61, mean pair distance 1.8 / 13.6 / 46.6 positions. Parameter pilot on media (10 runs, seeds outside the protocol): N ∈ {50, 100, 200} × Pm ∈ {0.2, 0.5, 1.0} medians 19 297–21 254 with wide spread, no setting clearly better → defaults kept.
- **Incremental evaluation timing** (`python -m tp2.experiments.tempo_movimentos`, 20 solutions × 5000 random moves): gain 1.0–1.2× at n = 12, 1.25–1.33× at n = 50, 1.38–1.44× at n = 150 (≈ 10 µs per successor at n = 150 for all three operators). Definitive table: `results/2026-10-15_t2/tempo_movimentos.csv`.
- **T2 (M3, `make t2` → `results/2026-10-15_t2/`, commit `a3be940`, 210/210 runs ok, 31 s on 15 processes):** first-improvement GD + RR. Pequena: all 3 neighborhoods reach h* = 1875 in 30/30 runs; distinct local optima per run: swap 112.8, 2-opt 47.1, insertion 16.9. Median best h — media: insertion 17 457.5, 2-opt 18 468, swap 24 252; grande: insertion 82 796.5, 2-opt 89 078.5, swap 150 118. At n = 150 a run completes only 1.4–2.5 descents (scale effect for the report). **Insertion adopted** for GD, SA and GA mutation (`configs.VIZINHANCA`, CONTEXT §8).
- **h* = 1875 confirmed independently** (M1): an exact DP over (visited set, last asset) with Pareto labels (C, h) finds the optimum (5, 4, 1, 6, 7, 2, 8, 12, 3, 10, 9, 11) in < 1 s. It's valid because future cost never decreases as C grows, so (C, h) labels dominate componentwise.
- Pure-Python full evaluation with a precomputed integer travel matrix: **~15 µs/eval at n = 150**, so 300k evals ≈ 4.5 s/run (16 cores available). Compute is not a constraint.

### Bug log

| Date | Bug | Root cause | Fix | Status |
|---|---|---|---|---|
| — | — | — | — | — |

---

## 2. Introduction

TP2 asks us to answer an empirical question: **how do the matching between an algorithm and a problem's structure, and the balance between exploration and intensification, decide which metaheuristic wins under a fixed computational budget?** The test problem is a single-crew maintenance sequencing problem with weighted tardiness. Choosing the order of n assets costs travel (rounded Euclidean distance) plus service time. Every hour an asset finishes past its regulatory deadline d_j costs w_j. The search space is n!: 4.8·10⁸ for the small instance, ~3·10⁶⁴ for the intermediate one, and ~5.7·10²⁶² for the large one. The two natural greedy criteria (nearest vs most urgent) pull in opposite directions. On the small instance the statement's greedy reaches 3168, 69% above the optimum 1875.

The three algorithms are deliberately different in how they spend evaluations. Greedy descent with random restart spends them scanning neighborhoods; at n = 150 a single swap-neighborhood scan costs 11 175 of the 300 000 available evaluations. Simulated annealing spends one evaluation per step and trades exploration for intensification through temperature. The GA spends them on a population and relies on recombination being meaningful for permutations. The grade depends less on raw numbers than on a **fair, reproducible comparison** (same budget, exact stop, 30/30/10 runs, non-parametric tests) and an **honest analysis** of four mandatory questions: local optima, exploration × intensification, scale effect, and when the GA pays off, which needs one additional experiment of our own design.

---

## 3. Scope note

**In scope (v1 = delivery):**
- Fitness h (Eq. 1–3) with rounding, validated on 4366 / 1875-reachable / toy 39 / 22.
- Three neighborhoods (swap, insertion, 2-opt) with sizes as a function of n, plus incremental evaluation for **all three** (the statement requires ≥ 1). Tested against full evaluation, with the time gain measured.
- Greedy descent + random restart with **all three** successor-selection variants (best improvement, first improvement, random-successor-accept-if-better; the statement requires ≥ 2).
- Simulated annealing with geometric cooling, calibrated per instance (T0, Tf, α), logging the worsening-move acceptance rate.
- GA: tournament selection, OX crossover (slide convention), swap/insertion mutation, elitism, budget-only stopping, diversity logging.
- Full protocol of statement §3: budgets 50k / 150k / 300k, runs 30 / 30 / 10, exact stop, wall-clock time, mean/sd/min/median, boxplots, Mann–Whitney with p-values, convergence curves (median; GA also the population mean).
- T1, T2 (neighborhood comparison), T3 (main experiments) and the extra "GA pays off?" experiment.
- Report (PDF, ~5 pages plus appendices, no code in the body) and README with one command per table and figure.

**Pulled forward into v1 on 2026-10-15 (ahead of schedule; Bruno's choice), run in M6:**
- PMX crossover and the GA-PMX arm of the extra experiment.
- The SA sensitivity check: SA with B minus the calibration evaluations (suite `robustez`).
- A memetic GA (GA + first-improvement descent on each child with probability p_ls = 0.1) as an arm of the extra experiment, not as a fourth main algorithm.
- The three algorithms with a doubled budget (2B) on media and grande (suite `robustez`).

**Explicitly deferred (Phase 2+, only if time is left):**
- Sensitivity of the K factor of the GD `random` variant.
- Numba/NumPy acceleration. Pure Python is fast enough (§1 benchmark). Revisit only if T2 plus calibration sweeps get slow.
- Adaptive / reheating SA schedules. Geometric cooling is what the statement suggests and what the class covered.
- Differential Evolution (Part 3 slides). It's for continuous problems and isn't part of TP2.

**Acceptable v1 fallbacks:**
- If incremental 2-opt or insertion turns out tricky, deliver incremental **swap** only (statement minimum is 1 neighborhood) and log the others in Known Holes.
- If the SA calibration procedure (C8) is unstable on one instance, use a hand-tuned (T0, α) for that instance, documented with the acceptance-rate plot that justifies it.

**Out of scope:**
- Exact methods (MIP, DP, branch and bound) beyond what's needed to check the 1875 optimum on n = 12. The statement already provides h*.
- Any GUI.

---

## 4. Design Philosophy

- **Algorithms see an interface, never the problem.** It's a graded requirement (§2.1), and it's what makes 3 algorithms × 3 neighborhoods × 3 instances a configuration matrix instead of 27 code paths.
- **One counter, one place, one exception.** Every h evaluation goes through `CountingProblem`. Evaluation B+1 raises `BudgetExhausted`, so "stop exactly at B" is enforced by construction, not by each algorithm's discipline.
- **The wrapper records the convergence curve.** Best-so-far is tracked where evaluations are counted, so every algorithm gets the same x-axis for free and can't fudge it.
- **Fitness first, then everything else.** 4366, 39 and 22 are pytest assertions before any algorithm code exists. "Metade dos erros graves … está na função de fitness."
- **Incremental evaluation is an optimization, never a semantic.** Each incremental Δ-evaluation counts exactly 1, and a property test asserts it equals the full h on thousands of random moves.
- **Every run is a row, every row has a seed.** `seed = base_seed + run_index`, written to CSV with the git commit hash. A run must be bit-reproducible from its row.
- **Never hand-edit a number in the report.** Tables (`.tex`) and figures (`.pdf`) are generated by `make` targets from a dated `results/` folder.
- **Calibrate on data, justify with plots.** SA temperatures come from sampled Δh distributions per instance, and the acceptance-rate plot is the evidence.
- **Measure diversity, don't assume it.** GA logs distinct-count and mean pairwise distance every generation.
- **Honest beats impressive.** If the GA loses everywhere, the report says so and the extra experiment explains why.

---

## 5. Functional Requirements

### FR-1 — Fitness validation (T1)
- **Trigger:** `make verify`
- **Input:** `INPUTS/manutencao_pequena.txt`, identity permutation; the toy instance; the known optimum (if found, else the statement value).
- **Output:** stdout block printed verbatim into the report (§T1 asks to "show the program output"): `h(identidade) = 4366 ✔` and `h* = 1875` (statement value). If our own GD/SA finds a permutation with h = 1875, print it and re-evaluate it from scratch. Also print the toy checks `h(1,4,2,3)=39`, `h(1,4,3,2)=22`. Save to `results/verify.txt`.
- **State:** none.
- **Errors:** non-zero exit if any value mismatches. `make experiments` depends on `make verify`.
- **Scope:** doesn't run algorithms, apart from re-evaluating a stored best permutation if one exists.

### FR-2 — Neighborhood comparison (T2)
- **Trigger:** `make t2`
- **Input:** 3 instances × 3 neighborhoods × GD variant chosen for T2 (first improvement; rationale in C7). Same budgets and run counts as §3 (30/30/10).
- **Output:** `results/<date>_t2/runs.csv` (best h, #local optima reached, #improvement steps, wall time), `moves_timing.csv` (µs per move evaluation: full vs incremental, per neighborhood per instance). Generated `relatorio/tabelas/t2_vizinhancas.tex` and `relatorio/figuras/t2_boxplot_<inst>.pdf`.
- **Decision output:** the neighborhood adopted for T3 SA/GD (and GA mutation), recorded in `CONTEXT.md` §8 and in `configs.py`.
- **Errors:** runner aborts the cell, keeps already-written rows (append mode + flush per row).

### FR-3 — Main experiments (T3)
- **Trigger:** `make experiments` (depends on `verify`, reads calibrated SA params from `configs/sa_<inst>.json`).
- **Input:** 3 algorithms × 3 instances × runs (30/30/10), the T2-chosen neighborhood, GA params.
- **Output (per results folder `results/<date>_t3/`):**
  - `runs.csv`: one row per run with the columns in C10.
  - `curvas.csv`: long format `run_id, evals, best_h`, one row per improvement of the best-so-far (exact evaluation index). The analysis derives any fixed grid (0, B/200, …, B) from it.
  - `ga_generations.csv`: `run_id, generation, evals, best_h, mean_h, distinct, mean_dist`.
  - `sa_acceptance.csv`: `run_id, window_end_evals, T, worse_proposed, worse_accepted, rate`.
  - `gd_local_optima.csv`: `run_id, variant, restart_idx, h_local_opt, perm_hash`.
  - `config.json`: all params, git commit, Python version, datetime, machine.
- **Errors:** a crashed run is logged with `status=error` and the traceback in `erros.txt` (`*.log` is gitignored). The cell is re-run by `make experiments RESUME=1`, which keeps only `status=ok` rows and their telemetry and re-runs the rest.
- **Scope:** no plotting. That's FR-5.

### FR-4 — Extra experiment: does recombination help? (§5 last bullet)
- **Trigger:** `make extra`
- **Input:** GA variants on all 3 instances, same budgets and run counts: (a) GA-OX (main config), (b) GA mutation-only (Pc = 0), (c) GA "headless chicken" (OX with a random permutation as second parent, Jones 1995). (A fourth arm, GA-PMX, is deferred; see §3.)
- **Output:** `results/<date>_extra/…` (same schema), table plus boxplots plus pairwise tests.
- **Hypothesis framed in the report:** OX preserves contiguous blocks and relative order. If good solutions share useful blocks ("visit this cluster of nearby, similar-deadline assets in this order"), then (a) should beat (b) and (c). If (a) ≈ (c), crossover is acting as macro-mutation and recombination doesn't carry building blocks.

### FR-5 — Analysis and figures
- **Trigger:** `make tables figures` (or `make analysis`)
- **Input:** a results folder (default: the pointer in `results/LATEST_T3`, `LATEST_T2`, `LATEST_EXTRA`).
- **Output:** `relatorio/tabelas/*.tex`, `relatorio/figuras/*.pdf` (list in C11).
- **Scope:** pure function of the CSVs. Never runs algorithms.

### FR-6 — Report and delivery
- **Trigger:** `make report` (latexmk if installed, else Overleaf), `make zip`.
- **Output:** `relatorio/main.pdf`; `entrega/tp2-fundia-<date>.zip` (code + README + results CSV + report PDF; excludes `INPUTS/slides`, `.agents-skills`, `tmp`, `archive`).

---

## 6. High-Level Architecture

```
                    INPUTS/manutencao_*.txt
                              │
                              ▼
                     ┌──────────────────┐
                     │ C3 load_instance │  → Instance(n, coords, p, d, w, T matrix)
                     └────────┬─────────┘
                              ▼
   ┌───────────────────────────────────────────────────────────────┐
   │ C4 MaintenanceProblem  (implements C1 Problem)                │
   │   h(s) · solucao_aleatoria() · sucessores(s) ·                │
   │   sucessor_aleatorio(s) · aplicar(s, mov) · cruzamento · mutacao│
   │   uses C5 neighborhoods (swap/insertion/2-opt + incremental)  │
   │   uses C6 crossover/mutation operators                        │
   └───────────────────────────┬───────────────────────────────────┘
                               │ wrapped by
                               ▼
   ┌───────────────────────────────────────────────────────────────┐
   │ C2 CountingProblem(problem, budget B)                         │
   │   counts every h / Δh  · raises BudgetExhausted at B+1        │
   │   tracks best_h, best_s, improvement trace, checkpoints       │
   └───────────────────────────┬───────────────────────────────────┘
                               │ only sees Problem protocol
          ┌────────────────────┼─────────────────────┐
          ▼                    ▼                     ▼
   C7 GreedyDescent     C8 SimulatedAnnealing   C9 GeneticAlgorithm
   (best/first/random)  (geometric schedule,    (tournament, OX,    
   + random restart      acceptance log)         mutation, elitism,
                                                 diversity log)
          └────────────────────┼─────────────────────┘
                               ▼
                 C10 runner (multiprocessing, seeds, CSV)
                               ▼
                 results/<date>_<label>/*.csv + config.json
                               ▼
                 C11 analysis (pandas, scipy, matplotlib)
                               ▼
                 relatorio/tabelas/*.tex · relatorio/figuras/*.pdf
                               ▼
                 C14 relatorio/main.tex → main.pdf
```

**C1 interface (Protocol).** Python `typing.Protocol` with the six statement methods plus `aplicar(s, mov)`. `sucessores(s)` yields *(move, h_of_successor)* pairs rather than full permutations. The algorithm only builds the successor permutation when it accepts the move, which is what makes incremental evaluation pay off. The algorithm stays ignorant of what a "move" is: it's an opaque tuple it hands back to `aplicar`. This is the minimal extension of the statement's suggested interface. The statement says "uma sugestão mínima", so extending it is allowed; we justify it in the report.

**C2 counting wrapper.** It implements the same Protocol by delegation. Every method that evaluates h increments the counter before returning a value. The counted methods are `h`, each item yielded by `sucessores`, `sucessor_aleatorio`, and the `h` the GA calls on offspring. When `count == B`, the next evaluation raises `BudgetExhausted`. The algorithm's `run()` doesn't catch it; the runner does, then reads `best_h`/`best_s`/trace from the wrapper. Rejected alternative: each algorithm checks `evals < B` itself. That's three places to get wrong, and §6 of the statement warns about exactly this.

**C4/C5 problem and neighborhoods.** The travel matrix `T[i][j]` (ints, (n+1)²) is precomputed once per instance. For incremental evaluation, `MaintenanceProblem` caches, for the *current* solution s (keyed by `id`/version of s), the prefix arrays `C[k]` (completion time after position k) and `H[k]` (cost of the first k positions). A move touching positions ≥ i reuses `C[i−1]`, `H[i−1]` and the predecessor asset, then recomputes positions i..n−1 only: O(n − i) instead of O(n). Expected saving is ~1/3 of the work for swap and 2-opt with uniformly random i<j. This is because the first touched position min(i,j) has expectation ≈ n/3, so ≈ 2n/3 positions are recomputed. Further savings (early exit when the suffix shift becomes 0 after position j and nothing else changed) are listed in §10 as an optional optimization.

**C7–C9 algorithms.** Plain classes with `run(problem, rng, params) -> None`. They mutate no global state and log telemetry through a `Recorder` passed in (SA acceptance windows, GA generations, GD local optima). They import only from `tp2.core`. A test greps the AST of `tp2/algorithms/*.py` for imports of `tp2.problem` and fails if found.

**C10 runner.** It builds the matrix of jobs (algorithm config × instance × run index), maps them over `multiprocessing.Pool(processes=os.cpu_count()-1)`, and appends CSV rows as results arrive (one writer in the parent process). Determinism: each job gets `random.Random(seed)`. No global `random`, no NumPy global state.

**C11 analysis.** It reads the CSVs into pandas. Stats: `scipy.stats.mannwhitneyu(alternative='two-sided')`, Holm correction across the 3 pairs per instance, and the Vargha–Delaney A12 effect size. Plots use matplotlib with the `pdf` backend and one consistent color per algorithm across all figures.

**Why Python + uv + make (rejected: C++/Rust, notebooks).** It's the same stack as TP1 (`BrunoL28/tp1-fundIA`), so the group already knows it. The measured 15 µs/eval makes the full protocol a few minutes of compute. Notebooks were rejected as the primary artifact because the statement asks for a README with *exact* commands per table and figure; scripts plus `make` targets satisfy that literally.

---

## 7. Integration Feasibility Report

This project has no external services at runtime. The "integrations" are the local toolchain and the delivery channels.

### 7.1 Python toolchain (uv)

| Item | Detail |
|---|---|
| SDK / packages | Python ≥ 3.12 (3.12 present). Runtime: `numpy`, `scipy` (Mann–Whitney), `pandas`, `matplotlib`. Dev: `pytest`, `hypothesis` (property tests for incremental eval), `ruff`. |
| Credential type | none |
| Existing or to-create | `uv` installed at `~/.local/bin/uv`; `make` at `/usr/bin/make` ✅ |
| Setup steps | 1. `uv init --package --name tp2 --python 3.12` (then reshape to `src/tp2`) 2. `uv add numpy scipy pandas matplotlib` 3. `uv add --dev pytest hypothesis ruff` 4. commit `pyproject.toml` + `uv.lock` |

**Operations:** `uv sync`, `uv run pytest`, `uv run python -m tp2.<module>`. Windows teammates without `uv`/`make` follow the README fallback: `python -m venv .venv && .venv\Scripts\pip install -e .[dev]`, same as TP1's README pattern.

**Potential issues:** `pip install` is blocked system-wide on this machine (PEP 668), so always go through `uv`. Matplotlib needs no GUI backend (`MPLBACKEND=Agg` set in the Makefile).

**Overall feasibility:** ✅ — everything is installed locally except the Python packages, which `uv` fetches.

### 7.2 LaTeX / Overleaf (report)

| Item | Detail |
|---|---|
| Tooling | TP1 used `relatorio/main.tex` + `referencias.bib` + `figuras/`. Locally, `pdflatex`/`latexmk` are **not installed** (checked 2026-10-14). |
| Credential type | Overleaf account (if Git sync is used: Overleaf Git token, which goes in `CREDENTIALS.md`) |
| Existing or to-create | **Decided 2026-10-14:** compile locally with TeX Live (`make report`) while writing; export `relatorio/` as a zip to an Overleaf project for the group's final edits. |
| Setup steps | Read `.agents/skills/overleaf/SKILL.md` first. Option A: Overleaf Git integration (premium; user `git` + token). Option B: zip upload of `relatorio/`. Option C: install TeX Live locally (`sudo apt install latexmk texlive-latex-extra texlive-lang-portuguese`), which needs sudo. |

**Potential issues:** generated `tabelas/*.tex` and `figuras/*.pdf` must reach Overleaf after each analysis run, so a manual upload every time is error-prone. Prefer Git sync (A) or local TeX (C).

**Overall feasibility:** ✅ — local TeX Live (Bruno installs it with `sudo apt install latexmk texlive-latex-extra texlive-lang-portuguese texlive-science` before M8), then Overleaf by zip upload.

### 7.3 GitHub (code delivery)

| Item | Detail |
|---|---|
| Repo | `BrunoL28/tp2-fundia`, **private** |
| Delivery | **Decided 2026-10-14: clean zip** (`make zip`). It contains only code, tests, configs, results, build files, the delivery README, the instances and the report PDF. No agent-protocol files (`CLAUDE.md`, `AGENTS.md`, `NEXT_UP.md`, `CONTEXT.md`, `IMPLEMENTATION_PLAN.md`, `.agents-skills`). |
| Collaborators | `BrunoL28` (admin); Arthur Fernandes (`EluriaTecnologia`, write; invite sent 2026-10-14). |
| Potential issues | The machine has two `gh` accounts; `BrunoL28` is active since 2026-10-14. If `bruno-soares-meerkat` is active again, use `gh auth switch -u BrunoL28`. |

**Overall feasibility:** ✅ — clean zip via `make zip`.

---

## 8. Pre-Build Checklist

- [x] Delivery deadline: **2026-10-18**. Submission channel still to confirm (owner: Bruno).
- [ ] Group: Bruno + Arthur confirmed; Felipe pending (owner: Bruno). Update `CONTEXT.md` §2 and the report cover.
- [x] Report workflow: local TeX Live, then Overleaf by zip (§7.2).
- [x] Review and approve this plan's design decisions, especially: extended interface (`sucessores` yields `(move, h)`), all three GD variants, offline SA calibration per instance (not counted in B), GA defaults, and the extra experiment design (owner: group).
- [ ] Create the package skeleton and `uv.lock` (C0), then turn the verified scratch facts into tests before writing any algorithm.

---

## 9. Component-by-component breakdown

### C0 — Scaffolding

- **Type:** repo layout + build files
- **Job:** a reproducible environment with one-command targets.
- **Layout:**
  ```
  pyproject.toml            # [project] name="tp2", requires-python=">=3.12"; [tool.uv] package=true
  uv.lock
  Makefile
  src/tp2/
    __init__.py
    core/interface.py       # C1
    core/counting.py        # C2
    core/recorder.py        # telemetry sink used by algorithms
    problem/instance.py     # C3
    problem/maintenance.py  # C4
    problem/neighborhoods.py# C5
    problem/operators.py    # C6
    algorithms/greedy_descent.py      # C7
    algorithms/simulated_annealing.py # C8
    algorithms/genetic.py             # C9
    experiments/configs.py  # all parameter sets, budgets, run counts
    experiments/runner.py   # C10 CLI
    experiments/calibrate_sa.py
    analysis/stats.py       # C11
    analysis/tables.py
    analysis/plots.py
    verify.py               # C12
  configs/sa_pequena.json, sa_media.json, sa_grande.json   # output of calibrate_sa
  tests/
  results/                  # dated result folders + LATEST_* pointers
  relatorio/                # main.tex, referencias.bib, tabelas/, figuras/
  ```
- **Makefile targets (exact):**
  ```make
  export MPLBACKEND=Agg
  BASE_SEED ?= 20261014
  JOBS ?= $(shell nproc)

  setup:        ; uv sync
  test:         ; uv run pytest -q
  lint:         ; uv run ruff check src tests
  verify:       ; uv run python -m tp2.verify | tee results/verify.txt
  calibrate-sa: ; uv run python -m tp2.experiments.calibrate_sa --all --seed $(BASE_SEED)
  t2: verify    ; uv run python -m tp2.experiments.runner --suite t2 --seed $(BASE_SEED) --jobs $(JOBS)
  experiments: verify ; uv run python -m tp2.experiments.runner --suite t3 --seed $(BASE_SEED) --jobs $(JOBS)
  extra: verify ; uv run python -m tp2.experiments.runner --suite extra --seed $(BASE_SEED) --jobs $(JOBS)
  tables:       ; uv run python -m tp2.analysis.tables
  figures:      ; uv run python -m tp2.analysis.plots
  analysis: tables figures
  report:       ; cd relatorio && latexmk -pdf main.tex
  zip:          ; ./scripts/make_zip.sh
  all: setup test verify calibrate-sa t2 experiments extra analysis
  ```
- **Next:** C1–C4.

### C1 — `Problem` interface

- **Type:** module `tp2/core/interface.py`
- **Job:** the only thing algorithms know about.
- **Code:**
  ```python
  from typing import Protocol, Iterator, Hashable, Sequence
  import random

  Solution = list[int]          # permutation of 1..n (opaque to algorithms)
  Move = Hashable                # opaque; produced by sucessores/sucessor_aleatorio

  class Problem(Protocol):
      def solucao_aleatoria(self, rng: random.Random) -> Solution: ...
      def h(self, s: Solution) -> int: ...                       # counted
      def sucessores(self, s: Solution, h_s: int,
                     rng: random.Random | None = None) -> Iterator[tuple[Move, int]]: ...
                                                                  # each yield counted; rng → shuffled order (first improvement)
      def sucessor_aleatorio(self, s: Solution, h_s: int,
                             rng: random.Random) -> tuple[Move, int]: ...   # counted
      def aplicar(self, s: Solution, mov: Move) -> Solution: ...  # NOT counted (no evaluation)
      def cruzamento(self, s1: Solution, s2: Solution, rng: random.Random) -> tuple[Solution, Solution]: ...
      def mutacao(self, s: Solution, rng: random.Random) -> Solution: ...
      def distancia(self, s1: Solution, s2: Solution) -> int: ...  # for GA diversity; NOT counted
      def tamanho_vizinhanca(self) -> int: ...                     # for random-successor restart rule
  ```
  `h_s` is passed in so the problem can (re)build its prefix cache for s without an extra counted evaluation. **Rule:** the cache is keyed on `tuple(s)` hash plus `h_s`. On a miss it recomputes the prefix arrays *without* counting, because the statement counts evaluations of candidate solutions, not bookkeeping. This is stated explicitly in the report. Debug mode asserts that the recomputed h equals `h_s`.
- **Output:** n/a.
- **Next:** C2 wraps it.

### C2 — `CountingProblem`

- **Type:** class in `tp2/core/counting.py`
- **Job:** count evaluations, enforce the budget, record best-so-far and the convergence trace.
- **Code (essentials):**
  ```python
  class BudgetExhausted(Exception): ...

  class CountingProblem:
      def __init__(self, inner, budget: int, checkpoints: int = 200):
          self.inner, self.B = inner, budget
          self.evals = 0
          self.best_h, self.best_s = math.inf, None
          self.improvements: list[tuple[int, int]] = []        # (evals, best_h)
          self._grid = [round(k * budget / checkpoints) for k in range(checkpoints + 1)]
      def _tick(self, hv, s_or_thunk):
          if self.evals >= self.B: raise BudgetExhausted
          self.evals += 1
          if hv < self.best_h:
              self.best_h = hv
              self.best_s = s_or_thunk() if callable(s_or_thunk) else list(s_or_thunk)
              self.improvements.append((self.evals, hv))
          return hv
      def h(self, s):                       return self._tick(self.inner.h(s), s)
      def sucessores(self, s, h_s, rng=None):
          for mov, hv in self.inner.sucessores(s, h_s, rng):
              self._tick(hv, lambda: self.inner.aplicar(s, mov)); yield mov, hv
      def sucessor_aleatorio(self, s, h_s, rng):
          mov, hv = self.inner.sucessor_aleatorio(s, h_s, rng)
          self._tick(hv, lambda: self.inner.aplicar(s, mov)); return mov, hv
      # aplicar / cruzamento / mutacao / distancia / solucao_aleatoria: delegate, no count
      def curve(self) -> list[tuple[int, int]]:  # best_h at each grid point (step function from improvements)
  ```
  The check comes **before** the increment, so exactly B evaluations happen and the (B+1)-th raises. `best_s` is materialized lazily, only on improvement.
- **Output:** after the run: `evals == B` (assert in the runner), `best_h`, `best_s`, `curve()`.
- **Tests:** a dummy problem with a counter runs a loop of B+10 `h` calls: exactly B succeed. `sucessores` stops mid-iteration at B. The `best_s` re-evaluated with the inner `h` equals `best_h`.
- **Next:** algorithms receive a `CountingProblem` typed as `Problem`.

### C3 — Instance loader

- **Type:** `tp2/problem/instance.py`
- **Job:** parse `manutencao_*.txt` and precompute the travel matrix.
- **Code:**
  ```python
  @dataclass(frozen=True)
  class Instance:
      name: str; n: int
      xy: tuple[tuple[int, int], ...]   # index 0 = base, 1..n = assets
      p: tuple[int, ...]; d: tuple[int, ...]; w: tuple[int, ...]   # index 0 = base (p0 = 0, d0 = w0 = 0)
      T: tuple[tuple[int, ...], ...]    # (n+1)×(n+1), T[i][j] = round(hypot(dx, dy))

  def load_instance(path) -> Instance:
      tok = Path(path).read_text().split()
      n = int(tok[0]); assert len(tok) == 3 + 5 * n
      ...
  ```
  Rounding uses `round(math.hypot(dx, dy))`. Integer coordinates mean no exact .5 ties can occur (√k = m + ½ ⇒ k = m² + m + ¼, not an integer), so Python's banker's rounding is safe. A comment in the code says so, and a test asserts no T entry came from an exact half.
- **Output:** `Instance(n=12, …)` etc.
- **Tests:** n and Σp for the 3 files equal 12/55, 50/239, 150/684. Base (50,50) for all.
- **Next:** C4.

### C4 — `MaintenanceProblem` (full fitness)

- **Type:** `tp2/problem/maintenance.py`
- **Job:** implement the Protocol for this problem. The neighborhood and operators are injected by configuration.
- **Code (full h):**
  ```python
  def h(self, s):
      T, P, D, W = self.T, self.P, self.D, self.W
      prev = 0; C = 0; tot = 0
      for j in s:
          C += T[prev][j] + P[j]; prev = j
          late = C - D[j]
          if late > 0: tot += W[j] * late
      return tot
  ```
  Constructor: `MaintenanceProblem(instance, vizinhanca="swap"|"insertion"|"2opt", crossover="ox"|"pmx", mutacao="swap"|"insertion"|"2opt", incremental=True)`.
  `solucao_aleatoria`: `rng.sample(range(1, n+1), n)`.
  `distancia(s1, s2)`: number of positions k with `s1[k] != s2[k]` (Hamming on positions). It's simple, O(n), and matches the "gene = position" view from Fig. 2. Kendall-tau distance would also be an option, and is mentioned in the report as an alternative.
- **Tests (pytest, before any algorithm):**
  - `h(identity, pequena) == 4366`.
  - Toy instance (fixture `tests/fixtures/toy4.txt`: `4 / 0 0 / 3 4 2 10 3 / 6 0 3 14 1 / 0 8 1 25 2 / 6 8 4 20 5`): `h([1,4,2,3]) == 39`, `h([1,4,3,2]) == 22`, brute force over 24 permutations gives min 22, unique.
  - Greedy reference: `greedy_min_increment(pequena, tiebreak="travel") == 3168` (documents the tie-break; used as the baseline line in the plots).
  - Nearest neighbour on pequena == 2590 (baseline).
- **Next:** C5.

### C5 — Neighborhoods + incremental evaluation

- **Type:** `tp2/problem/neighborhoods.py`
- **Job:** enumerate, sample, apply and incrementally evaluate moves for the three operators of Fig. 3.
- **Move encodings and semantics (0-based positions):**
  | Operator | Move | `aplicar` | Distinct neighborhood size | n=12 | n=50 | n=150 |
  |---|---|---|---|---|---|---|
  | Swap | `("S", i, j)`, i<j | exchange s[i], s[j] | n(n−1)/2 | 66 | 1 225 | 11 175 |
  | Insertion | `("I", i, j)`, i≠j, excluding `j == i−1` | pop s[i], insert at j | (n−1)² | 121 | 2 401 | 22 201 |
  | 2-opt | `("R", i, j)`, i<j | reverse s[i..j] | n(n−1)/2 | 66 | 1 225 | 11 175 |

  Insertion detail: moving element i to position i+1 produces the same permutation as moving element i+1 to position i. Enumerating i≠j gives n(n−1) moves with n−1 duplicate pairs, hence (n−1)² distinct. We enumerate exactly the distinct set (skip `j == i−1`) so "neighborhood scan cost" is exact. Note also that swap(i, i+1) ≡ 2-opt(i, i+1): the two neighborhoods share n−1 elements. This is worth one sentence in the report because it shows that they overlap but aren't equivalent (Fig. 3 caption).
- **Incremental Δ-evaluation (all three):**
  ```python
  # prefix cache for current s: Cpre[k] = completion time after position k (Cpre[-1] = 0),
  # Hpre[k] = cost of positions 0..k, node[k] = s[k] (node[-1] = 0 = base)
  def eval_from(self, s_new, start, Cprev, Hprev, prev_node):
      C, tot, prev = Cprev, Hprev, prev_node
      for k in range(start, n):
          j = s_new[k]; C += T[prev][j] + P[j]; prev = j
          late = C - D[j]
          if late > 0: tot += W[j] * late
      return tot
  ```
  For a move with first touched position a = min(i, j): `h' = eval_from(s', a, Cpre[a−1], Hpre[a−1], node[a−1])`. To avoid allocating s' for every move, iterate positions a..n−1 through an index-mapping function per operator (`pos → element`) instead of materializing the list. Swap maps positions i↔j. 2-opt maps k ∈ [i, j] → s[i + j − k]. Insertion is a shifted window between i and j.
- **Optional optimization (Known Holes #6):** after the last touched position b = max(i, j), the suffix is the same sequence shifted by δ = C'_b − C_b. If δ = 0 we can return `Hpre[n−1] − Hpre[b] + (partial)` immediately. If δ ≠ 0 we still need the scan (max(0,·) isn't linear). Implement it only if T2 shows evaluation time matters.
- **Tests:** a `hypothesis` property over random instances (n ∈ [2, 30]) × random permutations × every move. Incremental h' must equal the full `h(aplicar(s, mov))`. Plus exhaustive checks on the toy instance and on pequena for all moves of 50 random permutations. Also: the move count per scan equals the table above, and all successors are distinct and differ from s.
- **Timing (for T2 and the report):** `moves_timing.csv`, giving µs per evaluated move, full vs incremental, per operator per instance (10⁵ random moves, `time.perf_counter_ns`).
- **Next:** C6, C7.

### C6 — Crossover and mutation operators

- **Type:** `tp2/problem/operators.py`
- **OX (Order Crossover, main):** pick cut points a<b uniformly. The child keeps `p1[a..b]` in place, then fills the remaining positions starting at b+1 (wrapping around) with p2's genes in p2's order starting at b+1, skipping genes already present. The symmetric child swaps the parents' roles. This is the class version (Part 3 slide 15/30: "copia bloco do Pai 1; preenche os vazios seguindo a ordem das corridas no Pai 2"). **Check the class's fill convention against the slide example:** P1 = (C1 C2 C3 C4 C5), P2 = (C5 C4 C2 C1 C3), child = (C5 C2 C3 C4 C1). That corresponds to block = positions 1..3 (C2 C3 C4) and filling the free positions **left to right from position 0** with P2's order (C5, C1). It's **not** the textbook "start after b" variant. Implement the slide's convention (left-to-right fill) as `ox`, keep `ox_classic` (Davis 1985, wrap from b+1) as an option, and unit-test the slide example exactly.
- **PMX (deferred, §3):** standard Goldberg & Lingle mapping with chained repair. Only if time is left after M9.
- **Step-by-step numeric example for the report (§2.5 requires one):** generated by `python -m tp2.problem.operators --demo ox --seed 1 --n 8`, which prints parents, cut points, the intermediate fill and the child. The output is pasted into the report as a table, not as code.
- **Mutation:** `mutacao(s)` applies **one** random move of the configured operator (**insertion**, chosen in T2; CONTEXT §8) with probability Pm per individual. Pm is the per-individual probability, documented as such. Per-gene rates would also be possible but make Pm harder to compare.
- **Tests:** children are always valid permutations (hypothesis); OX on the slide example yields exactly (5,2,3,4,1).
- **Next:** C9.

### C7 — Greedy Descent + Random Restart

- **Type:** `tp2/algorithms/greedy_descent.py`
- **Job:** statement §2.3.
- **Variants:**
  - `best`: scan `sucessores(s, h_s)` entirely, take the min h (ties → first encountered). If min h ≥ h_s → local optimum → restart.
  - `first`: scan `sucessores(s, h_s, rng)` in a **random order** (shuffled move list each step, to avoid positional bias). Accept the first move with h < h_s. If the full scan has no improvement → local optimum → restart.
  - `random`: `sucessor_aleatorio`, accept if h < h_s. There's no exact local-optimum test, so restart after **K consecutive non-improving samples**, with **K = neighborhood size** by default (one "virtual scan"). The parameter is `k_factor` (K = k_factor · |N|), and the sensitivity is noted in the report. With K = |N| and sampling with replacement, the probability of missing a specific single improving move is (1 − 1/|N|)^|N| ≈ e⁻¹ ≈ 37%. That's an honest number to quote.
- **Pseudocode:**
  ```python
  def run(P, rng, variant, rec):
      while True:                                  # until BudgetExhausted propagates
          s = P.solucao_aleatoria(rng); hs = P.h(s)   # restart evaluation counts 1
          steps = 0
          while True:
              mov, hv = select(variant)            # counted inside P
              if mov is None or hv >= hs: break    # local optimum (best/first) / K failures (random)
              s = P.aplicar(s, mov); hs = hv; steps += 1
          rec.local_optimum(hs, s, steps, is_true_local_opt = variant != "random")
  ```
  The current solution's h is never recomputed: it's carried as `hs`, so there's no hidden extra evaluation. Restarts count exactly 1 (the new random solution).
- **Telemetry:** per restart: h of the local optimum, a hash of the permutation (to count **distinct local optima**, statement §5 bullet 1), the number of improvement steps, and whether the budget cut the descent mid-way (incomplete descents are not counted as local optima). Per run: total improvement steps (statement §2.3: "reporte quantos passos de melhoria cada variante consegue dar").
- **Expected behavior to discuss:** at n = 150 with swap, `best` spends 11 175 evals per step, so ≤ 26 improvement steps in 300k. It will likely **never reach a local optimum** from a random start, because random starts need hundreds of improving steps. `first` takes many cheap steps early and gets expensive near local optima. This is the core of the "scale effect" discussion.
- **T2 uses `first`.** It's the variant that actually reaches local optima on all instances within budget, so "which neighborhood gives better local optima" is answerable. T3 reports `first` as algorithm (A), and also runs `best` and `random` as the required variant comparison (main table row for (A) = the best variant, chosen on the medium instance; all variants in an appendix table).
- **Next:** C10.

### C8 — Simulated Annealing + calibration

- **Type:** `tp2/algorithms/simulated_annealing.py`, `tp2/experiments/calibrate_sa.py`
- **Algorithm:**
  ```python
  def run(P, rng, T0, Tf, alpha, L, rec):
      s = P.solucao_aleatoria(rng); hs = P.h(s); T = T0
      while True:
          for _ in range(L):                       # L evaluations per temperature level
              mov, hv = P.sucessor_aleatorio(s, hs, rng)
              d = hv - hs
              if d <= 0 or rng.random() < math.exp(-d / T):
                  s = P.aplicar(s, mov); hs = hv
              rec.sa_step(worse=(d > 0), accepted=…)
          T = max(T * alpha, Tf)                   # geometric; floor at Tf
  ```
  With L and α tied to the budget so that T reaches Tf exactly at B: number of levels M = B / L, α = (Tf / T0)^(1/(M−1)). The run ends by budget; at the end T ≈ Tf.
- **Calibration (per instance, offline, deterministic seed, NOT counted in B):**
  1. Sample 2 000 random (s, random move) pairs from random permutations. Collect Δ⁺ = positive Δh. Set **T0 = −median(Δ⁺) / ln(χ0)** with χ0 = 0.9, meaning ~90% of typical worsening moves are accepted at the start ("começa praticamente como random walk").
  2. **Tf = −q10(Δ⁺) / ln(χf)** with χf = 10⁻³, from the same sample, so even small worsenings (10th percentile) are almost never accepted at the end ("termina praticamente como greedy descent"). Δ⁺ near local optima is larger (q10 ≈ 1 760–1 980 vs 1 129 on grande), so acceptance there is even lower. *Changed in M4:* the original rule sampled Δ⁺ around 3 local optima, but full descents cost > 150k evaluations per optimum on grande (503k in total, more than B), and an exploratory pilot on seeds outside the protocol (10 runs, media/grande) didn't favour it: median 17 572 vs 17 836 on media, 89 576 vs 83 464 on grande.
  3. L = 100 (pequena), 300 (media), 1 000 (grande). α then follows from the formula above (with B − 1 steps after the initial evaluation). The values are stored in `configs/sa_<inst>.json` with the sampled statistics (median, q10, sample sizes, evaluations spent), so the report can show the calibration table. Calibrated (M4): T0 = 5 481 / 25 019 / 63 416, Tf = 14.8 / 62.3 / 163.4, α = 0.98822 / 0.98806 / 0.98026.
  4. Justification sentence for the report: Δh scales with n (tens on pequena, thousands on grande; statement §2.4). A fixed T across instances would be a random walk on one and greedy descent on another. The per-instance calibration makes the *acceptance profile*, not the temperature, the thing that's held constant.
  - Is calibration "free"? It's tuning, like choosing N/Pc/Pm for the GA. We disclose its cost in the report: 4 000 evaluations per instance (2 000 random solutions + 1 successor each) = 8% / 2.7% / 1.3% of B, done once per instance, not per run (Known Holes #7; the sensitivity check is deferred).
- **Telemetry:** windows of W = B/100 evaluations: `worse_proposed`, `worse_accepted`, `rate`, `T` at the window end → `sa_acceptance.csv`. Plot: rate vs evaluations, one median line per instance with an IQR band. The expected shape is ≈ 0.9 at the start → ≈ 0 at the end. If the start is ≪ 0.9 or the end ≫ 0, the calibration failed, and that's the diagnostic the statement wants (§6 "SA mal calibrado vira outro algoritmo").
- **Next:** C10.

### C9 — Genetic Algorithm

- **Type:** `tp2/algorithms/genetic.py`
- **Defaults (to be confirmed by a small pilot on media; the pilot is reported):**
  | Param | pequena | media | grande | Note |
  |---|---|---|---|---|
  | N | 50 | 100 | 100 | population |
  | selection | tournament k=3 | k=3 | k=3 | on raw h (lower wins) |
  | Pc | 0.9 | 0.9 | 0.9 | per pair |
  | Pm | 0.2 | 0.2 | 0.2 | per child, one move of `mutacao` op |
  | elitism | e = 2 | 2 | 2 | best e of P survive into P_new |
  | generations (≈ (B−N)/(N−e)) | ~1 041 | ~1 530 | ~3 060 | budget-driven, last generation partial |
- **Loop (class pseudocode, Part 3 slide 18/30, with elitism made explicit):**
  ```python
  P = [P_.solucao_aleatoria(rng) for _ in range(N)]; H = [P_.h(s) for s in P]   # N evals
  gen = 0
  while True:
      elite = top_e(P, H, e)
      kids, kh = [], []
      while len(kids) < N - e:
          a, b = tournament(P, H, k, rng), tournament(P, H, k, rng)
          c1, c2 = P_.cruzamento(a, b, rng) if rng.random() < Pc else (a[:], b[:])
          for c in (c1, c2):
              if rng.random() < Pm: c = P_.mutacao(c, rng)
              if len(kids) < N - e: kids.append(c); kh.append(P_.h(c))   # 1 eval each (may raise BudgetExhausted)
      P, H = elite.solutions + kids, elite.h + kh
      rec.ga_generation(gen, evals, min(H), mean(H), distinct(P), mean_pairwise_dist(P, sample=200))
      gen += 1
  ```
  Every child is evaluated and counted, including unchanged clones (conservative and simple). Caching clone fitness would be legal ("no evaluation happened") but complicates the fairness argument (Known Holes #8).
- **Cost→fitness conversion (statement asks to explain):** tournament selection compares h directly (lower wins). It's rank-based, so no transformation is needed and it's invariant to h's scale. That's an argument *for* tournament here, since h spans 10³–10⁶ across instances. For completeness the report notes what roulette would require: f = h_max(P) − h + ε, or 1/(1+h), and its scale sensitivity.
- **Diversity:** `distinct` = number of distinct permutations in P. `mean_dist` = mean Hamming-position distance over 200 random pairs (O(200·n) per generation, not counted). Plot: diversity vs generations, plus best and mean h curves (statement §3 "curva da média da população").
- **Next:** C10.

### C10 — Experiment runner

- **Type:** `tp2/experiments/runner.py` + `configs.py`
- **CLI:** `--suite {t2,t3,extra,pilot}`, `--seed`, `--jobs`, `--resume`, `--only ALG@INST` (debug), `--out results/<date>_<label>`.
- **`runs.csv` columns (as built in M3):** `run_id, suite, algoritmo, variante, vizinhanca, instancia, n, run, seed, orcamento, evals, best_h, ref_h, gap (vs Table 1 reference), wall_s, passos, descidas, otimos_locais, otimos_distintos (GD), params (JSON with the algorithm's parameters), best_perm (space-separated), git_commit, status`. SA/GA summary columns are added in M4/M5; each results folder keeps the header it was created with.
- **Seeds:** `seed = BASE_SEED + 1000 * instance_idx + run`. All algorithms on the same instance and run index share the seed for `solucao_aleatoria`'s first draw. This doesn't make samples paired for the Mann–Whitney test (which is unpaired), but it removes one source of variance in the curves.
- **Post-run assertions:** `evals == budget`; `h(best_perm)` recomputed by a fresh, uncounted `MaintenanceProblem` equals `best_h`.
- **Wall time:** `time.perf_counter()` around `run()` only (excluding I/O). Machine info goes in `config.json`. Runs execute in parallel on separate processes, so per-run wall time is comparable across algorithms. We note that parallel load adds noise, and also time a sequential subset of 3 runs per cell for the time table (Known Holes #9).
- **Expected compute:** pequena 50k × 90 runs, media 150k × 90, grande 300k × 30. That's ≈ 27M evals for the 9 main cells, plus 2 more GD variants for (A) (another ≈ 18M), ≈ 10–15 min on 15 workers including Python overhead. T2 (3 neighborhoods) and extra (4 GA variants) are of the same order. The full pipeline should finish in < 1 h.

### C11 — Analysis

- **Type:** `tp2/analysis/{stats,tables,plots}.py`
- **Tables (`relatorio/tabelas/`):**
  - `principal.tex`: 9 rows (instance × algorithm): mean ± sd, median, min (= best), gap% (pequena), mean wall s, evals (= B). This is statement §5 item 1 plus item 5.
  - `testes.tex`: per instance, 3 pairwise Mann–Whitney tests: U, p (raw), p (Holm), A12, and the winner, or "—" when p_Holm ≥ 0.05.
  - `gd_variantes.tex`: best/first/random improvement steps, local optima reached, best h, on each instance.
  - `t2_vizinhancas.tex`: neighborhood size formula and value per n; best h per neighborhood; µs/move full vs incremental; speedup.
  - `sa_calibracao.tex`: per instance: median Δ⁺, q10 Δ⁺_local, T0, Tf, α, L.
  - `ga_parametros.tex`: N, k, Pc, Pm, e, generations.
  - `otimos_locais.tex`: pequena, number of distinct local optima found by GD (per variant, total and per run), runs reaching 1875 for each algorithm.
  - `extra.tex`: extra experiment results and tests.
- **Figures (`relatorio/figuras/`):**
  - `boxplot_<inst>.pdf` ×3: three algorithms, with horizontal reference lines at the reference value (1875 / 16 332 / 60 417) and the greedy baseline.
  - `convergencia_<inst>.pdf` ×3: best h vs evaluations, median per algorithm, with an IQR band. GA adds the population-mean median curve. Log-y if the range spans more than 10×.
  - `sa_aceitacao.pdf`: acceptance rate vs evaluations, 3 instances.
  - `ga_diversidade.pdf`: distinct and mean distance vs generation, 3 instances.
  - `t2_<inst>.pdf`: boxplots per neighborhood.
  - `extra_<inst>.pdf`: GA variant boxplots.
- **Consistency:** one color per algorithm, set in a single `STYLE` dict; PDF output; fonts embedded.

### C12 — `verify`

- Prints: instance summary (n, Σp), `h(identidade) = 4366 ✔`, toy `39 ✔ / 22 ✔`, greedy (min increment, tie by travel) `= 3168 ✔`, nearest neighbour `= 2590`. If `results/LATEST_T3` exists, it also prints any permutation with h = 1875 found by our algorithms, re-evaluated. Exit code 1 on mismatch. The output goes into the report verbatim, as T1 requires.

### C13 — Extra experiment (GA pays off?)

- Specified in FR-4. The report must contain: the hypothesis (as stated), the design (four GA variants, same budget, same runs), the result table and tests, and a one-paragraph conclusion. A useful supporting measurement is the **offspring improvement rate**: the fraction of children with h < min(h_parent1, h_parent2) for OX vs headless chicken. It's logged by the GA when `--log-offspring` is on.

### C14 — Report

- **Structure (target ~5 pages plus appendices; PT-BR):**
  1. Introdução e problema (½ p): one paragraph plus the instance table.
  2. Implementação (¾ p): interface (with the extension argument), counting, incremental evaluation (gain table pointer), neighborhood sizes, OX worked example, cost→fitness for tournament, SA calibration table.
  3. T1 — verificação (¼ p): verbatim `verify` output.
  4. T2 — vizinhanças (½ p): table plus one figure; the chosen neighborhood and why.
  5. T3 — resultados (1½ p): main table, boxplots, convergence, tests, time vs evaluations.
  6. Discussão (1½ p): four mandatory bullets plus the extra experiment.
  7. Conclusão (¼ p).
  - Appendices: GD variants table, SA acceptance plot, GA diversity plot, parameter tables, reproduction commands.
- **Writing:** follow `.agents/skills/humanize-text/SKILL.md`. Every comparative claim cites a p-value from `testes.tex`.
- **Build:** local TeX Live (`make report`), then a zip export to Overleaf (§7.2).

### C15 — Delivery

- `README.md` section "Como reproduzir": a table with one row per table and figure in the report → the exact `make` command and the output file.
- `scripts/make_zip.sh`: `git archive` HEAD + `results/LATEST_*` folders + `relatorio/main.pdf`, excluding `INPUTS/slides`, `.agents-skills`, `archive`, `tmp`.

---

## 10. Known Holes & Open Items

| # | Item | Status | Action |
|---|---|---|---|
| 1 | Delivery deadline and channel | Deadline ✅ 2026-10-18; channel Open | Bruno: confirm the submission channel (Moodle?) |
| 2 | Group composition for TP2 | Open (Felipe) | Bruno + Arthur confirmed 2026-10-14; Felipe Augusto still undefined. Needed for the report cover and README |
| 3 | Toy instance coordinates aren't in the statement | ✅ Resolved 2026-10-14 | Reconstructed: 1=(3,4), 2=(6,0), 3=(0,8), 4=(6,8); verified 39/22 unique optimum |
| 4 | Report workflow | ✅ Resolved 2026-10-14 | Local TeX Live → Overleaf by zip (§7.2). Bruno must install TeX Live before M8 |
| 5 | Interface extension (`sucessores` yields `(move, h)`, extra `aplicar`, `h_s` param) vs the statement's "sugestão mínima" | Low risk | Keep; justify in report §2 as necessary for incremental evaluation without leaking the problem into algorithms |
| 6 | Incremental eval suffix early-exit (δ = 0 after last touched position) | Deferred | Only if T2 timing shows evaluation dominates |
| 7 | SA calibration evaluations not counted in B | Low risk | Decided 2026-10-14: disclose in the report as offline hyperparameter tuning. Cost measured in M4: 4 000 evaluations per instance (8% / 2.7% / 1.3% of B), once per instance. The sensitivity check is deferred (§3) |
| 8 | GA counts unchanged clones as evaluations | Low risk | Conservative choice; mention it. An alternative cache would favor the GA slightly |
| 9 | Wall time measured under parallel load | ✅ Resolved 2026-10-15 | `make tempos` → `results/2026-10-15_tempos/`: the T3 cells, 3 runs per instance, 1 process. The time table uses these |
| 10 | Delivery format | ✅ Resolved 2026-10-14 | Clean zip (`make zip`), no agent-protocol files (§7.3) |
| 11 | Greedy 3168 depends on an unstated tie-break | Low risk | Documented (tie → min travel time); cite it in the report as our reproduction |
| 12 | Which GD variant represents algorithm (A) in the main table | ✅ Resolved 2026-10-15 | Rule applied to T3: best median on media → `random` (17 366 vs `first` 17 457.5, `best` 20 054.5). All variants go in the appendix table; M7 tests whether random vs first differ |

---

## 11. Build Order

Delivery schedule approved 2026-10-14 (deadline **2026-10-18**). Each mission is one branch and one PR into `main`.

**Git flow (all missions):**
- `git switch -c <branch>` from an up-to-date `main` → commits → `git push -u origin <branch>` → `gh pr create` (title and description in PT-BR: what changes, how to test, test evidence).
- Squash-merge **only after Bruno approves**. To keep the schedule, the next mission may branch off the previous unmerged one (stacked PR) and is rebased onto `main` after the merge.
- Merge gate: CI green (`uv sync` + `ruff` + `pytest`) and `make verify` OK.
- Every PR also updates `NEXT_UP.md` (date bump) and the §1 status for its components. A mission ends when its PR is merged.
- **No attribution:** commit messages, PR texts, branch names and code comments carry no AI/assistant mention or co-author trailer (see `CLAUDE.md` / `AGENTS.md`).

| Day | Mission | Branch | Content (components in §9) | Done when |
|---|---|---|---|---|
| 14/10 | **M0** Delivery plan | `docs/plano-entrega` | Deadline, decisions, scope cut and this schedule in the state docs; no-attribution rule in `CLAUDE.md`/`AGENTS.md` | PR merged |
| 14/10 | **M1** Foundation + fitness | `feat/fundacao-fitness` | C0 (`pyproject.toml` via `uv`, `uv.lock`, `Makefile`, `.github/workflows/ci.yml`), C3, C4 full `h`, C12 `make verify`, `tests/fixtures/toy4.txt`. Tests: 4366, toy 39/22 plus brute-force unique optimum, Σp 55/239/684, greedy 3168 (tie → travel), NN 2590 | CI green; `make verify` prints every ✔ |
| 14–15/10 | **M2** Interface, counter, neighborhoods | `feat/vizinhancas` | C1, C2 (`BudgetExhausted` at evaluation B+1, best-so-far trace), C5 swap/insertion/2-opt with incremental evaluation, AST architecture test, timing script | Hypothesis: incremental == full; sizes 66/1225/11175 and 121/2401/22201; exact budget |
| 15/10 | **M3** Local search + runner + T2 | `feat/busca-local-t2` | C7 (best / first / random with K = \|N\|), C10 (multiprocessing, seeds, append CSV, `--resume`), `t2` suite. Run T2 → `results/2026-10-15_t2/`; record the chosen neighborhood in CONTEXT §8 and `configs.py` | `evals == B` on every row; neighborhood chosen with a justification |
| 15/10 | **M4** Simulated annealing | `feat/simulated-annealing` | C8 (geometric, α derived from B and L), `calibrate_sa` → `configs/sa_*.json`, windowed acceptance log | Acceptance ≈ 0.9 → ≈ 0 on all 3 instances (1-run pilot) |
| 15–16/10 | **M5** Genetic algorithm | `feat/algoritmo-genetico` | C6 (OX with the slide convention, exact test (5,2,3,4,1); one-move mutation; `--demo ox`), C9 (tournament k=3, Pc=0.9, Pm=0.2, elitism 2, budget-only stop, diversity log). Quick pilot on media | Children always valid permutations; diversity logged per generation |
| 16/10 | **M6** T3 + extra experiments | `exp/t3-extra` | `make experiments` (3 algorithms × 3 instances × 30/30/10 + GD variants) and `make extra` (OX × Pc = 0 × headless chicken). CSVs + `config.json` in `results/2026-10-16_*`, `LATEST_*` pointers | No `status=error`; re-evaluated h(best_perm) == best_h; pequena reaches 1875 in some run (expected) |
| 16/10 | **M7** Analysis | `feat/analise` | C11 tables and figures | `make analysis` regenerates everything from the CSVs; group reviews the numbers |
| 17/10 | **M8** Report | `docs/relatorio` | TeX Live installed by Bruno; C14 `relatorio/main.tex` + `referencias.bib` (~5 pp + appendices, no code), verbatim `verify` output, the 4 mandatory discussions with p-values; `make report`; zip export to Overleaf (read `.agents/skills/overleaf` first) | PDF compiles locally and on Overleaf; every number comes from generated tables |
| 17/10 | **M9** Delivery | `chore/entrega` | C15: delivery README (PT-BR, "Como reproduzir" table), `scripts/make_zip.sh` | Clean clone reproduces the CSVs; zip has no agent-protocol files and no AI mention |
| 18/10 | Buffer + submission | — | Final group review, fixes, submission | Delivered |

**Fallback:** if incremental insertion/2-opt delays M2, ship incremental swap only (the statement minimum) and log the rest in §10.

---

## 12. Appendices

### A. Test protocol

| Test | Input | Expected output | Result |
|---|---|---|---|
| Fitness identity | pequena, π = (1..12) | 4366 | ✅ |
| Toy greedy route | toy4, (1,4,2,3) | 39; C = (7,16,27,38) | ✅ |
| Toy optimum | toy4, brute force | min 22 at (1,4,3,2), unique | ✅ |
| Exact optimum (DP) | pequena; toy4 | 1875; 22 at (1,4,3,2) | ✅ |
| Σp per instance | 3 files | 55 / 239 / 684 | ✅ |
| Statement greedy | pequena, min-increment, tie → travel | 3168 | ✅ |
| Nearest neighbour | pequena | 2590 | ✅ |
| Budget exactness | pequena, B = 100, 110 calls | 100 succeed, 101st raises | ✅ |
| Incremental == full | hypothesis, n ∈ [2, 30], all ops | equality on every move | ✅ |
| Neighborhood sizes | n = 12/50/150 | 66/1225/11175 (swap, 2-opt), 121/2401/22201 (insertion) | ✅ |
| Successor distinctness | n = 2, 3, 5, 12, all ops | no duplicates, none equal to s | ✅ |
| OX slide example | P1 = (1,2,3,4,5), P2 = (5,4,2,1,3), block = positions 1..3 | (5,2,3,4,1) | ✅ |
| Permutation validity | hypothesis, OX/mutations | always a permutation of 1..n | ✅ |
| Architecture | AST of `tp2/algorithms/*.py` | no `tp2.problem` import | ✅ |
| Run invariants | every T2/T3 row | evals == B; fresh h(best_perm) == best_h | ✅ T2 (210/210); T3 ⬜ |
| Reproducibility | same seed, two runs | identical best_h and curve | ✅ (test + T2 rerun identical) |

### B. AI test prompts

Not applicable (no LLM in the project).

### C. Reference values (statement Table 1 and §3)

| Instance | n | Reference h | Nature | B | Runs |
|---|---|---|---|---|---|
| pequena | 12 | 1 875 | global optimum (exact) | 50 000 | 30 |
| intermediária | 50 | 16 332 | best known | 150 000 | 30 |
| grande | 150 | 60 417 | best known | 300 000 | 10 |

### D. Mapping: statement requirement → where it's satisfied

| Statement | Requirement | Component / artifact |
|---|---|---|
| §1.1 Eq. 1 | Rounded travel | C3 |
| §1.2 Eq. 2–3 | C and h | C4 |
| §1.4 | Verify 4366 / 1875 | C4 tests, C12 |
| Fig. 1 | Verify 39 / 22 | C4 tests (toy4) |
| §2.1 | Algorithm ≠ problem | C1, C2, architecture test |
| §2.2 | 3 operators + sizes(n) | C5, `t2_vizinhancas.tex` |
| §2.3 | GD + RR, ≥ 2 variants, improvement steps | C7, `gd_variantes.tex` |
| §2.4 | SA, schedule justified, acceptance plot | C8, `sa_calibracao.tex`, `sa_aceitacao.pdf` |
| §2.5 | GA, selection conversion, valid crossover + example, mutation, budget stop, diversity | C6, C9, `ga_diversidade.pdf` |
| §3 | Budgets, runs, exact stop, incremental + test + time gain, stats, boxplots, MW tests, convergence (+ pop mean) | C2, C5, C10, C11 |
| §4 T1–T3 | Tasks | C12, FR-2, FR-3 |
| §5 | Table, boxplots, curves, tests, time; 4 discussion points; extra experiment | C11, C13, C14 |
| Deliverables | PDF ≤ ~5 p, no code; code + README with exact commands | C14, C15 |
