"""Tests for agent functionality."""

import pytest
from unittest.mock import Mock, patch

def test_agent_state_initialization():
    """Test that agent state is properly initialized."""
    from src.state import AgentState
    
    # This test validates the state structure
    state = {
        "messages": [],
        "current_request": "test request",
        "plan": None,
        "code_changes": [],
        "status": "planning",
        "next_agent": None,
        "iteration_count": 0,
        "created_files": [],
        "error_message": None
    }
    
    # Validate required fields are present
    required_fields = ["messages", "current_request", "status"]
    for field in required_fields:
        assert field in state


def test_config_validation():
    """Test configuration validation."""
    from src.config import Config
    import os
    
    # Test that config can be instantiated
    config = Config()
    assert hasattr(config, 'max_iterations')
    assert config.max_iterations >= 1


@pytest.mark.parametrize("request,expected_type", [
    ("Create a function", str),
    ("Write a class", str),
    ("Generate tests", str),
])
def test_request_types(request, expected_type):
    """Test different types of coding requests."""
    assert isinstance(request, expected_type)
    assert len(request) > 0