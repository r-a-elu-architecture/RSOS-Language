"""A9 analysis (PREREGISTRATION_A9.md section 5). 0 model calls. Written and sealed before any A9 result exists.

    python experiments/a9_analyse.py          -> results/a9.json and a printed verdict table
"""

import glob
import json
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a1_agents as A          # noqa: E402

R = os.path.join(A.ROOT, "results")
N_SEEDS, N_TC = 8, 4
PLAN = {"Z300": ["TC", "CAv", "CAb", "B2", "X5b"], "Z30": ["TC", "CAv", "CAb", "B2", "X5b"],
        "Z100": ["B2", "X5b", "CAv", "CAb"]}
FLAT = 0.005                    # 0.5 percentage points


def load():
    rows = []
    for p in sorted(glob.glob(os.path.join(R, "a9_results_*.jsonl"))):
        for line in open(p):
            rows.append(json.loads(line))
    seen, out = set(), []
    for r in rows:                                   # first record per (label, cell, arm, seed) counts
        key = (r["label"], r["set"], r["arm"], r["seed"])
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def quarter(step, n=56):
    return min(3, step * 4 // n)


def mh_or(strata):
    """Mantel-Haenszel odds ratio, Q4 vs Q1; strata: list of (a, b, c, d) = (Q4 wrong, Q4 right, Q1 wrong, Q1 right).
    95% CI by Robins-Breslow-Greenland."""
    num = den = 0.0
    P = Q = PQ = 0.0
    sr = ss = 0.0
    for a, b, c, d in strata:
        n = a + b + c + d
        if n == 0:
            continue
        R_, S_ = a * d / n, b * c / n
        num += R_
        den += S_
        Pi, Qi = (a + d) / n, (b + c) / n
        P += Pi * R_
        PQ += Pi * S_ + Qi * R_
        Q += Qi * S_
        sr += R_
        ss += S_
    if num > 0 and den == 0:                     # no Q1 error at all: the odds ratio is unbounded above
        return {"or": math.inf, "lo": None, "hi": None}
    if num == 0 or den == 0:
        return {"or": None, "lo": None, "hi": None}
    orr = num / den
    var = P / (2 * sr ** 2) + PQ / (2 * sr * ss) + Q / (2 * ss ** 2)
    se = math.sqrt(var)
    return {"or": orr, "lo": math.exp(math.log(orr) - 1.96 * se), "hi": math.exp(math.log(orr) + 1.96 * se)}


def main():
    rows = load()
    cells = defaultdict(list)
    for r in rows:
        cells[(r["label"], r["set"], r["arm"])].append(r)
    complete = {k for k, v in cells.items() if len(v) >= (N_TC if k[2] == "TC" else N_SEEDS)}
    comp_rows = [r for r in rows if (r["label"], r["set"], r["arm"]) in complete]

    table = {}
    for k, v in sorted(cells.items()):
        table["|".join(k)] = {"tasks": len(v), "complete": k in complete,
                              "exact": sum(r["success"] for r in v),
                              "steps_wrong": sum(r["steps_wrong"] for r in v),
                              "steps_failed": sum(r["steps_failed"] for r in v),
                              "calls_per_task": sum(r["n_calls"] for r in v) / len(v),
                              "in_tok_per_task": sum(r["in_tok"] for r in v) / len(v),
                              "out_tok_per_task": sum(r["out_tok"] + r.get("think_tok", 0) for r in v) / len(v)}

    def by(arm, cell=None):
        return [r for r in comp_rows if r["arm"] == arm and (cell is None or r["set"] == cell)]

    def exact_rate(rs):
        return sum(r["success"] for r in rs) / len(rs) if rs else None

    def q_rates(rs):
        w, n = [0] * 4, [0] * 4
        for r in rs:
            for s in r["steps"]:
                q = quarter(s["step"])
                n[q] += 1
                w[q] += (not s["ok"]) or (not s["correct"])
        return [w[i] / n[i] if n[i] else None for i in range(4)], w, n

    def q_or(rs):
        st = defaultdict(lambda: [0, 0, 0, 0])
        for r in rs:
            for s in r["steps"]:
                q = quarter(s["step"])
                bad = (not s["ok"]) or (not s["correct"])
                if q == 3:
                    st[s["kind"]][0 if bad else 1] += 1
                elif q == 0:
                    st[s["kind"]][2 if bad else 3] += 1
        return mh_or([tuple(v) for v in st.values()])

    quarters = {arm: dict(zip(("rates", "wrong", "steps"), q_rates(by(arm)))) for arm in ("B2", "X5b", "CAv", "CAb",
                                                                                        "TC")}
    for arm in quarters:
        quarters[arm]["mh_q4_vs_q1"] = q_or(by(arm))

    def flat(arm):
        q = quarters[arm]["rates"]
        return None if q[0] is None or q[3] is None else (q[3] - q[0]) <= FLAT

    def per_task(arm, cell, f):
        rs = by(arm, cell)
        return sum(f(r) for r in rs) / len(rs) if rs else None

    def tok(r):
        return r["in_tok"] + r["out_tok"] + r.get("think_tok", 0)

    def tok_per_correct(arm, cell):
        rs = by(arm, cell)
        c = sum(r["success"] for r in rs)
        return sum(tok(r) for r in rs) / c if c else math.inf

    labels = sorted({r["label"] for r in comp_rows})
    x5b_cells = [v for k, v in table.items() if k.endswith("|X5b") and v["complete"]]
    B2q = quarters["B2"]
    v = {}
    v["Q1_blind_exact"] = (bool(x5b_cells) and all(c["exact"] / c["tasks"] >= 0.90 for c in x5b_cells)
                           and exact_rate(by("X5b")) >= 0.95)
    v["Q2a_B2_rises"] = (B2q["rates"][0] is not None and B2q["rates"][3] > B2q["rates"][0]
                         and (B2q["mh_q4_vs_q1"]["or"] or 0) > 1)
    v["Q2b_readers_flat"] = all(flat(a) for a in ("X5b", "CAb", "TC", "CAv") if quarters[a]["rates"][0] is not None)
    e30, e300 = exact_rate(by("B2", "Z30")), exact_rate(by("B2", "Z300"))
    v["Q3a_B2_worse_with_size"] = None if e30 is None or e300 is None else (1 - e300) > (1 - e30)
    v["Q3b_blind_flat_with_size"] = all(
        None not in (exact_rate(by(a, "Z30")), exact_rate(by(a, "Z300"))) and
        abs(exact_rate(by(a, "Z30")) - exact_rate(by(a, "Z300"))) <= 0.10 for a in ("X5b", "CAb"))
    v["Q4_blind_code_as_exact"] = (exact_rate(by("CAb")) is not None and exact_rate(by("CAb")) >= 0.90 and
                                   abs(exact_rate(by("CAb")) - exact_rate(by("X5b"))) <= 0.10)
    v["Q5a_rsos_shorter_than_python"] = all(
        per_task("X5b", "Z300", lambda r: r["out_tok"] + r.get("think_tok", 0)) <
        per_task("CAb", "Z300", lambda r: r["out_tok"] + r.get("think_tok", 0))
        for _ in [0] if by("X5b", "Z300") and by("CAb", "Z300"))
    v["Q5b_cheapest_per_correct_Z300"] = (bool(by("X5b", "Z300")) and
                                          tok_per_correct("X5b", "Z300") < tok_per_correct("B2", "Z300") and
                                          tok_per_correct("X5b", "Z300") < tok_per_correct("TC", "Z300"))
    tc_calls, x_calls = per_task("TC", None, lambda r: r["n_calls"]), per_task("X5b", None, lambda r: r["n_calls"])
    v["Q6a_TC_calls_20x"] = None if tc_calls is None or x_calls is None else tc_calls >= 20 * x_calls

    def step_rate(rs):
        n = sum(len(r["steps"]) for r in rs)
        w = sum(r["steps_wrong"] + r["steps_failed"] for r in rs)
        return w / n if n else None
    t3, b3 = step_rate(by("TC", "Z300")), step_rate(by("B2", "Z300"))
    v["Q6b_TC_steps_beat_B2_Z300"] = None if t3 is None or b3 is None else t3 <= b3
    i30, i300 = per_task("TC", "Z30", lambda r: r["in_tok"]), per_task("TC", "Z300", lambda r: r["in_tok"])
    v["Q6c_TC_input_grows_with_size"] = None if not i30 or i300 is None else i300 / i30 >= 1.2
    e_tc, e_x = exact_rate(by("TC", "Z300")), exact_rate(by("X5b", "Z300"))
    v["Q7_blind_at_least_TC_Z300"] = None if e_tc is None or e_x is None else e_x >= e_tc

    out = {"labels": labels, "cells": table, "quarters": quarters, "verdicts": v,
           "incomplete": sorted("|".join(k) for k in cells if k not in complete)}
    json.dump(out, open(os.path.join(R, "a9.json"), "w"), indent=1, default=str)
    for k, val in v.items():
        print(f"{k:34s} {val}")
    print("incomplete cells:", out["incomplete"] or "none")
    return out


if __name__ == "__main__":
    main()
