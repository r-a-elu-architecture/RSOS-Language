# A9 report (round 2, final, 20 Nov 2026): the strongest rival patterns, three sizes, one law

**Status: final for Claude Haiku 5.5 and GPT-6.2 Sol (all cells complete).** Scored at 15:00 (UTC+02:00) Helsinki, Kyiv, Riga, Sofia, Tallinn, Vilnius with the sealed
`a9_analyse.py`. Round 1 (14:20) is in the history of this file. Gemini 3.8 Flash completed 2 tasks before its free
quota ran out (incomplete, reported, not scored). Every task seed traces back to drand round 6657746 (randomness
`22da2428e4b5f26a…`), drawn after the predictions were public (09:08). Error logs of every attempt that did not run
(usage limits, provider overload, a full disk on the runner) are in `results/a9_errors_*.jsonl`; none produced a
result. Re-score yourself: `python3 research/verify.py`.

## What it shows, in plain words

- **The principle holds; the syntax is not what makes it exact.** RSOS blind **48/48**, Python seeing the state
  **48/48**, blind Python **47/48**, one-call JSON Patch **46/48**, tool-calling **15/16**. Q4, written in advance as
  the outcome against RSOS, passed: exactness comes from never showing the model the values and reading them at run time.
- **RSOS blind and Python-seeing-the-state are the only arms with no failure of any kind.** Blind Python failed one
  task silently (a reversed copy at request 14, inherited by four later requests). JSON Patch failed two tasks: one
  refused step (Claude, 300 keys) and one task with **3 silent wrong values** plus a refused step (Codex, 100 keys).
- **Where JSON Patch broke, it broke late.** All 5 bad JSON Patch steps fall in the last quarter of the plan (steps
  45–49 of 56); none in the first three quarters. Q2a holds on 5 events in 2 tasks: a direction, not yet a curve.
- **Tool-calling is exact but expensive:** 15/16 tasks at about **100 model calls per task** against 2–3 for RSOS blind;
  on Codex at 300 keys about **2.0 million input tokens per task** against about 51,000.
- **Misses:** RSOS was not more compact than Python (Q5a), and tool-calling's input did **not** grow with state size
  once Codex's 30-key cell was in (Q6c failed in round 2; it had passed in round 1). Both stand.

## Pattern seal (A9-PAT, sealed 13:32, scored on Codex's cells that ran after it)

| # | Prediction | Verdict |
|---|---|---|
| PA1 | RSOS blind 8/8 at 102 keys | **pass** (8/8) |
| PA2 | blind Python ≥ 7/8 | **pass** (8/8) |
| PA3 | tool-calling ≥ 3/4 at 30 keys on a strong host | **pass** (4/4) |
| PA4 | tool-calling ≥ 20× the calls of RSOS blind | **pass** (about 102 vs about 2.5) |
| PA5 | JSON Patch errors fall in the second half of the plan | **pass**: steps 45, 47, 48, 49 |
| PA6 | silent code errors fall on relational requests | not scorable (no code errors) |
| PA7 | RSOS never fails silently | **pass** (0 wrong steps) |

PA5 was the sharp one: it predicted *where* errors would fall, sealed before the data existed. Four of four landed in
the predicted half. Small numbers; a direction worth a larger sealed test.

Families: claude_haiku, codex_sol. Pre-registration: `PREREGISTRATION_A9.md`. Scored by `a9_analyse.py` (sealed) on complete cells only.

## Verdicts

| Prediction | Verdict |
|---|---|
| Q1 Blind RSOS stays exact | **pass** |
| Q2a Law: JSON Patch errors rise along the plan | **pass** |
| Q2b Law: arms that read at run time stay flat | **pass** |
| Q3a JSON Patch worse with state size | **pass** |
| Q3b Blind arms flat with size | **pass** |
| Q4 Mechanism is blindness (blind Python as exact as blind RSOS) | **pass** |
| Q5a RSOS more compact than Python | **fail** |
| Q5b RSOS cheapest per correct task at 300 keys | **pass** |
| Q6a Tool-calling uses >= 20x the calls | **pass** |
| Q6b Tool-calling beats JSON Patch on steps | **pass** |
| Q6c Tool-calling input grows with size | **fail** |
| Q7 Blind RSOS at least as exact as tool-calling | **pass** |

## Cells

| Family | Size | Arm | Tasks | Exact | Wrong steps | Failed steps | Calls/task | Input tok/task | Output tok/task | Complete |
|---|---|---|---|---|---|---|---|---|---|---|
| claude_haiku | Z100 | B2 | 8 | 8/8 | 0 | 0 | 2.0 | 10354 | 14865 | yes |
| claude_haiku | Z100 | CAb | 8 | 8/8 | 0 | 0 | 1.0 | 2294 | 8515 | yes |
| claude_haiku | Z100 | CAv | 8 | 8/8 | 0 | 0 | 1.0 | 3346 | 7245 | yes |
| claude_haiku | Z100 | X5b | 8 | 8/8 | 0 | 0 | 2.0 | 9583 | 11566 | yes |
| claude_haiku | Z30 | B2 | 8 | 8/8 | 0 | 0 | 2.0 | 8153 | 14612 | yes |
| claude_haiku | Z30 | CAb | 8 | 7/8 | 5 | 0 | 1.0 | 2224 | 8382 | yes |
| claude_haiku | Z30 | CAv | 8 | 8/8 | 0 | 0 | 1.0 | 2480 | 6626 | yes |
| claude_haiku | Z30 | TC | 4 | 3/4 | 1 | 0 | 104.2 | 98278 | 15136 | yes |
| claude_haiku | Z30 | X5b | 8 | 8/8 | 0 | 0 | 2.8 | 9116 | 12046 | yes |
| claude_haiku | Z300 | B2 | 8 | 7/8 | 0 | 1 | 2.8 | 16287 | 18930 | yes |
| claude_haiku | Z300 | CAb | 8 | 8/8 | 0 | 0 | 1.0 | 2291 | 7826 | yes |
| claude_haiku | Z300 | CAv | 8 | 8/8 | 0 | 0 | 1.0 | 5528 | 7350 | yes |
| claude_haiku | Z300 | TC | 4 | 4/4 | 0 | 0 | 102.8 | 97623 | 15995 | yes |
| claude_haiku | Z300 | X5b | 8 | 8/8 | 0 | 0 | 2.2 | 11377 | 12475 | yes |
| codex_sol | Z100 | B2 | 8 | 7/8 | 3 | 1 | 2.8 | 66907 | 1690 | yes |
| codex_sol | Z100 | CAb | 8 | 8/8 | 0 | 0 | 1.0 | 20280 | 1576 | yes |
| codex_sol | Z100 | CAv | 8 | 8/8 | 0 | 0 | 1.0 | 20186 | 1542 | yes |
| codex_sol | Z100 | X5b | 8 | 8/8 | 0 | 0 | 2.5 | 51548 | 1047 | yes |
| codex_sol | Z30 | B2 | 8 | 8/8 | 0 | 0 | 2.5 | 65466 | 1344 | yes |
| codex_sol | Z30 | CAb | 8 | 8/8 | 0 | 0 | 1.0 | 24080 | 1462 | yes |
| codex_sol | Z30 | CAv | 8 | 8/8 | 0 | 0 | 1.0 | 22678 | 1452 | yes |
| codex_sol | Z30 | TC | 4 | 4/4 | 0 | 0 | 102.5 | 1996255 | 2660 | yes |
| codex_sol | Z30 | X5b | 8 | 8/8 | 0 | 0 | 2.5 | 64412 | 858 | yes |
| codex_sol | Z300 | B2 | 8 | 8/8 | 0 | 0 | 2.4 | 54871 | 1914 | yes |
| codex_sol | Z300 | CAb | 8 | 8/8 | 0 | 0 | 1.0 | 19947 | 1571 | yes |
| codex_sol | Z300 | CAv | 8 | 8/8 | 0 | 0 | 1.0 | 23227 | 1530 | yes |
| codex_sol | Z300 | TC | 4 | 4/4 | 0 | 0 | 99.0 | 1983395 | 2983 | yes |
| codex_sol | Z300 | X5b | 8 | 8/8 | 0 | 0 | 2.2 | 50904 | 1062 | yes |
| gemini_flash | Z300 | CAv | 2 | 2/2 | 0 | 0 | 1.0 | 3902 | 2042 | no |

## Wrong-step rate by quarter of the plan (complete cells, pooled)

| Arm | Q1 | Q2 | Q3 | Q4 | MH odds ratio Q4 vs Q1 (95% CI) |
|---|---|---|---|---|---|
| B2 | 0.00% (0/672) | 0.00% (0/672) | 0.00% (0/672) | 0.74% (5/672) | inf |
| X5b | 0.00% (0/672) | 0.00% (0/672) | 0.00% (0/672) | 0.00% (0/672) | — |
| CAv | 0.00% (0/672) | 0.00% (0/672) | 0.00% (0/672) | 0.00% (0/672) | — |
| CAb | 0.15% (1/672) | 0.30% (2/672) | 0.30% (2/672) | 0.00% (0/672) | — |
| TC | 0.00% (0/224) | 0.45% (1/224) | 0.00% (0/224) | 0.00% (0/224) | — |

Incomplete cells (reported, not scored): gemini_flash|Z300|CAv.
