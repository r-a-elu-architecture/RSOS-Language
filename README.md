# RSOS Language

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24304403.svg)](https://doi.org/10.5281/zenodo.24304403) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE) [![tests](https://github.com/r-a-elu-architecture/RSOS-Language/actions/workflows/tests.yml/badge.svg)](https://github.com/r-a-elu-architecture/RSOS-Language/actions/workflows/tests.yml)

*RSOS: an executable spatial-symbolic language for human–AI and AI–AI communication.* Whitepaper: R. A. Elu (2026),
[doi:10.5281/zenodo.24304403](https://doi.org/10.5281/zenodo.24304403) (all versions). Code: Apache 2.0. Software 0.3.1:
[doi:10.5281/zenodo.24339364](https://doi.org/10.5281/zenodo.24339364) (all versions: [doi:10.5281/zenodo.24317657](https://doi.org/10.5281/zenodo.24317657)).

## Blind planning: the model names keys, the runtime computes values

**For multi-agent workflows that edit shared state.** The planner writes the whole task as operations that name keys
and relations (`INHERIT auth.retries search.retries CAP 8`), never values; a deterministic runtime computes every
value, hash-checks every agent's copy and heals drift with zero model calls.

**Against the most efficient market pattern we could build** (A7a, pre-registered: one call writes the whole task as
JSON Patch, one audit call, the same model, seeds, hash check and audit rule), RSOS **matched or beat it on every
measured axis**: **32/32 exact vs 31/32**, **0.79–0.91× its cost per correct task** (95% CI below 1 on both task
sets), about 2 calls per task for both, **while the planner never saw a single state value**. The market pattern's one
failure was a step whose values depend on earlier steps; it stayed wrong after three attempts although the auditor
named the error each time. Against one model call per step (A5): **2.2–2.4 calls instead of 42–43, 0.27–0.35× the
cost, 12 s instead of ~100 s.**

**Limits:** one task family (30 keys, 14 requests), one model family (Claude Haiku 5.5), 32 tasks per arm; margins at
this scale are small. The next tests, with predictions fixed in advance, are in **[NEXT_TESTS.md](NEXT_TESTS.md)**.

**Try to break it.** Score any framework on the same 32 tasks with **[RSOS-StateBench](bench/)** (plain JSONL and a
scorer, no harness needed), or re-run A7 on a Claude plan for $0. Every result, confirming or not, is listed.

```bash
pip install rsoslang                             # or, from a clone: pip install -e .
claude mcp add rsos -- rsoslang mcp              # or with no install: claude mcp add rsos -- uvx rsoslang mcp
python experiments/a5_runtime_equivalence.py     # from a clone: this runtime replays every measured plan, 32/32 match
```

**MCP:** listed in the [official MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.r-a-elu-architecture/rsos) as `io.github.r-a-elu-architecture/rsos` (0.3.1). Works in any MCP
client over stdio (Claude Code, Claude Desktop, Cursor, …). Verified on 18 Nov 2026 on Windows 11: `pip install rsoslang`
then `claude mcp add` → Connected; `uvx rsoslang mcp` starts with no install step.

**[Drop it in (Python or MCP) →](STATE.md)** · **[StateBench →](bench/)** · **[Replicate it →](REPLICATE.md)** ·
**[All results, failures included →](https://r-a-elu-architecture.github.io/RSOS-Language/results.html)**

**A spatial-symbolic programming language for humans and AI.** You write a program the way you think it: objects in
a scene, placed, touched, pierced, entered, coloured, connected by lines, kept in the rooms of a house. The same
program runs in two places:
- in a **machine**: an AI agent workflow, a simulation;
- in a **person**: a practised mental model, delivered as a timed session of images, words, sounds, scents and
  vibration codes.

**[Open the editor →](docs/editor.html)** A real 12-module support agent, painted. Put a guest at the head, heart,
brain or beside a module, and see the measured effect.

**All results** (pre-registered, real LLM agents, every failure reported; 49 predictions so far, 29 passed, 20
failed): [results page](https://r-a-elu-architecture.github.io/RSOS-Language/results.html). Newest first: **A7a**
(blind planning vs one-call JSON Patch, above), **A5** (one plan vs one call per step), **A4** (hidden drift becomes
wrong answers for an anchor protocol without a hash check: 0/16), **A3c** (0.141× the channel tokens of a
Slipstream-style anchor protocol at zero model calls). Whitepaper v2 ([doi:10.5281/zenodo.24320392](https://doi.org/10.5281/zenodo.24320392),
17 Nov) covers A1–A3b and HT1; A3c–A7a are in `experiments/` and will be in the next version.

**First real-host test (A1, 17 Nov 2026, pre-registered):** three LLM agents (planner, worker, checker) on 8 tasks. The RSOS palace protocol used about 7× fewer channel tokens than JSON with full state (2,563 vs 17,311), finished 7/8 tasks exactly correct (JSON 5/8), and caught and healed 24/24 injected drifts with 0 model calls (38 tokens per repair). Summaries + retrieval: 0/8 correct, 24/24 drifts kept. One model family, 8 tasks. Report: [`experiments/A1_REPORT.md`](experiments/A1_REPORT.md).

## Purpose

RSOS grew from one seed: healing, transforming, signalling and evolving. It integrates the whole of human
experience, including its shadow, so that what is integrated can be transformed rather than denied. Because its seed
is healing, RSOS is used with consent and for the good of the person or system it works with, never to harm or
coerce. See [`RESPONSIBLE_USE.md`](RESPONSIBLE_USE.md),
[`GOVERNANCE.md`](GOVERNANCE.md), [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`TRADEMARKS.md`](TRADEMARKS.md).

## What makes it different

- **Where you place an operator decides what it does.** The same spell corrector placed at a module's head, heart,
  brain or beside it gives four different results, measured on held-out data.
- **Meanings in three tiers.**
  - a fixed core, shared by everyone;
  - declared variations, scoped to a person, host, world or state;
  - meanings left open on purpose, found by search.

  Nothing changes silently.
- **The host decides.** Every operation runs on a declared host with its own channels and states. A cue on a channel
  the host does not have is an error.
- **Safety is in the compiler.** Person-facing operations need consent and pass a constitution of seven checks;
  return to baseline is always available.
- **Every result is reproducible.** Pre-registered experiments, seeds, result hashes; negatives published with
  positives.

## Quick start

```bash
pip install -e .
python -m rsoslang check examples/robot_head.rsl
python -m rsoslang ir examples/sol_remote.rsl
RSOS_CUE_FRAMEWORK=/path/to/RSOS-Multimodal-Cue-Framework python -m rsoslang session examples/healing.rsl
./reproduce.sh
```

## Use it from Claude or any MCP assistant

```json
{"mcpServers": {"rsos-language": {"command": "python", "args": ["-m", "rsoslang.mcp_server"],
  "env": {"RSOS_CUE_FRAMEWORK": "/path/to/RSOS-Multimodal-Cue-Framework"}}}}
```

The tools are `rsos_statements`, `rsos_check`, `rsos_compile`, `rsos_session`, `rsos_paint_workflow`,
`rsos_apply_gestures` and `rsos_paint_graph`.

## Results

See `results/BUILD_REPORT.md`. It covers every pre-registered test, the ones that failed included.

## Licence

Apache 2.0. Research and development software; not a medical device.

<!-- mcp-name: io.github.r-a-elu-architecture/rsos -->
