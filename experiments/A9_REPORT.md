# A9 report (round 1, 20 Nov 2026): the strongest rival patterns, three sizes, one law

**Status: round 1.** Scored at 14:20 (UTC+02:00) Helsinki, Kyiv, Riga, Sofia, Tallinn, Vilnius with the sealed `a9_analyse.py` on every complete cell: Claude Haiku 5.5
(all 13 cells) and GPT-6.2 Sol through Codex (300- and 30-key cells except tool-calling at 30 keys). Codex's remaining
cells (tool-calling at 30 keys, all 100-key cells) are running after a usage-limit reset; Gemini 3.8 Flash completed 2
tasks before its free quota ran out (incomplete). Round 2 re-scores with the same script and is added with its own
commit. Re-score yourself: `python3 research/verify.py`.

Tasks: drand round 6657746 (randomness `22da2428e4b5f26a…`), drawn after the predictions were public (09:08). All 174 task
seeds in this round trace back to the beacon. Amendments 1–5 are in the pre-registration (transport fixes; Gemini
without tool-calling; an open 7B model withdrawn below the capability floor before any scored call).

## What it shows, in plain words

- **The principle holds; the syntax is not what makes it exact.** Every arm that does not compute values from a copy
  of the state stayed exact: RSOS blind **40/40**, Python seeing the state 40/40, blind Python **39/40** (one-call JSON Patch 39/40, one refused step). Q4, the outcome
  written in advance as the one against RSOS, passed: exactness comes from never showing the model the values and
  reading them at run time.
- **RSOS blind is the only arm with no failure of any kind** in this round. Blind Python's one failure was silent: a
  stray line copied a value in the reversed direction (request 14), and four later requests that copy from those keys
  inherited it (5 wrong steps).
- **Tool-calling is exact but expensive:** 11/12 tasks exact (one silent wrong step) at about **100 model calls per
  task** against 2–3 for RSOS blind; on Codex at 300 keys about **2.0 million input tokens per task** against about
  51,000.
- **Missed: RSOS is not more compact than Python** (Q5a failed). Blind Python wrote fewer tokens; part of the gap is
  RSOS blind's audit call, which the Python arms do not have, but the prediction failed and stands.
- **Weak passes, said plainly:** Q2a ("JSON Patch errors rise along the plan") and Q3a ("JSON Patch worse with size")
  pass by the sealed rule on **a single refused JSON Patch step** (last quarter, 300 keys). Strong models made almost no
  JSON Patch errors on these tasks; one event is not evidence for a curve.

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
| Q6c Tool-calling input grows with size | **pass** |
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
| codex_sol | Z30 | B2 | 8 | 8/8 | 0 | 0 | 2.5 | 65466 | 1344 | yes |
| codex_sol | Z30 | CAb | 8 | 8/8 | 0 | 0 | 1.0 | 24080 | 1462 | yes |
| codex_sol | Z30 | CAv | 8 | 8/8 | 0 | 0 | 1.0 | 22678 | 1452 | yes |
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
| B2 | 0.00% (0/560) | 0.00% (0/560) | 0.00% (0/560) | 0.18% (1/560) | inf |
| X5b | 0.00% (0/560) | 0.00% (0/560) | 0.00% (0/560) | 0.00% (0/560) | — |
| CAv | 0.00% (0/560) | 0.00% (0/560) | 0.00% (0/560) | 0.00% (0/560) | — |
| CAb | 0.18% (1/560) | 0.36% (2/560) | 0.36% (2/560) | 0.00% (0/560) | — |
| TC | 0.00% (0/168) | 0.60% (1/168) | 0.00% (0/168) | 0.00% (0/168) | — |

Incomplete cells (reported, not scored): gemini_flash|Z300|CAv.
