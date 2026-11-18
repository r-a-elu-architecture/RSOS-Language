# Replicate the core claim (about 1 hour, under $1 at API prices)

**Claim (A5, pre-registered):** in a three-agent workflow that edits a shared 30-line state over 14 change requests
with 3 injected drifts, the RSOS assembly line (X5: the model writes RSOS operations for the whole task in one call,
the runtime executes them, one audit call) uses **2.2–2.4 model calls per task instead of 42–43**, costs
**0.268× (S1) and 0.354× (S2)** of B1 (the same agents with one model call per step: RSOS's own per-step protocol, H-dragon) at API prices, and is
**16/16 exact on both sets**. Failure would be: X5/B1 cost ratio above 0.5 on either set, or X5 exact below 15/16.

## What you need

- Python 3.11+, `pip install -e .` and `pip install tiktoken`
- The Claude Code CLI (`claude`), logged in or with `ANTHROPIC_API_KEY` set. Model: `claude-haiku-5-5`
  (any other: `export A5_MODEL=<model id>`; a different model is a new result, please label it).

## Run

```bash
python experiments/a5_run.py replaycheck S1      # offline: the harness reproduces the recorded baseline, 0 calls
python experiments/a5_run.py run S1 B1,X5        # 16 tasks x 2 arms, about 16 minutes
python experiments/a5_run.py run S2 B1,X5
python experiments/a5_analyse.py                 # writes results/a5_cost.json: ratios, CIs, verdicts
```

Run in a fresh clone (the runner appends to `results/a5_results_S*.jsonl`). Compare your `X5 / B1` ratio and exact
counts with the table in `experiments/A5_REPORT.md` §1.

## Check our numbers without any model call

```bash
python experiments/a5_analyse.py                 # recomputes results/a5_cost.json from the recorded runs (sha 9cd1eb92…)
python experiments/a5_runtime_equivalence.py     # the shipped rsoslang.state runtime replays every recorded X5 plan: 32/32 final states match
python experiments/a3c_edges_check.py            # A3c per-edge numbers from text-free counts
```

## Tell us

Open an issue titled "Replication: <model> <date>" with your `results/a5_cost.json`. Every replication, confirming or
not, is listed in the README and credited in the next whitepaper version.
