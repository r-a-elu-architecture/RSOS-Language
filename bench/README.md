# RSOS-StateBench v1: multi-agent shared state

32 tasks where agents edit one shared configuration state (30 lines, 14 change requests per task), from the
pre-registered experiments A5 and A7. Each task gives the start state, the requests in order, the true state after
every step, the final truth and the drift events of the integrity test. **Use any framework, any model, any number of
agents**, write your final states to a JSONL file and score it. No RSOS code is needed.

| File | Content |
|---|---|
| `statebench_v1_S1.jsonl` | 16 tasks (seeds 100–107, 300–307), sha256 `0c76c17d7d57859e…` |
| `statebench_v1_S2.jsonl` | 16 tasks (seeds 400–415), requests that depend on earlier values marked `Worker-computed:`, sha256 `11c5b8d4a8b460db…` |
| `score.py` | the scorer (0 model calls) |

```bash
python bench/score.py my_results.jsonl --name "my framework + my model"
```

Submission, one line per task: `{"set": "S1", "seed": 100, "final_state": {...}, "calls": 2, "cost_usd": 0.0012}`
(`calls` and `cost_usd` optional; cost per correct task is computed when every task has a cost). The `drift` events
are optional: inject them into one agent's copy before the given step if your system keeps several copies.

## Leaderboard

Exact tasks of 32 (S1 + S2). Cost per correct task at Claude Haiku 5.5 API prices (A5's api basis). Add yours with a
replication issue: the results file, the scorer output and its `submission_sha256`.

| System | Model | Exact | Calls / task | Cost per correct task | Planner sees values | Source |
|---|---|---|---|---|---|---|
| RSOS blind (X5b): operations, runtime computes, one audit | Haiku 5.5 | **32/32** | 2.3 | **$0.00120 / $0.00130** | **no** | A7a |
| RSOS (X5r) | Haiku 5.5 | 32/32 | 2.3 | $0.00125 / $0.00133 | lines named | A7a |
| One-call JSON Patch + audit (M\*), same hash check | Haiku 5.5 | 31/32 | 2.1 | $0.00153 / $0.00143 | all | A7a |
| One model call per step (H-dragon, per-step protocol) | Haiku 5.5 | 31/32 | 42.6 | $0.00460 / $0.00407 | all | A5 |

Costs are S1 / S2. All rows used the same seeds; the A7a rows also the same hash check, zero-call healing and audit
rule. Limits: one task family, one model family. Results on other models and frameworks, confirming or not, are the
point of this table.
