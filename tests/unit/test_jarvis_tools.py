# ABOUTME: Unit tests for Jarvis tools.

from unittest.mock import MagicMock

import pytest
from autobots_devtools_shared_lib.dynagent.models.state import Dynagent
from langchain.tools import ToolRuntime

from autobots_agents_jarvis.agents.jarvis_tools import (
    get_forecast,
    get_joke_categories,
    tell_joke,
)


@pytest.fixture
def mock_runtime() -> ToolRuntime:
    """Create a mock runtime for testing tools."""
    runtime = MagicMock(spec=ToolRuntime)
    runtime.state = Dynagent(session_id="test-session")
    return runtime


def test_tell_joke_valid_category(mock_runtime):
    """Test tell_joke with a valid category."""
    result = tell_joke(mock_runtime, "programming")
    assert isinstance(result, str)
    assert "Category: programming" in result
    assert "Rating:" in result


def test_tell_joke_invalid_category(mock_runtime):
    """Test tell_joke with an invalid category returns error."""
    result = tell_joke(mock_runtime, "invalid")
    assert isinstance(result, str)
    assert "Invalid category" in result


def test_get_joke_categories():
    """Test get_joke_categories returns formatted string."""
    result = get_joke_categories()
    assert isinstance(result, str)
    assert "Available joke categories:" in result
    assert "programming" in result
    assert "dad-joke" in result


def test_get_forecast_valid_location(mock_runtime):
    """Test get_forecast with valid location."""
    result = get_forecast(mock_runtime, "San Francisco", days=3)
    assert isinstance(result, str)
    assert "San Francisco" in result
    assert "Day 1:" in result
    assert "Day 2:" in result
    assert "Day 3:" in result


def test_get_forecast_invalid_location(mock_runtime):
    """Test get_forecast with invalid location returns error."""
    result = get_forecast(mock_runtime, "InvalidCity", days=3)
    assert isinstance(result, str)
    assert "Weather data not available" in result
