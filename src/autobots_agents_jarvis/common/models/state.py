# ABOUTME: Jarvis-specific state wrapper extending Dynagent with workspace params.

from typing import NotRequired

from autobots_devtools_shared_lib.dynagent.models.state import Dynagent


class JarvisState(Dynagent):
    """Jarvis state wrapper adding jira_number and repo_name for session context."""

    jira_number: NotRequired[str]  # pyright: ignore[reportInvalidTypeForm]
    repo_name: NotRequired[str]  # pyright: ignore[reportInvalidTypeForm]
