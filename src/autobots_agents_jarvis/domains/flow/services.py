# ABOUTME: Loads generated flow JSON and answers node lookups for the flow tools.

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


class FlowData:
    """Read-only accessor over data/flows/<id>.json files."""

    def __init__(self, base_dir: Path | str) -> None:
        self._base = Path(base_dir)

    def get_flow(self, flow_id: str) -> dict[str, Any] | None:
        path = self._base / f"{flow_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def get_node(self, flow_id: str, node_id: str) -> dict[str, Any] | None:
        flow = self.get_flow(flow_id)
        if not flow:
            return None
        return next((n for n in flow["nodes"] if n["id"] == node_id), None)

    def list_nodes(self, flow_id: str, node_type: str | None = None) -> list[dict[str, Any]]:
        flow = self.get_flow(flow_id)
        if not flow:
            return []
        nodes = flow["nodes"]
        if node_type:
            nodes = [n for n in nodes if n["type"] == node_type]
        return nodes


@lru_cache(maxsize=1)
def get_flow_data() -> FlowData:
    """Singleton FlowData rooted at the configured flow_data_dir (repo-relative)."""
    from autobots_agents_jarvis.domains.flow.settings import get_flow_settings

    base = Path(get_flow_settings().flow_data_dir)
    if not base.is_absolute():
        base = Path(__file__).resolve().parents[4] / base  # repo root / data/flows
    return FlowData(base)
