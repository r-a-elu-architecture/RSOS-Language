# RSOS Language

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24304403.svg)](https://doi.org/10.5281/zenodo.24304403) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE) [![tests](https://github.com/r-a-elu-architecture/RSOS-Language/actions/workflows/tests.yml/badge.svg)](https://github.com/r-a-elu-architecture/RSOS-Language/actions/workflows/tests.yml)

*RSOS: an executable spatial-symbolic language for human–AI and AI–AI communication.* Whitepaper: R. A. Elu (2026),
[doi:10.5281/zenodo.24304403](https://doi.org/10.5281/zenodo.24304403) (all versions). Code: Apache 2.0. Software release 0.2.0:
[doi:10.5281/zenodo.24317658](https://doi.org/10.5281/zenodo.24317658).

**A spatial-symbolic programming language for humans and AI.** You write a program the way you think it: objects in
a scene, placed, touched, pierced, entered, coloured, connected by lines, kept in the rooms of a house. The same
program runs in two places:
- in a **machine**: an AI agent workflow, a simulation;
- in a **person**: a practised mental model, delivered as a timed session of images, words, sounds, scents and
  vibration codes.

**[Open the editor →](docs/editor.html)** A real 12-module support agent, painted. Put a guest at the head, heart,
brain or beside a module, and see the measured effect.

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
