---
license: apache-2.0
pretty_name: RSOS pre-registered multi-agent experiments
tags:
  - multi-agent
  - llm-agents
  - agent-communication
  - shared-state
  - mcp
  - pre-registered
  - negative-results
  - langgraph
---

# RSOS pre-registered multi-agent experiments (A1–A9)

Results, transcripts, pre-registrations and reports of the RSOS experiments on real LLM agents. Every experiment was
pre-registered before it ran; every failed prediction is included.

**Headline (A9, 20 Nov 2026):** against the strongest rival patterns we know, on tasks drawn from a public randomness
beacon after the predictions were public: RSOS blind planning 48/48 exact, Python seeing the state 48/48, blind Python
47/48 (one silent reversed copy), one-call JSON Patch 46/48 (errors only in the last quarter of the plan, as sealed),
a tool-calling agent 15/16 at about 100 calls per task. The principle (the model never computes a value) drives
exactness more than the RSOS syntax; RSOS was not more compact than Python (a published miss).

**Earlier:** A7 (80 tasks, up to 300 keys): RSOS blind 80/80 vs one-call JSON Patch 77/80. A8 (six models from four
companies): RSOS blind 256/256; JSON Patch failed at the step named in public beforehand. A5: 2.2–2.4 model calls per
task instead of 42–43. Every injected drift repaired with 0 model calls.

**Limits:** one task family (configuration-style key–value state), 16 tasks per cell, one writer per step (concurrent
writes not yet tested). Failed predictions are listed in `experiments/FAILURES_MAP.md` in the code repository.

## Contents

| Path | What |
|---|---|
| `experiments/PREREGISTRATION_*.md` | the predictions, written before each run |
| `experiments/*_REPORT.md` | the reports, with every verdict |
| `results/*_results_*.jsonl` | one record per task and arm: success, accuracy, final state, drift events |
| `results/*_transcripts_*.jsonl` | every message between agents and runtime, with token counts |
| `results/*.json` | analyses; each carries a `results_sha256` you can recompute |

Two A3c coded transcripts are held back; their SHA-256 and text-free counts are in `results/a3c_withheld.json`, and
`experiments/a3c_edges_check.py` reproduces every A3c number from the counts.

## Reproduce

Code, analysis scripts and the one-hour replication guide (under $1):
[github.com/r-a-elu-architecture/RSOS-Language](https://github.com/r-a-elu-architecture/RSOS-Language)
(`REPLICATE.md`). Every analysis re-runs from these files with 0 model calls.

## Cite

Software v0.5.0: [doi:10.5281/zenodo.24401943](https://doi.org/10.5281/zenodo.24401943) (all versions:
[doi:10.5281/zenodo.24317657](https://doi.org/10.5281/zenodo.24317657)). Whitepaper:
[doi:10.5281/zenodo.24304403](https://doi.org/10.5281/zenodo.24304403).
