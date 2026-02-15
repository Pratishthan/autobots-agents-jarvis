# ABOUTME: Shared test fixture helpers importable by domain-level conftest.py files.

from collections.abc import Generator


def concierge_tools_registered() -> Generator[None, None, None]:
    """Register Concierge tools for testing; reset after use.

    Usage in conftest.py:
        from tests.helpers import concierge_tools_registered

        @pytest.fixture
        def concierge_registered():
            yield from concierge_tools_registered()
    """
    from autobots_devtools_shared_lib.dynagent import AgentMeta
    from autobots_devtools_shared_lib.dynagent.tools.tool_registry import (
        _reset_usecase_tools,
    )

    from autobots_agents_jarvis.domains.concierge.tools import register_concierge_tools

    _reset_usecase_tools()
    AgentMeta.reset()
    register_concierge_tools()
    yield
    _reset_usecase_tools()
    AgentMeta.reset()
