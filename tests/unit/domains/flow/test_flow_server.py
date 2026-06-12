# ABOUTME: Unit tests for the flow copilot server's host bridge (active-flow pull).
from __future__ import annotations

import pytest

from autobots_agents_jarvis.domains.flow import server


class _FakeCopilotFunction:
    """Stand-in for cl.CopilotFunction that returns a canned value (or raises)."""

    last_name: str | None = None
    _result: object = None
    _raise: bool = False

    def __init__(self, name: str, args: dict | None = None) -> None:
        type(self).last_name = name
        self.name = name
        self.args = args or {}

    async def acall(self):
        if type(self)._raise:
            raise RuntimeError("no host connected")
        return type(self)._result


@pytest.fixture
def fake_copilot(monkeypatch):
    _FakeCopilotFunction.last_name = None
    _FakeCopilotFunction._result = None
    _FakeCopilotFunction._raise = False
    monkeypatch.setattr(server.cl, "CopilotFunction", _FakeCopilotFunction)
    return _FakeCopilotFunction


async def test_pulls_flow_id_from_host(fake_copilot):
    fake_copilot._result = "feature"
    assert await server._get_active_flow_id() == "feature"
    assert fake_copilot.last_name == "getActiveFlow"


async def test_empty_host_response_is_none(fake_copilot):
    fake_copilot._result = ""
    assert await server._get_active_flow_id() is None


async def test_no_host_response_is_none(fake_copilot):
    fake_copilot._result = None
    assert await server._get_active_flow_id() is None


async def test_host_error_is_swallowed(fake_copilot):
    fake_copilot._raise = True
    assert await server._get_active_flow_id() is None
