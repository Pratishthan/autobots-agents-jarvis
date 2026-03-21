# ABOUTME: Sanity tests for Dynagent canary - validates all Dynagent APIs via Concierge.

import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import pytest
import yaml
from langchain_core.messages import AIMessage

from autobots_agents_jarvis.domains.concierge.call_invoke_agent import (
    call_invoke_agent_async,
    call_invoke_agent_sync,
)
from autobots_agents_jarvis.domains.concierge.concierge_batch import concierge_batch
from autobots_agents_jarvis.domains.concierge.get_schema_for_agent import get_schema_for_agent
from tests.conftest import requires_google_api

# Pytest marker for sanity tests
pytestmark = [pytest.mark.sanity, requires_google_api]

CHAINLIT_PORT = 12338
FILE_SERVER_PORT = 19002
HEADLESS = True


@pytest.fixture(autouse=True)
def setup_concierge(concierge_registered):
    """Ensure Concierge tools are registered before each test."""
    pass


def _start_file_server(root_dir: str, port: int = FILE_SERVER_PORT) -> subprocess.Popen:
    """Start the Dynagent file server with FILE_SERVER_ROOT pointing to a temp dir."""
    env = os.environ.copy()
    env["FILE_SERVER_ROOT"] = root_dir
    env["FILE_SERVER_PORT"] = str(port)
    env["FILE_SERVER_HOST"] = "127.0.0.1"
    return subprocess.Popen(  # noqa: S603
        [
            sys.executable,
            "-m",
            "uvicorn",
            "autobots_devtools_shared_lib.common.servers.fileserver.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _wait_for_file_server(port: int, timeout: float = 15.0) -> bool:
    """Wait for the file server health endpoint to respond."""
    url = f"http://127.0.0.1:{port}/health"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:  # noqa: S310
                if resp.status == 200:
                    return True
        except (OSError, TimeoutError):
            time.sleep(0.5)
    return False


@pytest.fixture
def file_server(monkeypatch):
    """Start a file server backed by a temp directory; yield the root Path."""
    with tempfile.TemporaryDirectory(prefix="canary_fserver_") as tmpdir:
        # Point fserver_client_utils at our test server
        monkeypatch.setenv("FILE_SERVER_HOST", "127.0.0.1")
        monkeypatch.setenv("FILE_SERVER_PORT", str(FILE_SERVER_PORT))
        # Also patch the module-level constants so already-imported code picks them up
        import autobots_devtools_shared_lib.common.utils.fserver_client_utils as futils

        monkeypatch.setattr(futils, "FILE_SERVER_HOST", "127.0.0.1")
        monkeypatch.setattr(futils, "FILE_SERVER_PORT", str(FILE_SERVER_PORT))
        monkeypatch.setattr(
            futils,
            "FILE_SERVER_BASE_URL",
            f"http://127.0.0.1:{FILE_SERVER_PORT}",
        )

        proc = _start_file_server(tmpdir, port=FILE_SERVER_PORT)
        try:
            if not _wait_for_file_server(FILE_SERVER_PORT):
                _out, err = proc.communicate(timeout=2)
                err_msg = err.decode("utf-8", errors="replace") if err else ""
                pytest.fail(f"File server did not start in time. Stderr:\n{err_msg[:2000]}")
            yield Path(tmpdir)
        finally:
            proc.terminate()
            proc.wait(timeout=5)


# ---------------------------------------------------------------------------
# Invoke (sync)
# ---------------------------------------------------------------------------


def test_invoke_sync(concierge_registered):
    """Sanity: invoke_agent (sync) via call_invoke_agent_sync."""
    result = call_invoke_agent_sync(
        agent_name="joke_agent",
        user_message="Tell me a short joke",
        enable_tracing=False,
    )
    assert "messages" in result
    assert len(result["messages"]) > 1
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    assert len(ai_messages) > 0


# ---------------------------------------------------------------------------
# Invoke (async)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_invoke_async(concierge_registered):
    """Sanity: ainvoke_agent via call_invoke_agent_async."""
    result = await call_invoke_agent_async(
        agent_name="joke_agent",
        user_message="Tell me a short joke",
        enable_tracing=False,
    )
    assert "messages" in result
    assert len(result["messages"]) > 1
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    assert len(ai_messages) > 0


# ---------------------------------------------------------------------------
# Batch
# ---------------------------------------------------------------------------


def test_batch(concierge_registered):
    """Sanity: batch_invoker via concierge_batch."""
    result = concierge_batch("joke_agent", ["Tell me a joke"], user_id="test_user")
    assert result.total == 1
    assert len(result.results) == 1
    assert result.results[0].success
    assert result.results[0].output is not None
    assert len(result.results[0].output) > 0


# ---------------------------------------------------------------------------
# File upload (move_file_tool routing)
# ---------------------------------------------------------------------------


def test_upload_routes_to_move_file(concierge_registered, file_server):
    """Sanity: welcome_agent routes uploaded-file messages to move_file_tool."""
    # Seed the source file in the file server root so the move succeeds
    temp_dir = file_server / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    source_file = temp_dir / "abc12345_20260101_120000_TEST-1234-Upload.xlsx"
    source_file.write_bytes(b"fake-xlsx-content")

    upload_message = (
        "[Uploaded files:\n"
        "- TEST-1234-Upload.xlsx "
        "(Path: temp/abc12345_20260101_120000_TEST-1234-Upload.xlsx)]\n"
        "I uploaded a file."
    )
    result = call_invoke_agent_sync(
        agent_name="welcome_agent",
        user_message=upload_message,
        enable_tracing=False,
    )
    assert "messages" in result
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    assert len(ai_messages) > 0
    # The agent should attempt to call move_file_tool
    tool_calls_found = [
        tc
        for msg in ai_messages
        if hasattr(msg, "tool_calls")
        for tc in (msg.tool_calls or [])
        if tc.get("name") == "move_file_tool"
    ]
    assert len(tool_calls_found) > 0, (
        "Expected welcome_agent to call move_file_tool for uploaded file message"
    )


# ---------------------------------------------------------------------------
# Get schema
# ---------------------------------------------------------------------------


def test_get_schema(concierge_registered):
    """Sanity: get_schema_for_agent (AgentMeta.schema_map)."""
    schema = get_schema_for_agent("joke_agent")
    assert isinstance(schema, str)
    assert len(schema) > 0
    assert not schema.startswith("Error:")


# ---------------------------------------------------------------------------
# UI (Playwright + predefined script)
# ---------------------------------------------------------------------------


def _start_chainlit_no_auth(concierge_dir: Path, port: int = 1337) -> subprocess.Popen:
    """Start Chainlit with OAuth disabled for sanity test."""
    env = os.environ.copy()
    env["OAUTH_GITHUB_CLIENT_ID"] = ""
    env["OAUTH_GITHUB_CLIENT_SECRET"] = ""
    env["CHAINLIT_AUTH_SECRET"] = ""
    env["DYNAGENT_CONFIG_ROOT_DIR"] = str(concierge_dir / "agent_configs" / "concierge")
    env["JARVIS_DATABASE_URL"] = env.get("JARVIS_DATABASE_URL", "sqlite:///:memory:")
    app_path = (
        concierge_dir / "src" / "autobots_agents_jarvis" / "domains" / "concierge" / "server.py"
    )
    return subprocess.Popen(  # noqa: S603
        [
            sys.executable,
            "-m",
            "chainlit",
            "run",
            str(app_path),
            "--port",
            str(port),
            "--host",
            "127.0.0.1",
            "--headless",
        ],
        env=env,
        cwd=str(concierge_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _wait_for_chainlit(port: int, timeout: float = 45.0) -> bool:
    """Wait for Chainlit to be ready."""
    url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:  # noqa: S310
                if resp.status in (200, 302):
                    return True
        except (OSError, TimeoutError):
            time.sleep(0.5)
    return False


def test_ui_chat_script(concierge_registered):
    """Sanity: stream_agent_events via Chainlit UI + Playwright + predefined script."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip(
            "playwright not installed; run: pip install playwright && playwright install chromium"
        )

    concierge_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    script_path = Path(__file__).resolve().parent / "fixtures" / "chat_script.yaml"
    with script_path.open() as f:
        script = yaml.safe_load(f)
    messages = script.get("messages", [])

    proc = _start_chainlit_no_auth(concierge_dir, port=CHAINLIT_PORT)
    try:
        if not _wait_for_chainlit(CHAINLIT_PORT):
            _out, err = proc.communicate(timeout=2)
            err_msg = err.decode("utf-8", errors="replace") if err else ""
            pytest.fail(f"Chainlit did not become ready in time. Stderr:\n{err_msg[:2000]}")

        with sync_playwright() as p:
            # Force Chromium headless - unset PWDEBUG so VS Code debug doesn't open headed browser
            pwdebug = os.environ.pop("PWDEBUG", None)
            try:
                browser = p.chromium.launch(headless=HEADLESS)
            finally:
                if pwdebug is not None:
                    os.environ["PWDEBUG"] = pwdebug
            try:
                page = browser.new_page()
                page.set_default_timeout(45000)
                # "networkidle" times out with Chainlit's persistent WebSocket/SSE; use "load".
                page.goto(f"http://127.0.0.1:{CHAINLIT_PORT}", wait_until="load")
                page.wait_for_load_state("domcontentloaded")
                # Wait for the chat input to be visible before interacting.
                page.wait_for_selector('[role="textbox"], textarea', timeout=15000)

                for item in messages:
                    user_msg = item.get("user", "")
                    assert_contains = item.get("assert_contains", [])
                    if not user_msg:
                        continue

                    textbox = page.locator('[role="textbox"], textarea').first
                    textbox.wait_for(state="visible", timeout=15000)
                    textbox.fill(user_msg)
                    textbox.press("Enter")

                    page.wait_for_timeout(5000)
                    if assert_contains:
                        # inner_text returns rendered text (apostrophes as literals, not HTML entities).
                        content = page.inner_text("body").lower()
                        for substr in assert_contains:
                            assert substr.lower() in content, (
                                f"Expected '{substr}' in response for message '{user_msg}'"
                            )
            finally:
                browser.close()
    finally:
        proc.terminate()
        proc.wait(timeout=5)
