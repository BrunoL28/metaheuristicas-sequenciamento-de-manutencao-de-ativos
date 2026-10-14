# NEXT UP — tp2-fundia

> Live worklist. Read this first every session; update it at every mission-end (and bump the date). Omit empty sections. Facts that change project state must also be written where that state lives (CONTEXT, plan status, Known Holes); the ✅ log is only a handoff aid.

_Last updated: 2026-10-14_

**Deadline: 2026-10-18.** Schedule and Git flow: `IMPLEMENTATION_PLAN.md` §11 (one branch and one PR per mission; squash-merge after Bruno approves).

## 🔴 Blockers

- [ ] Arthur must accept the repo invite (`EluriaTecnologia`, write) to review PRs.
- [ ] Before M8 (17/10): Bruno installs TeX Live → `! sudo apt install latexmk texlive-latex-extra texlive-lang-portuguese texlive-science`.

## 🟡 In progress

- [ ] **M0** Delivery plan (`docs/plano-entrega`): deadline, decisions, scope cut, schedule, no-attribution rule. Awaiting PR review.

## 🟢 This week / next

- [ ] 14/10 **M1** Foundation + fitness (`feat/fundacao-fitness`): uv/Makefile/CI, loader, h, `make verify` (4366, 39/22, 3168, 2590).
- [ ] 14–15/10 **M2** Interface + counter + neighborhoods + incremental evaluation (`feat/vizinhancas`).
- [ ] 15/10 **M3** Greedy descent (3 variants) + runner + T2 (`feat/busca-local-t2`).
- [ ] 15/10 **M4** Simulated annealing + calibration (`feat/simulated-annealing`).
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

- 2026-10-14 — Delivery plan approved: deadline 18/10, missions M0–M9, Git flow with PRs, local TeX → Overleaf, clean-zip delivery. Arthur invited to the repo. Decisions recorded in `CONTEXT.md` §8 and plan §3/§7/§10/§11.
- 2026-10-14 — Bootstrap: private repo `BrunoL28/tp2-fundia`, canonical files, agents-skills submodule. Prompt-injection audit of all 6 inputs → all **NÃO** (`archive/input-audits/2026-10-14-injection-audit.md`). `CONTEXT.md` distilled from the statement and slides. Plan rev 1 drafted. Verified in scratch: h(identity) = 4366, Σp, toy coordinates reconstructed (39/22), greedy-3168 tie-break identified, eval speed benchmarked. QA: fresh `gh repo clone … --recurse-submodules` has every canonical file and folder, and resolves `.agents/skills/self-managed-project/SKILL.md` and `prompt-injection-audit/SKILL.md` ✅
