"""A9 runner (PREREGISTRATION_A9.md). Same backends as A7/A8: A7_BACKEND=cli (claude -p), codex, openai, ollama.

    python experiments/a9_beacon.py                      # once, after the sealed round is emitted
    A7_LABEL=<family> python experiments/a9_run.py smoke # one task per arm, seed 999, never scored
    A7_LABEL=<family> python experiments/a9_run.py all   # every cell in the sealed order, resumable
    A7_LABEL=<family> python experiments/a9_run.py cell Z300 TC,CAv

Order (decisive cells first): Z300 TC, CAv, CAb, B2, X5b; then Z30 all arms; then Z100 B2, X5b, CAv, CAb.
TC runs on the first 4 seeds of Z30 and Z300 only (its calls per task are about 50x the others').
Results: results/a9_results_<cell>_<label>.jsonl; transcripts results/a9_transcripts_<cell>_<label>.jsonl.
"""

import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a9_tasks as Z           # noqa: E402

Z.register()
import a7_run as R7            # noqa: E402
import a9_arms as N            # noqa: E402

R7.SEEDS.update({c: s for c, s in Z.load_seeds().items()})
if os.name == "nt":            # amendment 1 (transport only): on Windows `claude -p` needs the user profile to find its
    import a5_llm as _L        # login; a5_llm.py stays frozen, its environment filter is extended here at run time
    _L.KEEP = tuple(_L.KEEP) + ("USERPROFILE", "APPDATA", "LOCALAPPDATA", "SYSTEMROOT", "SystemRoot", "TEMP", "TMP",
                                "HOMEDRIVE", "HOMEPATH", "PATHEXT", "COMSPEC", "ProgramData", "ProgramFiles")
if R7.BACKEND == "ollama":     # amendment 2: open-weights family on a free GPU; a 300-key task needs more than A7c's
    import a7_local as _O      # 8,192-token context, so A9 raises it at run time (a7_local.py unchanged)
    _O.OPTIONS["num_ctx"] = int(os.environ.get("A9_NUM_CTX", "32768"))
N_TC = 4
ORDER = [("Z300", ["TC", "CAv", "CAb", "B2", "X5b"]), ("Z30", ["TC", "CAv", "CAb", "B2", "X5b"]),
         ("Z100", ["B2", "X5b", "CAv", "CAb"])]
_lock = threading.Lock()


def seeds_for(cell, arm):
    s = R7.SEEDS[cell]
    return s[:N_TC] if arm == "TC" else s


def one(arm, cell, seed):
    if arm in N.ARMS:
        r = N.run(arm, cell, seed)
    else:
        r = R7.run_one(arm, cell, seed)
    r["set"], r["label"], r["backend"] = cell, R7.LABEL, R7.BACKEND
    r.pop("final_state", None)
    return r


def run_cell(cell, arms):
    if cell not in R7.SEEDS:
        raise SystemExit("no seeds: run python experiments/a9_beacon.py first (after the sealed round)")
    R7.setup(cell)
    res_path = os.path.join(R7.R, f"a9_results_{cell}_{R7.LABEL}.jsonl")
    os.environ["A7_TRANSCRIPTS"] = os.path.join(R7.R, f"a9_transcripts_{cell}_{R7.LABEL}.jsonl")
    done = set()
    if os.path.exists(res_path):
        for line in open(res_path):
            r = json.loads(line)
            done.add((r["arm"], r["seed"]))
    todo = [(a, s) for a in arms for s in seeds_for(cell, a) if (a, s) not in done]
    print(f"{cell} label={R7.LABEL} backend={R7.BACKEND}: done {len(done)}, live {len(todo)}", flush=True)
    workers = int(os.environ.get("A7_WORKERS", "1" if R7.BACKEND == "ollama" else "2" if R7.BACKEND in
                                 ("openai", "codex") else "4"))
    errors = []
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(one, a, cell, s): (a, s) for a, s in todo}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:  # noqa: BLE001  a provider error stops one task, never the others
                errors.append({"arm": futs[fu][0], "seed": futs[fu][1], "error": str(e)[:300]})
                print(f"{cell} {futs[fu][0]} {futs[fu][1]} NOT RUN: {str(e)[:120]}", flush=True)
                continue
            with _lock:
                with open(res_path, "a") as f:
                    f.write(json.dumps(r) + "\n")
    if errors:
        with open(os.path.join(R7.R, f"a9_errors_{cell}_{R7.LABEL}.jsonl"), "a") as f:
            for e in errors:
                f.write(json.dumps(e) + "\n")
        print(f"{len(errors)} task(s) not run; run the same command again to resume", flush=True)


def smoke(arms):
    """One task per arm on Z30, seed 999 (not a beacon seed; never scored): checks the backend end to end."""
    R7.T.CELLS.update(Z.CELLS)
    R7.setup("Z30")
    os.environ["A7_TRANSCRIPTS"] = os.path.join(R7.R, f"a9_smoke_transcripts_{R7.LABEL}.jsonl")
    for a in arms:
        r = one(a, "Z30", 999)
        with open(os.path.join(R7.R, f"a9_smoke_{R7.LABEL}.jsonl"), "a") as f:
            f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    if sys.argv[1] == "smoke":
        smoke(sys.argv[2].split(",") if len(sys.argv) > 2 else ["X5b", "CAb", "B2", "CAv", "TC"])
    elif sys.argv[1] == "all":
        for cell, arms in ORDER:
            run_cell(cell, arms)
    elif sys.argv[1] == "cell":
        run_cell(sys.argv[2], sys.argv[3].split(","))
