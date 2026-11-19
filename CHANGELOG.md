# Changelog

## 0.4.0 (19 Nov 2026)

- **RSOS Core 1.0** (`rsoslang.core`): the technical layer. Neutral operation names (`set`, `copy`, `delete`, `derive`,
  `sum_into`, `multiply`, `select_if`, `reassign_where`; `state_digest`, `reconcile`), one compiled form (a JSON IR with
  a schema and a digest), a Core syntax beside the RSOS syntax (both compile to identical IR, tested), stable error
  codes, and an RFC-style specification (`spec/core/STATE_OPS.md`). `registry/operators.json` is the single source of
  truth (status, evidence, tests, origins); `spec/core/OPERATORS.md` is generated from it and CI fails if they differ.
  Publication rule: an operator is in Core only once tested and backed by an experiment (`copy` is tested, not yet
  executed, so it is listed outside Core). Corpus findings enter as candidates (`registry/candidates.schema.json`,
  `tools/import_candidates.py`), hashes only. `rsoslang.state` still works (alias of `rsoslang.core.state`).
- **State Runtime fixes** (`rsoslang.state`). `SET k other.key` with a key that does not exist
  is now an error, not the literal text `other.key`; to set text that contains a dot, quote it (`SET k "a.b"`), and the
  planner grammar says so. `SCALE` to a fraction is now an error instead of storing a value later operations reject.
  The green dot is computed from sorted JSON, so a value with a line break can no longer produce another state's dot.
  **Breaking:** green dots from 0.3.x do not match 0.4.0. Published results are unaffected: the A7/A8 harness does not
  import this module, StateBench scores final states, the A5 equivalence still matches 32/32, all replay checks pass
  and the A8 results hash is unchanged (`8cb9a1fd…`). Fixes first proposed in RSOS-Language PR #1.
- **A8, OpenAI (19 Nov):** GPT-6.2 Sol through Codex: RSOS blind 32/32 exact; one-call JSON Patch 30/32. **G10, published before the run, hit:** GPT failed seed 712 at step 35, the same step that broke Gemini and Claude models; G8 now met. RSOS blind 256/256 across six models from four companies.
- **A8, other families (19 Nov):** RSOS blind exact on Mistral Large 4 and Gemini 3.8 Flash, 64/64 (S1 and L3); one-call JSON Patch 59/64, all failures state-dependent. **The named-step prediction published before the runs (G9) hit:** Gemini failed seed 712 at step 35, Mistral failed seed 702 at step 35, RSOS blind exact on both. G7 (invalid operations proposed ≥ 3× Claude) and G8 (same step on two new families) not met; published. Report: `experiments/A8_FAMILIES_REPORT.md`.
- **Predictions fixed before the next runs** (`experiments/PREREGISTRATION_A8.md`, amendments 2 and 3): G6 decoupling, G7 immunity, G8 same request across families, and **G9 named step**: on L3, one-call JSON Patch fails seed 712 or 702 at step 35 on Mistral or Gemini while RSOS blind stays exact. Basis: across Claude models, all 8 JSON Patch failures were one request type ("Everything owned by X is now owned by Y"; 8 of 553 vs 0 of 472 for RSOS blind). Amendment 2 also corrects amendment 1's header text against the code and keeps the first-run gpt-oss-120b failure (S1 X5b seed 302).
- **A7b long tasks** (56–224 steps, up to 300 keys): RSOS blind 48/48 exact, 0 wrong steps; one-call JSON Patch 46/48,
  all 7 failed steps state-dependent; cost per correct task 0.50–0.68×. P9 and P10 failed (published). StateBench v1
  now 80 tasks (L1–L3 added); the scorer scores every set present.

## 0.3.1 (18 Nov 2026)

- **A7a results:** against one-call JSON Patch with the same model, seeds, hash check and audit rule (M\*), RSOS blind
  (the planner shown no state value) was 32/32 exact vs 31/32, at 0.79× / 0.91× M\*'s cost per correct task.
  Pre-registration, code, results, transcripts and report in `experiments/` and `results/`.
- **RSOS-StateBench v1** (`bench/`): the 32 tasks as plain JSONL and a scorer, for any framework or model; leaderboard.
- `NEXT_TESTS.md`: the next tests with their predictions fixed in advance. `REPLICATE.md`: verify in one minute,
  score your own framework, or re-run. Replication issue template.
- Wording: B1 is RSOS's own per-step protocol, not the market's best (corrected on 18 Nov).

## 0.3.0 (18 Nov 2026)

- Package: `pip install rsoslang` (PyPI), `rsoslang mcp` runs the MCP server; `server.json` for the official MCP
  Registry; MCP SDK 1.x and 2.x supported.
- `experiments/a5_runtime_equivalence.py`: the shipped `rsoslang.state` runtime replays every recorded A5 plan, 32/32
  final states match the measured run (0 model calls).
- `examples/langgraph_state.py`: the State Runtime as LangGraph nodes (1 model call for a whole task).
- `tools/build_hf.sh`: the Hugging Face dataset (results, transcripts, pre-registrations, reports) and editor Space.
- **RSOS State Runtime** (`rsoslang.state`): the model writes operations for a whole task in one call; the runtime
  executes them, checks every copy against the green dot and heals drift with zero model calls. Python API and five
  MCP tools (`rsos_state_new`, `rsos_state_prompt`, `rsos_state_apply`, `rsos_state_sync`, `rsos_state_get`).
  Docs: `STATE.md`; replication guide: `REPLICATE.md`.
- **`REACH` operator (U108):** a stretch target used as an instrument, not a claim. `REACH name ON target TARGET n
  AGAINST baseline MEASURE m [RESULT r] [LIMIT l] [BLOCKERS …] [FROM earlier]`: each blocker opens a part (a planet)
  the White Dragon can land on; the verdict is the measured distance, the baseline and the named limit; `FROM` starts
  the next target from an earlier verdict. New codes `E022_REACH`, `W007_REACH_LIMIT`; tests `tests/test_reach.py`;
  example `examples/reach_a5.rsl` (A5's measured result).
- Painting editor: a live **REACH** panel turns the selected speed-test task into a REACH line with the measured
  distance after every gesture.
- Experiments **A3c** (prose floor), **A4** (latent drift) and **A5** (model bill against the market's best setup):
  pre-registrations, code, results with hashes, transcripts and reports.
- `spec/REFERENCE.md` regenerated from the code (it was missing 26 statements and several diagnostic codes).
- `CITATION.cff`: software DOI 0.2.1 and whitepaper DOIs.
- A3c's two H-pred transcript files stay private: H-pred sends coded bits as words from a 47,424-word alphabet, so
  coded messages can contain arbitrary words as code digits. Published in their place: text-free count files
  (`results/a3c_counts_Hp.jsonl`, `results/a3c_replay_a3P_Hp_counts.jsonl`), the SHA-256 of the withheld files
  (`results/a3c_withheld.json`) and `experiments/a3c_edges_check.py`, which reproduces A3c's per-edge channel numbers
  and the offline replay from the counts alone (all match). Full transcripts available on request for verification.
- Website (GitHub Pages, `docs/`): home, results with every failure, try it (editor, keyboard), paper and
  reproduction, research programme, family (cue framework). Built from `tools/site/` by `tools/build_site.py`.

## 0.2.1 (17 November 2026)

- Whitepaper v2: doi:10.5281/zenodo.24320392.
- A2 (knowing White Dragon, errors −63%), A3 (head to head vs compact protocols), A3b (hologram palace: 0.55× BPE
  of the anchor protocol, every copy true, 0-call heal), HT1 (failed), keyboard layer with functional check (12/12).
- Research programme (24 domains); seed purpose statement.

## 0.2.0 (17 November 2026)

First public release.

- Language: 108 statements, operator register U1–U107, governance checked by the compiler (E018–E021), runtime,
  two-way painting interface, palace communication layer (green dot, heal), White Dragon engine over spheres.
- Whitepaper v1: doi:10.5281/zenodo.24304404 (all versions: doi:10.5281/zenodo.24304403).
- First real-host test A1 (pre-registered): ~7× fewer channel tokens than JSON, 7/8 exact, 24/24 drift healed with
  0 model calls.
- Mission kit: responsible use, code of conduct, contributing (pre-registration, DCO), governance, security,
  name use.
