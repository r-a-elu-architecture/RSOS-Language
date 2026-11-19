# Pre-registration SC2: the first predicted gap of the operation table

Fixed 19 Nov 2026, 08:40 Vilnius (06:40 UTC), **before the operation is built**, before any SC2 task exists and before
any SC1 result was seen. Decision D102. Table and law: `experiments/OPERATION_TABLE.md`.

## 1. What is predicted

The operation table orders Core operations by what they read and write. One cell is empty: an operation that **scans
the whole state and computes a new value for every match** (gap D). No such operation exists in RSOS Core, in the A7/A8
harness or in any task run so far. The measured law (one-call JSON Patch fails more often the more of the state it must
read itself: 0.00% when it reads nothing, 0.14–0.17% for one or two keys, 2.31% for a whole-state scan; RSOS blind 0
failures on every row) predicts its properties before it is built.

## 2. The operation (form fixed now)

Core: `derive_where(field, cond_field, equals, add, max)`. For every object `o` with `o.cond_field = equals`:
`o.field := min(int(o.field) + add, max)`. Atomic with the step; no match is not an error; `E_NOT_INTEGER` if a matched
value is not an integer; `E_NOT_KEY`/`E_PARSE` as in Core. Deterministic. RSOS keyword: named by the language's author
from the symbols before the build, and recorded here as an amendment before any run.

Request template (robot scene): "Move every object owned by {robot} {n} cell(s) {right|up} ({x|y} plus {n}, capped at 9)."

## 3. Tasks

The SC1 scene and generator (`experiments/sc1_tasks.py`: 50 objects, 300 keys, 56 requests, depth 4, three drift
events), new seeds **1000–1015**, with **8 of the 56 requests per task** of the new kind, placed by the seed; the
`reassign_where` hand-overs of the SC1 mix stay in, so both scan kinds are measured in the same runs. 128 new-kind
requests per model. Exported to `bench/statebench_v1_SC2.jsonl` with its sha256 before any run.

## 4. Arms, models, settings

As SC1 (A8 settings): B2 (one-call JSON Patch with literal values from the full state, one audit) and X5b (RSOS blind),
Mistral Large 4 and Gemini 3.8 Flash, temperature 0, top_p 1, 2 workers. The X5b planner grammar gains one line
describing the new operation; that is the only prompt change, applied before any run. A zero-call replay check must
pass first (oracle plans exact on every arm, every drift repaired at 0 calls, no value reaching the blind planner).

## 5. Predictions

| ID | Prediction | Pass when |
|---|---|---|
| **Q1** | RSOS blind stays exact on the new operation | X5b exact on 16/16 on each complete model, 0 failed `derive_where` steps |
| **Q2** | **The gap's JSON Patch failure rate, predicted from the law** | B2 fails ≥ 5% of `derive_where` requests, pooled over the complete models (≥ 7 of 128 per model on average) |
| **Q3** | The law's ordering holds inside one run | B2 failure rate per request: `derive_where` > `reassign_where` > one-key operations, pooled |
| **Q4** | The channel saving is largest on the new row | RSOS program + digest ≤ 0.1× the bytes of JSON Patch + digest on `derive_where` steps (0 model calls, measured at export) |
| **Q5** | A new operation is learnt from one grammar line | X5b proposes ≤ 1 invalid operation per task on average (all rejected before they run) |

Basis for Q2: `reassign_where` 2.31% across all A7/A8 models; `derive_where` adds a value read and an arithmetic step
per match, each of which alone added failures on the one-key rows. The prediction is that the effects compound, to at
least twice the scan rate.

## 6. What would count against the law

Q2 failing (JSON Patch handles the new row at the rate of the one-key rows) means the law's first factor (scanning) does
not compound with the second (computing); the table then orders but does not predict. Q1 failing means blind planning
does not extend to a new operation learnt from its description, and is reported first.

## 7. Order

This pre-registration published now, before the SC1 results → RSOS name chosen → operation built in Core (registry status
`specified` → `implemented` → `tested`) and in the harness → SC2 tasks exported with sha256 → replay check → runs →
`experiments/sc2_analyse.py` (written before the runs) → report, confirming or not.

## Amendment 1 (19 Nov 2026, 08:39 Vilnius; before the build, before any run)

RSOS name chosen by the language's author: **FLOW** (owner, 08:39, after weighing FLOW, SHIFT, BEAM, MOVE and LIGHT;
LIGHT, proposed first at 08:34, stays the White Dragon's light and the origin of `reconcile`). FLOW is the language's
existing statement `FLOW <source> DIRECTION … TO …` (register U3, U22: a flow with a direction), used in the state
syntax with an OVER clause:

    FLOW x OVER owner rover +1 CAP 9      ≡  derive_where(field=x, cond_field=owner, equals=rover, add=1, max=9)

"Everything of rover flows one cell on, at most to the edge." Nothing else changes.
