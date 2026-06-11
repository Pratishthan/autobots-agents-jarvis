# ABOUTME: Flow-assistant tools — read flow nodes server-side and render node-ref chips.
from __future__ import annotations

import chainlit as cl
from autobots_devtools_shared_lib.common.observability import get_logger, set_session_id
from autobots_devtools_shared_lib.dynagent import register_usecase_tools
from langchain.tools import ToolRuntime, tool

from autobots_agents_jarvis.domains.flow.services import get_flow_data
from autobots_agents_jarvis.domains.flow.state import FlowState  # noqa: TC001

logger = get_logger(__name__)

_NO_FLOW = "No flow is open yet — ask the user to open a flow on the canvas first."


def _flow_id(runtime: ToolRuntime[None, FlowState]) -> str | None:
    set_session_id(runtime.state.get("session_id", "default"))
    return runtime.state.get("flow_id")


@tool
def get_flow(runtime: ToolRuntime[None, FlowState]) -> str:
    """Summarize the currently open flow: its name and the count of each node type."""
    fid = _flow_id(runtime)
    if not fid:
        return _NO_FLOW
    flow = get_flow_data().get_flow(fid)
    if not flow:
        return f"Flow '{fid}' was not found."
    nodes = flow["nodes"]
    counts = {
        t: sum(1 for n in nodes if n["type"] == t)
        for t in ("system", "manual", "decision", "terminal")
    }
    return (
        f"'{flow['name']}' has {len(nodes)} steps — "
        f"{counts['system']} system, {counts['manual']} manual, "
        f"{counts['decision']} decision gates, {counts['terminal']} terminal."
    )


@tool
def list_nodes(runtime: ToolRuntime[None, FlowState], node_type: str = "") -> str:
    """List nodes in the open flow. Optionally filter by node_type:
    system | manual | decision | terminal. Returns 'id: title (type)' lines."""
    fid = _flow_id(runtime)
    if not fid:
        return _NO_FLOW
    nodes = get_flow_data().list_nodes(fid, node_type or None)
    if not nodes:
        return f"No nodes{f' of type {node_type}' if node_type else ''} in this flow."
    return "\n".join(f"{n['id']}: {n['title']} ({n['type']})" for n in nodes)


@tool
def get_node(runtime: ToolRuntime[None, FlowState], node_id: str) -> str:
    """Get full detail for one node by id: owner, team, SLA, description, inputs,
    outputs, and documents produced."""
    fid = _flow_id(runtime)
    if not fid:
        return _NO_FLOW
    n = get_flow_data().get_node(fid, node_id)
    if not n:
        return f"Node '{node_id}' was not found in this flow."
    docs = ", ".join(d["name"] for d in n["documents"]) or "—"
    team = f" · {n['team']}" if n["team"] else ""
    return (
        f"{n['title']} ({n['type']}). Owner: {n['owner'] or '—'}{team}. "
        f"SLA: {n['sla'] or '—'}.\n"
        f"{n['desc'] or ''}\nInputs: {', '.join(n['inputs']) or '—'}. "
        f"Outputs: {', '.join(n['outputs']) or '—'}. Documents: {docs}."
    )


@tool
async def show_node_references(runtime: ToolRuntime[None, FlowState], node_ids: list[str]) -> str:
    """Display clickable node-reference chips for the given node ids so the user can
    jump to them on the canvas. Call this AFTER answering, with the ids you referenced."""
    fid = _flow_id(runtime)
    if not fid:
        return _NO_FLOW
    fd = get_flow_data()
    refs = [
        {"id": n["id"], "title": n["title"], "type": n["type"], "term": n["term"]}
        for nid in node_ids
        if (n := fd.get_node(fid, nid)) is not None
    ]
    if not refs:
        return "No matching nodes to show."
    el = cl.CustomElement(name="NodeChips", props={"refs": refs})
    await cl.Message(content="", elements=[el]).send()
    return f"Showed {len(refs)} node chip(s)."


def register_flow_tools() -> None:
    """Register flow tools into the dynagent usecase pool. Call once at startup."""
    register_usecase_tools([get_flow, list_nodes, get_node, show_node_references])
