"""A9 arms: the two strongest rival patterns we know, run on the same tasks, models and backends as B2 and X5b.

CAv  code-as-action, seeing the state: one planner call writes a Python program with one function per request
     (step_k(state) edits the dict in place); the model is shown the full state, as B2 is.
CAb  code-as-action, blind: the same, but the model sees no values, only the requests (as X5b).
TC   tool-calling agent: one request at a time, tools get / find / services / set / delete, up to 4 turns per
     request; the agent reads what it needs, computes every value itself and writes it (the standard agent loop).

Every arm is scored exactly as B2/X5b (a7_arms.run_plan): a step is correct if its change, applied to the arm's own
state before the step, equals the true change; a task is exact if the final state equals the truth. Code runs in a
separate Python process (isolated mode, no imports, no dunder names, no I/O builtins, 20 s timeout).
No auditor and no replicas in these arms (B2/X5b keep theirs); this is recorded in the pre-registration.
"""

import ast
import json
import os
import re
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a1_agents as A          # noqa: E402
import a5_llm as L             # noqa: E402

ARMS = ("CAv", "CAb", "TC")
MAX_RETRY = 2
TC_TURNS = 4
_wlock = threading.Lock()

CA_SYS = ("You are the PLANNER in a pipeline that edits a configuration state: a Python dict whose keys are "
          "'service.field' and whose values are strings (numbers as decimal strings, e.g. '300'). You receive all "
          "change requests of one task, numbered; they are applied in order, each on the result of the previous one. "
          "Write one Python program that defines, for every request #k, a function step_k(state) that changes "
          "`state` in place (assign, delete, or add keys). Plain Python only: no import, no files, no input or "
          "output, no names starting with an underscore. Output only the program, in one ```python block.")
CAV_NOTE = " You also receive the current state."
CAB_NOTE = (" You see no state values, only the requests: your code must read every value it needs from `state` "
            "when it runs. Fields include replicas, timeout_ms, retries, owner, region, log_level; requests may add "
            "others.")

TC_SYS = ("You are an AGENT that edits a configuration state through tools. Keys are 'service.field'; values are "
          "strings (numbers as decimal strings). You handle ONE change request at a time; requests are applied in "
          "order, each on the result of the previous one. Reply with one JSON object only: "
          "{\"calls\": [...], \"done\": true|false}. Tools: {\"tool\": \"services\"} lists the services; "
          "{\"tool\": \"get\", \"keys\": [\"auth.retries\"]} returns values; {\"tool\": \"find\", \"field\": "
          "\"owner\", \"value\": \"bruno\"} returns every key of that field with that value (omit \"value\" to get "
          "every key of the field with its value); {\"tool\": \"set\", \"key\": \"auth.retries\", \"value\": \"5\"} "
          "writes (adds the key if new); {\"tool\": \"delete\", \"key\": \"auth.retries\"}. Calls run in order. "
          "With \"done\": false you receive the results and continue; with \"done\": true the request ends after "
          "the calls run. At most 4 turns per request. Read what you need, compute every value yourself, then write.")

BANNED = {"open", "exec", "eval", "compile", "input", "globals", "locals", "vars", "getattr", "setattr", "delattr",
          "breakpoint", "help", "memoryview", "__import__", "print"}

CHILD = r"""
import json, sys
SAFE = ("abs all any bool dict enumerate filter float int isinstance len list map max min range reversed round "
        "set sorted str sum tuple zip KeyError ValueError Exception").split()
import builtins
B = {k: getattr(builtins, k) for k in SAFE}
d = json.loads(sys.stdin.read())
g = {"__builtins__": B}
out = {"load_error": None, "steps": []}
try:
    exec(d["code"], g)
except Exception as e:
    out["load_error"] = type(e).__name__ + ": " + str(e)[:200]
state = dict(d["state"])
for k in range(1, d["n"] + 1):
    f = g.get("step_%d" % k)
    if out["load_error"] or not callable(f):
        out["steps"].append({"error": "no function step_%d" % k, "state": dict(state)})
        continue
    trial = dict(state)
    try:
        f(trial)
        norm = {}
        for kk, v in trial.items():
            if isinstance(v, bool) or not isinstance(kk, str):
                raise ValueError("bad key or value type")
            if isinstance(v, float) and v.is_integer():
                v = int(v)
            norm[kk] = str(v)
        state = norm
        out["steps"].append({"error": None, "state": dict(state)})
    except Exception as e:
        out["steps"].append({"error": type(e).__name__ + ": " + str(e)[:200], "state": dict(state)})
print(json.dumps(out))
"""


def check_code(code):
    """Static gate before any execution. Returns an error string or None."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"syntax error line {e.lineno}: {e.msg}"
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal, ast.AsyncFunctionDef, ast.Await)):
            return f"not allowed: {type(node).__name__}"
        if isinstance(node, ast.Name) and (node.id in BANNED or node.id.startswith("_")):
            return f"not allowed name: {node.id}"
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            return f"not allowed attribute: {node.attr}"
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and "__" in node.value:
            return "not allowed: dunder text"
    return None


def run_code(code, state, n, timeout=20):
    p = subprocess.run([sys.executable, "-I", "-c", CHILD], input=json.dumps({"code": code, "state": state, "n": n}),
                       capture_output=True, text=True, timeout=timeout, cwd=_tmpdir(), env=_env())
    if p.returncode != 0 or not p.stdout.strip():
        raise RuntimeError("code process failed: " + p.stderr[-300:])
    return json.loads(p.stdout)


def _env():
    keep = {k: os.environ[k] for k in ("SYSTEMROOT", "SystemRoot") if k in os.environ}   # Windows needs SYSTEMROOT
    return {"PATH": "", **keep}


def _tmpdir():
    import tempfile
    d = os.path.join(tempfile.gettempdir(), "rsos_a9_sandbox")
    os.makedirs(d, exist_ok=True)
    return d


def extract_code(text):
    m = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, flags=re.S)
    return (m.group(1) if m else text).strip()


def expect_after(truths, k, pre):
    exp = dict(pre)
    for key in set(truths[k]) | set(truths[k + 1]):
        if key not in truths[k + 1]:
            exp.pop(key, None)
        elif truths[k].get(key) != truths[k + 1][key]:
            exp[key] = truths[k + 1][key]
    return exp


def _kind(req):
    import a7_arms as S
    return S.request_kind(req)


def _result(arm, set_name, seed, task, step_states, step_ok, calls, invalid, attempts, t0, log, extra=None):
    truths, n = task["truths"], len(task["requests"])
    step_log, pre = [], dict(task["init"])
    for k in range(n):
        post = step_states[k]
        rec = {"step": k, "ok": step_ok[k], "correct": post == expect_after(truths, k, pre),
               "attempts_n": attempts[k], "kind": _kind(task["requests"][k])}
        step_log.append(rec)
        pre = post
    final, truth = pre, task["final"]
    keys = set(truth) | set(final)
    res = {"arm": arm, "cond": arm, "seed": seed, "set": set_name, "success": final == truth,
           "line_acc": sum(final.get(k) == truth.get(k) for k in keys) / len(keys),
           "final_errors": sorted(k for k in keys if final.get(k) != truth.get(k)),
           "steps_failed": sum(1 for s in step_log if not s["ok"]),
           "steps_wrong": sum(1 for s in step_log if s["ok"] and not s["correct"]), "invalid_ops": invalid,
           "n_calls": len(calls), "out_tok": sum(c["out"] for c in calls),
           "think_tok": sum(c.get("think", 0) for c in calls),
           "in_tok": sum(c["in"] + c["cache_w"] + c["cache_r"] for c in calls),
           "cost_usd": sum(c.get("cost") or 0 for c in calls), "wall_sec": time.time() - t0,
           "steps": step_log, "calls_full": calls, **(extra or {})}
    tr = os.environ.get("A7_TRANSCRIPTS")
    if tr:
        with _wlock:
            with open(tr, "a") as f:
                f.write(json.dumps({"arm": arm, "set": set_name, "seed": seed, "calls": log, "steps": step_log}) + "\n")
    print(f"{set_name} {arm} {seed} success={res['success']} calls={len(calls)} wrong={res['steps_wrong']} "
          f"fail={res['steps_failed']} inv={invalid} wall={res['wall_sec']:.0f}s", flush=True)
    return res


def _call(system, prompt, calls, log, llm=None):
    if llm is not None:
        text = llm(system, prompt)
        rec = {"in": 0, "cache_w": 0, "cache_r": 0, "out": 0, "think": 0, "cost": 0.0, "sec": 0.0}
    else:
        text, _, rec = L.llm(system, prompt, None, log)
    calls.append(rec)
    return text


def run_ca(arm, set_name, seed, llm=None):
    assert arm in ("CAv", "CAb")
    task = A.make_task(seed)
    n, t0 = len(task["requests"]), time.time()
    system = CA_SYS + (CAV_NOTE if arm == "CAv" else CAB_NOTE)
    reqs = "Change requests:\n" + "\n".join(f"#{k + 1} {r}" for k, r in enumerate(task["requests"]))
    head = ("State:\n" + A.text_of(task["init"]) + "\n\n") if arm == "CAv" else ""
    calls, log, invalid, feedback, out = [], [], 0, "", None
    for rnd in range(MAX_RETRY + 1):
        code = extract_code(_call(system, head + reqs + feedback, calls, log, llm))
        err = check_code(code)
        if err is None:
            out = run_code(code, task["init"], n)
            errs = [f"step_{k + 1}: {s['error']}" for k, s in enumerate(out["steps"]) if s["error"]]
            if out["load_error"]:
                err = "the program did not load: " + out["load_error"]
            elif errs:
                err = "runtime errors: " + "; ".join(errs[:10])
            else:
                break
        invalid += 1
        feedback = f"\n\nYour previous program was rejected ({err}). Write the whole program again."
    attempts = [len(calls)] * n
    if out is None:                                    # never passed the static gate: nothing executed
        states, ok = [dict(task["init"])] * n, [False] * n
    else:
        states = [s["state"] for s in out["steps"]]
        ok = [s["error"] is None for s in out["steps"]]
    return _result(arm, set_name, seed, task, states, ok, calls, invalid, attempts, t0, log,
                   {"code": code if out is not None else None})


def _parse_json(text):
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.M).strip()
    i, j = t.find("{"), t.rfind("}")
    d = json.loads(t[i:j + 1])
    if not isinstance(d, dict) or not isinstance(d.get("calls", []), list):
        raise ValueError("expected {\"calls\": [...], \"done\": ...}")
    return d


def _services(state):
    return sorted({k.split(".")[0] for k in state})


def apply_tool(state, c):
    t = c.get("tool")
    if t == "services":
        return _services(state)
    if t == "get":
        return {k: state.get(k) for k in c.get("keys", [])}
    if t == "find":
        f, v = c.get("field"), c.get("value")
        return {k: x for k, x in state.items() if k.split(".", 1)[1] == f and (v is None or x == str(v))}
    if t == "set":
        k, v = c.get("key"), c.get("value")
        if not isinstance(k, str) or "." not in k or v is None or isinstance(v, (dict, list, bool)):
            raise ValueError("set needs a key 'service.field' and a value")
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        state[k] = str(v)
        return "ok"
    if t == "delete":
        state.pop(c.get("key"), None)
        return "ok"
    raise ValueError(f"unknown tool {t!r}")


def run_tc(set_name, seed, llm=None):
    task = A.make_task(seed)
    n, t0 = len(task["requests"]), time.time()
    state = dict(task["init"])
    calls, log, invalid = [], [], 0
    states, ok, attempts, turns_used = [], [], [], []
    for k, req in enumerate(task["requests"]):
        convo = f"Request #{k + 1} of {n}: {req}"
        done, t = False, 0
        while not done and t < TC_TURNS:
            t += 1
            text = _call(TC_SYS, convo, calls, log, llm)
            try:
                d = _parse_json(text)
                results = []
                for c in d.get("calls", []):
                    try:
                        results.append(apply_tool(state, c))
                    except Exception as e:  # noqa: BLE001
                        invalid += 1
                        results.append(f"error: {e}")
                done = bool(d.get("done"))
                convo += f"\n\nYou: {json.dumps(d)}\nResults: {json.dumps(results)}"
            except Exception as e:  # noqa: BLE001
                invalid += 1
                convo += f"\n\nYou: {text.strip()[:500]}\nResults: error: {e}. Reply with one JSON object only."
        states.append(dict(state))
        ok.append(done)
        attempts.append(t)
        turns_used.append(t)
    return _result("TC", set_name, seed, task, states, ok, calls, invalid, attempts, t0, log,
                   {"turns": turns_used})


def run(arm, set_name, seed, llm=None):
    return run_tc(set_name, seed, llm) if arm == "TC" else run_ca(arm, set_name, seed, llm)
