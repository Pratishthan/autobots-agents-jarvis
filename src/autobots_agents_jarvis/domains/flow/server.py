# ABOUTME: Flow-assistant Chainlit copilot entry point. Streams a flow-aware Dynagent
# ABOUTME: agent, tracks the active flow id from the host, and bridges canvas jumps.

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import chainlit as cl
from autobots_devtools_shared_lib.common.observability import (
    TraceMetadata,
    flush_tracing,
    get_logger,
    init_tracing,
    set_session_id,
)
from autobots_devtools_shared_lib.dynagent import create_base_agent
from autobots_devtools_shared_lib.dynagent.ui import stream_agent_events
from dotenv import load_dotenv

from autobots_agents_jarvis.common.services.context_setup import init_context_store
from autobots_agents_jarvis.common.utils.context_utils import init_context_key_resolver
from autobots_agents_jarvis.domains.flow.settings import init_flow_settings
from autobots_agents_jarvis.domains.flow.state import FlowState
from autobots_agents_jarvis.domains.flow.tools import register_flow_tools

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig

# Load environment variables from .env file
load_dotenv()

# Override the concierge-scoped value from .env: this server is the flow domain.
os.environ["DYNAGENT_CONFIG_ROOT_DIR"] = str(
    Path(__file__).resolve().parents[4] / "agent_configs" / "flow"
)

logger = get_logger(__file__)

# Application name for tracing and identification
APP_NAME = "flow"

# Register flow settings so shared-lib (dynagent) uses the same instance.
init_flow_settings()

# Initialise context key resolver and backing store at startup.
# init_context_store() uses InMemoryContextStore when JARVIS_DATABASE_URL is not set.
init_context_key_resolver()
init_context_store(app_name=APP_NAME)

# Registration must precede AgentMeta.instance() (called inside create_base_agent).
register_flow_tools()


def _get_user_identifier() -> str:
    """User ID for tracing and state; anonymous copilot access (no OAuth)."""
    return f"anonymous-{cl.context.session.thread_id}"[:200]


@cl.on_chat_start
async def start() -> None:
    """Initialize the copilot session with a flow-aware agent."""
    init_tracing()
    base_agent = create_base_agent(state_schema=FlowState)
    cl.user_session.set("base_agent", base_agent)

    user_id = _get_user_identifier()
    cl.user_session.set("user_id", user_id)

    trace_metadata = TraceMetadata.create(
        session_id=cl.context.session.thread_id,
        app_name=APP_NAME,
        user_id=user_id,
        tags=[APP_NAME],
    )
    set_session_id(cl.context.session.thread_id)
    cl.user_session.set("trace_metadata", trace_metadata)


@cl.on_window_message
async def on_window_message(message: str) -> None:
    """Receive `{"kind":"flow:switch","flowId":"…"}` from the host; store the flow id."""
    try:
        data = json.loads(message) if isinstance(message, str) else message
    except (ValueError, TypeError):
        return
    if isinstance(data, dict) and data.get("kind") == "flow:switch":
        cl.user_session.set("flow_id", data.get("flowId"))
        logger.info(f"Active flow set to {data.get('flowId')}")


@cl.action_callback("jump_to_node")
async def jump_to_node(action: cl.Action) -> None:
    """Chip clicked in the NodeChips element → tell the host to pan the canvas."""
    node_id = (action.payload or {}).get("id")
    if node_id:
        await cl.CopilotFunction(name="jumpToNode", args={"id": node_id}).acall()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Handle incoming messages from the user."""
    set_session_id(cl.context.session.thread_id)

    base_agent = cl.user_session.get("base_agent")
    if not base_agent:
        await cl.Message(content="Session not ready — please refresh.").send()
        return

    config: RunnableConfig = {
        "configurable": {
            "thread_id": cl.context.session.thread_id,
        },
        "recursion_limit": 50,
        "run_name": APP_NAME,  # Set trace name for Langfuse
    }

    input_state: dict[str, Any] = {
        "messages": [{"role": "user", "content": message.content}],
        "app_name": APP_NAME,
        "session_id": cl.context.session.thread_id,
        "flow_id": cl.user_session.get("flow_id"),
    }

    trace_metadata = cl.user_session.get("trace_metadata")

    result = await stream_agent_events(
        agent=base_agent,
        input_state=input_state,
        config=config,
        enable_tracing=True,
        trace_metadata=trace_metadata,
    )
    logger.debug(f"Agent execution completed with result: {result}")


@cl.on_stop
def on_stop() -> None:
    """Handle chat stop."""
    flush_tracing()
    logger.info("Chat session stopped")


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
