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

def test_clone_repo_failure(tmp_path):
    """Test clone_repo handles invalid URL gracefully."""
    i = IntegrationModule()
    repo = i.clone_repo("invalid_url", str(tmp_path / "fail"))
    assert repo is None

def test_create_branch_failure(tmp_path):
    """Test create_branch handles missing repo gracefully."""
    i = IntegrationModule()
    result = i.create_branch(str(tmp_path / "no_repo"), "feature/test")
    assert result is False

def test_commit_changes_failure(tmp_path):
    """Test commit_changes handles missing repo gracefully."""
    i = IntegrationModule()
    result = i.commit_changes(str(tmp_path / "no_repo"), "msg")
    assert result is False

def test_push_changes_failure(tmp_path):
    """Test push_changes handles missing repo gracefully."""
    i = IntegrationModule()
    result = i.push_changes(str(tmp_path / "no_repo"), "main")
    assert result is False

def test_create_pull_request_and_monitor():
    """Test create_pull_request and monitor_pr_status simulate expected flow."""
    i = IntegrationModule()
    pr_id = i.create_pull_request("https://example.com/repo.git", "feature", "title", "desc")
    assert isinstance(pr_id, int)
    status = i.monitor_pr_status("https://example.com/repo.git", pr_id)
    assert status in ("Pending Review", "Merged", "Needs Rebase")

def test_post_pr_monitor_and_rebase_needs_rebase(monkeypatch):
    """Test post_pr_monitor_and_rebase handles 'Needs Rebase' scenario."""
    i = IntegrationModule()
    monkeypatch.setattr(i, "monitor_pr_status", lambda repo_url, pr_id: "Needs Rebase")
    result = i.post_pr_monitor_and_rebase("https://example.com/repo.git", 1, "feature")
    assert "Rebased" in result or "PR status" in result

def test_handle_merge_conflict(capsys):
    """Test handle_merge_conflict outputs expected message."""
    i = IntegrationModule()
    i.handle_merge_conflict("/tmp/repo")
    captured = capsys.readouterr()
    assert "Merge conflict detected" in captured.out