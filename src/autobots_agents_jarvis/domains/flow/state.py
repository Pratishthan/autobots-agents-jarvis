# ABOUTME: Flow domain state — extends Dynagent with the active flow id.

from __future__ import annotations

from typing import NotRequired

from autobots_devtools_shared_lib.dynagent.models.state import Dynagent


class FlowState(Dynagent):
    """Flow-assistant state: tracks the flow the user is currently viewing."""

    flow_id: NotRequired[str]  # pyright: ignore[reportInvalidTypeForm]
