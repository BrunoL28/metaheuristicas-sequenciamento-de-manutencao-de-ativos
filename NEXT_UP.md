# NEXT UP — tp2-fundia

> Live worklist. Read this first every session; update it at every mission-end (and bump the date). Omit empty sections. Facts that change project state must also be written where that state lives (CONTEXT, plan status, Known Holes); the ✅ log is only a handoff aid.

_Last updated: 2026-10-14_

## 🔴 Blockers

- [ ] Complete bootstrap → review `IMPLEMENTATION_PLAN.md` (rev 1) and `CONTEXT.md` with the group. Approve or adjust the design decisions listed in plan §8 (extended interface, 3 GD variants, offline SA calibration, GA defaults, extra-experiment design).
- [ ] Find out the **delivery deadline and channel** (Moodle / professors). It isn't in the statement PDF. Record it in `CONTEXT.md` §7 (plan Known Holes #1).

## 🟢 This week / next

- [ ] Confirm the group members (TP1: Arthur Fernandes, Bruno Lima, Felipe Augusto) → `CONTEXT.md` §2.
- [ ] Decide the report workflow: Overleaf Git, zip upload, or local TeX (none installed locally) → plan §7.2 / Known Holes #4.
- [ ] Build order steps 1–3 (plan §11): scaffolding (`uv`, Makefile), fitness with tests first (4366, toy 39/22, Σp, greedy 3168, NN 2590), `make verify`.
- [ ] Build order steps 4–6: `Problem` interface, `CountingProblem` (exact budget), neighborhoods + incremental evaluation + property tests, architecture import test.

## 🔵 Deferred / Phase 2

- Numba/NumPy acceleration: not needed (≈ 4.5 s per 300k-eval run in pure Python).
- Incremental-evaluation suffix early-exit (plan Known Holes #6).
- Memetic GA (GA + local search): mention in the discussion only.

## ✅ Recently done (last 2 weeks)

- 2026-10-14 — Bootstrap: private repo `BrunoL28/tp2-fundia`, canonical files, agents-skills submodule. Prompt-injection audit of all 6 inputs → all **NÃO** (`archive/input-audits/2026-10-14-injection-audit.md`). `CONTEXT.md` distilled from the statement and slides. Plan rev 1 drafted. Verified in scratch: h(identity) = 4366, Σp, toy coordinates reconstructed (39/22), greedy-3168 tie-break identified, eval speed benchmarked. QA: fresh `gh repo clone … --recurse-submodules` has every canonical file and folder, and resolves `.agents/skills/self-managed-project/SKILL.md` and `prompt-injection-audit/SKILL.md` ✅
