"""Verify the opened research in one command: python3 research/verify.py

1. Recomputes every opened seal (files concatenated in the order of their SEALS.md line) and checks the hash is in
   SEALS.md.
2. Runs the zero-cost checks: the engine library tests, the protocol conformance tests, and the AGENTS2 analysis
   (0 model calls) against the published results files, re-run in a temporary folder; its output must equal the
   sealed RESULTS_AGENTS2.json byte for byte.
3. A9 (experiments/): recomputes the A9 seal from the sealed commit, and once results/a9.json exists, re-scores every
   results/a9_results_*.jsonl with the sealed a9_analyse.py in a temporary folder; verdicts and cells must equal the
   published a9.json.
"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
S = os.path.join(HERE, "sealed")

SEALS = {
    "T2b": ["roots/RESULTS_T2B.md", "roots/PREREG_T2B.md", "roots/t2b.py", "roots/RESULTS_T2B.json"],
    "T2c": ["roots/PREREG_T2C.md", "roots/t2c.py", "roots/RESULTS_T2C.json", "roots/RESULTS_T2C.md"],
    "seed and plan": ["seed/SEED_V1.md", "seed/SEED_V2.md", "seed/SEED_V3.md", "seed/MISSION_100X.md"],
    "OPS1": ["seed/ops/PREREG_OPS1.md", "seed/ops/ops1.py", "seed/ops/RESULTS_OPS1_part1.json",
             "seed/ops/RESULTS_OPS1_part2.json", "seed/ops/RESULTS_OPS1.md"],
    "OPS2": ["seed/ops2/PREREG_OPS2.md", "seed/ops2/calibration_sqlite.py", "seed/ops2/ops2.py",
             "seed/ops2/RESULTS_OPS2.json", "seed/ops2/RESULTS_OPS2.md"],
    "ENGINE1": ["seed/engine/PREREG_ENGINE1.md", "seed/engine/engine1.py", "seed/engine/RESULTS_ENGINE1.json",
                "seed/engine/ROOT_GENOME.jsonl", "seed/engine/RESULTS_ENGINE1.md"],
    "ENGINE2": ["seed/engine2/PREREG_ENGINE2.md", "seed/engine2/engine2.py", "seed/engine2/RESULTS_ENGINE2.json",
                "seed/engine2/ROOT_GENOME_2.jsonl", "seed/engine2/RESULTS_ENGINE2.md"],
    "SPHERE1": ["seed/sphere/PREREG_SPHERE1.md", "seed/sphere/sphere1.py", "seed/sphere/RESULTS_SPHERE1.json",
                "seed/sphere/RESULTS_SPHERE1.md"],
    "SPHERE2": ["seed/sphere2/PREREG_SPHERE2.md", "seed/sphere2/sphere2.py", "seed/sphere2/RESULTS_SPHERE2.json",
                "seed/sphere2/RESULTS_SPHERE2.md"],
    "SPHERE3": ["seed/sphere3/PREREG_SPHERE3.md", "seed/sphere3/sphere3.py", "seed/sphere3/RESULTS_SPHERE3.json",
                "seed/sphere3/RESULTS_SPHERE3.md"],
    "SQLITE2": ["seed/sqlite2/PREREG_SQLITE2.md", "seed/sqlite2/sqlite2.py", "seed/sqlite2/RESULTS_SQLITE2.json",
                "seed/sqlite2/RESULTS_SQLITE2.md"],
    "AGENTS2": ["seed/agents2/PREREG_AGENTS2.md", "seed/agents2/agents2.py", "seed/agents2/RESULTS_AGENTS2.json",
                "seed/agents2/RESULTS_AGENTS2.md"],
}


A9_SEAL = ("fc44d4d", ["PREREGISTRATION_A9.md", "a9_tasks.py", "a9_beacon.py", "a9_arms.py", "a9_run.py",
                       "a9_analyse.py", "test_a9.py"])


def check_a9(seals):
    import glob, json, shutil, tempfile
    ok_all = True
    commit, files = A9_SEAL
    try:
        blob = b"".join(subprocess.run(["git", "-C", ROOT, "show", f"{commit}:experiments/{f}"], capture_output=True,
                                       check=True).stdout for f in files)
        h = hashlib.sha256(blob).hexdigest()
        ok = h in seals
        print(f"{'OK ' if ok else 'BAD'} seal A9             {h[:16]}… (from commit {commit})")
        ok_all &= ok
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("--  seal A9: needs a git clone (git show of the sealed commit); skipped")
    pub = os.path.join(ROOT, "results", "a9.json")
    if not os.path.exists(pub):
        print("--  A9 re-score: results/a9.json not published yet; skipped")
        return ok_all
    sys.path.insert(0, os.path.join(ROOT, "experiments"))
    import a9_analyse as AN
    tmp = tempfile.mkdtemp()
    for p in glob.glob(os.path.join(ROOT, "results", "a9_results_*.jsonl")):
        shutil.copy(p, tmp)
    AN.R = tmp
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        AN.main()
    mine, theirs = json.load(open(os.path.join(tmp, "a9.json"))), json.load(open(pub))
    ok = all(json.dumps(mine[k], sort_keys=True) == json.dumps(theirs[k], sort_keys=True)
             for k in ("verdicts", "cells", "quarters", "incomplete"))
    print(f"{'OK ' if ok else 'BAD'} A9 re-score from raw results (sealed a9_analyse.py) equals results/a9.json")
    return ok_all and ok


def main():
    seals = open(os.path.join(ROOT, "SEALS.md")).read()
    ok_all = True
    for name, files in SEALS.items():
        h = hashlib.sha256(b"".join(open(os.path.join(S, f), "rb").read() for f in files)).hexdigest()
        ok = h in seals; ok_all &= ok
        print(f"{'OK ' if ok else 'BAD'} seal {name:14s} {h[:16]}…")
    for label, cmd, cwd in (
            ("engine library tests", [sys.executable, "-m", "unittest", "-q", "test_rsos_engine"], os.path.join(HERE, "rsos_engine")),
            ("protocol v0 tests", [sys.executable, "-m", "unittest", "-q", "test_protocol_v0"], os.path.join(S, "seed", "protocol")),
            ("AGENTS2 analysis (0 model calls), re-run in a temporary copy", None, None)):
        env = dict(os.environ, RSOS_LANGUAGE=ROOT)
        if cmd is None:                                    # re-run AGENTS2 elsewhere; its output must equal the sealed file
            import shutil, tempfile
            tmp = tempfile.mkdtemp(); src = os.path.join(S, "seed", "agents2")
            shutil.copy(os.path.join(src, "agents2.py"), tmp)
            r = subprocess.run([sys.executable, "agents2.py"], cwd=tmp, env=env, capture_output=True, text=True)
            ok = r.returncode == 0 and open(os.path.join(tmp, "RESULTS_AGENTS2.json"), "rb").read() == \
                open(os.path.join(src, "RESULTS_AGENTS2.json"), "rb").read()
        else:
            r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
            ok = r.returncode == 0
        ok_all &= ok
        print(f"{'OK ' if ok else 'BAD'} {label}")
    ok_all &= check_a9(seals)
    print("ALL OK" if ok_all else "SOMETHING FAILED")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
