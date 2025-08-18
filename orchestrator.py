from memory_module import MemoryModule
from analysis_module import AnalysisModule
from generation_module import GenerationModule
from integration_module import IntegrationModule
import os
import json
from config import PR_RESULTS_PATH

class Orchestrator:
    """
    Core orchestrator module for SIA.

    Responsibilities:
    - Coordinates the workflow and interactions between all core modules as described in the PRD.
    - Manages execution order, data flow, and error handling across the system.
    - Provides a unified interface for initiating and controlling SIA operations.
    """

    def __init__(self):
        """
        Initialize all core modules and prepare orchestrator state.
        """
        self.memory = MemoryModule()
        self.analysis = AnalysisModule()
        self.generation = GenerationModule()
        self.integration = IntegrationModule()
        # Placeholder for UI/external trigger hooks
        self.external_trigger = None

    def run_agent_loop(self):
        """
        Main agent loop: coordinates memory retrieval, analysis, code generation, and PR submission.
        This is the core workflow for self-improvement cycles.
        """
        # Placeholder: In production, this could be a scheduled loop or event-driven
        memories = self.retrieve_memory()
        analysis_report = self.analyze(memories)
        code_diff = self.generate_code(analysis_report)
        pr_url = self.submit_pr(code_diff)
        # Placeholder for UI/CLI notification
        # e.g., self.notify_ui(pr_url)
        return pr_url

    def retrieve_memory(self):
        """
        Retrieve relevant memories for the current context/task.
        Returns:
            list: Retrieved memory objects or data.
        """
        # Placeholder: Replace with actual retrieval logic and context
        return self.memory.retrieve_relevant_memories()

    def analyze(self, memories):
        """
        Perform self-analysis using the analysis module.
        Args:
            memories (list): List of relevant memories or context.
        Returns:
            dict: Analysis report or findings.
        """
        # Placeholder: Replace with actual analysis logic
        return self.analysis.run_analysis(memories)

    def generate_code(self, analysis_report):
        """
        Generate new code/features based on analysis results.
        Args:
            analysis_report (dict): Findings from the analysis module.
        Returns:
            str: Code diff or generated code.
        """
        # Placeholder: Replace with actual code generation logic
        return self.generation.generate(analysis_report)

    def submit_pr(self, code_diff):
        """
        Submit a pull request with the generated code.
        Args:
            code_diff (str): The code changes to submit.
        Returns:
            str: URL or identifier of the created PR.
        """
        # Placeholder: Replace with actual PR submission logic
        return self.integration.create_pull_request(code_diff)

    def sample_memory_task(self):
        """
        Demonstrates end-to-end memory-backed task execution.

        Stores a sample memory, retrieves it, and returns the results.
        Returns:
            dict: {
                'stored_index': int,
                'stored_text': str,
                'retrieved': list of tuples (memory, metadata, score)
            }
        """
        sample_text = "This is a sample memory for demonstration."
        meta = {"source": "sample_task"}
        stored_index = self.memory.store_memory(sample_text, meta)
        stored_text, stored_meta = self.memory.get_memory(stored_index)
        # Retrieve using a similar query
        retrieved = self.memory.retrieve_memory("sample demonstration", top_k=3)
        return {
            "stored_index": stored_index,
            "stored_text": stored_text,
            "stored_meta": stored_meta,
            "retrieved": retrieved
        }

    def run_self_analysis_cycle(self, code_paths=None, report_format="markdown"):
        """
        Run the self-analysis and reporting cycle.

        Analyzes the codebase/tools and generates a report using the AnalysisModule.

        Args:
            code_paths (list, optional): List of file paths to analyze. If None, analyzes orchestrator.py.
            report_format (str): Format of the report ('json' or 'markdown').

        Returns:
            str: The generated analysis report.
        """
        if code_paths is None:
            code_paths = ["orchestrator.py"]
        code_str = ""
        for path in code_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    code_str += f.read() + "\n"
            except Exception as e:
                code_str += f"# Error reading {path}: {e}\n"
        analysis_results = self.analysis.analyze_codebase(code_str)
        report = self.analysis.generate_report(analysis_results, format=report_format)
        return report

    # Placeholder for external triggers or UI integration
    def trigger_from_ui(self, event):
        """
        Placeholder for UI or external event integration.
        Args:
            event (str): Event name or data from UI.
        """
        pass

    def automate_code_and_pr_workflow(self, repo_url, file_path, branch_name, pr_title, pr_description):
        """
        Automate the workflow: analyze, generate code, integrate, and submit a PR.
        Persists PR results to disk.

        Args:
            repo_url (str): URL of the remote repository.
            file_path (str): Path (relative to repo root) to write generated code.
            branch_name (str): Name of the feature branch to create.
            pr_title (str): Title for the pull request.
            pr_description (str): Description for the pull request.

        Returns:
            str: Result message or PR info.
        """
        # Step 1: Retrieve memory and run analysis
        memories = self.retrieve_memory()
        analysis_report = self.analyze(memories)
        memory_context = {"memories": memories}
        # Step 2: Generate code
        generated_code = self.generation.generate_code(analysis_report, memory_context)
        # Step 3: Clone repo
        import tempfile, os, shutil
        temp_dir = tempfile.mkdtemp()
        pr_result = {}
        try:
            repo = self.integration.clone_repo(repo_url, temp_dir)
            if repo is None:
                pr_result["status"] = "Failed to clone repository."
                self.save_pr_result_to_disk(pr_result)
                return pr_result["status"]
            # Step 4: Create branch
            if not self.integration.create_branch(temp_dir, branch_name):
                pr_result["status"] = "Failed to create branch."
                self.save_pr_result_to_disk(pr_result)
                return pr_result["status"]
            # Step 5: Write generated code to file
            abs_file_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(abs_file_path), exist_ok=True)
            with open(abs_file_path, "w", encoding="utf-8") as f:
                f.write(generated_code)
            # Step 6: Commit changes
            if not self.integration.commit_changes(temp_dir, "Automated code generation by SIA"):
                pr_result["status"] = "Failed to commit changes."
                self.save_pr_result_to_disk(pr_result)
                return pr_result["status"]
            # Step 7: Push changes
            if not self.integration.push_changes(temp_dir, branch_name):
                pr_result["status"] = "Failed to push changes."
                self.save_pr_result_to_disk(pr_result)
                return pr_result["status"]
            # Step 8: Create PR (prints to console)
            pr_url = self.integration.create_pull_request(repo_url, branch_name, pr_title, pr_description)
            pr_result = {
                "status": "PR workflow completed",
                "branch": branch_name,
                "pr_url": pr_url,
                "repo_url": repo_url,
                "file_path": file_path,
                "pr_title": pr_title,
                "pr_description": pr_description
            }
            self.save_pr_result_to_disk(pr_result)
            return f"PR workflow completed for branch '{branch_name}'."
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def save_pr_result_to_disk(self, pr_result, result_name=None):
        """
        Persist PR result data to disk as JSON.

        Args:
            pr_result (dict): The PR result data to save.
            result_name (str, optional): The filename for the result. If None, uses 'pr_result_<n>.json'.

        Returns:
            str: The full path to the saved PR result.
        """
        os.makedirs(PR_RESULTS_PATH, exist_ok=True)
        if result_name is None:
            existing = [f for f in os.listdir(PR_RESULTS_PATH) if f.startswith("pr_result_")]
            idx = len(existing) + 1
            result_name = f"pr_result_{idx}.json"
        full_path = os.path.join(PR_RESULTS_PATH, result_name)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(pr_result, f, indent=2)
        return full_path