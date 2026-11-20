"""Fetch the sealed drand round once (after it is emitted) and write results/a9_beacon.json. Standard library.

    python experiments/a9_beacon.py
"""

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a9_tasks as Z          # noqa: E402

URL = f"https://api.drand.sh/public/{Z.ROUND}"

if __name__ == "__main__":
    if os.path.exists(Z.BEACON):
        print("already fetched:", json.load(open(Z.BEACON))["randomness"][:16], "…")
        sys.exit(0)
    req = urllib.request.Request(URL, headers={"User-Agent": "rsos-a9"})
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())
    assert d["round"] == Z.ROUND
    os.makedirs(os.path.dirname(Z.BEACON), exist_ok=True)
    json.dump({"round": d["round"], "randomness": d["randomness"], "signature": d.get("signature"), "url": URL},
              open(Z.BEACON, "w"), indent=1)
    print("round", d["round"], "randomness", d["randomness"][:16], "…")
    for c in Z.CELLS:
        print(c, Z.seeds_from(d["randomness"], c)[:3], "…")
