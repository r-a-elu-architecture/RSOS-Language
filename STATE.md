# RSOS State Runtime: drop it into your agents

**For multi-agent workflows that edit shared state** (configs, plans, tickets, records, models that several agents
read and write). The model decides what should change; the RSOS runtime executes it, checks every copy and heals
drift. Measured on real LLM agents (A4, A5; pre-registered, every failure reported):

| | Best setup built for the same agents | RSOS (assembly line) |
|---|---|---|
| Model calls for a 14-step task | 42–43 | **2.2–2.4** |
| Cost per task (API prices) | 1× | **0.27–0.35× (2.8–3.7× cheaper)** |
| Time per task | ~100 s | **12 s** |
| Tasks fully correct | 31/32 | **32/32** |
| Injected drifts healed without a model call | 96/96 | **96/96** |

And when agents compute from their own copies, a Slipstream-style anchor protocol (our re-implementation) got
**0 of 16** tasks right, with 93 of 96 wrong values traced to silent drift; the RSOS integrity protocols got 15–16 of
16 (A4). These numbers come from the experiment harness (`experiments/a5_*.py`); this runtime is the same operation
set and integrity layer, packaged. Verify them yourself: [REPLICATE.md](REPLICATE.md).

## In 60 seconds (Python)

```bash
pip install -e .            # from a clone of this repository
```

```python
from rsoslang.state import Ledger, plan_prompt, parse_plan

led = Ledger({"auth.timeout_ms": "700", "auth.retries": "3", "search.retries": "6"})
p = plan_prompt(["Raise auth timeout by 100", "Set auth retries to auth plus search, at most 8"], led.state)
reply = your_model(p["system"], p["user"])          # one call for the whole task, any model
out = led.apply_plan(parse_plan(reply))             # the runtime computes every value; failures come back with a reason
healed = led.sync(worker_copy)                      # any agent's copy: drift restored, 0 model calls
```

## As an MCP tool (Claude Code, Claude Desktop, any MCP client)

```bash
claude mcp add rsos -- python -m rsoslang.mcp_server
```

Tools: `rsos_state_new`, `rsos_state_prompt` (one prompt for all requests), `rsos_state_apply` (execute a plan),
`rsos_state_sync` (heal an agent's copy, 0 model calls), `rsos_state_get`.

## The operations

`SET k v` · `DEL k` · `INHERIT d s [+n] [CAP m]` · `FUSE d a b [CAP m]` · `SCALE k f [CAP m]` ·
`ROUTE s = x : d v1 | v2` · `REHOST field a b`. Keys are dotted names; the model names keys, the runtime reads and
computes every value. That is why a whole task fits in one call: the operations do not depend on the state, so steps
no longer wait for each other's model round trips.

## Limits (stated, not hidden)

One model family (Claude Haiku 5.5), one task family (structured state editing), 16 tasks per set. 10× was the
target and was not reached; after batching, the model's thinking tokens are most of the bill. Cross-model and
real-workflow results are what we want next: run it on yours and tell us.
