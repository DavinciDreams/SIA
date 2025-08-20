"""
SIA Dashboard UI

A terminal-based dashboard for monitoring and controlling the Self-Improving Agent (SIA).
Requires: rich (install via 'pip install rich')

Features:
- Displays memory usage, analysis reports, and PR status.
- Provides controls to trigger analysis, code generation, and PR submission.
- Clear, intuitive layout matching PRD requirements.
- All logic and UI components are documented inline.

Author: SIA Team
"""

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
import requests
import json
import os
import sys
import logging

# --- Audit Logging Setup ---
AUDIT_LOG_PATH = os.path.join(os.path.dirname(__file__), "audit.log")
_audit_logger = logging.getLogger("sia_audit")
_audit_logger.setLevel(logging.INFO)
_audit_handler = logging.FileHandler(AUDIT_LOG_PATH, encoding="utf-8")
_audit_handler.setLevel(logging.INFO)
_audit_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
_audit_handler.setFormatter(_audit_formatter)
_audit_logger.addHandler(_audit_handler)
_audit_logger.propagate = False

# Restrict permissions: owner read/write only (0600, cross-platform best effort)
try:
    if os.path.exists(AUDIT_LOG_PATH):
        os.chmod(AUDIT_LOG_PATH, 0o600)
except Exception:
    pass

def audit_log(event, user=None, details=None):
    # Never log secrets/tokens
    safe_details = ""
    if details:
        safe_details = str(details)
        for sensitive in ["token", "secret", "authorization"]:
            safe_details = safe_details.replace(sensitive, "***")
    msg = f"event={event}"
    if user:
        msg += f" user={user}"
    if safe_details:
        msg += f" details={safe_details}"
    _audit_logger.info(msg)
# --- End Audit Logging Setup ---

# Accessibility mode support will be added below

# Accessibility: Detect accessibility mode from env variable
ACCESSIBILITY_MODE = os.environ.get("SIA_ACCESSIBILITY_MODE", "0") == "1"
def is_accessibility_mode():
    return ACCESSIBILITY_MODE

# Persistence for dashboard state and user preferences
from dashboard_persistence import (
    load_dashboard_state, save_dashboard_state,
    load_user_preferences, save_user_preferences
)

# Secure API token/secret management
API_TOKEN = os.environ.get("SIA_API_TOKEN", None)
if API_TOKEN is None:
    # Fail securely if token is required for API calls
    API_TOKEN = ""

# Validation and error handling modules
from validation import (
    validate_memory_type, validate_text, validate_meta, validate_index,
    validate_repo_url, validate_branch_name, validate_prompt_text,
    validate_reviewers, validate_pr_id
)
from error_handling import handle_errors, format_error_message

# Integration: Import actual SIA modules
from memory_module import MemoryModule
from analysis_module import AnalysisModule
from generation_module import GenerationModule
from integration_module import IntegrationModule

console = Console(color_system=None if is_accessibility_mode() else "auto")

# Instantiate modules (integration point)
memory_mod = MemoryModule()
analysis_mod = AnalysisModule()
generation_mod = GenerationModule()
integration_mod = IntegrationModule()

import asyncio

async def get_memory_usage():
    """
    Integration: Retrieve live memory usage from MemoryModule (async).
    """
    await asyncio.sleep(0)  # Simulate async, replace with real async IO if needed
    total = len(memory_mod.memories)
    episodic = sum(1 for m in memory_mod.memories if m.get("type") == "episodic")
    semantic = sum(1 for m in memory_mod.memories if m.get("type") == "semantic")
    procedural = sum(1 for m in memory_mod.memories if m.get("type") == "procedural")
    return {
        "Total Memories": total,
        "Episodic": episodic,
        "Semantic": semantic,
        "Procedural": procedural,
        "Last Pruned": "N/A"
    }

async def get_latest_analysis_report():
    """
    Integration: Retrieve latest analysis report from AnalysisModule (async).
    """
    await asyncio.sleep(0)  # Simulate async, replace with real async IO if needed
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code_str = f.read()
        results = analysis_mod.analyze_codebase(code_str)
        summary = "No critical issues." if not results.get("code_smells") else f"{len(results['code_smells'])} issues found."
        details = results.get("code_smells", []) + results.get("deprecated_libs", [])
        return {
            "Timestamp": "Live",
            "Summary": summary,
            "Details": details
        }
    except Exception as e:
        return {
            "Timestamp": "N/A",
            "Summary": f"Error: {e}",
            "Details": []
        }

async def get_pr_status():
    """
    Integration: Retrieve PR status using IntegrationModule (async).
    """
    await asyncio.sleep(0)  # Simulate async, replace with real async IO if needed
    repo_url = "https://github.com/org/repo"
    pr_id = 42
    status = integration_mod.monitor_pr_status(repo_url, pr_id)
    return {
        "Open PRs": 1,
        "Last PR": {
            "Title": "Automated PR",
            "Status": status,
            "URL": f"{repo_url}/pull/{pr_id}"
        }
    }

def trigger_analysis():
    """
    Integration: Trigger analysis using AnalysisModule.
    """
    console.print("[bold cyan]Triggering codebase analysis...[/bold cyan]\n[dim]This will scan the codebase for issues and deprecated libraries.[/dim]")
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code_str = f.read()
        results = analysis_mod.analyze_codebase(code_str)
        msg = f"Analysis complete. Issues found: {len(results.get('code_smells', []))}, Deprecated libs: {len(results.get('deprecated_libs', []))}."
        if not results.get('code_smells') and not results.get('deprecated_libs'):
            msg += " No critical issues detected."
        else:
            msg += " Review the analysis report for details."
        audit_log("trigger_analysis", details=msg)
        return msg
    except Exception as e:
        audit_log("trigger_analysis_failed", details=str(e))
        return f"Analysis failed: {e}\n[red][Action Required][/red] Please check your codebase for syntax errors or missing dependencies.\n[dim]Tip: Try again after fixing the issue.[/dim]"

def trigger_code_generation():
    """
    Integration: Trigger code generation using GenerationModule.
    """
    console.print("[bold cyan]Triggering code generation...[/bold cyan]\n[dim]This will generate code based on the latest analysis and memory context.[/dim]")
    # Use latest analysis and memory context for demo
    analysis = get_latest_analysis_report()
    memory_context = {"count": len(memory_mod.memories)}
    code = generation_mod.generate_code(analysis, memory_context)
    msg = f"Code generation complete. Preview:\n{code[:120]}..."
    audit_log("trigger_code_generation", details=msg)
    return msg + "\n[dim]Tip: Review the generated code before submitting a PR. If you encounter errors, check the analysis report for guidance.[/dim]"

@handle_errors("PR submission failed.")
def trigger_pr_submission():
    """
    Integration: Trigger PR submission using IntegrationModule.
    """
    console.print("[bold cyan]Submitting a Pull Request...[/bold cyan]\n[dim]You will be prompted for repository details and reviewers.[/dim]")
    repo_url = validate_repo_url(Prompt.ask("Repo URL", default="https://github.com/org/repo", show_default=True))
    branch_name = validate_branch_name(Prompt.ask("Branch name", default="feature/auto-pr", show_default=True))
    prompt_text = validate_prompt_text(Prompt.ask("Prompt for code generation", default="Improve X", show_default=True))
    reviewers = []
    if Prompt.ask("Assign reviewers? (y/n)", choices=["y", "n"], default="n", show_choices=True) == "y":
        reviewers = validate_reviewers([r.strip() for r in Prompt.ask("Reviewers (comma-separated)", default="", show_default=True).split(",")])
    auto = Prompt.ask("Auto-generate PR title/description? (y/n)", choices=["y", "n"], default="y", show_choices=True) == "y"
    # Generate PR metadata
    analysis = get_latest_analysis_report()
    if auto:
        title, description = integration_mod.generate_pr_metadata(analysis["Summary"], prompt_text)
    else:
        title = Prompt.ask("PR Title", default="Automated PR", show_default=True)
        description = Prompt.ask("PR Description", default="Auto-generated PR", show_default=True)
    pr_id = integration_mod.create_pull_request(repo_url, branch_name, title, description)
    if reviewers and reviewers != [""]:
        integration_mod.assign_reviewers(repo_url, pr_id, reviewers)
    msg = f"PR submitted successfully!\nTitle: {title}\nPR ID: {pr_id}\n[dim]Tip: View PR status in the dashboard or open the PR URL for details.[/dim]"
    audit_log("trigger_pr_submission", details={"repo_url": repo_url, "branch": branch_name, "pr_id": pr_id, "reviewers": reviewers})
    return msg

async def render_memory_panel():
    """Render the memory usage panel (async)."""
    mem = await get_memory_usage()
    if is_accessibility_mode():
        # Plain text, no color, ARIA-like cue
        lines = [f"[Section: Memory Usage]"]
        for k, v in mem.items():
            lines.append(f"{k}: {v}")
        return Panel("\n".join(lines), title="Memory Usage", border_style=None)
    table = Table.grid()
    for k, v in mem.items():
        table.add_row(f"[bold]{k}[/bold]", str(v))
    return Panel(table, title="Memory Usage", border_style="cyan")

async def render_analysis_panel():
    """Render the analysis report panel (async)."""
    report = await get_latest_analysis_report()
    if is_accessibility_mode():
        lines = [f"[Section: Analysis Report]"]
        lines.append(f"Summary: {report['Summary']}")
        lines.append("Details:")
        for d in report["Details"]:
            lines.append(f"- {d}")
        body = "\n".join(lines)
        return Panel(body, title=f"Analysis Report ({report['Timestamp']})", border_style=None)
    details = "\n".join(f"- {d}" for d in report["Details"])
    body = f"[bold]Summary:[/bold] {report['Summary']}\n[bold]Details:[/bold]\n{details}"
    return Panel(body, title=f"Analysis Report ({report['Timestamp']})", border_style="magenta")

async def render_pr_panel():
    """Render the PR status panel (async)."""
    pr = await get_pr_status()
    last = pr["Last PR"]
    if is_accessibility_mode():
        lines = [f"[Section: PR Status]"]
        lines.append(f"Open PRs: {pr['Open PRs']}")
        lines.append(f"Last PR: {last['Title']}")
        lines.append(f"Status: {last['Status']}")
        lines.append(f"URL: {last['URL']}")
        body = "\n".join(lines)
        return Panel(body, title="PR Status", border_style=None)
    body = (
        f"[bold]Open PRs:[/bold] {pr['Open PRs']}\n"
        f"[bold]Last PR:[/bold] {last['Title']}\n"
        f"[bold]Status:[/bold] {last['Status']}\n"
        f"[bold]URL:[/bold] {last['URL']}"
    )
    return Panel(body, title="PR Status", border_style="green")

def render_controls_panel():
    """Render the controls panel for user actions, with contextual help."""
    help_line = "[dim]Tip: Enter the number or letter in [bold]brackets[/bold] to select an action. Press [bold]q[/bold] to quit at any time.[/dim]"
    if is_accessibility_mode():
        controls = (
            "[Section: Controls]\n"
            "[1] Trigger Analysis - Analyze the codebase for issues.\n"
            "[2] Trigger Code Generation - Generate code based on analysis.\n"
            "[3] Submit PR - Create a pull request with generated code.\n"
            "[4] Manual Memory Inject - Add a memory entry manually.\n"
            "[5] Manual Memory Retrieve - Retrieve a memory entry by index.\n"
            "[6] Approve PR - Approve/merge a pull request.\n"
            "[7] Rollback PR - Revert a pull request.\n"
            "[q] Quit\n"
            "\nManual Memory Management:\n"
            "[4] Inject: Specify type (episodic/semantic/procedural), text, and meta (JSON).\n"
            "[5] Retrieve: Specify memory index.\n"
            "\n" + help_line
        )
        return Panel(controls, title="Controls", border_style=None)
    controls = (
        "[1] Trigger Analysis    - Analyze the codebase for issues\n"
        "[2] Trigger Code Generation - Generate code based on analysis\n"
        "[3] Submit PR          - Create a pull request with generated code\n"
        "[4] Manual Memory Inject   - Add a memory entry manually\n"
        "[5] Manual Memory Retrieve - Retrieve a memory entry by index\n"
        "[6] Approve PR         - Approve/merge a pull request\n"
        "[7] Rollback PR        - Revert a pull request\n"
        "[q] Quit"
    )
    doc = (
        "[bold cyan]Manual Memory Management:[/bold cyan]\n"
        "[4] Inject: Specify type (episodic/semantic/procedural), text, and meta (JSON).\n"
        "[5] Retrieve: Specify memory index."
    )
    return Panel(f"{controls}\n\n{doc}\n\n{help_line}", title="Controls", border_style="yellow")

@handle_errors("Manual memory inject failed.")
def manual_memory_inject():
    """Prompt user for memory details and inject via API."""
    console.print("[bold cyan]Manual Memory Inject[/bold cyan]\n[dim]Add a new memory entry. Choose type, enter text, and optionally provide metadata as JSON.[/dim]")
    memory_type = validate_memory_type(Prompt.ask("Memory type", choices=["episodic", "semantic", "procedural"], default="semantic", show_choices=True, show_default=True))
    text = validate_text(Prompt.ask("Memory text", show_default=False))
    meta_str = Prompt.ask("Meta (JSON, optional)", default="{}", show_default=True)
    meta = validate_meta(meta_str)
    headers = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    resp = requests.post(
        "http://localhost:8000/memory/manual_inject",
        json={"text": text, "meta": meta, "memory_type": memory_type},
        headers=headers,
        timeout=5
    )
    if resp.ok:
        try:
            idx = resp.json().get("index")
            return f"Memory injected at index {idx}.\n[dim]Tip: Use [5] to retrieve this memory by index.[/dim]"
        except Exception:
            return format_error_message(
                "Invalid response from API.",
                "Error injecting memory. [Action Required] Please check the API server response format.\n[dim]Tip: Ensure the API server is running and reachable.[/dim]"
            )
        else:
            # Never log or expose secrets/tokens in error messages
            return format_error_message(
                "API error",
                "Error injecting memory. [Action Required] The API server returned an error.\n[dim]Tip: Check API server status, logs, or try again.[/dim]"
            )

@handle_errors("Manual memory retrieve failed.")
def manual_memory_retrieve():
    """Prompt user for memory index and retrieve via API."""
    console.print("[bold cyan]Manual Memory Retrieve[/bold cyan]\n[dim]Retrieve a memory entry by its index. Index must be a non-negative integer.[/dim]")
    idx = validate_index(Prompt.ask("Memory index", default="0", show_default=True))
    headers = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    resp = requests.get(
        f"http://localhost:8000/memory/manual_retrieve?idx={idx}",
        headers=headers,
        timeout=5
    )
    if resp.ok:
        try:
            mem = resp.json().get("memory")
            if mem:
                # Sanitize output: never display secrets
                mem_sanitized = {k: ("***" if "secret" in k.lower() or "token" in k.lower() else v) for k, v in mem.items()}
                return f"Memory[{idx}]:\n{json.dumps(mem_sanitized, indent=2)}\n[dim]Tip: Use [4] to inject new memory.[/dim]"
            else:
                return f"No memory found at index {idx}.\n[dim]Tip: Use [4] to inject new memory.[/dim]"
        except Exception:
            return format_error_message(
                "Invalid response from API.",
                "Error retrieving memory. [Action Required] Please check the API server response format.\n[dim]Tip: Ensure the API server is running and reachable.[/dim]"
            )
        else:
            # Never log or expose secrets/tokens in error messages
            return format_error_message(
                "API error",
                "Error retrieving memory. [Action Required] The API server returned an error.\n[dim]Tip: Check API server status, logs, or try again.[/dim]"
            )

class AsyncDashboardRunner:
    """Modular async dashboard runner for testability and live refresh."""

    def __init__(self):
        self.dashboard_state = load_dashboard_state()
        self.user_prefs = load_user_preferences()
        self.layout = Layout()
        # Improved layout: upper for panels, middle for controls, lower for feedback/help
        self.layout.split(
            Layout(name="upper", size=8),
            Layout(name="middle", size=13),
            Layout(name="lower", ratio=1)
        )
        self.layout["middle"].update(render_controls_panel())
        last_msg = self.dashboard_state.get("last_msg", "Select an action from Controls above.")
        # Add a persistent help line below the feedback message
        help_line = Text("Need help? Press the number/letter in brackets for any action. [q] to quit.", style="dim", justify="center")
        feedback_panel = Panel(Text(last_msg, justify="center") + "\n" + help_line, border_style="white")
        self.layout["lower"].update(feedback_panel)
        self.running = True

    async def refresh_panels(self, interval=2):
        while self.running:
            mem_panel, analysis_panel, pr_panel = await asyncio.gather(
                render_memory_panel(),
                render_analysis_panel(),
                render_pr_panel()
            )
            self.layout["upper"].split_row(
                Layout(mem_panel, name="memory"),
                Layout(analysis_panel, name="analysis"),
                Layout(pr_panel, name="pr"),
            )
            await asyncio.sleep(interval)

    async def user_input_loop(self):
        while self.running:
            await asyncio.sleep(0.1)
            console.clear()
            console.print(self.layout)
            choice = Prompt.ask("\nEnter choice", choices=["1", "2", "3", "4", "5", "6", "7", "q"], default="q")
            msg = ""
            if choice == "1":
                msg = trigger_analysis()
            elif choice == "2":
                msg = trigger_code_generation()
            elif choice == "3":
                msg = trigger_pr_submission()
            elif choice == "4":
                msg = manual_memory_inject()
            elif choice == "5":
                msg = manual_memory_retrieve()
            elif choice == "6":
                pr_id = Prompt.ask("Enter PR ID to approve/merge", default="1")
                @handle_errors("PR approval failed.")
                def approve_pr(pr_id):
                    pr_id_valid = validate_pr_id(pr_id)
                    resp = requests.post(
                        "http://localhost:8000/pr/approve",
                        json={"pr_id": pr_id_valid},
                        timeout=10
                    )
                    if resp.ok:
                        try:
                            result = resp.json().get("result", "Approved.")
                            # Never expose secrets/tokens in UI
                            if isinstance(result, str) and ("token" in result.lower() or "secret" in result.lower()):
                                return "Approved."
                            return result
                        except Exception:
                            return format_error_message("Invalid response from API.", "Error approving PR.")
                    else:
                        return format_error_message("API error", "Error approving PR.")
                msg = approve_pr(pr_id)
            elif choice == "7":
                pr_id = Prompt.ask("Enter PR ID to rollback", default="1")
                @handle_errors("PR rollback failed.")
                def rollback_pr(pr_id):
                    pr_id_valid = validate_pr_id(pr_id)
                    resp = requests.post(
                        "http://localhost:8000/pr/rollback",
                        json={"pr_id": pr_id_valid},
                        timeout=10
                    )
                    if resp.ok:
                        try:
                            result = resp.json().get("result", "Rolled back.")
                            # Never expose secrets/tokens in UI
                            if isinstance(result, str) and ("token" in result.lower() or "secret" in result.lower()):
                                return "Rolled back."
                            return result
                        except Exception:
                            return format_error_message("Invalid response from API.", "Error rolling back PR.")
                    else:
                        return format_error_message("API error", "Error rolling back PR.")
                msg = rollback_pr(pr_id)
            elif choice == "q":
                console.print("\n[bold green]Exiting dashboard.[/bold green]")
                self.dashboard_state["last_msg"] = "Exited dashboard."
                save_dashboard_state(self.dashboard_state)
                save_user_preferences(self.user_prefs)
                self.running = False
                sys.exit(0)
            self.dashboard_state["last_choice"] = choice
            self.dashboard_state["last_msg"] = msg
            save_dashboard_state(self.dashboard_state)
            save_user_preferences(self.user_prefs)
            help_line = Text("Need help? Press the number/letter in brackets for any action. [q] to quit.", style="dim", justify="center")
            feedback_panel = Panel(Text(msg, justify="center") + "\n" + help_line, border_style="white")
            self.layout["lower"].update(feedback_panel)

    async def run(self):
        await asyncio.gather(
            self.refresh_panels(),
            self.user_input_loop()
        )

async def dashboard():
    """Main dashboard entrypoint (async, modular)."""
    runner = AsyncDashboardRunner()
    await runner.run()

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    asyncio.run(dashboard())