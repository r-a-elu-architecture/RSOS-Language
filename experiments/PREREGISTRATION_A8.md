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
