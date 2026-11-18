# Failures map: every pre-registered failure, its objects, and whether the White Dragon's logic applies (D84, D90)

17 Nov 2026. "Objects" names each side of the failure in one word, as the owner asked (17:11–17:16).
"Dragon logic" = the White Dragon (who knows) chooses where to land, at what depth and order, and predicts the
gain; the hologram = the whole held in every part, so a reference replaces resending.

| # | Test | Failure | Objects | Dragon logic applies? | Next landing |
|---|---|---|---|---|---|
| 1 | A3 R1 | Palace 1.84× the tent's size | Palace / Tent | **Yes** | **Tested in A3b: H-dragon 0.64× the tent (BPE 0.55×) with 16/16 replica-consistent → passed B1. 5× (B2) failed: 87% of what remains is lossless planner prose.** Next: A3c |
| 2 | A3 R4 | Repair 38 vs 96 tokens (0.39×) | Palace / Workshop / Tent | **Yes** | **Fixed in A3b (B7): heal 0 tokens per drift (H-dragon), 2.0 (H-copy); 18.5 if both copies are corrupted (offline)** |
| 3 | A1 P2 | JSON checker with memory also caught all drift | Palace / Archive | Partly | Advantage is healing without the model; test where the archive must pay to repair |
| 4 | HT1 K1 | Typed symbols not faster, elements dropped | Hand / Keyboard | **Yes** | Keyboard layer after a learning phase (HT2) |
| 5 | T7 | Meaning not robust to 10% relation noise (47.5%) | Map / Fog | **Yes** | Green dot per relation + heal from the book |
| 6 | T5 | Predicted sign change across hosts absent | Seed / Soil | Partly | Dragon chooses the host binding per host, predicts the sign |
| 7 | R-003 | Move + pierce negative in 40/40 worlds | Arrow / Wall | Yes | Dragon sets the order (pierce before move, or the reverse) and predicts |
| 8 | R-004 | Four placement rules did not hold | Room / Furniture | Yes | Dragon derives placement from depth and order (A2 map) |
| 9 | U1 P3, U1b P2–P3 | Node-universe predictions; 6 nodes without trigger | Star / Orbit | Partly | Dragon assigns missing triggers; retest |
| 10 | S1 P1–P2 | Colour-map predictions | Prism / Light | Partly | Lenses chosen by the dragon instead of fixed regexes |
| 11 | S2 P1 | VAKOG lens rose 1.8×, not 2× | Body / Lens | No (threshold miss) | Keep as measured |
| 12 | E1 P2, P5, P6 | Growth predictions | Tree / Branch | Yes | Knowing landings instead of blind growth (A2 showed blind harms) |
| 13 | V1 P1–P3, P5 | Four thresholds (main effect held) | Key / Lock | Partly | Retest on people (neuroscience row) |
| 14 | H1 all three | Predictive heal missed thresholds, cost bytes | Guard / Gate | Yes | Hologram heal by reference (cheaper) |
| 15 | H2 P1, P3 | Herding in host-reported lack | Flock / Shepherd | Fixed | H2b passed (net of help in flight) |
| 16 | F1 P1–P2 | Feedback halved useful share | River / Dam | Fixed | F1b: scored fairly, roots improved |
| 17 | F1b P1–P3 | Entry reinforcement +0.02, less steady | Seed / Storm | **Yes** | Replace blind reinforcement with knowing landings (A2) |
| 18 | H3c P2 | 50.3% of oracle gain (just passed) | Mirror / Oracle | Yes | Every book carries its test (more measurable versions) |
| 19 | I1 | IMIP does not track its claim (ρ 0.09) | Compass / North | Yes | Dragon redefines the instrument from what it must measure |
| 20 | I2 | CRI and ARC do not track their claims | Scale / Weight | Yes | Same as 19 |

**Pattern:** 14 of 20 are failures of blind choice (fixed rules, random growth, resending, typing); the dragon's
knowing landing and the hologram address them directly. 2 are already fixed (H2b, F1b scoring); 4 are threshold
misses or need people. Each "Yes" is a hypothesis to pre-register, not a result.

## New from A3b (17 Nov 2026)

| # | Test | Failure | Objects | Dragon logic applies? | Next landing |
|---|---|---|---|---|---|
| 21 | A3b B2 | Hologram 1.57× smaller than the tent, not 5× | Hologram / Prose | **Yes** | A3c: shared predictor as reference beam for prose (owner decision on local model) |
| 22 | A3b B6 | Dragon predicted 321 tok/task, measured 932 (−66%) | Dragon / Template | Partly | Dragon saw 2 example steps; give it coverage statistics, it flagged the risk itself |
| 23 | A3b H-copy B3/B4 | 12/16 exact (LLM edit errors, approved by checker) | Copy / Error | No (LLM variance) | Keep as measured; codec cannot make an approved edit right |

### Answered since A3b

- **21 (A3b B2, 5× not reached): answered by A3c.** H-pred 0.141× D in BPE with 0 model calls; H-local 0.106× D in
  BPE with full integrity (C3 pass). The prose floor fell to 0.60 / 0.41 bits per character.
- **22 (dragon size prediction −66%): answered by A3c.** With coverage statistics, the dragon predicted H-pred within
  +5.4% (C4 pass) and H-local within −3.7%.

## New from A3c and A4 (17 Nov 2026)

| # | Test | Failure | Objects | Dragon logic applies? | Next landing |
|---|---|---|---|---|---|
| 24 | A3c C1 | H-pred size and integrity pass (0.141× BPE, 48/48, 0/1,160), but 15/16 replica-consistent: checker rejected a correct `DEL` 3× (seed 300) | Checker / Error | No (LLM variance; codec byte-exact) | Error-source split: rerun H-pred on the same steps to measure the checker's model-error rate |
| 25 | A3c C2 | H-pred 15/16 exact vs D 16/16 (same seed 300 step) | Checker / Error | No | Same as 24 |
| 26 | A4 L2 | H-dragon 15/16 exact and replica-consistent: worker wrote a wrong value from a true, healed copy (seed 407, step 6); 0 drift-traced errors | Worker / Error | No (LLM variance) | A4 next action 2: 3× reruns of the 128 compute steps to separate protocol from model noise |

**Pattern across 23–26:** every remaining failure of the integrity protocols is a single model error on a true copy,
approved or rejected wrongly by an LLM, never a codec or integrity failure. The registered rule counts them, as it
should. The open question they share is the base rate of model error per step, which none of the tests has
measured yet; one error-source experiment answers 23–26 together.

## New from A5 (18 Nov 2026)

| # | Test | Failure | Objects | Dragon logic applies? | Next landing |
|---|---|---|---|---|---|
| 27 | A5 K1 | X3 0.581× / 0.828× of the honest market best (target ≤ 0.1); X5 (secondary) 0.268× / 0.354× | Cost / Thinking | **Yes** | A5b: thinking control applied equally to B1 and X5 (counterfactual ≈ 0.12, unmeasured) |
| 28 | A5 K2 | X1s calls 0.51× / 0.63× (target ≤ 0.4): the audit rule selects 10–12 of 14 steps | Audit / Calls | Yes | Audit by equality (second planner translation, model audit only on disagreement) |
| 29 | A5 K3 | X2 output 0.36× / 0.54× (target ≤ 0.25): X planners think more than B1's | Planner / Thinking | Yes | Worked examples and templates; thinking control |
| 30 | A5 K4 (X3) | X3 replica 15/16 on both sets: auditor false rejects (palace notation read wrongly) | Palace notation / Auditor | Partly | Drop palace notation in prompts at this scale; audit by equality |
| 31 | A5 X1s S2 seed 403 | The only audit miss in 192 tasks: a compute written as a literal `SET`, unsampled | Risk class | Yes | Risk class from the request's verbs as well as the operations |

**Pattern:** the integrity layer held everywhere (48/48 heals, 0 drift-traced values, 0 wrong steps approved by the
audit). The cost gap is now thinking tokens and audit calls, not calls per step; the assembly line removed the
per-step dependency.
