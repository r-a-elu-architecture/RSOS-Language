"""RSOS under LangGraph: the model never sees a state value; the runtime computes; copies heal with 0 model calls."""
import importlib.util

import pytest

from rsoslang.adapters.langgraph import add_rsos, blind_prompt, rsos_nodes, run_without_langgraph, values_shown

# Sentinel values: if any reaches a prompt, the audit and the test both catch it.
START = {"svc.alpha.owner": "owner_bruno_7f3a", "svc.beta.owner": "owner_bruno_7f3a",
         "svc.gamma.owner": "owner_dana_91c2", "svc.alpha.timeout_ms": "7310", "svc.beta.retries": "4"}
REQUESTS = ["Everything owned by bruno now goes to chen (chen's id is owner_chen_55e1)",
            "Raise the alpha timeout by 200, at most 8000",
            "Set beta retries to beta retries plus... wait, just double them, at most 6"]


class Model:
    def __init__(self, replies):
        self.replies, self.prompts = list(replies), []

    def __call__(self, system, user):
        self.prompts.append(system + "\n" + user)
        return self.replies.pop(0)


PLAN = ("#0\nREHOST owner owner_bruno_7f3a owner_chen_55e1\n"
        "#1\nINHERIT svc.alpha.timeout_ms svc.alpha.timeout_ms +200 CAP 8000\n"
        "#2\nSCALE svc.beta.retries 2 CAP 6")


def test_blind_prompt_has_keys_not_values():
    p = blind_prompt(REQUESTS, START)
    assert all(k in p["user"] for k in START)
    assert values_shown(p, START, REQUESTS) == []
    for v in ("owner_dana_91c2", "7310"):
        assert v not in p["system"] + p["user"]


def test_full_run_exact_and_blind():
    m = Model([PLAN])
    out = run_without_langgraph({"state": dict(START), "requests": REQUESTS,
                                 "copies": {"worker": {**START, "svc.beta.retries": "5"}, "checker": dict(START)}}, m)
    assert out["state"] == {**START, "svc.alpha.owner": "owner_chen_55e1", "svc.beta.owner": "owner_chen_55e1",
                            "svc.alpha.timeout_ms": "7510", "svc.beta.retries": "6"}
    rep = out["rsos"]
    assert rep["model_calls"] == 1 and rep["values_shown"] == 0 and rep["failed"] == []
    assert out["copies"]["worker"] == out["copies"]["checker"] == out["state"]
    assert set(rep["healed"]["worker"]) >= {"svc.beta.retries"}
    for prompt in m.prompts:                       # the only values in any prompt are those the user wrote
        assert "owner_dana_91c2" not in prompt and "7310" not in prompt and "4" not in prompt.split("Requests:")[0]


def test_reask_sends_code_and_keys_not_values():
    bad = "#0\nREHOST owner owner_bruno_7f3a owner_chen_55e1\n#1\nINHERIT svc.alpha.timeout_ms svc.alpha.owner +200\n#2\nSCALE svc.beta.retries 2 CAP 6"
    m = Model([bad, "#0\nINHERIT svc.alpha.timeout_ms svc.alpha.timeout_ms +200 CAP 8000"])
    out = run_without_langgraph({"state": dict(START), "requests": REQUESTS}, m)
    rep = out["rsos"]
    assert rep["reasked"] == [1] and rep["failed"] == [] and rep["model_calls"] == 2 and rep["values_shown"] == 0
    assert "E_NOT_INTEGER" in m.prompts[1] and "owner_chen_55e1" not in m.prompts[1].split("#0")[0]
    assert out["state"]["svc.alpha.timeout_ms"] == "7510"


def test_failed_step_leaves_state_unchanged():
    m = Model(["#0\nSET svc.alpha.owner svc.missing.key", "#0\nSET svc.alpha.owner svc.missing.key"])
    out = run_without_langgraph({"state": dict(START), "requests": ["copy a key that does not exist"]}, m)
    assert out["state"] == START and out["rsos"]["failed"] == [{"step": 0, "code": "E_MISSING_KEY"}]


def test_custom_field_names_fit_an_existing_schema():
    m = Model([PLAN])
    out = run_without_langgraph({"config": dict(START), "changes": REQUESTS}, m,
                                state_field="config", requests_field="changes", report_field="audit")
    assert out["config"]["svc.beta.owner"] == "owner_chen_55e1" and out["audit"]["values_shown"] == 0


def test_strict_refuses_a_prompt_that_would_show_a_value():
    nodes = rsos_nodes(Model([PLAN]))
    state = {**START, "svc.keys.list": "svc.alpha.owner"}   # a value that is itself a key name is allowed
    nodes["rsos_plan"]({"state": state, "requests": REQUESTS})
    import rsoslang.adapters.langgraph as A
    orig = A.blind_prompt
    A.blind_prompt = lambda r, s: {"system": "", "user": "leak " + s["svc.gamma.owner"]}
    try:
        with pytest.raises(RuntimeError):
            rsos_nodes(Model([PLAN]))["rsos_plan"]({"state": dict(START), "requests": REQUESTS})
    finally:
        A.blind_prompt = orig


def test_add_rsos_wires_an_existing_graph():
    class G:
        def __init__(self):
            self.nodes, self.edges = {}, []

        def add_node(self, n, f):
            self.nodes[n] = f

        def add_edge(self, a, b):
            self.edges.append((a, b))
    g = G()
    names = add_rsos(g, Model([PLAN]), after="intake", before="respond")
    assert names == ["rsos_plan", "rsos_apply", "rsos_sync"]
    assert g.edges == [("rsos_plan", "rsos_apply"), ("rsos_apply", "rsos_sync"), ("intake", "rsos_plan"),
                       ("rsos_sync", "respond")]


@pytest.mark.skipif(importlib.util.find_spec("langgraph") is None, reason="langgraph not installed")
def test_real_langgraph():
    from typing import TypedDict
    from langgraph.graph import END, START as S, StateGraph

    class Flow(TypedDict, total=False):
        state: dict
        requests: list
        copies: dict
        rsos: dict
    g = StateGraph(Flow)
    add_rsos(g, Model([PLAN]))
    g.add_edge(S, "rsos_plan")
    g.add_edge("rsos_sync", END)
    out = g.compile().invoke({"state": dict(START), "requests": REQUESTS, "copies": {}})
    assert out["state"]["svc.alpha.timeout_ms"] == "7510" and out["rsos"]["values_shown"] == 0
