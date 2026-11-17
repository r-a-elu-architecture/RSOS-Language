"""MCP server for the RSOS Language: lets Claude or any MCP-capable assistant read, write and run RSOS programs.

Run:  python -m rsoslang.mcp_server        (stdio transport)

Tools
  rsos_statements      the language: every statement with its signature and an example
  rsos_check           compile a program; errors and warnings (including the Spine's governance)
  rsos_compile         compile a program to its JSON IR (with its SHA-256)
  rsos_session         a person's practice session: RSX program + the cue framework's timeline summary
  rsos_paint_workflow  the 12-module support agent as a painting, with measured metrics
  rsos_apply_gestures  apply gestures (RSOS statements) to the support agent; measured before/after on held-out tickets
  rsos_paint_graph     paint an external agent graph (LangGraph-style JSON) and turn gestures into graph edits
"""

import json

from mcp.server.mcpserver import MCPServer

from . import compile_source
from .grammar import STATEMENTS, signature

server = MCPServer(name="rsos-language", version="0.2.0",
                   instructions="RSOS Language: write programs as scenes (place, pierce, enter, colour, connect). "
                                "Use rsos_statements to learn the language, rsos_check before running anything, and "
                                "rsos_apply_gestures to measure an effect. Person-facing programs need CONSENT.")
_DATA = {}


def _tickets():
    if "A" not in _DATA:
        from .agents.tickets import make_tickets
        _DATA["A"] = make_tickets(500, 2, typo_rate=0.3, unseen_rate=0.3)
    return _DATA["A"]


@server.tool(description="List every RSOS statement with its register links, signature and an example.")
def rsos_statements() -> str:
    return json.dumps({s.kw: {"family": s.family, "signature": signature(s), "example": s.doc}
                       for s in STATEMENTS.values()}, ensure_ascii=False)


@server.tool(description="Compile an RSOS program and report errors and warnings (governance included).")
def rsos_check(source: str) -> str:
    res = compile_source(source)
    return json.dumps({"ok": res.ok, "diagnostics": [d.to_dict() for d in res.diagnostics],
                       "operations": len(res.ir["ops"])}, ensure_ascii=False)


@server.tool(description="Compile an RSOS program to its JSON intermediate representation.")
def rsos_compile(source: str) -> str:
    res = compile_source(source)
    return json.dumps({"ok": res.ok, "sha256": res.digest(), "ir": res.ir}, ensure_ascii=False, default=str)


@server.tool(description="Compile a program with a person host into a practice session (RSX + timeline summary).")
def rsos_session(source: str) -> str:
    from .mind.session import compile_session
    res = compile_source(source)
    if not res.ok:
        return json.dumps({"ok": False, "errors": [str(d) for d in res.errors]})
    s = compile_session(res.ir)
    return json.dumps({"ok": True, "rsx": s["rsx"], "steps": len(s["steps"]), "skipped": s["skipped"],
                       "timeline_events": len(s["timeline"]["events"]),
                       "duration_s": s["timeline"].get("duration_ms", 0) / 1000, "footer": s["footer"]},
                      ensure_ascii=False)


@server.tool(description="The 12-module support agent as a painting, with metrics measured on held-out tickets.")
def rsos_paint_workflow() -> str:
    from .agents.workflow import build
    from .painting.scene import encode
    wf = build()
    return json.dumps(encode(wf, wf.evaluate(_tickets(), 2)), ensure_ascii=False)


@server.tool(description="Apply gestures (RSOS statements such as 'PIERCE spell_corrector THROUGH classify.brain') "
                         "to the support agent and measure the effect on 500 held-out tickets.")
def rsos_apply_gestures(gestures: str) -> str:
    from .agents.workflow import build
    from .painting.scene import apply
    base = build()
    try:
        wf, changes = apply(base, gestures if gestures.endswith("\n") else gestures + "\n")
    except ValueError as e:
        return json.dumps({"ok": False, "error": str(e)})
    keys = ("accuracy", "crashed", "cost_per_ticket", "score")
    b, a = base.evaluate(_tickets(), 2), wf.evaluate(_tickets(), 2)
    return json.dumps({"ok": True, "changes": changes, "before": {k: b[k] for k in keys},
                       "after": {k: a[k] for k in keys}})


@server.tool(description="Paint an external agent graph (LangGraph-style JSON: nodes with id, edges with source/target) "
                         "and optionally turn gestures [[op, guest, node, place], ...] into graph edits.")
def rsos_paint_graph(graph_json: str, gestures_json: str = "[]") -> str:
    from .painting.graphs import read_graph, patch
    scene = read_graph(json.loads(graph_json))
    edits = patch(scene, [tuple(g) for g in json.loads(gestures_json)])
    return json.dumps({"scene": scene, "edits": edits})


def main():
    server.run("stdio")


if __name__ == "__main__":
    main()
