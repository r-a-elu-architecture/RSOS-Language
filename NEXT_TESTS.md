# Next tests, with their predictions fixed in advance

Every test below is pre-registered in `experiments/PREREGISTRATION_A7.md` before any of its runs. Results, confirming
or not, are added here and to `experiments/FAILURES_MAP.md`. Come back and check whether we were right.

| Test | What changes | Prediction (fixed 18 Nov 2026) | Status |
|---|---|---|---|
| **A7a** | one-call JSON Patch (M\*) vs RSOS vs RSOS blind, A5 scale | P1 M\* ≤ 13/16 on a set · P2 blind loses ≤ 1 · P3 cost per correct ≤ 0.5× M\* | **Done, 18 Nov:** P1 fail (M\* 31/32), P2 pass (blind 32/32), P3 fail (0.79× / 0.91×). [Report](experiments/A7_REPORT.md) |
| **A7b, thinking off** | every arm with thinking off | P1b M\* drops ≥ 3 tasks on a set while RSOS blind drops ≤ 1 · P3b RSOS blind ≤ 0.3× M\* per correct task | **Blocked, 18 Nov:** the CLI ignores every thinking control for Haiku 5.5, so no verdict. The S1 run became a replicate: RSOS 16/16 again; M\*'s one failure reproduced exactly (seed 107, step 13) |
| **A7b, depth and horizon** | dependency depth 16, tasks of 224 steps | P9 M\* ≤ 50% exact while RSOS blind ≥ 90% · P10 RSOS blind input grows with requests only, not state size | **Done, 18 Nov:** P9 fail (M\* 15/16 on 224 steps; RSOS blind 16/16), P10 fail (blind input 1.53× at 10× the state; M\* 2.15×). Across A7: RSOS blind 80/80, M\* 77/80, all 8 M\* failures on state-dependent steps; cost per correct 0.50× at 300 keys. [Report](experiments/A7_REPORT.md) |
| **A7c, size floor** | a local open model (qwen2.5:1.5b) as planner and auditor | P11 RSOS blind ≥ 12/16 on S1 where M\* on the same model ≤ 4/16 | **running, 18 Nov:** qwen2.5:1.5b through Ollama on a 2014 laptop CPU (amendment logged before the run) |
| **External** | your framework, your model | — | [score it on StateBench](bench/) and open a replication issue |
