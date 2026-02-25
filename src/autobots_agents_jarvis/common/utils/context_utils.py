# ABOUTME: Jarvis context key resolution for UI (Chainlit).
# ABOUTME: Registers a resolver that uses user_name from agent state so context store lookups align with the logged-in user.

from __future__ import annotations

from autobots_devtools_shared_lib.common.utils.context_utils import set_context_key_resolver


def init_context_key_resolver() -> None:
    """Register a context_key_resolver that uses user_name from agent state.

    Call once at UI startup (e.g. in each domain server.py before create_base_agent)
    so that resolve_context_key(state) returns the current user, and context store
    get/set/update use the same key (e.g. for workspace context and session persistence).
    """
    set_context_key_resolver(lambda state: state.get("user_name") or "default")
