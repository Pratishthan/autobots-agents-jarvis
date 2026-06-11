# ABOUTME: Tests for the Mermaid+YAML -> normalized flow JSON build script.

from __future__ import annotations

from scripts.build_flow_data import _norm_docs, build_flow, parse_mermaid

MMD = """flowchart LR
  fr_intake(["Feature Request"]):::start
  triage[/"Triage & Prioritize"/]:::manual
  d_design{"Design approved?"}:::decision
  data_ingest["Data Ingestion"]:::system
  failed(["Rejected"]):::declined
  fr_intake --> triage
  triage --> d_design
"""

CARDS = {
    "flow": {"id": "feature", "name": "Feature Generation"},
    "cards": {
        "triage": {
            "owner": "PM",
            "team": "Product",
            "sla": "Weekly",
            "desc": "Score impact.",
            "inputs": ["ticket"],
            "outputs": ["priority"],
            "steps": ["score"],
            "documents": ["Brief"],
        },
    },
}


def test_norm_docs_dict_form_aliases():
    # straight-through: name/format/status keys map directly
    assert _norm_docs([{"name": "Spec", "format": "PDF", "status": "Draft"}]) == [
        {"name": "Spec", "format": "PDF", "status": "Draft"}
    ]
    # alias path: title→name, type→format; status absent → None
    assert _norm_docs([{"title": "Charter", "type": "DOC"}]) == [
        {"name": "Charter", "format": "DOC", "status": None}
    ]
    # dict with neither name nor title is dropped
    assert _norm_docs([{"foo": "bar"}]) == []
    # non-list input is dropped
    assert _norm_docs(None) == []


def test_parse_mermaid_node_types_and_terms():
    nodes = parse_mermaid(MMD)
    by_id = {n["id"]: n for n in nodes}
    assert by_id["fr_intake"] == {
        "id": "fr_intake",
        "title": "Feature Request",
        "type": "terminal",
        "term": "start",
    }
    assert by_id["triage"]["type"] == "manual" and by_id["triage"]["term"] is None
    assert by_id["d_design"]["type"] == "decision"
    assert by_id["data_ingest"]["type"] == "system"
    assert by_id["failed"]["term"] == "declined"


def test_build_flow_merges_cards_and_normalizes_docs():
    flow = build_flow("feature", MMD, CARDS)
    assert flow["id"] == "feature"
    assert flow["name"] == "Feature Generation"
    triage = next(n for n in flow["nodes"] if n["id"] == "triage")
    assert triage["owner"] == "PM"
    assert triage["documents"] == [{"name": "Brief", "format": None, "status": None}]
    # node with no card entry still present with empty fields
    intake = next(n for n in flow["nodes"] if n["id"] == "fr_intake")
    assert intake["owner"] is None and intake["inputs"] == []
