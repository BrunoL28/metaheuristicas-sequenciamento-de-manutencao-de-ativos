# NEXT UP — tp2-fundia

> Live worklist. Read this first every session; update it at every mission-end (and bump the date). Omit empty sections. Facts that change project state must also be written where that state lives (CONTEXT, plan status, Known Holes); the ✅ log is only a handoff aid.

_Last updated: 2026-10-15_

**Deadline: 2026-10-18.** Schedule and Git flow: `IMPLEMENTATION_PLAN.md` §11 (one branch and one PR per mission; squash-merge after Bruno approves).

## 🔴 Blockers

- [ ] Arthur must accept the repo invite (`EluriaTecnologia`, write) to review PRs.
- [ ] Before M8 (17/10): Bruno installs TeX Live → `! sudo apt install latexmk texlive-latex-extra texlive-lang-portuguese texlive-science`.

## 🟡 In progress

- [ ] **M3** Greedy descent + runner + T2: PR #4 (`feat/busca-local-t2`), CI green, awaiting review. Group: confirm the insertion choice (CONTEXT §8).
- [ ] **M4** Simulated annealing + calibration: PR (`feat/simulated-annealing`, stacked on #4), awaiting review. Group: confirm the calibration change (CONTEXT §8).

## 🟢 This week / next

- [ ] 15–16/10 **M5** Genetic algorithm (`feat/algoritmo-genetico`).
- [ ] 16/10 **M6** T3 + extra experiments (`exp/t3-extra`).
- [ ] 16/10 **M7** Analysis: tables and figures (`feat/analise`).
- [ ] 17/10 **M8** Report (`docs/relatorio`).
- [ ] 17/10 **M9** Delivery README + clean zip (`chore/entrega`).
- [ ] Confirm whether Felipe Augusto joins the group (report cover, README).
- [ ] Confirm the submission channel (Moodle?).

## 🔵 Deferred / Phase 2

- PMX crossover and the GA-PMX arm of the extra experiment (cut for the deadline).
- SA sensitivity check that counts calibration samples in B (the report only discloses the offline calibration).
- Numba/NumPy acceleration: not needed (≈ 4.5 s per 300k-eval run in pure Python).
- Incremental-evaluation suffix early-exit (plan Known Holes #6).
- Memetic GA (GA + local search): mention in the discussion only.

## ✅ Recently done (last 2 weeks)

- 2026-10-15 — M4: SA (Gibbs acceptance, geometric levels, α from B), windowed acceptance log, `make calibrate` → `configs/sa_*.json` (4 000 evaluations per instance), `make sa-piloto` → `results/2026-10-15_sa_piloto/`: acceptance 0.87 → 0.002–0.006 on all 3 instances. Tf rule changed to the q10 of random-start worsenings (CONTEXT §8). 86 tests green.
- 2026-10-15 — M3: greedy descent + random restart (best / first / random with K = |N|), `Recorder`, parallel runner (seeds, append CSV, `--resume`, evals == B and re-evaluated best checks), `make t2`. T2 run → `results/2026-10-15_t2/` (210/210 ok): every neighborhood hits 1875 in 30/30 on pequena; **insertion** wins on media and grande and is adopted (CONTEXT §8). 75 tests green.
- 2026-10-14 — PRs #1–#3 (M0–M2) merged by Bruno.

- 2026-10-14 — M2: `Problem` protocol, `CountingProblem` (exact budget, best-so-far trace), swap/insertion/2-opt with incremental evaluation, AST architecture test, timing script. 56 tests green. Incremental gain measured at 1.1–1.4× (plan §1).
- 2026-10-14 — M1: `uv` project (hatchling), Makefile (`setup test lint verify`), CI workflow, instance loader, h, constructive baselines and an exact DP for n = 12. 15 tests green; `make verify` confirms 4366, **h* = 1875 computed exactly**, greedy 3168, NN 2590, Fig. 1 39/22.
- 2026-10-14 — Delivery plan approved: deadline 18/10, missions M0–M9, Git flow with PRs, local TeX → Overleaf, clean-zip delivery. Arthur invited to the repo. Decisions recorded in `CONTEXT.md` §8 and plan §3/§7/§10/§11.
- 2026-10-14 — Bootstrap: private repo `BrunoL28/tp2-fundia`, canonical files, agents-skills submodule. Prompt-injection audit of all 6 inputs → all **NÃO** (`archive/input-audits/2026-10-14-injection-audit.md`). `CONTEXT.md` distilled from the statement and slides. Plan rev 1 drafted. Verified in scratch: h(identity) = 4366, Σp, toy coordinates reconstructed (39/22), greedy-3168 tie-break identified, eval speed benchmarked. QA: fresh `gh repo clone … --recurse-submodules` has every canonical file and folder, and resolves `.agents/skills/self-managed-project/SKILL.md` and `prompt-injection-audit/SKILL.md` ✅
