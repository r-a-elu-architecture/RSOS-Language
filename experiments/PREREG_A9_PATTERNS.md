# A9-PAT: six patterns read jointly, predicted for A9 cells that do not exist yet (sealed 20 Nov 2026, ~13:40 Vilnius)

Author: R. A. Elu. Scorer: `a9_patterns.py` (sealed with this file; 0 model calls).

## Why

Read jointly, results from the recovery program (LSGPA/CRCG/LIA), the law studies and A9 fall into six patterns that
match the parts of the RSOS seed: (1) structure carries identity, not surface (component); (2) relations matter more
than parts (operator); (3) the signal is local, order matters (grammar); (4) the host decides, capability included
(host); (5) the mirror is symmetric (mirror); (6) repair needs a landing (reach). Those assignments were made **after**
seeing the results, so they may come from the reader, not the data. This file turns them into predictions for data
that does not exist at the time of this commit.

## Data (not yet produced at this commit)

A9 cells of family `codex_sol` that had not run when this file was committed: **Z30 TC** (4 tasks) and **Z100 B2, X5b,
CAv, CAb** (8 tasks each). Codex's usage window reopens at 14:11 Vilnius. Same sealed A9 tasks, code and scoring;
nothing in A9 changes. If a cell is incomplete, its predictions are reported as not scorable.

## Predictions

| # | Pattern | Prediction | Pass if |
|---|---|---|---|
| PA1 | 1 structure | RSOS blind stays exact at 102 keys on Codex | X5b Z100: 8/8 exact |
| PA2 | 1 structure | blind Python stays near exact | CAb Z100: ≥ 7/8 exact |
| PA3 | 4 host / capability | a strong host keeps tool-calling exact at 30 keys | TC Z30: ≥ 3/4 exact |
| PA4 | 4 host / cost | tool-calling costs ≥ 20× the calls of RSOS blind on Codex | mean TC calls (Z30) ≥ 20 × mean X5b calls (Z100) |
| PA5 | 3 locality | JSON Patch errors fall late in the plan | every wrong or failed B2 step in Z100 is at step ≥ 29 of 56 (not scorable if B2 has none) |
| PA6 | 2 relations | silent code errors fall on relational requests | every wrong step of CAv/CAb in Z100 has kind INHERIT, FUSE, REHOST or ROUTE (not scorable if none) |
| PA7 | 6 landing | RSOS never fails silently | X5b Z100: 0 wrong steps (a refused step is not silent) |

Pattern 5 (mirror) has no measurable quantity in this data and is not tested here.

## What would count against the six-pattern reading

PA1, PA3, PA5 or PA6 failing. PA5 and PA6 are the sharpest: they predict *where* errors fall, not only how many.
If the pattern is fitted rather than real, errors should fall without regard to position or request kind.
