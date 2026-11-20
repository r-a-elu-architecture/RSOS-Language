"""Score PREREG_A9_PATTERNS.md from A9 result files. 0 model calls.

    python experiments/a9_patterns.py [results_dir]
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "results")
FAM = "codex_sol"
RELATIONAL = {"INHERIT", "FUSE", "REHOST", "ROUTE"}


def cell(c, arm):
    p = os.path.join(R, f"a9_results_{c}_{FAM}.jsonl")
    if not os.path.exists(p):
        return []
    seen, out = set(), []
    for line in open(p):
        r = json.loads(line)
        if r["arm"] == arm and r["seed"] not in seen:
            seen.add(r["seed"])
            out.append(r)
    return out


def bad_steps(rows):
    return [s for r in rows for s in r["steps"] if (not s["ok"]) or (not s["correct"])]


def main():
    x, cab, cav, b2 = cell("Z100", "X5b"), cell("Z100", "CAb"), cell("Z100", "CAv"), cell("Z100", "B2")
    tc = cell("Z30", "TC")
    full = lambda rows, n: len(rows) >= n
    v = {}
    v["PA1"] = sum(r["success"] for r in x) == 8 if full(x, 8) else None
    v["PA2"] = sum(r["success"] for r in cab) >= 7 if full(cab, 8) else None
    v["PA3"] = sum(r["success"] for r in tc) >= 3 if full(tc, 4) else None
    v["PA4"] = (sum(r["n_calls"] for r in tc) / len(tc) >= 20 * sum(r["n_calls"] for r in x) / len(x)
                if full(tc, 4) and full(x, 8) else None)
    bb = bad_steps(b2)
    v["PA5"] = (all(s["step"] + 1 >= 29 for s in bb) if bb else None) if full(b2, 8) else None
    cw = [s for s in bad_steps(cab) + bad_steps(cav) if s["ok"] and not s["correct"]]
    v["PA6"] = (all(s["kind"] in RELATIONAL for s in cw) if cw else None) if full(cab, 8) and full(cav, 8) else None
    v["PA7"] = sum(r["steps_wrong"] for r in x) == 0 if full(x, 8) else None
    detail = {"tasks": {"X5b_Z100": len(x), "CAb_Z100": len(cab), "CAv_Z100": len(cav), "B2_Z100": len(b2),
                        "TC_Z30": len(tc)},
              "B2_bad_steps": [(s["step"] + 1, s["kind"]) for s in bb],
              "code_wrong_steps": [(s["step"] + 1, s["kind"]) for s in cw]}
    for k, val in v.items():
        print(k, "pass" if val is True else "fail" if val is False else "not scorable")
    print(json.dumps(detail))
    json.dump({"verdicts": v, "detail": detail}, open(os.path.join(R, "a9_patterns.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
