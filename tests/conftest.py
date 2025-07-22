"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def sample_request():
    """Sample coding request for testing."""
    return "Create a Python function to calculate factorial"


@pytest.fixture
def agent_state():
    """Sample agent state for testing."""
    return {
        "messages": [],
        "current_request": "Create a test function",
        "plan": None,
        "code_changes": [],
        "status": "planning",
        "next_agent": None,
        "iteration_count": 0,
        "created_files": [],
        "error_message": None
    }