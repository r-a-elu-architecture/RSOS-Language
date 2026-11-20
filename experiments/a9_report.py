"""Write experiments/A9_REPORT_DRAFT.md from results/a9.json (run a9_analyse.py first). Formatting only: every number
comes from a9.json; the verdicts are a9_analyse.py's, unchanged. 0 model calls."""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "results", "a9.json")))

NAMES = {"Q1_blind_exact": "Q1 Blind RSOS stays exact", "Q2a_B2_rises": "Q2a Law: JSON Patch errors rise along the plan",
         "Q2b_readers_flat": "Q2b Law: arms that read at run time stay flat",
         "Q3a_B2_worse_with_size": "Q3a JSON Patch worse with state size",
         "Q3b_blind_flat_with_size": "Q3b Blind arms flat with size",
         "Q4_blind_code_as_exact": "Q4 Mechanism is blindness (blind Python as exact as blind RSOS)",
         "Q5a_rsos_shorter_than_python": "Q5a RSOS more compact than Python",
         "Q5b_cheapest_per_correct_Z300": "Q5b RSOS cheapest per correct task at 300 keys",
         "Q6a_TC_calls_20x": "Q6a Tool-calling uses >= 20x the calls",
         "Q6b_TC_steps_beat_B2_Z300": "Q6b Tool-calling beats JSON Patch on steps",
         "Q6c_TC_input_grows_with_size": "Q6c Tool-calling input grows with size",
         "Q7_blind_at_least_TC_Z300": "Q7 Blind RSOS at least as exact as tool-calling"}


def verdict(v):
    return "**pass**" if v is True else "**fail**" if v is False else "not scorable (cells incomplete)"


L = ["# A9 report (draft, generated): the strongest rival patterns, three sizes, one law", "",
     f"Families: {', '.join(d['labels']) or 'none complete'}. Pre-registration: `PREREGISTRATION_A9.md`. "
     "Scored by `a9_analyse.py` (sealed) on complete cells only.", "", "## Verdicts", "",
     "| Prediction | Verdict |", "|---|---|"]
L += [f"| {NAMES.get(k, k)} | {verdict(v)} |" for k, v in d["verdicts"].items()]
L += ["", "## Cells", "", "| Family | Size | Arm | Tasks | Exact | Wrong steps | Failed steps | Calls/task | "
      "Input tok/task | Output tok/task | Complete |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for k, c in d["cells"].items():
    fam, cell, arm = k.split("|")
    L.append(f"| {fam} | {cell} | {arm} | {c['tasks']} | {c['exact']}/{c['tasks']} | {c['steps_wrong']} | "
             f"{c['steps_failed']} | {c['calls_per_task']:.1f} | {c['in_tok_per_task']:.0f} | "
             f"{c['out_tok_per_task']:.0f} | {'yes' if c['complete'] else 'no'} |")
L += ["", "## Wrong-step rate by quarter of the plan (complete cells, pooled)", "",
      "| Arm | Q1 | Q2 | Q3 | Q4 | MH odds ratio Q4 vs Q1 (95% CI) |", "|---|---|---|---|---|---|"]
for arm, q in d["quarters"].items():
    rates = " | ".join("—" if r is None else f"{100 * r:.2f}% ({w}/{n})"
                       for r, w, n in zip(q["rates"], q["wrong"], q["steps"]))
    m = q["mh_q4_vs_q1"]
    orr = "—" if m["or"] in (None, "None") else (f"{float(m['or']):.2f}" + (
        f" ({m['lo']:.2f}–{m['hi']:.2f})" if m.get("lo") not in (None, "None") else ""))
    L.append(f"| {arm} | {rates} | {orr} |")
L += ["", "Incomplete cells (reported, not scored): " + (", ".join(d["incomplete"]) or "none") + "."]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "A9_REPORT_DRAFT.md")
open(out, "w").write("\n".join(L) + "\n")
print("wrote", out)
