"""Offline tests for A9 (0 model calls): scoring, sandbox gate, tool loop. python experiments/test_a9.py"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a9_tasks as Z           # noqa: E402

Z.register()
import a1_agents as A          # noqa: E402
import a7_tasks as T           # noqa: E402
import a9_arms as N            # noqa: E402

SEED = 4242


def oracle_program(task, wrong_step=None):
    lines = []
    for k in range(len(task["requests"])):
        a, b = task["truths"][k], task["truths"][k + 1]
        body = [f"    state.pop({x!r}, None)" for x in a if x not in b]
        body += [f"    state[{x!r}] = {b[x]!r}" for x in b if a.get(x) != b[x]]
        if k + 1 == wrong_step:
            body.append("    state['auth.retries'] = '99'")
        lines.append(f"def step_{k + 1}(state):\n" + ("\n".join(body) or "    pass"))
    return "```python\n" + "\n\n".join(lines) + "\n```"


def test_ca_exact_and_wrong():
    for cell in ("Z30", "Z300"):
        T.patch(cell)
        task = A.make_task(SEED)
        r = N.run_ca("CAb", cell, SEED, llm=lambda s, p: oracle_program(task))
        assert r["success"] and r["steps_wrong"] == 0 and r["steps_failed"] == 0, r
        r = N.run_ca("CAv", cell, SEED, llm=lambda s, p: oracle_program(task, wrong_step=50))
        assert r["steps_wrong"] == 1, r["steps_wrong"]   # final may still be exact: a later step overwrites it


def test_gate():
    for bad in ("import os\ndef step_1(s): pass", "def step_1(s): s.__class__", "def step_1(s): open('x')",
                "def step_1(s): getattr(s, 'x')", "def step_1(s): s['a']='__x'"):
        assert N.check_code(bad), bad
    assert N.check_code("def step_1(state):\n    for k in list(state):\n        state[k] = str(int(state[k]) + 1)") \
        is None


def test_ca_retry_on_bad_code():
    T.patch("Z30")
    task = A.make_task(SEED)
    answers = iter(["```python\nimport os\n```", oracle_program(task)])
    r = N.run_ca("CAb", "Z30", SEED, llm=lambda s, p: next(answers))
    assert r["success"] and r["invalid_ops"] == 1 and r["n_calls"] == 2, r


def test_tc_oracle_and_garbage():
    T.patch("Z30")
    task = A.make_task(SEED)

    def agent(system, prompt):
        k = int(re.search(r"Request #(\d+) of", prompt).group(1)) - 1
        a, b = task["truths"][k], task["truths"][k + 1]
        calls = [{"tool": "delete", "key": x} for x in a if x not in b]
        calls += [{"tool": "set", "key": x, "value": b[x]} for x in b if a.get(x) != b[x]]
        return json.dumps({"calls": calls, "done": True})
    r = N.run_tc("Z30", SEED, llm=agent)
    assert r["success"] and r["n_calls"] == len(task["requests"]), r
    r = N.run_tc("Z30", SEED, llm=lambda s, p: "I will think about it.")
    assert not r["success"] and r["steps_failed"] == len(task["requests"]), r
    assert r["n_calls"] == N.TC_TURNS * len(task["requests"])


def test_seeds_deterministic():
    s = Z.seeds_from("ab" * 32, "Z30")
    assert s == Z.seeds_from("ab" * 32, "Z30") and len(set(s)) == Z.N_SEEDS
    assert s != Z.seeds_from("ab" * 32, "Z300")


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f()
            print("ok", name)
    print("ALL OK")
