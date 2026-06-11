# ABOUTME: Unit tests for flow-assistant read tools (TDD — red then green).
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from autobots_agents_jarvis.domains.flow import tools as flow_tools
from autobots_agents_jarvis.domains.flow.services import FlowData


@pytest.fixture(autouse=True)
def patch_flow_data(tmp_path, monkeypatch):
    flow = {
        "id": "feature",
        "name": "Feature Generation",
        "nodes": [
            {
                "id": "triage",
                "title": "Triage",
                "type": "manual",
                "term": None,
                "owner": "PM",
                "team": "Product",
                "sla": "Weekly",
                "desc": "Score impact.",
                "inputs": ["ticket"],
                "outputs": ["priority"],
                "steps": [],
                "documents": [],
            },
            {
                "id": "d_design",
                "title": "Design approved?",
                "type": "decision",
                "term": None,
                "owner": None,
                "team": None,
                "sla": None,
                "desc": None,
                "inputs": [],
                "outputs": [],
                "steps": [],
                "documents": [],
            },
        ],
    }
    (tmp_path / "feature.json").write_text(json.dumps(flow))
    monkeypatch.setattr(flow_tools, "get_flow_data", lambda: FlowData(tmp_path))


def _rt(flow_id="feature"):
    return SimpleNamespace(state={"flow_id": flow_id, "session_id": "s1"})


def test_get_node_formats_owner_and_sla():
    out = flow_tools.get_node.func(_rt(), "triage")
    assert "Triage" in out and "PM" in out and "Weekly" in out


def test_get_node_missing_is_graceful():
    out = flow_tools.get_node.func(_rt(), "ghost")
    assert "not found" in out.lower()


def test_list_nodes_by_type():
    out = flow_tools.list_nodes.func(_rt(), "manual")
    assert "triage" in out and "d_design" not in out


def test_tools_guard_missing_flow_id():
    out = flow_tools.get_node.func(_rt(flow_id=None), "triage")
    assert "no flow" in out.lower()
