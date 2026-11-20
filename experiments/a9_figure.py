"""A9 figure: wrong-step rate by quarter of the plan, one line per arm (from results/a9.json). Formatting only.
Writes docs/a9_quarters.svg (standard library, no plotting package).

    python experiments/a9_figure.py [path/to/a9.json] [out.svg]
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "results", "a9.json")
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "docs", "a9_quarters.svg")
d = json.load(open(src))

ARMS = [("B2", "One-call JSON Patch", "#c2410c", ""), ("TC", "Tool-calling agent", "#7c3aed", "6 3"),
        ("CAv", "Python, sees state", "#0369a1", "2 3"), ("CAb", "Python, blind", "#0f766e", "8 3 2 3"),
        ("X5b", "RSOS blind", "#15803d", "")]
W, H, L, R, T, B = 640, 340, 56, 190, 24, 44
rates = {a: d["quarters"][a]["rates"] for a, *_ in ARMS if a in d["quarters"]}
vals = [r for rs in rates.values() for r in rs if r is not None]
top = max(0.01, max(vals) if vals else 0.01) * 1.15


def x(i):
    return L + i * (W - L - R) / 3


def y(v):
    return T + (H - T - B) * (1 - v / top)


s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" font-family="system-ui,sans-serif" '
     f'font-size="12"><title>A9: wrong-step rate by quarter of the plan, per arm</title>']
for k in range(5):
    v = top * k / 4
    s.append(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#d4d4d4" stroke-width="0.5"/>'
             f'<text x="{L - 6}" y="{y(v) + 4:.1f}" text-anchor="end" fill="#525252">{100 * v:.1f}%</text>')
for i, q in enumerate(("Steps 1–14", "15–28", "29–42", "43–56")):
    s.append(f'<text x="{x(i):.1f}" y="{H - B + 18}" text-anchor="middle" fill="#525252">{q}</text>')
s.append(f'<text x="{(L + W - R) / 2:.1f}" y="{H - 6}" text-anchor="middle" fill="#525252">Quarter of the plan</text>')
ly = T + 6
for a, name, col, dash in ARMS:
    if a not in rates:
        continue
    pts = [(x(i), y(v)) for i, v in enumerate(rates[a]) if v is not None]
    if not pts:
        continue
    s.append(f'<polyline fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}" points="' +
             " ".join(f"{px:.1f},{py:.1f}" for px, py in pts) + '"/>')
    s += [f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{col}"/>' for px, py in pts]
    s.append(f'<line x1="{W - R + 16}" x2="{W - R + 40}" y1="{ly}" y2="{ly}" stroke="{col}" stroke-width="2" '
             f'stroke-dasharray="{dash}"/><text x="{W - R + 46}" y="{ly + 4}" fill="#262626">{name}</text>')
    ly += 22
s.append("</svg>")
open(out, "w").write("\n".join(s))
print("wrote", out)
