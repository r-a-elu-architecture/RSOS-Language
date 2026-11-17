"""The MCP server lists and runs its tools (in-process)."""
import asyncio
import json

import pytest

mcp = pytest.importorskip("mcp.server.mcpserver")


def test_tools_listed_and_callable():
    from rsoslang.mcp_server import server

    async def go():
        tools = {t.name for t in await server.list_tools()}
        r = await server.call_tool("rsos_check", {"source": "LANGUAGE RSOS 0.2\nWORLD w\nOBJECT a\n"})
        return tools, r
    tools, r = asyncio.run(go())
    assert {"rsos_check", "rsos_compile", "rsos_session", "rsos_apply_gestures", "rsos_paint_graph"} <= tools
    text = r.content[0].text
    assert json.loads(text)["ok"] is True
