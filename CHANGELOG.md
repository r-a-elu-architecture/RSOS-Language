# Changelog

## Unreleased

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
- Held back pending review: `results/a3c_transcripts_Hp.jsonl` and `results/a3c_replay_a3P_Hp_transcripts.jsonl`
  (H-pred's coded messages; the word alphabet puts arbitrary words, including clinical terms, into coded text).
  `a3c_analyse.py` needs them to recount A3c's per-edge channel tokens; every other A3c number reproduces without them.
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
