"""
Unit tests for AnalysisModule.
"""

import pytest
from analysis_module import AnalysisModule

def test_init():
    """Test AnalysisModule initializes."""
    a = AnalysisModule()
    assert hasattr(a, "list_tools")

def test_list_tools():
    """Test listing tools returns a list."""
    a = AnalysisModule()
    tools = a.list_tools()
    assert isinstance(tools, list)

def test_evaluate_tool_invalid():
    """Test evaluating an invalid tool returns expected result."""
    a = AnalysisModule()
    result = a.evaluate_tool("nonexistent")
    assert result is not None

def test_analyze_codebase_empty():
    """Test analyzing empty codebase returns expected result."""
    a = AnalysisModule()
    result = a.analyze_codebase("")
    assert isinstance(result, dict)

def test_generate_report_json():
    """Test report generation in JSON format."""
    a = AnalysisModule()
    report = a.generate_report({"result": 1}, format="json")
    assert isinstance(report, str)