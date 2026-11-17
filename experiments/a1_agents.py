"""A1: the first real-host test. Three LLM agents (planner -> worker -> checker) under four channel conditions.

Pre-registration: experiments/PREREGISTRATION_A1.md. Agents are Claude instances called headless (`claude -p`).
Every LLM call and every inter-agent message is logged to results/a1_transcripts.jsonl.

    python experiments/a1_agents.py run      # live run (LLM calls)
    python experiments/a1_agents.py analyse  # numbers + truncation test from the transcripts
"""

import json
import os
import random
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from rsoslang import palace as PAL        # noqa: E402

MODEL = os.environ.get("A1_MODEL", "claude-haiku-5-5")
SEEDS = list(range(100, 108))
STEPS = 14
DRIFT_STEPS = (4, 8, 12)
MAX_RETRY = 2
CONDS = ["P", "A", "B", "C"]
TOK = re.compile(r"\w+|[^\w\s]")
TRANSCRIPTS = os.path.join(ROOT, "results", "a1_transcripts.jsonl")
_lock = threading.Lock()


def ntok(s):
    return len(TOK.findall(s))


# ---------------------------------------------------------------- task generator (ground truth)

SERVICES = ["auth", "billing", "search", "cache", "gateway"]
FIELDS = ["replicas", "timeout_ms", "retries", "owner", "region", "log_level"]
OWNERS = ["alice", "bruno", "chen", "dara", "emeka", "farah"]
REGIONS = ["eu-west", "us-east", "ap-south", "sa-east"]
LEVELS = ["debug", "info", "warn", "error"]
FORMAT = {"replicas": r"[1-9]\d?", "timeout_ms": r"\d{3,5}", "retries": r"\d", "owner": "|".join(OWNERS),
          "region": "|".join(REGIONS), "log_level": "|".join(LEVELS), "max_conn": r"\d{1,4}",
          "tier": r"gold|silver|bronze"}


def rand_value(field, rng):
    return {"replicas": lambda: str(rng.randint(1, 9)), "timeout_ms": lambda: str(rng.randint(1, 50) * 100),
            "retries": lambda: str(rng.randint(0, 7)), "owner": lambda: rng.choice(OWNERS),
            "region": lambda: rng.choice(REGIONS), "log_level": lambda: rng.choice(LEVELS),
            "max_conn": lambda: str(rng.choice([16, 32, 64, 128, 256])),
            "tier": lambda: rng.choice(["gold", "silver", "bronze"])}[field]()


def valid_line(line):
    m = re.fullmatch(r"([a-z]+)\.([a-z_]+) = (\S+)", line.strip())
    return bool(m) and m.group(2) in FORMAT and re.fullmatch(FORMAT[m.group(2)], m.group(3)) is not None


def to_lines(state):
    return [f"{k} = {v}" for k, v in state.items()]


def text_of(state):
    return "\n".join(to_lines(state))


def make_task(seed):
    rng = random.Random(seed)
    state = {f"{s}.{f}": rand_value(f, rng) for s in SERVICES for f in FIELDS}
    state = dict(list(state.items()))
    init = dict(state)
    reqs, touched, truths = [], [], [dict(state)]
    for _ in range(STEPS):
        kind = rng.choice(["set", "set", "inc", "double", "owner", "add", "delete", "cond", "copy"])
        keys = list(state)
        if kind == "set":
            k = rng.choice(keys); f = k.split(".")[1]; v = rand_value(f, rng)
            while v == state[k]:
                v = rand_value(f, rng)
            text = rng.choice([f"Set {k} to {v}.", f"Change the {f} of {k.split('.')[0]} to {v}.",
                               f"{k.split('.')[0]} needs {f} = {v} from now on."])
            state[k] = v; t = [k]
        elif kind in ("inc", "double"):
            cand = [k for k in keys if k.endswith(("replicas", "retries"))]
            k = rng.choice(cand); old = int(state[k])
            if kind == "inc":
                d = rng.randint(1, 2); new = min(old + d, 9)
                text = f"Increase {k} by {d} (cap at 9)."
            else:
                new = min(old * 2, 9); text = f"Double {k}, capped at 9."
            state[k] = str(new); t = [k]
        elif kind == "owner":
            present = sorted({v for k, v in state.items() if k.endswith(".owner")})
            a = rng.choice(present); b = rng.choice([o for o in OWNERS if o != a])
            text = f"Everything owned by {a} is now owned by {b}."
            t = [k for k, v in state.items() if k.endswith(".owner") and v == a]
            for k in t:
                state[k] = b
        elif kind == "add":
            s = rng.choice(SERVICES); f = rng.choice(["max_conn", "tier"])
            k = f"{s}.{f}"
            if k in state:
                v = rand_value(f, rng); text = f"Set {k} to {v}."
            else:
                v = rand_value(f, rng); text = f"Add a new line {k} = {v} at the end."
            state[k] = v; t = [k]
        elif kind == "delete":
            k = rng.choice(keys); text = f"Remove the line {k} entirely."
            del state[k]; t = [k]
        elif kind == "cond":
            s = rng.choice(SERVICES)
            if f"{s}.region" not in state or f"{s}.log_level" not in state:
                k = rng.choice(keys); f = k.split(".")[1]; v = rand_value(f, rng)
                text = f"Set {k} to {v}."; state[k] = v; t = [k]
            else:
                r = rng.choice(REGIONS); l1, l2 = rng.sample(LEVELS, 2)
                text = f"If {s}.region is {r}, set {s}.log_level to {l1}; otherwise set it to {l2}."
                state[f"{s}.log_level"] = l1 if state[f"{s}.region"] == r else l2; t = [f"{s}.log_level"]
        else:  # copy
            f = rng.choice(["timeout_ms", "retries", "replicas"])
            pair = [s for s in SERVICES if f"{s}.{f}" in state]
            a, b = rng.sample(pair, 2)
            text = f"Make {b}.{f} equal to {a}.{f}."
            state[f"{b}.{f}"] = state[f"{a}.{f}"]; t = [f"{b}.{f}", f"{a}.{f}"]
        reqs.append(text); touched.append(t); truths.append(dict(state))
    return {"seed": seed, "init": init, "requests": reqs, "touched": touched, "final": state, "truths": truths}


def drift_plan(task, truths):
    """For each drift step: (key, wrong value). Key present before the step, untouched at/after it."""
    rng = random.Random(task["seed"] * 7 + 1)
    later = set()
    plan = {}
    for st in DRIFT_STEPS:
        later = set(k for t in task["touched"][st:] for k in t)
        cand = [k for k in truths[st] if k not in later and k in truths[-1] and truths[st][k] == truths[-1][k]]
        k = rng.choice(sorted(cand)); f = k.split(".")[1]
        v = rand_value(f, rng)
        while v == truths[st][k]:
            v = rand_value(f, rng)
        plan[st] = (k, v)
    return plan


# ---------------------------------------------------------------- LLM call

def llm(system, prompt, schema=None, log=None):
    cmd = ["claude", "-p", "--output-format", "json", "--model", MODEL, "--system-prompt", system,
           "--tools", "", "--no-session-persistence"]
    if schema:
        cmd += ["--json-schema", json.dumps(schema)]
    for attempt in range(4):
        t0 = time.time()
        try:
            p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=180, cwd="/tmp")
            d = json.loads(p.stdout)
            if d.get("is_error"):
                raise RuntimeError(d.get("result"))
            u = d["usage"]
            rec = {"in": u["input_tokens"], "cache_w": u.get("cache_creation_input_tokens", 0),
                   "cache_r": u.get("cache_read_input_tokens", 0), "out": u["output_tokens"],
                   "sec": time.time() - t0, "api_ms": d.get("duration_api_ms"), "turns": d.get("num_turns"),
                   "cost": d.get("total_cost_usd")}
            text = d.get("result") or ""
            so = d.get("structured_output")
            if log is not None:
                log.append({"kind": "llm", "system": system[:40], "prompt": prompt, "text": text,
                            "structured": so, **rec})
            return text, so, rec
        except Exception as e:  # noqa: BLE001
            err = str(e)[:200]
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("llm failed: " + err)


def billed(rec):
    return rec["in"] + rec["cache_w"] + rec["cache_r"] + rec["out"]


# ---------------------------------------------------------------- prompts

SYS = {
    "planner": "You are the PLANNER in a three-agent pipeline that edits a configuration state. Given one change "
               "request and the state, write ONE precise instruction for the worker: name every exact key and its "
               "final value (resolve conditions, arithmetic and owner transfers yourself). Output only the "
               "instruction, no preamble.",
    "worker": "You are the WORKER in a three-agent pipeline that edits a configuration state of lines "
              "'service.field = value'. Apply exactly the instruction and change nothing else.",
    "checker": "You are the CHECKER in a three-agent pipeline. Verify that the worker made exactly the requested "
               "change and nothing else (no other line changed, added or removed). Be strict.",
}

W_A = ("Output ONLY a JSON object: {\"note\": \"<one sentence>\", \"state\": {\"<key>\": \"<value>\", ...}} with the "
       "complete new state, all lines, in the same order (new lines at the end).")
W_C = ("Output ONLY a JSON object: {\"summary\": \"<one sentence>\", \"writes\": [{\"key\": \"<key>\", \"value\": "
       "\"<value or DELETE>\"}]} listing only the lines that change.")
W_P = ("Output ONLY the edit lines, one per line: 'SET <key> = <value>' to change or add a line, 'DEL <key>' to "
       "remove one. Nothing else.")
C_OUT = "Answer with a JSON object only: {\"verdict\": \"approve\" or \"reject\", \"reason\": \"<short>\"}."

SCHEMA_W = {"type": "object", "properties": {"note": {"type": "string"}, "state": {"type": "array", "items": {
    "type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
    "required": ["key", "value"]}}}, "required": ["note", "state"]}
SCHEMA_C = {"type": "object", "properties": {"verdict": {"type": "string", "enum": ["approve", "reject"]},
                                             "reason": {"type": "string"}}, "required": ["verdict", "reason"]}


def parse_json(text):
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-z]*\n?|\n?```$", "", t)
    i, j = t.find("{"), t.rfind("}")
    return json.loads(t[i:j + 1])


def parse_verdict(text, so=None):
    try:
        d = so if so else parse_json(text)
        return d.get("verdict", "").lower().startswith("approve"), d.get("reason", "")
    except Exception:  # noqa: BLE001
        return text.lower().lstrip().startswith(("approve", "{\"verdict\": \"approve")), text[:200]


def retrieve(store_lines, query, k=8):  # noqa: D103
    q = set(re.findall(r"[a-z_]+", query.lower()))
    scored = []
    for i, ln in enumerate(store_lines):
        key = ln.split(" = ")[0]
        parts = set(key.split(".")) | {key}
        scored.append((-(len(parts & q) + (2 if key in query else 0)), i, ln))
    scored.sort()
    return [ln for _, _, ln in scored[:k]]


def apply_edits(state, text):
    s = dict(state)
    for ln in text.strip().splitlines():
        ln = ln.strip().strip("`")
        m = re.match(r"SET\s+([a-z]+\.[a-z_]+)\s*=\s*(\S+)", ln)
        if m:
            s[m.group(1)] = m.group(2); continue
        m = re.match(r"DEL\s+([a-z]+\.[a-z_]+)", ln)
        if m:
            s.pop(m.group(1), None)
    return s


def diff_view(old, new):
    out = []
    for k in old:
        if k not in new:
            out.append(f"- {k} = {old[k]} (removed)")
        elif new[k] != old[k]:
            out.append(f"~ {k}: {old[k]} -> {new[k]}")
    for k in new:
        if k not in old:
            out.append(f"+ {k} = {new[k]} (added)")
    return "\n".join(out) or "(no change)"


def state_of_text(text):
    s = {}
    for ln in text.split("\n"):
        if " = " in ln:
            k, v = ln.split(" = ", 1); s[k] = v
    return s


# ---------------------------------------------------------------- palace pieces (green dot + White Dragon heal)

def palace_msg(old_text, new_text):
    """`@state#base` + line edits + trailing green dot `=newhash`."""
    p = PAL.Palace({"state": old_text})
    return PAL.encode(p, "state", new_text) + "\n=" + PAL.h(new_text)


def palace_decode(book_text, msg):
    """Returns (new_text, status): status ok | drift | trunc."""
    rows = msg.split("\n")
    if not rows[-1].startswith("=") or len(rows[-1]) != 9:
        return None, "trunc"
    body, dot = "\n".join(rows[:-1]), rows[-1][1:]
    try:
        new = PAL.decode(PAL.Palace({"state": book_text}), body)
    except PAL.Drift:
        return None, "drift"
    except Exception:  # noqa: BLE001
        return None, "trunc"
    return (new, "ok") if PAL.h(new) == dot else (None, "trunc")


def dragon_heal(sender_text, receiver_text):
    """White Dragon heal with the H3c filter. Returns healed text, channel text, filter decisions."""
    req = ",".join(PAL.chunk_signals(receiver_text))
    bad = PAL.find(sender_text, PAL.chunk_signals(receiver_text))
    s, r = sender_text.split("\n"), receiver_text.split("\n")
    size = PAL.CHUNK
    nch = (len(s) + size - 1) // size
    reply, out, decisions = [], [], []
    for i in range(nch):
        sc, rc = s[i * size:(i + 1) * size], r[i * size:(i + 1) * size]
        if i in bad:
            reply.append(f"#{i}\n" + "\n".join(sc))
            s_ok = all(valid_line(x) for x in sc)
            r_ok = all(valid_line(x) for x in rc) and len(rc) == len(sc)
            # filter: drop a version failing its format test; else keep the approved chain (sender)
            keep = rc if (r_ok and not s_ok) else sc
            decisions.append("receiver" if keep is rc else "sender")
            out.extend(keep)
        else:
            out.extend(rc)
    reply.append(f"N{nch}")
    return "\n".join(out), req + "\n" + "\n".join(reply), decisions


# ---------------------------------------------------------------- one task under one condition

def run_task(cond, seed, mods=None, tag=None):
    """mods (A2 transplants, condition C only): {"sys": {role: text}, "proc": {role: text}, "struct": [names]}."""
    mods = mods or {}
    msys, mproc, mst = mods.get("sys", {}), mods.get("proc", {}), set(mods.get("struct", []))
    K = 16 if "retrieval_k16" in mst else 8
    task = make_task(seed)
    truths = task["truths"]
    plan = drift_plan(task, truths)
    log = []
    msgs = []                 # (step, sender, receiver, text)
    calls = []
    drift_events = []
    t_start = time.time()

    ctx = {"attempt": 0, "step": 0}

    def send(step, a, b, text, kind="msg"):
        msgs.append({"step": step, "attempt": ctx["attempt"], "from": a, "to": b, "text": text, "tok": ntok(text),
                     "bytes": len(text.encode()), "kind": kind})

    def call(role, prompt, schema=None, sysrole=None):
        r0 = sysrole or role
        system = SYS[r0] + ((" " + msys[r0]) if r0 in msys else "")
        if r0 in mproc:
            prompt = f"Procedure you must follow: {mproc[r0]}\n\n" + prompt
        text, so, rec = llm(system, prompt, schema, log)
        rec["role"] = r0; rec["step"] = ctx["step"]; rec["attempt"] = ctx["attempt"]
        calls.append(rec)
        return text, so, rec

    approved = dict(task["init"])          # checker's memory / authoritative in A, B
    store = dict(task["init"])             # C: shared memory
    journal = dict(task["init"])           # A2 memory_journal: last approved value per line
    books = {r: text_of(task["init"]) for r in ("planner", "worker", "checker")}   # P
    step_fail = 0
    for st, req in enumerate(task["requests"]):
        ctx["step"], ctx["attempt"] = st, 0
        # ---------- planner
        if cond == "P":
            view = books["planner"]
        elif cond == "C":
            view = "\n".join(retrieve(to_lines(store), req, K))
        else:
            view = text_of(approved)
        instr, _, _ = call("planner", f"Change request: {req}\n\nState:\n{view}")
        instr = instr.strip()
        # ---------- drift injection + planner -> worker message
        worker_state = None
        dr = plan.get(st)
        d_ev = None
        if cond == "P":
            sig = PAL.h(books["planner"])
            send(st, "planner", "worker", f"@state#{sig}\n{instr}")
            if dr:
                ws = state_of_text(books["worker"]); ws[dr[0]] = dr[1]; books["worker"] = text_of(ws)
                d_ev = {"step": st, "key": dr[0], "true": truths[st][dr[0]], "wrong": dr[1]}
            if PAL.h(books["worker"]) != sig:            # green dot: drift found
                t0 = time.time()
                healed, chan, dec = dragon_heal(books["planner"], books["worker"])
                books["worker"] = healed
                send(st, "worker", "planner", chan, kind="heal")
                if d_ev:
                    d_ev.update({"detected_by": "green_dot", "recovery_tok": ntok(chan),
                                 "recovery_sec": time.time() - t0, "resend_tok": ntok(books["planner"]),
                                 "filter": dec})
        elif cond in ("A", "B"):
            ws = dict(approved)
            if dr:
                ws[dr[0]] = dr[1]
                d_ev = {"step": st, "key": dr[0], "true": truths[st][dr[0]], "wrong": dr[1]}
            send(st, "planner", "worker", json.dumps({"instruction": instr, "state": ws}))
            worker_state = ws
        else:  # C
            if dr:
                store[dr[0]] = dr[1]
                d_ev = {"step": st, "key": dr[0], "true": truths[st][dr[0]], "wrong": dr[1]}
            if "memory_journal" in mst:              # per-line checksums + journal of approved writes
                bad = [k for k in set(store) | set(journal) if PAL.h(f"{k}={store.get(k)}") != PAL.h(f"{k}={journal.get(k)}")]
                for k in bad:
                    if journal.get(k) is None:
                        store.pop(k, None)
                    else:
                        store[k] = journal[k]
                if bad:
                    send(st, "memory", "memory", "restore " + " ".join(bad), kind="heal")
            send(st, "planner", "worker", json.dumps({"instruction": instr, "summary": req}))
        # ---------- worker / checker loop
        feedback = ""
        ok = False
        t_det = None
        for attempt in range(MAX_RETRY + 1):
            ctx["attempt"] = attempt
            fb = f"\n\nThe checker rejected your previous attempt: {feedback}" if feedback else ""
            if cond == "P":
                wtext, _, _ = call("worker", f"Instruction: {instr}{fb}\n\nYour state:\n{books['worker']}\n\n{W_P}")
                old = books["worker"]
                new_state = apply_edits(state_of_text(old), wtext)
                new_text = text_of(new_state)
                m = palace_msg(old, new_text)
                send(st, "worker", "checker", m)
                dec_text, status = palace_decode(books["checker"], m)
                if status != "ok":                       # trailing / leading dot mismatch: heal, then decode
                    healed, chan, _ = dragon_heal(old, books["checker"])
                    books["checker"] = healed
                    send(st, "checker", "worker", chan, kind="heal")
                    dec_text, status = palace_decode(books["checker"], m)
                cprompt = (f"Change request: {req}\nInstruction: {instr}\n\nChanges the worker made (decoded):\n"
                           f"{diff_view(state_of_text(books['checker']), state_of_text(dec_text))}\n\n{C_OUT}")
                ctext, so, _ = call("checker", cprompt)
                good, reason = parse_verdict(ctext, so)
                send(st, "checker", "worker", json.dumps({"verdict": "approve" if good else "reject",
                                                          "reason": reason}))
                if good:
                    books["checker"] = dec_text
                    send(st, "checker", "planner", m)     # forward the approved edits
                    dp, stp = palace_decode(books["planner"], m)
                    if stp != "ok":
                        healed, chan, _ = dragon_heal(dec_text, books["planner"])
                        send(st, "planner", "checker", chan, kind="heal")
                        dp = dec_text
                    books["planner"] = dp
                    books["worker"] = new_text
                    ok = True
                    break
                feedback = reason
            elif cond in ("A", "B"):
                prompt = f"Instruction: {instr}{fb}\n\nState:\n{json.dumps(worker_state, indent=0)}\n\n"
                if cond == "A":
                    wtext, _, _ = call("worker", prompt + W_A)
                    try:
                        new_state = {k: str(v) for k, v in parse_json(wtext)["state"].items()}
                    except Exception:  # noqa: BLE001
                        new_state = None
                    send(st, "worker", "checker", wtext.strip())
                else:
                    wtext, so, _ = call("worker", prompt + "Return the complete new state, all lines, in order.",
                                        SCHEMA_W)
                    try:
                        new_state = {d["key"]: str(d["value"]) for d in so["state"]}
                    except Exception:  # noqa: BLE001
                        new_state = None
                    send(st, "worker", "checker", json.dumps(so))
                if new_state is None:
                    feedback = "your output could not be parsed"
                    continue
                cprompt = (f"Change request: {req}\nInstruction: {instr}\n\nLast approved state:\n"
                           f"{text_of(approved)}\n\nNew state from the worker:\n{text_of(new_state)}\n\n")
                if cond == "A":
                    ctext, so, _ = call("checker", cprompt + C_OUT)
                else:
                    ctext, so, _ = call("checker", cprompt + "Return verdict and reason.", SCHEMA_C)
                good, reason = parse_verdict(ctext, so)
                if good:
                    approved = new_state
                    send(st, "checker", "planner", json.dumps({"verdict": "approve", "reason": reason,
                                                               "state": approved}))
                    ok = True
                    break
                send(st, "checker", "worker", json.dumps({"verdict": "reject", "reason": reason}))
                if d_ev and t_det is None and dr[0] in reason:
                    t_det = attempt
                feedback = reason
            else:  # C
                ret = (text_of(store) if "worker_full_view" in mst else "\n".join(retrieve(to_lines(store), instr, K)))
                wtext, _, _ = call("worker", f"Instruction: {instr}{fb}\n\nRelevant lines from memory:\n{ret}\n\n{W_C}")
                try:
                    d = parse_json(wtext); writes = d["writes"]; summ = d.get("summary", "")
                    writes = [(w["key"], str(w["value"])) for w in writes]
                except Exception:  # noqa: BLE001
                    feedback = "your output could not be parsed"; send(st, "worker", "checker", wtext.strip())
                    continue
                send(st, "worker", "checker", wtext.strip())
                ret2 = (text_of(store) if "checker_full_view" in mst else
                        "\n".join(retrieve(to_lines(store), summ + " " + " ".join(k for k, _ in writes), K)))
                if "readback" in mst:                    # planner confirms the worker's read-back of its writes
                    rb, so, _ = call("checker", f"Change request: {req}\nYour instruction was: {instr}\nThe worker reads back "
                                     "these writes:\n" + "\n".join(f"{k} = {v}" for k, v in writes) +
                                     f"\n\nDo they implement your instruction exactly? {C_OUT}", sysrole="planner")
                    send(st, "worker", "planner", "readback " + json.dumps(writes))
                    g0, r0 = parse_verdict(rb, so)
                    send(st, "planner", "worker", json.dumps({"verdict": "approve" if g0 else "reject", "reason": r0}))
                    if not g0:
                        feedback = r0
                        continue
                cprompt = (f"Change request: {req}\nInstruction: {instr}\n\nWorker summary: {summ}\nWrites:\n"
                           + "\n".join(f"{k} = {v}" for k, v in writes)
                           + f"\n\nRelevant lines from memory (before the writes):\n{ret2}\n\n{C_OUT}")
                ctext, so, _ = call("checker", cprompt)
                good, reason = parse_verdict(ctext, so)
                if good and "second_checker" in mst:
                    c2, so2, _ = call("checker", "You are an independent second checker.\n" + cprompt)
                    good, reason = parse_verdict(c2, so2)
                send(st, "checker", "planner", json.dumps({"verdict": "approve" if good else "reject",
                                                           "summary": summ, "reason": reason}))
                if good and "planner_go_nogo" in mst:      # go / no-go poll by the planner before commit
                    rel = "\n".join(retrieve(to_lines(store), req + " " + " ".join(k for k, _ in writes), K))
                    gq, so3, _ = call("checker", f"Change request: {req}\nWrites about to be committed:\n" +
                                      "\n".join(f"{k} = {v}" for k, v in writes) + f"\n\nCurrent memory lines:\n{rel}"
                                      f"\n\nGo or no-go: do these writes fulfil the request exactly? {C_OUT}",
                                      sysrole="planner")
                    good, r3 = parse_verdict(gq, so3)
                    send(st, "planner", "checker", json.dumps({"verdict": "go" if good else "no-go", "reason": r3}))
                    if not good:
                        reason = r3
                if good:
                    for k, v in writes:
                        if v == "DELETE":
                            store.pop(k, None); journal.pop(k, None)
                        else:
                            store[k] = v; journal[k] = v
                    ok = True
                    break
                feedback = reason
        if not ok:
            step_fail += 1
            if cond == "P":                      # discard the worker's attempt
                books["worker"] = books["planner"]
        # ---------- drift outcome at approval
        cur = state_of_text(books["planner"]) if cond == "P" else (approved if cond in ("A", "B") else store)
        if d_ev:
            d_ev["caught"] = cur.get(d_ev["key"]) == d_ev["true"]
            d_ev.setdefault("detected_by", "checker_or_worker" if d_ev["caught"] else "none")
            drift_events.append(d_ev)
    final = state_of_text(books["planner"]) if cond == "P" else (approved if cond in ("A", "B") else store)
    truth = task["final"]
    keys = set(truth) | set(final)
    acc = sum(final.get(k) == truth.get(k) for k in keys) / len(keys)
    for e in drift_events:
        e["silent_in_final"] = final.get(e["key"]) != e["true"]
    res = {"cond": cond, "seed": seed, "tag": tag, "success": final == truth, "line_acc": acc,
           "final_errors": sorted(k for k in keys if final.get(k) != truth.get(k)),
           "steps_failed": step_fail, "n_msgs": len(msgs), "n_calls": len(calls),
           "channel_tok": sum(m["tok"] for m in msgs), "channel_bytes": sum(m["bytes"] for m in msgs),
           "billed_tok": sum(billed(c) for c in calls), "out_tok": sum(c["out"] for c in calls),
           "in_tok": sum(c["in"] + c["cache_w"] + c["cache_r"] for c in calls),
           "cost_usd": sum(c["cost"] or 0 for c in calls),
           "wall_sec": time.time() - t_start, "drift": drift_events,
           "per_call": [{k: c[k] for k in ("role", "step", "attempt", "in", "cache_w", "cache_r", "out", "sec")}
                        for c in calls],
           "per_msg": [{k: m[k] for k in ("step", "attempt", "from", "to", "tok", "bytes", "kind")} for m in msgs]}
    with _lock:
        with open(TRANSCRIPTS, "a") as f:
            f.write(json.dumps({"cond": cond, "seed": seed, "tag": tag, "msgs": msgs, "calls": log}) + "\n")
    print(f"{cond} {seed} success={res['success']} acc={acc:.3f} chan={res['channel_tok']} "
          f"billed={res['billed_tok']} calls={len(calls)} wall={res['wall_sec']:.0f}s "
          f"drift_caught={sum(e['caught'] for e in drift_events)}/3", flush=True)
    return res


def scaffold():
    """Per-call fixed scaffold: a null call per role with the same flags (and with the schema for B)."""
    out = {}
    for role in SYS:
        _, _, rec = llm(SYS[role], "Reply OK.")
        out[role] = billed(rec) - rec["out"] - 3
    _, _, rec = llm(SYS["worker"], "Reply OK.", SCHEMA_C)
    out["schema_extra"] = billed(rec) - rec["out"] - 3 - out["worker"]
    return out


def main_run(conds=CONDS, seeds=SEEDS, workers=8, out="a1_runs.json"):
    jobs = [(c, s) for s in seeds for c in conds]
    with ThreadPoolExecutor(workers) as ex:
        runs = list(ex.map(lambda j: run_task(*j), jobs))
    sc = scaffold()
    path = os.path.join(ROOT, "results", out)
    json.dump({"model": MODEL, "scaffold": sc, "runs": runs}, open(path, "w"), indent=1)
    return path


if __name__ == "__main__":
    if sys.argv[1] == "run":
        main_run()
    elif sys.argv[1] == "smoke":
        c = sys.argv[2]
        global_runs = run_task(c, 999)
        print(json.dumps({k: v for k, v in global_runs.items() if k != "drift"}, indent=1))
        print(json.dumps(global_runs["drift"], indent=1))
