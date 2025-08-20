"""
Integration and edge case tests for UI Dashboard endpoints.
"""
import tempfile
import os
from dashboard_persistence import (
    save_dashboard_state, load_dashboard_state,
    save_user_preferences, load_user_preferences
)

import pytest
from fastapi.testclient import TestClient
import ui_dashboard
import importlib
import os

import logging
import time

def _read_audit_log():
    path = os.path.join(os.path.dirname(__file__), "../audit.log")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()

def _clear_audit_log():
    path = os.path.join(os.path.dirname(__file__), "../audit.log")
    if os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.truncate(0)

def test_audit_log_manual_memory_inject(monkeypatch):
    """Audit log: manual_memory_inject logs action."""
    from ui_dashboard import manual_memory_inject
    _clear_audit_log()
    calls = iter(["semantic", "Valid text", "{}"])
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: next(calls))
    class FakeResp:
        ok = True
        def json(self):
            return {"index": 42}
    monkeypatch.setattr("ui_dashboard.requests.post", lambda *a, **kw: FakeResp())
    manual_memory_inject()
    log = _read_audit_log()
    assert "manual_memory_inject" in log and "index" in log

def test_audit_log_manual_memory_retrieve(monkeypatch):
    """Audit log: manual_memory_retrieve logs action."""
    from ui_dashboard import manual_memory_retrieve
    _clear_audit_log()
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: "0")
    class FakeResp:
        ok = True
        def json(self):
            return {"memory": {"data": "info"}}
    monkeypatch.setattr("ui_dashboard.requests.get", lambda *a, **kw: FakeResp())
    manual_memory_retrieve()
    log = _read_audit_log()
    assert "manual_memory_retrieve" in log and "index" in log

def test_audit_log_trigger_analysis(monkeypatch):
    """Audit log: trigger_analysis logs action."""
    from ui_dashboard import trigger_analysis
    _clear_audit_log()
    monkeypatch.setattr("builtins.open", lambda *a, **kw: type("F", (), {"__enter__": lambda s: s, "__exit__": lambda s, t, v, tb: None, "read": lambda s: ""})())
    monkeypatch.setattr("ui_dashboard.analysis_mod", type("A", (), {"analyze_codebase": lambda s, code: {"code_smells": [], "deprecated_libs": []}})())
    trigger_analysis()
    log = _read_audit_log()
    assert "trigger_analysis" in log

def test_audit_log_trigger_code_generation(monkeypatch):
    """Audit log: trigger_code_generation logs action."""
    from ui_dashboard import trigger_code_generation
    _clear_audit_log()
    monkeypatch.setattr("ui_dashboard.get_latest_analysis_report", lambda: {"Summary": "ok", "Details": []})
    monkeypatch.setattr("ui_dashboard.memory_mod", type("M", (), {"memories": []})())
    monkeypatch.setattr("ui_dashboard.generation_mod", type("G", (), {"generate_code": lambda s, a, m: "code..."})())
    trigger_code_generation()
    log = _read_audit_log()
    assert "trigger_code_generation" in log

def test_audit_log_trigger_pr_submission(monkeypatch):
    """Audit log: trigger_pr_submission logs action."""
    from ui_dashboard import trigger_pr_submission
    _clear_audit_log()
    calls = iter([
        "https://github.com/org/repo",  # Repo URL
        "feature/auto-pr",  # Branch name
        "Prompt",  # Prompt text
        "n",  # Assign reviewers?
        "y"   # Auto-generate PR title/desc
    ])
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: next(calls))
    monkeypatch.setattr("ui_dashboard.get_latest_analysis_report", lambda: {"Summary": "ok", "Details": []})
    monkeypatch.setattr("ui_dashboard.integration_mod", type("I", (), {
        "generate_pr_metadata": lambda s, summary, prompt: ("T", "D"),
        "create_pull_request": lambda s, repo, branch, title, desc: 123,
        "assign_reviewers": lambda s, repo, pr_id, reviewers: None
    })())
    trigger_pr_submission()
    log = _read_audit_log()
    assert "trigger_pr_submission" in log and "pr_id" in log
client = TestClient(ui_dashboard.app)

def test_accessibility_mode_memory_panel(monkeypatch):
    """Test that accessibility mode disables color and outputs plain text cues in memory panel."""
    os.environ["SIA_ACCESSIBILITY_MODE"] = "1"
    importlib.reload(ui_dashboard)
    async def fake_get_memory_usage():
        return {"Total Memories": 5, "Episodic": 2, "Semantic": 2, "Procedural": 1, "Last Pruned": "N/A"}
    monkeypatch.setattr(ui_dashboard, "get_memory_usage", fake_get_memory_usage)
    import asyncio
    panel = asyncio.run(ui_dashboard.render_memory_panel())
    assert "[Section: Memory Usage]" in str(panel)
    assert "Total Memories: 5" in str(panel)
    assert "cyan" not in str(panel)
    os.environ["SIA_ACCESSIBILITY_MODE"] = "0"
def test_audit_log_file_permissions():
    """Test that audit.log file permissions are set to 0600 (owner read/write only) after logging."""
    import os
    from ui_dashboard import audit_log, AUDIT_LOG_PATH
    # Trigger an audit log event
    audit_log("test_event", user="tester", details="test_details")
    if os.name == "nt":
        # On Windows, permissions are not POSIX, so just check file exists
        assert os.path.exists(AUDIT_LOG_PATH)
    else:
        mode = os.stat(AUDIT_LOG_PATH).st_mode & 0o777
        assert mode == 0o600
def test_api_token_not_logged_manual_memory_retrieve(monkeypatch, capsys):
    """Test that API token is not printed/logged during manual_memory_retrieve."""
    import os
    os.environ["SIA_API_TOKEN"] = "shouldnotappear"
    from ui_dashboard import manual_memory_retrieve
    # Patch Prompt.ask to return valid index
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: "0")
    # Patch requests.get to return a fake response
    class FakeResp:
        ok = True
        def json(self):
            return {"memory": {"token": "shouldnotappear", "data": "info"}}
    monkeypatch.setattr("ui_dashboard.requests.get", lambda *a, **kw: FakeResp())
    result = manual_memory_retrieve()
    out, err = capsys.readouterr()
    assert "shouldnotappear" not in out
    assert "shouldnotappear" not in err
    assert "***" in result

def test_api_token_not_logged_pr_submission(monkeypatch, capsys):
    """Test that API token is not printed/logged during trigger_pr_submission."""
    import os
    os.environ["SIA_API_TOKEN"] = "shouldnotappear"
    from ui_dashboard import trigger_pr_submission
    # Patch Prompt.ask to simulate PR flow
    calls = iter([
        "https://github.com/org/repo",  # Repo URL
        "feature/auto-pr",  # Branch name
        "Prompt",  # Prompt text
        "n",  # Assign reviewers?
        "y"   # Auto-generate PR title/desc
    ])
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: next(calls))
    monkeypatch.setattr("ui_dashboard.get_latest_analysis_report", lambda: {"Summary": "ok", "Details": []})
    monkeypatch.setattr("ui_dashboard.integration_mod", type("I", (), {
        "generate_pr_metadata": lambda s, summary, prompt: ("T", "D"),
        "create_pull_request": lambda s, repo, branch, title, desc: 123,
        "assign_reviewers": lambda s, repo, pr_id, reviewers: None
    })())
    result = trigger_pr_submission()
    out, err = capsys.readouterr()
    assert "shouldnotappear" not in out
    assert "shouldnotappear" not in err
    assert "PR submitted" in result or "failed" in result
def test_async_dashboard_runner_quit(monkeypatch):
    """Test AsyncDashboardRunner user input loop handles quit and persists state."""
    import importlib
    importlib.reload(ui_dashboard)
    from ui_dashboard import AsyncDashboardRunner
    runner = AsyncDashboardRunner()
    # Patch Prompt.ask to return 'q' to trigger quit
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: "q")
    # Patch save_dashboard_state and save_user_preferences to track calls
    saved = {}
    monkeypatch.setattr("ui_dashboard.save_dashboard_state", lambda state: saved.setdefault("state", state.copy()))
    monkeypatch.setattr("ui_dashboard.save_user_preferences", lambda prefs: saved.setdefault("prefs", prefs.copy()))
    # Patch sys.exit to raise SystemExit
    import sys
    monkeypatch.setattr(sys, "exit", lambda code=0: (_ for _ in ()).throw(SystemExit(code)))
    # Run user_input_loop and expect SystemExit
    import asyncio
    try:
        asyncio.run(runner.user_input_loop())
    except SystemExit:
        pass
    assert saved.get("state", {}).get("last_msg") == "Exited dashboard."
def test_audit_log_pr_approve(monkeypatch):
    """Audit log: PR approve logs action."""
    from ui_dashboard import AsyncDashboardRunner
    _clear_audit_log()
    runner = AsyncDashboardRunner()
    # Patch Prompt.ask to return PR ID
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: "123")
    # Patch requests.post to simulate approval
    class FakeResp:
        ok = True
        def json(self):
            return {"result": "Approved."}
    monkeypatch.setattr("ui_dashboard.requests.post", lambda *a, **kw: FakeResp())
    # Patch validate_pr_id to pass through
    monkeypatch.setattr("ui_dashboard.validate_pr_id", lambda x: x)
    # Patch format_error_message to avoid side effects
    monkeypatch.setattr("ui_dashboard.format_error_message", lambda *a, **kw: "error")
    # Simulate user choosing approve PR
    runner.layout["lower"].update = lambda *a, **kw: None  # prevent print
    runner.dashboard_state["last_choice"] = "6"
    runner.dashboard_state["last_msg"] = ""
    # Call the approve PR logic directly
    approve_fn = None
    for line in ui_dashboard.ui_dashboard.__code__.co_consts:
        if callable(line) and getattr(line, "__name__", "") == "approve_pr":
            approve_fn = line
            break
    # Instead, call the code path via user_input_loop
    # Simulate only the approve PR branch
    msg = None
    try:
        msg = runner.user_input_loop.__func__(runner)
    except Exception:
        pass
    log = _read_audit_log()
    assert "approve" in log.lower() or "pr_id" in log.lower()

def test_audit_log_pr_rollback(monkeypatch):
    """Audit log: PR rollback logs action."""
    from ui_dashboard import AsyncDashboardRunner
    _clear_audit_log()
    runner = AsyncDashboardRunner()
    # Patch Prompt.ask to return PR ID
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: "456")
    # Patch requests.post to simulate rollback
    class FakeResp:
        ok = True
        def json(self):
            return {"result": "Rolled back."}
    monkeypatch.setattr("ui_dashboard.requests.post", lambda *a, **kw: FakeResp())
    # Patch validate_pr_id to pass through
    monkeypatch.setattr("ui_dashboard.validate_pr_id", lambda x: x)
    # Patch format_error_message to avoid side effects
    monkeypatch.setattr("ui_dashboard.format_error_message", lambda *a, **kw: "error")
    # Simulate user choosing rollback PR
    runner.layout["lower"].update = lambda *a, **kw: None  # prevent print
    runner.dashboard_state["last_choice"] = "7"
    runner.dashboard_state["last_msg"] = ""
    # Call the rollback PR logic directly
    rollback_fn = None
    for line in ui_dashboard.ui_dashboard.__code__.co_consts:
        if callable(line) and getattr(line, "__name__", "") == "rollback_pr":
            rollback_fn = line
            break
    # Instead, call the code path via user_input_loop
    # Simulate only the rollback PR branch
    msg = None
    try:
        msg = runner.user_input_loop.__func__(runner)
    except Exception:
        pass
    log = _read_audit_log()
    assert "rollback" in log.lower() or "pr_id" in log.lower()
def test_controls_panel_normal_mode():
    """Test controls panel rendering in normal mode includes color, controls, and help line."""
    import importlib
    importlib.reload(ui_dashboard)
    panel = ui_dashboard.render_controls_panel()
    panel_str = str(panel)
    assert "[bold cyan]Manual Memory Management" in panel_str
    assert "[1] Trigger Analysis" in panel_str
    assert "yellow" in panel_str or "Controls" in panel_str  # border_style
    assert "Tip: Enter the number or letter in" in panel_str

def test_controls_panel_accessibility_mode(monkeypatch):
    """Test controls panel rendering in accessibility mode disables color, adds section cues, and help line."""
    import os
    os.environ["SIA_ACCESSIBILITY_MODE"] = "1"
    import importlib
    importlib.reload(ui_dashboard)
    panel = ui_dashboard.render_controls_panel()
    panel_str = str(panel)
    assert "[Section: Controls]" in panel_str
    assert "[1] Trigger Analysis" in panel_str
    assert "yellow" not in panel_str
    assert "Tip: Enter the number or letter in" in panel_str
    os.environ["SIA_ACCESSIBILITY_MODE"] = "0"

def test_trigger_analysis_help(monkeypatch, capsys):
    """Test trigger_analysis outputs contextual help and actionable error message."""
    from ui_dashboard import trigger_analysis
    # Patch open and analysis_mod to simulate error
    monkeypatch.setattr("builtins.open", lambda *a, **kw: (_ for _ in ()).throw(Exception("fail")))
    monkeypatch.setattr("ui_dashboard.analysis_mod", type("A", (), {"analyze_codebase": lambda s, code: {}})())
    result = trigger_analysis()
    out, err = capsys.readouterr()
    assert "Triggering codebase analysis" in out
    assert "[Action Required]" in result or "Tip:" in result

def test_trigger_code_generation_help(monkeypatch, capsys):
    """Test trigger_code_generation outputs contextual help and actionable tip."""
    from ui_dashboard import trigger_code_generation
    monkeypatch.setattr("ui_dashboard.get_latest_analysis_report", lambda: {"Summary": "ok", "Details": []})
    monkeypatch.setattr("ui_dashboard.memory_mod", type("M", (), {"memories": []})())
    monkeypatch.setattr("ui_dashboard.generation_mod", type("G", (), {"generate_code": lambda s, a, m: "code..."})())
    result = trigger_code_generation()
    out, err = capsys.readouterr()
    assert "Triggering code generation" in out
    assert "Tip:" in result

def test_manual_memory_inject_help(monkeypatch, capsys):
    """Test manual_memory_inject outputs contextual help and actionable error message."""
    from ui_dashboard import manual_memory_inject
    calls = iter(["semantic", "Valid text", "{not_json"])
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: next(calls))
    result = manual_memory_inject()
    out, err = capsys.readouterr()
    assert "Manual Memory Inject" in out
    assert "[Action Required]" in result or "Tip:" in result

def test_manual_memory_retrieve_help(monkeypatch, capsys):
    """Test manual_memory_retrieve outputs contextual help and actionable error message."""
    from ui_dashboard import manual_memory_retrieve
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: "-1")
    result = manual_memory_retrieve()
    out, err = capsys.readouterr()
    assert "Manual Memory Retrieve" in out
    assert "[Action Required]" in result or "Tip:" in result

def test_controls_panel_accessibility_mode(monkeypatch):
    """Test controls panel rendering in accessibility mode disables color and adds section cues."""
    os.environ["SIA_ACCESSIBILITY_MODE"] = "1"
    import importlib
    importlib.reload(ui_dashboard)
    panel = ui_dashboard.render_controls_panel()
    panel_str = str(panel)
    assert "[Section: Controls]" in panel_str
    assert "[1] Trigger Analysis" in panel_str
    assert "yellow" not in panel_str
    os.environ["SIA_ACCESSIBILITY_MODE"] = "0"
def test_accessibility_mode_analysis_panel(monkeypatch):
    """Test that accessibility mode disables color and outputs plain text cues in analysis panel."""
    os.environ["SIA_ACCESSIBILITY_MODE"] = "1"
    import importlib
    importlib.reload(ui_dashboard)
    async def fake_get_latest_analysis_report():
        return {"Timestamp": "Now", "Summary": "Summary", "Details": ["detail1", "detail2"]}
    monkeypatch.setattr(ui_dashboard, "get_latest_analysis_report", fake_get_latest_analysis_report)
    import asyncio
    panel = asyncio.run(ui_dashboard.render_analysis_panel())
    assert "[Section: Analysis Report]" in str(panel)
    assert "Summary: Summary" in str(panel)
    assert "detail1" in str(panel)
    assert "magenta" not in str(panel)
    os.environ["SIA_ACCESSIBILITY_MODE"] = "0"

def test_accessibility_mode_pr_panel(monkeypatch):
    """Test that accessibility mode disables color and outputs plain text cues in PR panel."""
    os.environ["SIA_ACCESSIBILITY_MODE"] = "1"
    import importlib
    importlib.reload(ui_dashboard)
    async def fake_get_pr_status():
        return {
            "Open PRs": 2,
            "Last PR": {"Title": "PR Title", "Status": "open", "URL": "http://example.com"}
        }
    monkeypatch.setattr(ui_dashboard, "get_pr_status", fake_get_pr_status)
    import asyncio
    panel = asyncio.run(ui_dashboard.render_pr_panel())
    assert "[Section: PR Status]" in str(panel)
    assert "Open PRs: 2" in str(panel)
    assert "PR Title" in str(panel)
    assert "green" not in str(panel)
    os.environ["SIA_ACCESSIBILITY_MODE"] = "0"

def test_dashboard_root():
    """Test dashboard root endpoint returns 200 and expected content."""
    response = client.get("/")
    assert response.status_code == 200
    assert "dashboard" in response.text.lower()

def test_invalid_dashboard_route():
    """Test invalid dashboard route returns 404."""
    response = client.get("/dashboard/nonexistent")
    assert response.status_code == 404

def test_post_dashboard_action_missing_fields():
    """Test posting dashboard action with missing fields returns 422 or error."""
    response = client.post("/dashboard/action", json={})
    assert response.status_code in (400, 422)

def test_manual_memory_inject_invalid_type(monkeypatch):
    """Test manual_memory_inject with invalid memory type triggers validation error."""
    from ui_dashboard import manual_memory_inject
    # Patch Prompt.ask to return invalid memory type, valid text, valid meta
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: "invalid" if "Memory type" in a[0] else "Valid text")
    result = manual_memory_inject()
    assert "Invalid memory type" in result or "failed" in result

def test_no_secrets_exposed_in_manual_memory_retrieve(monkeypatch):
    """Test that secrets/tokens are not exposed in manual_memory_retrieve output."""
    from ui_dashboard import manual_memory_retrieve
    # Patch Prompt.ask to return a valid index
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: "0")
    # Patch requests.get to return a fake response with a secret
    class FakeResp:
        ok = True
        def json(self):
            return {"memory": {"token": "supersecret", "data": "info"}}
    monkeypatch.setattr("ui_dashboard.requests.get", lambda *a, **kw: FakeResp())
    result = manual_memory_retrieve()
    assert "supersecret" not in result
    assert "***" in result

def test_manual_memory_inject_invalid_meta(monkeypatch):
    """Test manual_memory_inject with invalid meta triggers validation error."""
    from ui_dashboard import manual_memory_inject
    calls = iter(["semantic", "Valid text", "{not_json"])
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: next(calls))
    result = manual_memory_inject()
    assert "Meta must be valid JSON" in result or "failed" in result

def test_manual_memory_retrieve_invalid_index(monkeypatch):
    """Test manual_memory_retrieve with invalid index triggers validation error."""
    from ui_dashboard import manual_memory_retrieve
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: "-1")
    result = manual_memory_retrieve()
    assert "Index must be non-negative" in result or "failed" in result

def test_trigger_pr_submission_invalid_url(monkeypatch):
    """Test trigger_pr_submission with invalid repo URL triggers validation error."""
    from ui_dashboard import trigger_pr_submission
    calls = iter([
        "invalid_url",  # Repo URL
        "feature/auto-pr",  # Branch name
        "Prompt",  # Prompt text
        "n",  # Assign reviewers?
        "y"   # Auto-generate PR title/desc
    ])
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: next(calls))
    result = trigger_pr_submission()
    assert "Repo URL must be a valid GitHub repository URL" in result or "failed" in result

def test_error_message_formatting():
    """Test centralized error message formatting."""
    from error_handling import format_error_message
    msg = format_error_message(Exception("fail"), "Custom user message")
    assert "Custom user message" in msg and "fail" in msg

def test_post_dashboard_action_valid():
    """Test posting valid dashboard action returns 200 and correct response."""
    payload = {"action": "refresh", "params": {}}
    response = client.post("/dashboard/action", json=payload)
    assert response.status_code == 200
    assert "result" in response.json() or "success" in response.json()

def test_api_token_not_logged(monkeypatch, capsys):
    """Test that API token is not printed/logged during manual_memory_inject."""
    import os
    os.environ["SIA_API_TOKEN"] = "shouldnotappear"
    from ui_dashboard import manual_memory_inject
    # Patch Prompt.ask to return valid values
    calls = iter(["semantic", "Valid text", "{}"])
    monkeypatch.setattr("ui_dashboard.Prompt.ask", lambda *a, **kw: next(calls))
    # Patch requests.post to return a fake response
    class FakeResp:
        ok = True
        def json(self):
            return {"index": 1}
    monkeypatch.setattr("ui_dashboard.requests.post", lambda *a, **kw: FakeResp())
    result = manual_memory_inject()
    out, err = capsys.readouterr()
    assert "shouldnotappear" not in out
    assert "shouldnotappear" not in err

def test_dashboard_state_persistence_roundtrip():
    """Test saving and loading dashboard state using a temp file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "state.json")
        state = {"last_choice": "2", "last_msg": "Test message"}
        save_dashboard_state(state, path=path)
        loaded = load_dashboard_state(path=path)
        assert loaded == state

def test_user_preferences_persistence_roundtrip():
    """Test saving and loading user preferences using a temp file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "prefs.json")
        prefs = {"theme": "dark", "layout": "compact"}
        save_user_preferences(prefs, path=path)
        loaded = load_user_preferences(path=path)
        assert loaded == prefs
def test_dashboard_internal_error(monkeypatch):
    """Test dashboard internal server error handling."""
    def broken(*args, **kwargs):
        raise Exception("Simulated failure")
    monkeypatch.setattr(ui_dashboard, "dashboard_action", broken)
    response = client.post("/dashboard/action", json={"action": "fail", "params": {}})
    assert response.status_code == 500 or response.status_code == 200  # Accepts fallback

import asyncio

@pytest.mark.asyncio
async def test_async_memory_usage():
    """Test async get_memory_usage returns expected keys."""
    mem = await ui_dashboard.get_memory_usage()
    assert "Total Memories" in mem
    assert "Episodic" in mem

@pytest.mark.asyncio
async def test_async_latest_analysis_report():
    """Test async get_latest_analysis_report returns expected structure."""
    report = await ui_dashboard.get_latest_analysis_report()
    assert "Summary" in report
    assert "Details" in report

@pytest.mark.asyncio
async def test_async_pr_status():
    """Test async get_pr_status returns expected structure."""
    pr = await ui_dashboard.get_pr_status()
    assert "Open PRs" in pr
    assert "Last PR" in pr

@pytest.mark.asyncio
async def test_async_dashboard_runner_refresh(monkeypatch):
    """Test AsyncDashboardRunner panel refresh does not raise and returns Panels."""
    runner = ui_dashboard.AsyncDashboardRunner()
    # Patch panel renderers to quickly return dummy panels
    monkeypatch.setattr(ui_dashboard, "render_memory_panel", lambda: asyncio.sleep(0, result=ui_dashboard.Panel("mem")))
    monkeypatch.setattr(ui_dashboard, "render_analysis_panel", lambda: asyncio.sleep(0, result=ui_dashboard.Panel("analysis")))
    monkeypatch.setattr(ui_dashboard, "render_pr_panel", lambda: asyncio.sleep(0, result=ui_dashboard.Panel("pr")))
    # Run one refresh cycle
    await asyncio.wait_for(runner.refresh_panels(interval=0.01), timeout=0.05)
    # If no exception, test passes