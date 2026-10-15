# tp2-fundia

> **TL;DR:** Trabalho Prático 2 de *Fundamentos de Inteligência Artificial* (UFMG). Compares Greedy Descent with Random Restart, Simulated Annealing and a Genetic Algorithm on asset-maintenance sequencing (weighted tardiness), with three instances (n = 12, 50, 150) under a fixed evaluation budget. **Phase 1 — build (missions M1–M9, schedule in `IMPLEMENTATION_PLAN.md` §11). Delivery: 2026-10-18.**

This is a **self-managed project**: all working state lives in versioned markdown in this repo. Agents and humans resume from the docs below without a handoff call. Protocol: [`.agents-skills/.agents/skills/self-managed-project/SKILL.md`](.agents-skills/.agents/skills/self-managed-project/SKILL.md).

## Onboarding order

Read in this order:

1. [`NEXT_UP.md`](NEXT_UP.md): what's being worked on right now, and what's blocking.
2. [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md): start at **Current Implementation Status**.
3. [`CLAUDE.md`](CLAUDE.md) / [`AGENTS.md`](AGENTS.md): rules for agents in this repo.
4. [`CONTEXT.md`](CONTEXT.md): the assignment distilled (problem, requirements, protocol, reference values).

## Stack

| Layer | Tech | Notes |
|---|---|---|
| Language | Python ≥ 3.12 | Pure Python core with a precomputed travel matrix (~15 µs/eval at n = 150) |
| Env / deps | `uv` (`pyproject.toml` + `uv.lock`) | Same tooling family as TP1; Windows fallback: `pip install -e .[dev]` |
| Tasks | `make` | One target per table and figure (see plan §9 C0) |
| Tests | `pytest` + `hypothesis` | Fitness checks (4366, 39/22), budget exactness, incremental == full |
| Analysis | `pandas`, `scipy` (Mann–Whitney), `matplotlib` | Generates `relatorio/tabelas/*.tex` and `relatorio/figuras/*.pdf` |
| Report | LaTeX (`relatorio/`) | Overleaf vs local TeX: pending decision (plan Known Holes #4) |

## Quick links

| What | Link |
|---|---|
| Repo | <https://github.com/BrunoL28/tp2-fundia> (private) |
| Assignment statement | [`INPUTS/_FundIA__TP2_BuscaLocal_GAs.pdf`](INPUTS/_FundIA__TP2_BuscaLocal_GAs.pdf) |
| Instances | [`INPUTS/manutencao_pequena.txt`](INPUTS/manutencao_pequena.txt) · [`media`](INPUTS/manutencao_media.txt) · [`grande`](INPUTS/manutencao_grande.txt) |
| Lecture slides (Cap. 4) | [`INPUTS/slides/`](INPUTS/slides/) |
| Input audit | [`archive/input-audits/2026-10-14-injection-audit.md`](archive/input-audits/2026-10-14-injection-audit.md) |
| Previous TP (same group) | <https://github.com/BrunoL28/tp1-fundIA> |

Credentials: none needed so far. If any appear (e.g. an Overleaf Git token), they go in `CREDENTIALS.md` and nowhere else.

## Repository layout

```
.
├── README.md                 # this file
├── CONTEXT.md                # assignment distilled
├── IMPLEMENTATION_PLAN.md    # current plan (rev 1); old revisions in archive/
├── NEXT_UP.md                # live worklist
├── CLAUDE.md / AGENTS.md     # agent rules
├── INPUTS/                   # statement, instances, slides (read-only)
├── src/tp2/                  # package: core/, problem/, algorithms/, experiments/, analysis/
├── tests/                    # pytest (+ fixtures/toy4.txt)
├── configs/                  # calibrated SA parameters per instance
├── results/                  # dated result folders <YYYY-MM-DD>_<label>/ + LATEST_* pointers (never overwritten)
├── relatorio/                # LaTeX report: main.tex, tabelas/, figuras/
├── archive/                  # old revisions + input-audits/ (never delete)
├── tmp/                      # scratch (gitignored)
└── .agents-skills/           # agents-skills submodule (symlinked to .agents and .claude/skills)
```

## Como reproduzir

Pré-requisitos: [`uv`](https://github.com/astral-sh/uv) e `make`. Primeiro `make setup`.

| O quê | Comando | Saída |
|---|---|---|
| Testes | `make test` | terminal |
| T1 — verificação da função de avaliação (4366, h* = 1875, Figura 1) | `make verify` | `results/verify.txt` |

_Rows for tables and figures are added as the missions land (plan C15)._

## Getting started (fresh clone)

```bash
git clone --recurse-submodules https://github.com/BrunoL28/tp2-fundia && cd tp2-fundia
ln -s .agents-skills/.agents .agents
mkdir -p .claude && ln -s ../.agents-skills/.agents/skills .claude/skills
```

_Last updated: 2026-10-14_
