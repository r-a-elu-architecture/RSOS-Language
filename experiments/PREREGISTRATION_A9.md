# PREREGISTRATION A9: the strongest rival patterns, three state sizes, one law (sealed 20 Nov 2026, before any A9 call)

Author: R. A. Elu. Code: `a9_tasks.py`, `a9_beacon.py`, `a9_arms.py`, `a9_run.py`, `a9_analyse.py`,
`test_a9.py` (offline, 0 model calls: ALL OK at seal). Commit order: this file and the code, then the beacon, then
results.

## 1. Why

Two attacks remain on A7–A8 and SC1–SC2: **"you beat a weak baseline"** (only one-call JSON Patch was compared) and
**"the error-window law was fitted after the fact"** (AGENTS2 analysed existing runs). A9 adds the two strongest
patterns we know of and seals, before any call, what the error-window law predicts for **every** arm, ours and
the rivals', at three state sizes.

The law, in the form tested here: a step fails according to the number of state changes between the moment its
values were read and the moment it is applied. An arm that reads the state once at the start and computes values
itself (B2) accumulates such changes along the plan; an arm that reads at the moment each step runs (X5b, CAb, CAv
when its code reads `state`, TC) does not.

## 2. Tasks (nobody chooses them)

The A7 long-task generator (56 requests, chain depth 4) at three sizes: **Z30** (5 services, 30 keys), **Z100** (17,
102 keys), **Z300** (50, 300 keys; the size of L3). 8 seeds per cell from the public drand beacon (League of Entropy
mainnet, default chain, 30-second rounds, genesis 1595431050), **round 6657746, emitted 20 Nov 2026 08:30:00 UTC**,
after this commit: seed_i = int(sha256("<randomness>:A9:<cell>:<i>")[:16], 16), i = 0…7.

## 3. Arms (same models, same tasks)

| Arm | What the model sees | What it writes | Calls per task |
|---|---|---|---|
| B2 | full state + all requests | JSON Patch with literal values (A7, unchanged) | 2–6 |
| X5b | requests only | RSOS operations; runtime computes values (A7, unchanged) | 2–6 |
| **CAv** | full state + all requests | Python, one function per request, run on the live state | 1–3 |
| **CAb** | requests only (+ field names) | the same Python program, blind | 1–3 |
| **TC** | one request at a time; tools get / find / services / set / delete | tool calls; reads what it needs, computes values, writes | ≈ 1–4 per request |

B2 and X5b keep A7's auditor and replicas; CAv, CAb and TC have neither (their own pattern). Code runs in a separate
Python process: isolated mode, empty environment, no imports, no names or attributes starting with `_`, no I/O
builtins, 20 s timeout; a program rejected by the gate is never executed. Up to 2 retries with the error shown, as in
A7. Scoring is A7's: a step is correct if its change, applied to the arm's own state before the step, equals the true
change; a task is exact if the final state equals the truth.

TC runs on the first 4 seeds of Z30 and Z300 only (its calls per task are about 50× the others').

## 4. Families and order

Families (label = results file label): **claude_haiku** (Claude Haiku 5.5 through `claude -p`, the model on which
B2 failed most in A7–A8), **codex_sol** (GPT-6.2 Sol through Codex, reasoning low), and, if available before their
first call, **gemini_flash** (Gemini 3.8 Flash, free tier) and **mistral_large4** (Mistral Large 4). An open-weights
family may be added by an amendment that names the model before its first call. Settings as A8 (temperature 0 where
the backend allows; output cap 16,000 tokens per call).

Order per family (decisive cells first): Z300 TC, CAv, CAb, B2, X5b → Z30 all five → Z100 B2, X5b, CAv, CAb.
A cell is **complete** when all its seeds ran (TC: 4; others: 8). Every prediction is scored on complete cells only,
pooled across families; incomplete cells are reported as incomplete, never dropped, never padded. Results are scored
at 13:30 Vilnius with whatever is complete; later cells are added with their own commit and the same script.

## 5. Predictions (scored by `a9_analyse.py`, unchanged after this commit)

A "wrong step" is a step not executed or executed incorrectly. Quarters: steps 1–14, 15–28, 29–42, 43–56.

| # | Prediction | Pass if |
|---|---|---|
| Q1 | Blind RSOS stays exact | X5b exact on ≥ 90 % of tasks in every complete cell and ≥ 95 % pooled |
| Q2a | **The law, B2:** errors rise along the plan | B2 wrong-step rate in Q4 > Q1, and Mantel–Haenszel odds ratio (Q4 vs Q1, stratified by request kind) > 1 |
| Q2b | **The law, readers:** no rise for arms that read at run time | for X5b, CAb, CAv, TC each: Q4 rate − Q1 rate ≤ 0.5 pp |
| Q3a | B2 gets worse with state size | B2 task failure rate at Z300 > Z30 |
| Q3b | Blind arms do not | X5b and CAb exact rates at Z30 and Z300 within 10 pp |
| Q4 | **The mechanism is blindness, not syntax** | CAb exact ≥ 90 % pooled and within 10 pp of X5b |
| Q5a | RSOS is more compact than Python | X5b output tokens per task < CAb at Z300 |
| Q5b | RSOS is the cheapest exact arm at 300 keys | X5b tokens per correct task < B2 and < TC at Z300 |
| Q6a | Tool-calling pays in calls | TC calls per task ≥ 20× X5b |
| Q6b | Tool-calling beats one-call JSON Patch on steps | TC wrong-step rate ≤ B2 at Z300 |
| Q6c | Tool-calling input grows with size | TC input tokens per task Z300 / Z30 ≥ 1.2 |
| Q7 | Blind RSOS at least as exact as tool-calling | X5b exact rate ≥ TC at Z300 |

What would count against RSOS, said in advance: if CAb ties X5b (Q4 passes), the exactness comes from **not
showing the model the values and executing at run time**, not from RSOS syntax; the RSOS claim then rests on that
principle plus compactness and cost (Q5). If TC is as exact and the cost gap is small (Q5b fails), tool-calling is a
sufficient answer for these tasks, and we say so.

## 6. Prior (inherited, labelled)

From A7/A8 L3 (300 keys, Claude): B2 failed 8 of 553 whole-state reassignments (1.4 %); AGENTS2 (sealed, existing
runs): B2 per-step error 0.19 % → 2.33 % from Q1 to Q4. These set the predictions; they are not A9 data.

## 7. Safety and limits

Model-written code is executed only after the static gate, in a separate process with no environment and a timeout.
Limits known now: 8 tasks per cell (4 for TC); one task family; TC capped at 4 turns per request; no auditor for the
new arms.

## Amendment 1 (20 Nov 2026, 09:20 Vilnius; before the beacon round and before any scored call)

Transport only. On the owner's Windows machine the Claude smoke failed: `claude -p` could not find its login because
A5's frozen environment filter (`a5_llm.KEEP`) passes no Windows profile variables. `a9_run.py` now extends that filter
at run time on Windows only (USERPROFILE, APPDATA, LOCALAPPDATA, SYSTEMROOT, TEMP, TMP, HOMEDRIVE, HOMEPATH, PATHEXT,
COMSPEC, ProgramData, ProgramFiles). `a5_llm.py` is unchanged. No arm, prompt, task, prediction or score changes.
