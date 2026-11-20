"""A9 zoom cells: the A7 long-task generator at three state sizes (PREREGISTRATION_A9.md).

Z30  =  5 services x 6 fields =  30 keys, 56 requests, chain depth 4
Z100 = 17 services x 6 fields = 102 keys, 56 requests, chain depth 4
Z300 = 50 services x 6 fields = 300 keys, 56 requests, chain depth 4 (the size of A7/A8's L3)

Seeds come from the public drand beacon (League of Entropy mainnet, default chain, 30-second rounds, genesis
1595431050), round ROUND, emitted after the seal: seed_i = int(sha256("<randomness>:A9:<cell>:<i>")[:16], 16).
`a9_beacon.py` fetches the round once and writes results/a9_beacon.json; nobody chooses the tasks.
"""

import hashlib
import json
import os

import a1_agents as A
import a7_tasks as T

ROUND = 6657746                      # 20 Nov 2026 08:30:00 UTC
CELLS = {"Z30": (56, 4, 5), "Z100": (56, 4, 17), "Z300": (56, 4, 50)}
N_SEEDS = 8
BEACON = os.path.join(A.ROOT, "results", "a9_beacon.json")


def seeds_from(randomness, cell, n=N_SEEDS):
    return [int(hashlib.sha256(f"{randomness}:A9:{cell}:{i}".encode()).hexdigest()[:16], 16) for i in range(n)]


def load_seeds():
    if not os.path.exists(BEACON):
        return {}
    b = json.load(open(BEACON))
    assert b["round"] == ROUND, "beacon file is not the sealed round"
    return {c: seeds_from(b["randomness"], c) for c in CELLS}


def register():
    """Make the Z cells visible to a7_tasks / a7_run exactly like L1-L3."""
    T.CELLS.update(CELLS)
    T.SEEDS.update(load_seeds())
    return T.SEEDS
