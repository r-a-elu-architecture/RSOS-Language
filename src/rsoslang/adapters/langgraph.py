"""RSOS under LangGraph: the model names operations, the runtime owns every value, every copy is hash-checked.

Drop-in for an existing LangGraph graph. Three plain node functions (dict in, dict out) read and write fields of
YOUR state schema, so nothing in your graph has to change except three nodes and their edges:

    from rsoslang.adapters.langgraph import add_rsos

    add_rsos(graph, call_model, after="intake", before="respond")   # graph = your StateGraph(YourState)

    # YourState needs: state (dict), requests (list of str); optional: copies (dict of agent copies).
    # Field names are configurable: add_rsos(..., state_field="config", requests_field="changes").

call_model(system: str, user: str) -> str is any chat model. The adapter guarantees, and reports, that the prompt it
builds contains the state's KEYS and the requests only, never a state VALUE ("blind planning", measured in
RSOS-Language A5-A9: RSOS blind 48/48 exact in A9). If a step fails, the model is re-asked once for that step with the
error CODE and the key names only, so a failure message cannot leak a value either.

LangGraph is not imported by this module; the nodes work in any orchestrator that passes dicts.
"""
from __future__ import annotations

import re

from rsoslang.core.state import GRAMMAR, Ledger, parse_plan

KEY_IN_TEXT = re.compile(r"[A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)+")

SYSTEM = ("You translate change requests into RSOS operations. " + GRAMMAR +
          " For each request write '#<n>' on its own line, then its operations. No prose.")


def blind_prompt(requests: list, state: dict) -> dict:
    """The planner's prompt: key names and requests only."""
    keys = ", ".join(sorted(state))
    reqs = "\n".join(f"#{i}\n{r}" for i, r in enumerate(requests))
    return {"system": SYSTEM, "user": f"Keys in the shared state: {keys}\n\nRequests:\n{reqs}"}


def values_shown(prompt: dict, state: dict, requests: list) -> list:
    """State values that appear in the prompt but not in the requests or key names (the adapter's audit; expect [])."""
    text = prompt["system"] + "\n" + prompt["user"]
    allowed = "\n".join(map(str, requests)) + "\n" + "\n".join(state)
    return sorted({v for v in map(str, state.values())
                   if len(v) >= 3 and v in text and v not in allowed and v not in SYSTEM})


def _reask_prompt(request: str, code: str, keys: list, state: dict) -> dict:
    known = [k for k in keys if k in state]
    return {"system": SYSTEM,
            "user": (f"Keys in the shared state: {', '.join(sorted(state))}\n\n"
                     f"Your operations for this request were rejected ({code}; keys involved: "
                     f"{', '.join(known) or 'none'}). Write them again.\n\n#0\n{request}")}


def rsos_nodes(call_model, *, state_field="state", requests_field="requests", copies_field="copies",
               report_field="rsos", reask=True, strict=True):
    """Three LangGraph-compatible nodes: rsos_plan (1 model call), rsos_apply (0 calls + at most one re-ask per
    failed step), rsos_sync (0 calls). Returns {"rsos_plan": f, "rsos_apply": f, "rsos_sync": f}."""

    def rsos_plan(s: dict) -> dict:
        state, reqs = s[state_field], list(s[requests_field])
        p = blind_prompt(reqs, state)
        shown = values_shown(p, state, reqs)
        if strict and shown:
            raise RuntimeError(f"blind prompt would show {len(shown)} state value(s)")
        plan = parse_plan(call_model(p["system"], p["user"]))
        rep = dict(s.get(report_field) or {})
        rep.update({"plan": {str(k): v for k, v in plan.items()}, "model_calls": rep.get("model_calls", 0) + 1,
                    "values_shown": len(shown)})
        return {report_field: rep}

    def rsos_apply(s: dict) -> dict:
        rep = dict(s.get(report_field) or {})
        reqs = list(s[requests_field])
        led = Ledger(s[state_field])
        failed, reasked = [], []
        for step in sorted(int(k) for k in rep.get("plan", {})):
            ops = rep["plan"][str(step)]
            r = led.apply(ops)
            if not r["ok"] and reask and step < len(reqs):
                keys = KEY_IN_TEXT.findall(ops)
                p = _reask_prompt(reqs[step], r["code"], keys, led.state)
                rep["values_shown"] = rep.get("values_shown", 0) + len(values_shown(p, led.state, reqs))
                again = parse_plan(call_model(p["system"], p["user"])).get(0, "")
                rep["model_calls"] = rep.get("model_calls", 0) + 1
                reasked.append(step)
                r = led.apply(again)
            if not r["ok"]:
                failed.append({"step": step, "code": r["code"]})
        rep.update({"dot": led.dot, "failed": failed, "reasked": reasked})
        return {state_field: dict(led.state), report_field: rep}

    def rsos_sync(s: dict) -> dict:
        rep = dict(s.get(report_field) or {})
        copies = dict(s.get(copies_field) or {})
        led = Ledger(s[state_field])
        healed = {}
        for name, c in copies.items():
            r = led.sync(c)
            copies[name], healed[name] = r["state"], r["healed"]
        rep["healed"] = healed
        return {copies_field: copies, report_field: rep}

    return {"rsos_plan": rsos_plan, "rsos_apply": rsos_apply, "rsos_sync": rsos_sync}


def add_rsos(graph, call_model, *, after=None, before=None, **kw):
    """Add the three nodes to an existing StateGraph (or anything with add_node/add_edge) and chain them:
    after -> rsos_plan -> rsos_apply -> rsos_sync -> before. Returns the node names."""
    nodes = rsos_nodes(call_model, **kw)
    for name, fn in nodes.items():
        graph.add_node(name, fn)
    graph.add_edge("rsos_plan", "rsos_apply")
    graph.add_edge("rsos_apply", "rsos_sync")
    if after is not None:
        graph.add_edge(after, "rsos_plan")
    if before is not None:
        graph.add_edge("rsos_sync", before)
    return list(nodes)


def run_without_langgraph(s: dict, call_model, **kw) -> dict:
    """The same three nodes in order, for tests and for orchestrators other than LangGraph."""
    for fn in rsos_nodes(call_model, **kw).values():
        s = {**s, **fn(s)}
    return s
