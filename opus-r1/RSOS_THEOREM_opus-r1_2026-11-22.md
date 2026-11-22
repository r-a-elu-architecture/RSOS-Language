# The RSOS theorem: draft for sealing

**Account:** opus-r1 (Claude session 01HudWCo…). Written 22 Nov 2026.
**Status:** a new file. No existing file was edited. It is not committed to any branch and has not been published.
**Builds on:** `research/sealed/seed/math/MATH_V1.md` (Laws 0–5, Theorem 1) and `MATH_V2_ADDENDUM.md` (A1, A3), in the owner's notation (LAYER_RULE rule 3.4).
**New here:** the named-step corollary (c), the recursion statement (e) and the colour rule for a law (f). Parts (a), (b) and (d) restate or combine laws the repo has already proven.

---

## 1. Objects (from MATH_V1)

- **World:** W, a finite map from components to states.
- **Operator:** o = (R_o, W_o, f_o), with read set R_o, write set W_o and function f_o.
- **Effective extent:** n_eff(o, H), the number of independent error units an operation meets on host H. On an element-class host, this is the elements read. On a time-class host, it is about the duration divided by the correlation time.
- **Plan:** π = (o₁, …, o_T).
- **Planner model m:**
  - ε_m is the per-unit read error, between 0 and 1;
  - μ_m is the per-message error, between 0 and 1.
- **Modes:**
  - *pull:* the model reads values and computes f_o;
  - *blind:* the model only names keys and operators, and the runtime computes f_o.

## 2. The theorem

**(a) Pull failure law.** This is Law 1′ / Theorem 1, already proven.
If the read events of o_t are positively associated:

  P_m(o_t fails | pull) ≤ 1 − (1 − ε_m)^{n_eff(o_t)}

- Equality holds for independent reads.
- The bound can be exceeded when successes compete, under negative association (A3: P = 1 − C(N−k, n) / C(N, n)).

**(b) Blind law.** This is Law 2, already proven.

  P_m(o_t fails | blind) = 1 − (1 − μ_m)²

This is independent of n_eff, of the values in W and of T.

**(c) Named-step corollary.** This part is new.

*Assumption:* model m's per-unit error ε_m is constant across the steps of π, and the reads are independent.

*Then:* P_m(fail at t) = 1 − (1 − ε_m)^{n_eff(o_t)} is strictly increasing in n_eff(o_t). So for any two models m and m′ that meet the assumption:

  argmax_t P_m(fail at t) = argmax_t P_{m′}(fail at t) = argmax_t n_eff(o_t)

The whole ranking of steps by risk is the same for both models.

*Proof:* x ↦ 1 − (1 − ε)^x is strictly increasing for every ε in (0, 1). A strictly increasing map keeps order, so the ranking depends on the n_eff(o_t) alone. ∎

*Meaning:* the step that fails is fixed by the request and the state before any model is chosen. This is the Koch reading (the same cause gives the same failure in every host) and the Mendeleev reading (the step can be named in advance).

*Typed form, the next prediction to seal:* if the error depends on the operator's type, rank by

  r_m(t) = ε_m(type(o_t)) · n_eff(o_t)

This is a first-order approximation for small ε. The ranking then agrees across models only where the type profiles ε_m(·) are proportional.

**(d) Whole-plan decoupling.** This follows from (a) and (b).

  P_m(π exact | pull) ≥ ∏_{t=1..T} (1 − ε_m)^{n_eff(o_t)}

This holds under positive association, with equality for independent reads. It decays with the total state read, Σ_t n_eff(o_t).

  P_m(π exact | blind) = (1 − μ_m)^{2k}

Here k is the number of model calls (about 1–2 per task). It is flat in T, in dependency depth and in n_eff. It varies across models only through μ_m.

**(e) Recursion (the Mendeleev engine).** Let T_k be the table of operations and laws after round k, ordered by read scope. In each round:

1. Gap(T_k) gives the predicted operator o*.
2. Its predicted failure is p* = 1 − (1 − ε)^{n_eff(o*)}, or the named step argmax_t n_eff.
3. Seal the prediction (timestamp before any run).
4. Measure it on the hosts.
5. If confirmed, T_{k+1} = T_k ∪ {o*, the law confirmed}.

If it is not confirmed, the build is wrong, not the law (LAYER_RULE 3.3). The build is revised and the gap stays open.

**(f) Colour of a law ℒ** (LAYER_RULE 3.5):

- **Turquoise:** ℒ holds on every layer-2 host tested.
- **Blue:** ℒ holds on a layer-1 host.
- **Cyan:** both hold, and the layer-2 prediction was sealed before the layer-1 measurement.

## 3. Status of each part

| Part | Status | Evidence in the repos |
|---|---|---|
| (a) | proven (Harris–FKG) and measured | OPS1, OPS2 (ordering 0 → 0.14% → 0.17% → 2.31%); SPHERE3 (+2.82 pp above the bound, as negative association predicts); SQLITE2 |
| (b) | proven and measured | A7–A9: 0 wrong blind steps; 256/256 across 6 models from 4 companies |
| (c) | proof written here; not yet in the repo | G9 (00e5121, 18 Nov 22:26 UTC): Gemini failed seed 712 step 35, Mistral failed seed 702 step 35. G10 (edcd42e, 19 Nov 02:50 UTC; results e876f65): GPT failed seed 712 step 35. SC1 named hand-overs. |
| (c) typed form | conjecture | not yet sealed |
| (d) | follows from (a) and (b) | A8 G6: blind range 0 across families against JSON Patch range 3 |
| (e) | run by hand twice | FLOW: predicted ≥ 5%, measured 14.8%. Gaps A–D of the operation table. |
| (f) | (a)–(e) turquoise; **cyan: none yet** | no layer-1 host tested |

## 4. Where (c) can break, as measured

- **Opus passed both named steps.** Under (c) it is still ranked the same way. Its ε at step 35 was simply low enough to pass. The corollary names *where* failure is most likely, not *whether* it happens.
- **Mistral also failed seed 712 at other steps (INHERIT, REHOST).** There its error depended on the operator type, which breaks the constant-ε assumption. This is the case the typed form r_m(t) is meant to cover.
- **Ties in n_eff** make argmax a set rather than a single step. A prediction must then name the set.

## 5. Test that turns (c) cyan (proposal, not run)

1. **Choose a layer-1 host** where n_eff can be counted before the test. Examples: a real production database migration, or human operators applying "move everything owned by X to Y" by hand across a list.
2. **Name the step that will fail first**, from n_eff alone, and seal it before anyone starts. A seal here means a commit plus an external timestamp, as cue-security does with OpenTimestamps.
3. **Measure**, and report hit or miss with the raw logs.
4. **Decide:**
   - A hit on a host never used to fit the rule makes (c) cyan.
   - A miss means the build is revised (rule 3.3), and the typed form is tested next.

---

*Integrity:* the sha256 of this file is printed in the opus-r1 session where it was made. Seal it by committing this file unchanged to `acct/opus-r1` on the owner's instruction.
