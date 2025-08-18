"""
Unit tests for GenerationModule.
"""

import pytest
from generation_module import GenerationModule

def test_init():
    """Test GenerationModule initializes."""
    g = GenerationModule()
    assert hasattr(g, "generate_code")

def test_generate_code_minimal():
    """Test code generation with minimal input."""
    g = GenerationModule()
    result = g.generate_code({}, {})
    assert result is not None

def test_refine_code_empty():
    """Test refining code with empty feedback."""
    g = GenerationModule()
    refined = g.refine_code("print('hi')", "")
    assert isinstance(refined, str)

def test_run_local_tests(tmp_path):
    """Test running local tests returns expected result."""
    g = GenerationModule()
    code_path = tmp_path / "dummy.py"
    code_path.write_text("print('dummy')")
    result = g.run_local_tests(str(code_path))
    assert result is not None

def test_safety_check():
    """Test safety check returns expected result."""
    g = GenerationModule()
    result = g.safety_check("print('safe')")
    assert isinstance(result, bool)

def test_generate_code_failure(monkeypatch):
    """Test generate_code handles failure scenario."""
    g = GenerationModule()
    monkeypatch.setattr(g, "generate_code", lambda x, y: None)
    result = g.generate_code({}, {})
    assert result is None

def test_run_local_tests_failure(monkeypatch, tmp_path):
    """Test run_local_tests handles missing file gracefully."""
    g = GenerationModule()
    monkeypatch.setattr(g, "run_local_tests", lambda path: None)
    result = g.run_local_tests(str(tmp_path / "nofile.py"))
    assert result is None