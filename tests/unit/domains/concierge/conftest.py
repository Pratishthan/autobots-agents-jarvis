# ABOUTME: Pytest fixtures for Concierge domain unit tests.

import pytest
from tests.helpers import concierge_tools_registered


@pytest.fixture
def concierge_registered():
    """Register Concierge tools; reset after test."""
    yield from concierge_tools_registered()
