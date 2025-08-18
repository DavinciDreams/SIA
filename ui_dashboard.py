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
 
import sys
 
# Placeholder imports for actual SIA modules
# from memory_module import get_memory_usage
# from analysis_module import get_latest_analysis_report
# from integration_module import get_pr_status, trigger_pr_submission
# from generation_module import trigger_code_generation

console = Console()

def get_memory_usage():
    """Stub: Replace with actual memory usage retrieval."""
    return {
        "Total Memories": 1234,
        "Episodic": 400,
        "Semantic": 600,
        "Procedural": 234,
        "Last Pruned": "2025-08-17 14:00"
    }

def get_latest_analysis_report():
    """Stub: Replace with actual analysis report retrieval."""
    return {
        "Timestamp": "2025-08-18 01:00",
        "Summary": "No critical issues. 2 optimizations suggested.",
        "Details": [
            "Optimize retrieval index for semantic memory.",
            "Refactor analysis_module for modularity."
        ]
    }

def get_pr_status():
    """
    Retrieve PR status from the API.
    """
    try:
        # For demo: use fixed repo_url and pr_id
        repo_url = "https://github.com/org/repo"
        pr_id = 42
        resp = requests.post(
            "http://localhost:8000/pr/status",
            json={"repo_url": repo_url, "pr_id": pr_id},
            timeout=5
        )
        if resp.ok:
            status = resp.json().get("status", "Unknown")
        else:
            status = "Error"
        return {
            "Open PRs": 1,
            "Last PR": {
                "Title": "Automated PR",
                "Status": status,
                "URL": f"{repo_url}/pull/{pr_id}"
            }
        }
    except Exception as e:
        return {
            "Open PRs": 0,
            "Last PR": {
                "Title": "N/A",
                "Status": f"Request failed: {e}",
                "URL": ""
            }
        }

def trigger_analysis():
    """Stub: Replace with actual analysis trigger."""
    return "Analysis triggered."

def trigger_code_generation():
    """Stub: Replace with actual code generation trigger."""
    return "Code generation triggered."

def trigger_pr_submission():
    """
    Trigger PR submission via API with auto-generation and reviewer assignment.
    """
    try:
        repo_url = Prompt.ask("Repo URL", default="https://github.com/org/repo")
        file_path = Prompt.ask("File path", default="example.py")
        branch_name = Prompt.ask("Branch name", default="feature/auto-pr")
        prompt_text = Prompt.ask("Prompt for code generation", default="Improve X")
        reviewers = Prompt.ask("Reviewers (comma-separated)", default="").split(",") if Prompt.ask("Assign reviewers? (y/n)", choices=["y", "n"], default="n") == "y" else []
        auto = Prompt.ask("Auto-generate PR title/description? (y/n)", choices=["y", "n"], default="y") == "y"
        resp = requests.post(
            "http://localhost:8000/pr",
            json={
                "repo_url": repo_url,
                "file_path": file_path,
                "branch_name": branch_name,
                "prompt": prompt_text,
                "reviewers": reviewers,
                "auto": auto
            },
            timeout=10
        )
        if resp.ok:
            data = resp.json()
            return f"PR submitted. Result: {data.get('result')}\nPR ID: {data.get('pr_id')}"
        else:
            return f"Error: {resp.text}"
    except Exception as e:
        return f"Request failed: {e}"

def render_memory_panel():
    """Render the memory usage panel."""
    mem = get_memory_usage()
    table = Table.grid()
    for k, v in mem.items():
        table.add_row(f"[bold]{k}[/bold]", str(v))
    return Panel(table, title="Memory Usage", border_style="cyan")

def render_analysis_panel():
    """Render the analysis report panel."""
    report = get_latest_analysis_report()
    details = "\n".join(f"- {d}" for d in report["Details"])
    body = f"[bold]Summary:[/bold] {report['Summary']}\n[bold]Details:[/bold]\n{details}"
    return Panel(body, title=f"Analysis Report ({report['Timestamp']})", border_style="magenta")

def render_pr_panel():
    """Render the PR status panel."""
    pr = get_pr_status()
    last = pr["Last PR"]
    body = (
        f"[bold]Open PRs:[/bold] {pr['Open PRs']}\n"
        f"[bold]Last PR:[/bold] {last['Title']}\n"
        f"[bold]Status:[/bold] {last['Status']}\n"
        f"[bold]URL:[/bold] {last['URL']}"
    )
    return Panel(body, title="PR Status", border_style="green")

def render_controls_panel():
    """Render the controls panel for user actions."""
    controls = (
        "[1] Trigger Analysis\n"
        "[2] Trigger Code Generation\n"
        "[3] Submit PR\n"
        "[4] Manual Memory Inject\n"
        "[5] Manual Memory Retrieve\n"
        "[6] Approve PR\n"
        "[7] Rollback PR\n"
        "[q] Quit"
    )
    doc = (
        "[bold cyan]Manual Memory Management:[/bold cyan]\n"
        "[4] Inject: Specify type (episodic/semantic/procedural), text, and meta (JSON).\n"
        "[5] Retrieve: Specify memory index."
    )
    return Panel(f"{controls}\n\n{doc}", title="Controls", border_style="yellow")

def manual_memory_inject():
    """Prompt user for memory details and inject via API."""
    console.print("[bold cyan]Manual Memory Inject[/bold cyan]")
    memory_type = Prompt.ask("Memory type", choices=["episodic", "semantic", "procedural"], default="semantic")
    text = Prompt.ask("Memory text")
    meta_str = Prompt.ask("Meta (JSON, optional)", default="{}")
    try:
        meta = json.loads(meta_str) if meta_str.strip() else {}
    except Exception:
        meta = {}
    try:
        resp = requests.post(
            "http://localhost:8000/memory/manual_inject",
            json={"text": text, "meta": meta, "memory_type": memory_type},
            timeout=5
        )
        if resp.ok:
            idx = resp.json().get("index")
            return f"Injected at index {idx}."
        else:
            return f"Error: {resp.text}"
    except Exception as e:
        return f"Request failed: {e}"

def manual_memory_retrieve():
    """Prompt user for memory index and retrieve via API."""
    console.print("[bold cyan]Manual Memory Retrieve[/bold cyan]")
    idx = Prompt.ask("Memory index", default="0")
    try:
        resp = requests.get(
            f"http://localhost:8000/memory/manual_retrieve?idx={idx}",
            timeout=5
        )
        if resp.ok:
            mem = resp.json().get("memory")
            if mem:
                return f"Memory[{idx}]:\n{json.dumps(mem, indent=2)}"
            else:
                return f"No memory found at index {idx}."
        else:
            return f"Error: {resp.text}"
    except Exception as e:
        return f"Request failed: {e}"

def dashboard():
    """Main dashboard loop."""
    layout = Layout()
    layout.split(
        Layout(name="upper", size=8),
        Layout(name="middle", size=12),
        Layout(name="lower", ratio=1)
    )
    layout["upper"].split_row(
        Layout(render_memory_panel(), name="memory"),
        Layout(render_analysis_panel(), name="analysis"),
        Layout(render_pr_panel(), name="pr"),
    )
    layout["middle"].update(render_controls_panel())
    layout["lower"].update(Panel(Text("Select an action from Controls above.", justify="center"), border_style="white"))

    while True:
        console.clear()
        console.print(layout)
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
            try:
                resp = requests.post(
                    "http://localhost:8000/pr/approve",
                    json={"pr_id": int(pr_id)},
                    timeout=10
                )
                if resp.ok:
                    msg = resp.json().get("result", "Approved.")
                else:
                    msg = f"Error: {resp.text}"
            except Exception as e:
                msg = f"Request failed: {e}"
        elif choice == "7":
            pr_id = Prompt.ask("Enter PR ID to rollback", default="1")
            try:
                resp = requests.post(
                    "http://localhost:8000/pr/rollback",
                    json={"pr_id": int(pr_id)},
                    timeout=10
                )
                if resp.ok:
                    msg = resp.json().get("result", "Rolled back.")
                else:
                    msg = f"Error: {resp.text}"
            except Exception as e:
                msg = f"Request failed: {e}"
        elif choice == "q":
            console.print("\n[bold green]Exiting dashboard.[/bold green]")
            sys.exit(0)
        layout["lower"].update(Panel(Text(msg, justify="center"), border_style="white"))

if __name__ == "__main__":
    dashboard()