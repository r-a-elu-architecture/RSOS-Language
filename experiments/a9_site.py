"""Print the A9 results block for docs/results.html from results/a9.json (formatting only; verdicts are
a9_analyse.py's). python experiments/a9_site.py [a9.json] > block.html"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "results", "a9.json")))
NAMES = {"Q1_blind_exact": "RSOS blind stays exact", "Q2a_B2_rises": "Law: JSON Patch errors rise along the plan",
         "Q2b_readers_flat": "Law: arms that read at run time stay flat",
         "Q3a_B2_worse_with_size": "JSON Patch worse with state size",
         "Q3b_blind_flat_with_size": "Blind arms flat with size",
         "Q4_blind_code_as_exact": "Blind Python as exact as blind RSOS (the principle, not the syntax)",
         "Q5a_rsos_shorter_than_python": "RSOS output shorter than Python",
         "Q5b_cheapest_per_correct_Z300": "RSOS cheapest per correct task at 300 keys",
         "Q6a_TC_calls_20x": "Tool-calling needs at least 20× the calls",
         "Q6b_TC_steps_beat_B2_Z300": "Tool-calling beats JSON Patch on steps",
         "Q6c_TC_input_grows_with_size": "Tool-calling input grows with size",
         "Q7_blind_at_least_TC_Z300": "RSOS blind at least as exact as tool-calling"}
ARM = {"B2": "One-call JSON Patch", "X5b": "RSOS blind", "CAv": "Python, sees state", "CAb": "Python, blind",
       "TC": "Tool-calling agent"}
tot = {}
for k, c in d["cells"].items():
    fam, cell, arm = k.split("|")
    if c["complete"]:
        t = tot.setdefault(arm, [0, 0, 0.0, 0.0])
        t[0] += c["exact"]; t[1] += c["tasks"]; t[2] += c["calls_per_task"] * c["tasks"]
        t[3] += (c["in_tok_per_task"] + c["out_tok_per_task"]) * c["tasks"]
v = d["verdicts"]
npass = sum(1 for x in v.values() if x is True)
nfail = sum(1 for x in v.values() if x is False)
o = ['<h2>A9: The strongest rival patterns, predicted by one law</h2>',
     f'<p>Families: {", ".join(d["labels"])}. Tasks from drand round 6657746, drawn after the predictions were public. '
     f'{npass} of {len(v)} predictions held, {nfail} failed'
     + (f', {len(v) - npass - nfail} not scorable' if len(v) - npass - nfail else '') + '. '
     '<a href="https://github.com/r-a-elu-architecture/RSOS-Language/blob/main/experiments/A9_REPORT.md">Report</a> · '
     '<a href="https://github.com/r-a-elu-architecture/RSOS-Language/blob/main/experiments/PREREGISTRATION_A9.md">'
     'Pre-registration</a></p>',
     '<table><thead><tr><th>Arm (complete cells, pooled)</th><th>Tasks exact</th><th>Calls per task</th>'
     '<th>Tokens per task</th></tr></thead><tbody>']
for a in ("X5b", "CAb", "CAv", "TC", "B2"):
    if a in tot:
        e, n, c, t = tot[a]
        o.append(f'<tr><td>{ARM[a]}</td><td>{e}/{n}</td><td>{c / n:.1f}</td><td>{t / n:,.0f}</td></tr>')
o.append('</tbody></table>')
o.append('<figure><img src="a9_quarters.svg" alt="Wrong-step rate by quarter of the plan, per arm" '
         'style="max-width:100%"><figcaption>Wrong-step rate by quarter of the plan (complete cells, pooled). '
         'Lines at zero overlap.</figcaption></figure>')
o.append('<table><thead><tr><th>Prediction</th><th>Verdict</th></tr></thead><tbody>')
for k, x in v.items():
    o.append(f'<tr><td>{NAMES.get(k, k)}</td><td>{"held" if x is True else "failed" if x is False else "not scorable"}'
             '</td></tr>')
o.append('</tbody></table>')
print("\n".join(o))
