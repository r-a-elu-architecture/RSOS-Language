# Pre-registration A8: does blind planning hold across model families, model sizes and a stronger M\*? ($0)

Written 18 Nov 2026, 14:50 Kyiv, before any A8 model call. Source: pass 10 (`corpus/dragon_landings/`, sealed): each
limit of the A7 result is turned into a test that costs nothing. Harness: A7's (`a7_arms.py`, `a7_run.py`), unchanged
except for one new arm (B2s) and one new backend (`a7_openai.py`); replay checks pass with B2s on S1 and L3; the A7a
and A7b hashes are unchanged (42be52d5…, b1287a37…).

## Limits addressed, and how

| Limit of A7 | A8 test | Access, $0 |
|---|---|---|
| One model (Haiku 5.5) | **Claude ladder:** Sonnet 5.5 and Opus 5.5 (`A5_MODEL`) | owner's Claude plan, `claude -p` |
| One model family | **Other families:** any OpenAI-compatible free tier (e.g. Google AI Studio, Groq, Mistral, OpenRouter `:free` models) and local open models (Ollama) | free keys / owner's PC |
| Our M\* only | **B2s:** M\* told to work out the current value of every line a request reads, applying all earlier patches, before each patch | as above |
| Few M\* failures | the cells where M\* failed (S1, L3) run on every model | as above |
| Accounting cost | every result keeps per-call token counts; re-pricing from any price sheet is offline | — |

Cells per model: **S1** (14 steps, 30 keys) and **L3** (56 steps, 300 keys); arms **B2** and **X5b** on every model;
**B2s** on Haiku 5.5. Labels: `sonnet55`, `opus55`, `haiku_b2s`, `local_<model>`, `<provider>_<model>`. A model that
cannot complete a cell (quota, context) is reported as such, not dropped silently.

## Predictions (fixed now)

| # | Prediction | Pass if |
|---|---|---|
| **G1** invariance | blind planning stays exact on capable models | X5b ≥ 15/16 on every cell run with every Claude model and every free-tier model of ≥ 7B parameters or undisclosed size |
| **G2** error class | M\*'s errors are state-dependent on every family | pooled over all models, ≥ 90% of B2 and B2s failed steps are INHERIT/FUSE/SCALE/ROUTE/REHOST kinds, and X5b's failed steps ≤ 10% of B2's |
| **G3** cost | blind is cheaper per correct task at 300 keys on every priced model | X5b cost per correct ≤ B2's on L3 for Haiku and Sonnet (the sheets in `a5_prices.json`, api basis); Opus and free tiers reported in tokens |
| **G4** stronger M\* | telling M\* to track state does not close the gap | on Haiku, B2s exact ≤ X5b exact on S1 and L3, and B2s cost per correct ≥ 1.2× X5b's on L3 |
| **G5** families | no family where M\* is clearly better | on no model does B2 beat X5b by ≥ 2 exact tasks in a cell |
| P11 (A7c) | small local model | unchanged: X5b ≥ 12/16 on S1 where B2 on the same model ≤ 4/16 |

**REACH:** `REACH families ON limits.one_family TARGET 10 AGAINST one_family MEASURE model_families_with_blind_exact`:
the measured distance is the number of model families on which X5b stays exact.

## Analysis

`python experiments/a8_analyse.py` (0 model calls) → `results/a8.json`: per model, cell and arm, exact, failed steps
by kind, cost per correct (where priced), and G1–G5. Every failed prediction goes to the failure map.

**Amendment log (18 Nov 2026, after the Claude ladder, before any free-tier run counts).** `a7_openai.py` sends an
explicit `User-Agent: rsos-a8/1.0` and `Accept: application/json`. Groq's edge (Cloudflare) refused Python's default
`Python-urllib/3.x` agent with `HTTP 403, error code: 1010` on the owner's first smoke call; no task ran. Transport
header only; prompts, settings, arms and predictions are unchanged.

**Amendment 2 (19 Nov 2026, 00:10 Kyiv; before any run of Mistral, Gemini, Qwen, gpt-oss-20b or the local model, and
before the remaining gpt-oss-120b tasks).**
1. *Record correction.* Amendment 1's header text is wrong: the code sends
   `User-Agent: rsos-a8/0.3.1 (+https://github.com/r-a-elu-architecture/RSOS-Language)` and no `Accept` header
   (`a7_openai.py` at `9bc86a2`). Transport only; nothing else changes.
2. *Runner fix (committed in `9bc86a2`).* A provider error now stops one task, is logged to
   `results/a7_errors_<cell>_<label>.jsonl`, and is never written as a result; a rerun resumes the missing tasks. Before
   the fix, a 429 stopped result writing and tasks finished in parallel were lost and re-run. **Every first-run outcome
   in the owner's console log (`results/a8_groq_gptoss120b_console_run1.txt`) is reported, including X5b seed 302
   failed (1 step failed after retries, inv=3), whatever the rerun shows.** For G1 the cell counts the first
   completed outcome of each task.
3. *Providers.* Mistral La Plateforme (free Experiment tier) and Google AI Studio (free tier) run S1 and L3; Groq
   (gpt-oss-120b, gpt-oss-20b, qwen3.8-27b) runs S1 only (L3 requests exceed the free 8,000 tokens a minute: reported
   as not runnable, not dropped); qwen2.5:1.5b local runs S1 (A7c, P11). The exact model id is recorded in the label
   and the results; `-latest` aliases are not used.
4. *New predictions, fixed now.* They are scored only on runs that start after this amendment; the gpt-oss-120b S1
   tasks already seen (run 1 and run 2) are excluded from G6–G8.

| # | Prediction | Pass if |
|---|---|---|
| **G6** decoupling | blind exactness does not depend on the model; M\*'s does more | across all models of ≥ 7B run after this amendment, X5b's exact count per cell ranges over ≤ 1 task, and B2's range is larger than X5b's in at least one cell |
| **G7** immunity | the runtime stops every invalid operation before it acts, on every family | 0 invalid operations executed on any model (every proposed invalid operation rejected before execution, checked in transcripts), and the mean invalid operations proposed per X5b task on non-Claude models ≥ 3× the Claude mean (A8) |
| **G8** same request | M\*'s failures belong to the request, not the model | at least one B2 failed step on L3 (same seed, same step) fails on ≥ 2 non-Claude families and also failed on a Claude model in A8 |

REACH (instrument, not a threshold): families with X5b exact (target 10) and size span with X5b exact (target 100×,
1.5B to frontier).

**Amendment 3 (19 Nov 2026, 00:35 Kyiv; before any Mistral or Gemini run).** One named-step prediction (White Dragon
pass 12, Mendeleev landing). Basis (Claude, A7 + A8): M\* failed L3 seed 712 step 35 in 3 of 4 runs and L3 seed 702 step
35 once; base rate of M\* failure per REHOST request 1.4% (8 of 553).

| # | Prediction | Pass if |
|---|---|---|
| **G9** named step | M\*'s failure is fixed by the request before the model is chosen | on L3, B2 fails seed 712 step 35 or seed 702 step 35 on at least one of Mistral and Gemini, while X5b ends exact on both tasks on both families |

Chance level, if M\* failures landed on REHOST requests at random: about 5% (2 named of 54 REHOST requests per L3 run,
about 1.5 failures expected over the two families). A miss is recorded in the failure map as the named-step effect not
generalising.
