# CONTEXT — tp2-fundia

> Distilled snapshot of the assignment, its domain and constraints, built from `INPUTS/`. **Rewrite sections in place when facts change — this is not a journal.** Raw sources stay in `INPUTS/`; this file is the interpretation. If this file and the statement PDF disagree, the PDF wins.

_Last updated: 2026-10-14_

## 1. One-paragraph summary

**Trabalho Prático 2** of *Fundamentos de Inteligência Artificial* (UFMG, Prof. Cristiano Leite de Castro and Prof. João Pedro Campos). We must implement and compare three metaheuristics: **(A) Greedy Descent with Random Restart**, **(B) Simulated Annealing**, **(C) Genetic Algorithm**. They are applied to a combinatorial problem: sequencing the preventive maintenance of *n* electrical-distribution assets visited by a single crew, minimizing **total weighted tardiness**. There are three instances (n = 12, 50, 150). The comparison is under a fixed budget of fitness evaluations, with a mandatory statistical protocol: 30/30/10 independent runs, boxplots, Mann–Whitney tests and convergence curves. The deliverables are a **PDF report** (~5 pages plus appendices, no code pasted in it) and **source code** (zip or Git repo) with a README giving exact commands to reproduce every table and figure. "Success" means a correct, validated fitness function, a fair same-budget comparison, and an honest analysis that answers the four mandatory discussion questions with data. The statement explicitly values *explaining a bad result honestly* over good numbers without understanding. Groups may be **orally questioned** on any part of the code.

## 2. Stakeholders

| Name | Role / org | What they decide or own | Contact channel |
|---|---|---|---|
| Prof. Cristiano Leite de Castro | Professor, DEE/UFMG — Engenharia de Sistemas | Statement, grading, oral questioning; author of the Cap. 4 slides | TODO: confirm channel (Moodle / e-mail) |
| Prof. João Pedro Campos (MSc) | Professor, DEE/UFMG | Co-author of statement and Cap. 4 Parts 1–2 slides; grading | TODO: confirm channel |
| Bruno Lima | Student, group member (repo owner `BrunoL28`) | Repo, implementation, report | — |
| Arthur Fernandes | Student, group member (confirmed 2026-10-14) | Reviews PRs; report | GitHub `EluriaTecnologia` (write access; invite sent 2026-10-14) |
| Felipe Augusto | Student, TP1 group member | Not yet known whether he joins TP2 (the statement allows keeping TP1 groups; max 4 students) | — |

## 3. The problem (as stated)

**Operational context (statement §1.1).** A power distribution utility must perform preventive maintenance on *n* assets (reclosers, distribution transformers, disconnect switches). One crew leaves the base at the start of the shift and serves **one asset at a time**. It **does not return to base**.

For each asset *j*: position (x_j, y_j), service duration p_j (hours), regulatory deadline d_j (hour by which it must be finished), and criticality weight w_j (cost per hour of delay; e.g. a feeder serving a hospital weighs more than a rural branch). The base is index 0, with p_0 = 0.

**Travel time (Eq. 1):** t_ij = round( sqrt((x_i − x_j)² + (y_i − y_j)²) ) hours, rounded to the nearest integer. Rounding is mandatory: without it, fitness values aren't comparable across groups. (All coordinates are integers, so sqrt(k) can never end in exactly .5. Python's banker's `round` therefore behaves identically to round-half-up here.)

**Solution encoding (§1.2):** a permutation π = (π_1, …, π_n) of the n assets, which is the visit order. The search space has n! points (n = 150 gives a number with more than 260 digits).

**Completion time (Eq. 2):** C_{π_k} = C_{π_{k−1}} + t_{π_{k−1} π_k} + p_{π_k}, with π_0 = 0 (base) and C_{π_0} = 0. There are no waiting or idle times and no time windows other than the soft deadline.

**Fitness, minimized (Eq. 3):** h(π) = Σ_j w_j · max(0, C_j − d_j). This is the total weighted tardiness.

**Properties the statement points out:**
- Every permutation is feasible: there are no hard constraints. In Cap. 4 terms this is a *soft-constraint* optimization problem, not a satisfaction problem.
- h is non-decreasing along the prefix: the accumulated cost of the first k assets never decreases when asset k+1 is appended. That is the hook for incremental evaluation, since a move only changes the suffix from its first modified position onward.
- The difficulty comes from two antagonistic greedy criteria: go to the *nearest* asset (saves travel) or go to the *most urgent* one (avoids penalty). Neither works well alone.

**Toy example (Fig. 1, n = 4, base (0,0)):** the proximity-greedy route π = (1,4,2,3) costs h = 39. The optimum π* = (1,4,3,2) costs h = 22, because postponing asset 2 (the lowest weight) pays off despite the longer travel. The figure gives p, d, w and C but **not** the coordinates. From the schedule: asset 1: p=2, d=10, w=3, C=7; asset 4: p=4, d=20, w=5, C=16; asset 2: p=3, d=14, w=1, C=27; asset 3: p=1, d=25, w=2, C=38. The statement says "verify these two values in your implementation". **Reconstructed coordinates** (from the drawing plus the schedule, checked 2026-10-14 by brute force over all 4! orders): base (0,0), 1 = (3,4), 2 = (6,0), 3 = (0,8), 4 = (6,8). These reproduce every C_j in the figure, h(1,4,2,3) = 39, and a **unique** optimum (1,4,3,2) with h = 22. The second best is (1,3,4,2) at 35. This is the toy test fixture.

## 4. What must be built and delivered (to-be)

**Mandatory architecture (§2.1): algorithm ≠ problem.** The three algorithms are generic and only see a common interface:

| Method | Role |
|---|---|
| `solucao_aleatoria()` | random starting point (a permutation) |
| `h(s)` | fitness, always minimization |
| `sucessores(s)` | iterates over **all** successors of s |
| `sucessor_aleatorio(s)` | samples **one** successor of s |
| `cruzamento(s1, s2)` | recombination operator |
| `mutacao(s)` | mutation operator |

**Neighborhood operators (§2.2, Fig. 3):** **Swap** (exchange two positions), **Insertion** (remove one element and reinsert it elsewhere), **2-opt** (reverse a contiguous segment). The report must state the **neighborhood size as a function of n** for each. Swap is n(n−1)/2 (11 175 at n = 150, as the statement says). Insertion is (n−1)² distinct (n(n−1) raw moves; adjacent moves coincide). 2-opt is n(n−1)/2 segment reversals.

**(A) Greedy Descent + Random Restart (§2.3):** move to the best successor until a local optimum (no successor improves h), then restart from a new random permutation, keeping the best so far, until the budget runs out. **At least two of three** successor-selection variants must be implemented and compared: *best improvement* (scan the whole neighborhood), *first improvement* (accept the first improving successor), *random successor accepted only if it improves*. Report the **number of improvement steps** each variant manages within the budget, and discuss what that means.

**(B) Simulated Annealing (§2.4):** exactly as in class. If h(π′) ≤ h(π), accept; otherwise accept with probability e^{−(h(π′)−h(π))/T} (Gibbs). You must **define and justify the annealing schedule** (e.g. geometric T ← αT) and explain how T0, Tf and α were calibrated. Δh ranges from tens to thousands and **changes with instance size**, so a temperature calibrated on the small instance doesn't work on the large one. You must **record the acceptance rate of worsening moves** over the run and plot it. A well-tuned run starts like a random walk and ends like greedy descent.

**(C) Genetic Algorithm (§2.5):** population N, selection, crossover with probability Pc, mutation with probability Pm, elitism, following the class pseudocode (Part 3 slide 18/30).
- Initialization: random sampling of N sequences.
- Selection: tournament or roulette. You must **explain how cost h was converted into a fitness suitable for the chosen selection**.
- Crossover: must preserve permutation validity: OX (seen in class), PMX, or edge recombination. **Describe the chosen operator with a step-by-step numerical example.**
- Mutation: small rate. Swap mutation is the natural start; other Fig. 3 operators are allowed.
- Stopping: **budget exhaustion only**.
- You must **report population diversity over generations** (distinct chromosomes, or mean pairwise distance). Premature convergence must be diagnosed with data.

**Experimental protocol (§3, mandatory):**

| Instance | Budget B (evaluations of h) | Independent runs |
|---|---|---|
| pequena (n = 12) | 50 000 | 30 |
| intermediária (n = 50) | 150 000 | 30 |
| grande (n = 150) | 300 000 | 10 |

- **Counting:** every successor examined by local search counts 1, and every individual evaluated by the GA counts 1. Stop **exactly** at B. If greedy descent recomputes h of the current solution, that counts too, so instrument the counting in a single place.
- **Incremental evaluation:** implement it for at least one neighborhood, verify it against full evaluation **with an automated test**, and report the measured time gain. It changes wall-clock time only, not the evaluation count. Wall-clock time must be reported.
- **Statistics:** for each algorithm × instance, report mean, standard deviation, minimum and median of the best h. Show boxplots per instance. Any claim that one algorithm beats another needs a **non-parametric test** (Mann–Whitney/Wilcoxon) with its **p-value**.
- **Convergence curves:** for each instance, best h (y) vs evaluations spent (x), one curve per algorithm (median over runs). For the GA, add the **population-mean curve**. The gap between the two shows diversity loss.

**Tasks (§4):**
- **T1:** implement h, validate with the two verification values, and show the program output for both in the report.
- **T2:** implement the 3 operators. Using greedy descent + random restart with the same budget, compare the 3 neighborhoods on the 3 instances: which gives better local optima, and which is cheapest per move with incremental evaluation? Justify the neighborhood used in the other experiments.
- **T3:** run the 3 algorithms on the 3 instances under the full §3 protocol.

**Report (§5), minimum contents:**
1. Main table, 9 rows (3 instances × 3 algorithms): mean ± sd and best h. For the small instance, add a gap column: gap = (h − h*)/h*.
2. Boxplots per instance.
3. Convergence curves.
4. Statistical tests for every pairwise claim made in the text.
5. Mean time per run next to the evaluation count, with a discussion of how the two metrics differ.

**Mandatory discussion points:**
- **Local optima:** how many distinct local optima did greedy descent find on the small instance across restarts? In how many runs did it reach h* = 1875? Compare with the other two algorithms and relate to local vs global optimum.
- **Exploration × intensification:** for each algorithm, name the mechanism that explores and the one that intensifies, and show in the data where the balance was well or badly tuned.
- **Scale effect:** does the ranking change from small to large? If yes, hypothesize why (neighborhood scan cost vs search-space size). If no, show the stability is statistically supported.
- **When does the GA pay off?** Is there an instance where it beats both local searches with statistical significance? Hypothesize in terms of the encoding (can recombination combine good subsequences from two parents into a better child?), then **propose, run and report one additional experiment** that tests it.

## 5. Domain glossary

| Term | Meaning in this project | Source |
|---|---|---|
| ativo (asset) | A maintenance job at (x_j, y_j) with p_j, d_j, w_j; indices 1..n | statement §1.1 |
| base | Point 0, crew start; p_0 = 0; no return | §1.1 |
| p_j | Service duration (h), integer 1–8 in the given instances | §1.1, instance files |
| d_j | Regulatory deadline (absolute hour) | §1.1 |
| w_j | Criticality weight = cost per hour late, integer 1–5 | §1.1 |
| t_ij | Rounded Euclidean travel time (Eq. 1) | §1.1 |
| C_j | Completion time of asset j under π (Eq. 2) | §1.2 |
| h(π) | Total weighted tardiness Σ w_j·max(0, C_j − d_j), minimized | §1.2 Eq. 3 |
| h* | Known global optimum, small instance only: 1875 | §1.4 |
| orçamento B | Budget in number of h evaluations | §3 |
| avaliação | One evaluation of h, full or incremental; each counts 1 | §3 |
| vizinhança / sucessores | Set of permutations reachable by one operator move | §2.2 |
| Swap / Insertion / 2-opt | Exchange 2 positions / move 1 element / reverse a segment | §2.2 Fig. 3 |
| best / first improvement | Scan everything and take the best / take the first improving successor | §2.3, slides P1-2 p.52–53 |
| random restart | Restart from a new random permutation after a local optimum | §2.3 |
| annealing schedule | Rule for lowering T (e.g. geometric T ← αT) | §2.4, slides P1-2 p.66 |
| OX / PMX | Order Crossover / Partially Mapped Crossover (permutation-preserving) | §2.5, slides P3 15/30 |
| elitismo | Best individual(s) survive unchanged to the next generation | §2.5, slides P3 18/30 |
| gap | (h − h*)/h* for the small instance | §5 |
| exploração / intensificação | Exploration (diversify) vs exploitation/intensification (refine) | slides P3 5/30 |

## 6. Systems & data

| System | What we use it for | Access (who/what account) | Key objects / fields |
|---|---|---|---|
| Instance files `INPUTS/manutencao_{pequena,media,grande}.txt` | Problem data | Read-only in repo | Line 1: `n`. Line 2: `x_0 y_0` (base). Lines 3..n+2: `x y p d w` per asset, in order 1..n. Whitespace-separated integers. |
| GitHub `BrunoL28/tp2-fundia` (private) | Code + state sync; candidate delivery format ("repositório Git") | `BrunoL28` | — |
| TeX Live (local) → Overleaf | Report (LaTeX): compiled locally with `make report`, then exported as a zip to Overleaf | Bruno installs TeX Live; Overleaf project to be created by the group | `relatorio/main.tex` |
| Python + `uv` + `make` | Implementation and experiments (same tooling as TP1) | local | — |

**Instance facts (computed 2026-10-14 from the files):**

| Instance | n | base | Σp (matches statement) | x range | y range | p | d range | w | h(identity) | reference h |
|---|---|---|---|---|---|---|---|---|---|---|
| pequena | 12 | (50,50) | 55 ✅ | 4–99 | 8–89 | 2–8 | 64–159 | 1–5 | **4366** ✅ (statement value) | 1875 (global optimum, exact) |
| media | 50 | (50,50) | 239 ✅ | 5–99 | 0–99 | 1–8 | 137–442 | 1–5 | 181 339 | 16 332 (best known) |
| grande | 150 | (50,50) | 684 ✅ | 0–99 | 0–99 | 1–8 | 294–987 | 1–5 | 1 308 503 | 60 417 (best known) |

**Greedy baseline 3168 (statement §1.4):** "always pick the asset with the smallest immediate tardiness increment". This value is reproduced **only** when ties are broken by **smallest travel time from the current position**, then lowest index. Early in the route every candidate adds 0 tardiness, so the tie-break dominates. Other tie-breaks give 3815 (by completion time), 5030 (by d), 6935 (by index). For reference, pure nearest-neighbour gives **2590**, better than the statement's greedy. Both are useful baselines for the report.

## 7. Constraints & non-negotiables

- **Fair comparison:** the same evaluation budget B for all algorithms, stopping exactly at B. Stopping is budget-only, including for the GA.
- **Algorithm ≠ problem** separation (graded architecture requirement).
- **Rounded** travel times (Eq. 1).
- **Statistical rigor:** non-parametric tests with p-values for every comparative claim. "Close means with large spread authorize no conclusion."
- **Report:** PDF, ~5 pages suggested (excluding appendices), **no code in the body**.
- **Code:** separate (zip or Git repo) with a README giving **exact commands to reproduce each table and each figure**.
- **Group:** at most 4 students; TP1 groups may continue.
- **Oral questioning:** any member may be asked about any part of the code, so everyone must understand it all.
- **Save everything to disk** (CSV): 9 combinations × dozens of runs.
- **Deadline: 2026-10-18** (given by the group; not stated in the PDF). Submission channel still to confirm.

## 8. Decisions made

| Date | Decision | Why | Decided by |
|---|---|---|---|
| 2026-10-14 | Private GitHub repo `BrunoL28/tp2-fundia`, self-managed protocol | User choice at bootstrap | Bruno |
| 2026-10-14 | Python + `uv` + `Makefile` + `pytest`, mirroring TP1 | Same group and course; proven workflow; `uv` and `make` are installed | Bootstrap (proposed; confirm at review) |
| 2026-10-14 | All 3 greedy-descent variants implemented (statement requires ≥ 2) | Third variant is cheap given the interface and strengthens the "improvement steps under budget" discussion | Bootstrap (proposed; confirm at review) |
| 2026-10-14 | Inputs audited for prompt injection before distillation: all 6 files **NÃO** | Standing protocol | `archive/input-audits/2026-10-14-injection-audit.md` |
| 2026-10-14 | Plan rev 1 design decisions approved (extended interface, 3 GD variants, offline SA calibration, GA defaults, extra experiment) | Plan review | Bruno |
| 2026-10-14 | Delivery schedule M0–M9 for the 18/10 deadline; scope cut: no PMX, no SA calibration sensitivity check | 4 days left | Bruno |
| 2026-10-14 | Branch per mission + PR into `main`, squash-merge after Bruno's approval; commits/PRs carry no AI attribution | Group workflow; Arthur joined the repo | Bruno |
| 2026-10-14 | Report: local TeX Live while writing, then export to Overleaf | No TeX installed; group edits on Overleaf | Bruno |
| 2026-10-14 | Code delivered as a clean zip (`make zip`), without agent-protocol files | Statement allows zip or Git repo | Bruno |
| 2026-10-15 | **Insertion** is the neighborhood for GD and SA in T3 and the GA mutation move | T2 (`results/2026-10-15_t2/`): best median on media (17 457.5 vs 18 468 2-opt, 24 252 swap) and grande (82 796.5 vs 89 078.5, 150 118); 30/30 optimal on pequena like the others; same cost per move (≈ 10 µs at n = 150) | T2 data; group confirms at PR review |
| 2026-10-15 | SA calibration: T0 and Tf both from one sample of 2 000 random (solution, successor) pairs; T0 = −median(Δ⁺)/ln 0.9, Tf = −q10(Δ⁺)/ln 10⁻³; L = 100/300/1000; α from B | The planned Tf from Δ⁺ around local optima cost 503k evaluations on grande (> B) and an exploratory pilot (seeds outside the protocol) didn't favour it (grande median 89 576 vs 83 464). Pilot `results/2026-10-15_sa_piloto/` shows acceptance ≈ 0.87 → ≈ 0.004, as the statement asks | M4; group confirms at PR review |
| 2026-10-15 | GA keeps the plan defaults: N = 50/100/100, tournament k = 3, Pc = 0.9 per pair, Pm = 0.2 per child (one insertion move), elitism 2, OX with the slide convention | Parameter pilot on media (`results/2026-10-15_ag_ajuste/`, 10 runs per setting, seeds outside the protocol): no N/Pm setting clearly better (medians 19 297–21 254, wide spread) | M5; group confirms at PR review |
| 2026-10-15 | V2 items pulled into v1: PMX arm, memetic GA arm, SA with B minus calibration, 2B for all algorithms on media/grande | Ahead of schedule | Bruno |
| 2026-10-15 | Memetic GA = first-improvement descent on each child with probability p_ls = 0.1 | Pilot `results/2026-10-15_memetico_ajuste/` (seeds outside the protocol): p_ls 0.1 best on media (16 816) and grande (78 443). A first design (a few random successor samples per child) didn't improve the GA and was dropped | M6 |
| 2026-10-15 | Algorithm (A) in the main table = GD `random` variant | Plan rule (best median on media in T3): 17 366 vs `first` 17 457.5 and `best` 20 054.5; the three variants go in the appendix | M6; group confirms at PR review |
| 2026-10-15 | Report: 10 pt, 2 cm margins, body ≈ 7 pages (statement suggests ~5) + appendices; authors Arthur Fernandes and Bruno Lima (Felipe pending) | The extra experiment and the robustness checks need the space; the SA calibration table, T2 tests, memetic-vs-local tests, robustness, GA parameters, best solutions and reproduction commands went to the appendices | Bruno, 2026-10-15: the 5 pages are a suggestion and exceeding by 1–2 pages (appendices excluded) is fine given the number of analyses |

## 9. Open questions

| # | Question | Who can answer | Blocking? |
|---|---|---|---|
| 1 | Submission channel (Moodle?). Deadline known: 2026-10-18; format decided: zip | Professors / Moodle | No (needed on 18/10) |
| 2 | Does Felipe Augusto join TP2? (Bruno and Arthur confirmed) | Bruno | No (affects report cover and README) |
| 3 | Is there a required report template? (Workflow decided: local TeX → Overleaf) | Professors | No |
| 4 | Is a single combined evaluation counter acceptable for incremental evaluation (each incremental Δ-evaluation counts 1)? Statement §3 implies yes: "isso não altera a contagem de avaliações". | Statement (already answered: yes) | No |

## 10. Sources

| File in INPUTS/ | What it is | Date |
|---|---|---|
| `INPUTS/_FundIA__TP2_BuscaLocal_GAs.pdf` | TP2 assignment statement, 7 pp. (pdfTeX) | created 2026-10-06 |
| `INPUTS/manutencao_pequena.txt` | Instance n = 12 | received 2026-10-14 |
| `INPUTS/manutencao_media.txt` | Instance n = 50 | received 2026-10-14 |
| `INPUTS/manutencao_grande.txt` | Instance n = 150 | received 2026-10-14 |
| `INPUTS/slides/Chapter_4_2026_1_Parts_1_2 (1).pdf` | Lecture slides Cap. 4 Parts 1–2: CSP, systematic methods, local search (random sampling/walk, best improvement, local vs global optima, random restart/steps, SA with Gibbs acceptance and geometric cooling example T0=10, α=0.99) | 2026-08-10 |
| `INPUTS/slides/Chapter_4_2026_1_Part3 (1).pdf` | Lecture slides Cap. 4 Part 3: population metaheuristics, exploration vs intensification, GA (life cycle, steel-heat sequencing case study, OX crossover, swap mutation, stopping criteria, pseudocode with elitism, convergence curve best vs population mean), Differential Evolution | 2026-08-10 |

All 6 files were **audited for prompt injection on 2026-10-14**. Verdict: **NÃO** for all. Report: `archive/input-audits/2026-10-14-injection-audit.md`.
