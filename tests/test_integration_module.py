"""
Unit tests for IntegrationModule.
"""

import pytest
from integration_module import IntegrationModule

def test_init():
    """Test IntegrationModule initializes."""
    i = IntegrationModule()
    assert hasattr(i, "clone_repo")

def test_list_branches_empty(tmp_path):
    """Test listing branches on empty repo path returns a list."""
    i = IntegrationModule()
    branches = i.list_branches(str(tmp_path))
    assert isinstance(branches, list)

def test_get_current_version_empty(tmp_path):
    """Test getting current version on empty repo path returns None or str."""
    i = IntegrationModule()
    version = i.get_current_version(str(tmp_path))
    assert version is None or isinstance(version, str)