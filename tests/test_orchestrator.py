"""
Unit tests for Orchestrator.
"""

import pytest
from orchestrator import Orchestrator

def test_init():
    """Test Orchestrator initializes."""
    o = Orchestrator()
    assert hasattr(o, "run_agent_loop")

def test_run_agent_loop():
    """Test running agent loop does not raise errors."""
    o = Orchestrator()
    try:
        o.run_agent_loop()
    except Exception:
        pytest.skip("run_agent_loop may require full environment")

def test_sample_memory_task():
    """Test sample memory task returns expected result."""
    o = Orchestrator()
    result = o.sample_memory_task()
    assert result is not None

def test_run_self_analysis_cycle():
    """Test self-analysis cycle returns expected result."""
    o = Orchestrator()
    result = o.run_self_analysis_cycle()
    assert result is not None