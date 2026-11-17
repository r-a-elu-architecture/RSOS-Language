#!/usr/bin/env bash
# Stage the public tree (D85) into $1 (default /tmp/rsos-public). Stages only; never pushes or publishes.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-/tmp/rsos-public}"; rm -rf "$OUT"; mkdir -p "$OUT"
grep -v '^#' RELEASE_WHITELIST.txt | sed 's/#.*//' | awk 'NF{print $1}' | while read -r p; do cp -r --parents "$p" "$OUT/"; done
mv "$OUT/README_PUBLIC.md" "$OUT/README.md"
cd "$OUT"
rm -f experiments/s2_chat_maps.py experiments/S2_REPORT.md experiments/PREREGISTRATION_S2.md results/s2_chat_maps.json \
      results/S2_chat_stack.png experiments/BRIEF_A1_AGENT_TEST.md tools/ingest_chat.py tools/chunk.py
# D85 + owner 11:30: the Tier Ledger is not on Zenodo, so ledger experiments stay private for v1
for x in s1_stacked_maps i1_instruments i2_panel u1_universe u1b_standing; do rm -f experiments/$x.py results/$x.json; done
for x in S1 I1 I2 U1 U1B; do rm -f experiments/PREREGISTRATION_$x.md results/${x}_REPORT.md; done
rm -f results/S1_stack.png tools/tiers.py tools/render_stack.py tools/tables.py tests/test_universe.py
find . -name __pycache__ -prune -exec rm -rf {} +
if grep -rqiE --exclude=stage_public.sh "suicid|psychos|schizo|depress|PTSD|hospital" .; then echo "STOP: sensitive term found"; exit 1; fi
grep -rlE --exclude=stage_public.sh "owner_turns|corpus/chat-" . | sed 's/^/owner to review (mentions the private chat corpus): /' || true
python3 -m pytest -q | tail -1
echo "staged: $OUT ($(find . -type f | wc -l) files)"
