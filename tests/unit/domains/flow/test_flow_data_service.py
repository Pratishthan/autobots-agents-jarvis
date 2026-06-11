# ABOUTME: Unit tests for FlowData service — read-only accessor over generated flow JSON.

from __future__ import annotations

import json

import pytest

from autobots_agents_jarvis.domains.flow.services import FlowData


@pytest.fixture
def flow_dir(tmp_path):
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
                "desc": "d",
                "inputs": [],
                "outputs": [],
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
    return tmp_path


def test_get_flow_returns_record(flow_dir):
    fd = FlowData(flow_dir)
    assert fd.get_flow("feature")["name"] == "Feature Generation"


def test_get_flow_unknown_returns_none(flow_dir):
    assert FlowData(flow_dir).get_flow("nope") is None


def test_get_node_hit_and_miss(flow_dir):
    fd = FlowData(flow_dir)
    assert fd.get_node("feature", "triage")["owner"] == "PM"
    assert fd.get_node("feature", "ghost") is None


def test_list_nodes_filters_by_type(flow_dir):
    fd = FlowData(flow_dir)
    assert [n["id"] for n in fd.list_nodes("feature", "manual")] == ["triage"]
    assert len(fd.list_nodes("feature")) == 2
    assert fd.list_nodes("feature", "system") == []
