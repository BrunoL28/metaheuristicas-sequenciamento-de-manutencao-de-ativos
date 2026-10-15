# NEXT UP — tp2-fundia

> Live worklist. Read this first every session; update it at every mission-end (and bump the date). Omit empty sections. Facts that change project state must also be written where that state lives (CONTEXT, plan status, Known Holes); the ✅ log is only a handoff aid.

_Last updated: 2026-10-15_

**Deadline: 2026-10-18.** Schedule and Git flow: `IMPLEMENTATION_PLAN.md` §11 (one branch and one PR per mission; squash-merge after Bruno approves).

## 🔴 Blockers

- [ ] Arthur must accept the repo invite (`EluriaTecnologia`, write) to review PRs.
- [ ] Before M8 (17/10): Bruno installs TeX Live → `! sudo apt install latexmk texlive-latex-extra texlive-lang-portuguese texlive-science`.

## 🟡 In progress

- [ ] **M6** T3 + extra + robustness: PR #7 (`exp/t3-extra`), CI green, awaiting review. Group: confirm GD-`random` as algorithm (A) and the memetic design (CONTEXT §8).
- [ ] **M7** Analysis: PR (`feat/analise`, stacked on #7), awaiting review. Group: review the numbers before the report (plan §1, "Statistics").

## 🟢 This week / next

- [ ] 17/10 **M8** Report (`docs/relatorio`).
- [ ] 17/10 **M9** Delivery README + clean zip (`chore/entrega`).
- [ ] Confirm whether Felipe Augusto joins the group (report cover, README).
- [ ] Confirm the submission channel (Moodle?).

## 🔵 Deferred / Phase 2

- Sensitivity of the K factor of the GD `random` variant.
- Numba/NumPy acceleration: not needed (≈ 4.5 s per 300k-eval run in pure Python).
- Incremental-evaluation suffix early-exit (plan Known Holes #6).

## ✅ Recently done (last 2 weeks)

- 2026-10-15 — M7: `make analysis` → 11 LaTeX tables + 6 figures + best solutions, from `results/LATEST_*`. GD-random and SA are statistically tied everywhere and both beat the GA; only the memetic arm beats GA-OX; the SA calibration cost is not significant. 114 tests green.
- 2026-10-15 — M6 (+ V2 items pulled forward): PMX, memetic GA, suites `t3`, `extra`, `robustez`, `tempos`; all runs ok from commit `7bd25eb`. SA has the best median on media and grande; GD-`random` is algorithm (A); three algorithms beat the media reference 16 332 (best 16 234, memetic GA); the GA stagnates on media (no improvement after 150k in 30/30 runs). 108 tests green.
- 2026-10-15 — PRs #4–#6 (M3–M5) merged by Bruno.
- 2026-10-15 — M5: OX (slide convention, `make ox-demo`), insertion mutation, GA (tournament, Pc, Pm, elitism, `headless` variant for the extra experiment), per-generation diversity log. Pilots: GA is the weakest so far (median 1 937 / 18 610 / 97 014) and loses diversity early; the N/Pm pilot on media kept the defaults. 100 tests green.
- 2026-10-15 — M4: SA (Gibbs acceptance, geometric levels, α from B), windowed acceptance log, `make calibrate` → `configs/sa_*.json` (4 000 evaluations per instance), `make sa-piloto` → `results/2026-10-15_sa_piloto/`: acceptance 0.87 → 0.002–0.006 on all 3 instances. Tf rule changed to the q10 of random-start worsenings (CONTEXT §8). 86 tests green.
- 2026-10-15 — M3: greedy descent + random restart (best / first / random with K = |N|), `Recorder`, parallel runner (seeds, append CSV, `--resume`, evals == B and re-evaluated best checks), `make t2`. T2 run → `results/2026-10-15_t2/` (210/210 ok): every neighborhood hits 1875 in 30/30 on pequena; **insertion** wins on media and grande and is adopted (CONTEXT §8). 75 tests green.
- 2026-10-14 — PRs #1–#3 (M0–M2) merged by Bruno.

- 2026-10-14 — M2: `Problem` protocol, `CountingProblem` (exact budget, best-so-far trace), swap/insertion/2-opt with incremental evaluation, AST architecture test, timing script. 56 tests green. Incremental gain measured at 1.1–1.4× (plan §1).
- 2026-10-14 — M1: `uv` project (hatchling), Makefile (`setup test lint verify`), CI workflow, instance loader, h, constructive baselines and an exact DP for n = 12. 15 tests green; `make verify` confirms 4366, **h* = 1875 computed exactly**, greedy 3168, NN 2590, Fig. 1 39/22.
- 2026-10-14 — Delivery plan approved: deadline 18/10, missions M0–M9, Git flow with PRs, local TeX → Overleaf, clean-zip delivery. Arthur invited to the repo. Decisions recorded in `CONTEXT.md` §8 and plan §3/§7/§10/§11.
- 2026-10-14 — Bootstrap: private repo `BrunoL28/tp2-fundia`, canonical files, agents-skills submodule. Prompt-injection audit of all 6 inputs → all **NÃO** (`archive/input-audits/2026-10-14-injection-audit.md`). `CONTEXT.md` distilled from the statement and slides. Plan rev 1 drafted. Verified in scratch: h(identity) = 4366, Σp, toy coordinates reconstructed (39/22), greedy-3168 tie-break identified, eval speed benchmarked. QA: fresh `gh repo clone … --recurse-submodules` has every canonical file and folder, and resolves `.agents/skills/self-managed-project/SKILL.md` and `prompt-injection-audit/SKILL.md` ✅
