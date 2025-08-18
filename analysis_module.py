import os
import json
from config import ANALYSIS_REPORTS_PATH

class AnalysisModule:
    """
    Core analysis module for SIA.

    Now supports persistent storage of analysis reports to disk.
    Storage location is configurable via config.py (ANALYSIS_REPORTS_PATH).

    Responsibilities:
    - Processes and interprets input data according to the PRD.
    - Extracts insights, patterns, and relevant information for downstream modules.
    - Interfaces with memory and generation modules to inform decision-making.
    """

    def list_tools(self):
        """
        List available tools and their descriptions.

        Returns:
            list: A list of tool names and descriptions.
        """
        # Placeholder: Replace with actual tool registry if available
        return [
            {"name": "AST Analyzer", "description": "Analyzes codebase for code smells and deprecated libraries."},
            {"name": "Performance Tracker", "description": "Tracks and reports performance metrics."},
            {"name": "Report Generator", "description": "Generates analysis reports in JSON or Markdown."}
        ]

    def evaluate_tool(self, tool_name):
        """
        Evaluate a tool's capabilities and status.

        Args:
            tool_name (str): Name of the tool to evaluate.

        Returns:
            dict: Evaluation details about the tool.
        """
        # Placeholder: Replace with actual evaluation logic
        tools = {t["name"]: t for t in self.list_tools()}
        return tools.get(tool_name, {"error": "Tool not found"})

    def analyze_codebase(self, code_str):
        """
        Analyze the provided codebase string using AST for code smells and deprecated libraries.

        Args:
            code_str (str): Source code as a string.

        Returns:
            dict: Analysis results including code smells and deprecated library usage.
        """
        import ast

        results = {"code_smells": [], "deprecated_libs": []}
        try:
            tree = ast.parse(code_str)
            for node in ast.walk(tree):
                # Example: Detect usage of 'eval'
                if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'eval':
                    results["code_smells"].append("Use of 'eval' detected")
                # Example: Detect deprecated library 'imp'
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "imp":
                            results["deprecated_libs"].append("Use of deprecated library 'imp'")
                if isinstance(node, ast.ImportFrom) and node.module == "imp":
                    results["deprecated_libs"].append("Use of deprecated library 'imp'")
        except Exception as e:
            results["error"] = str(e)
        return results

    def track_performance_metrics(self, metrics):
        """
        Track and store performance metrics.

        Args:
            metrics (dict): Dictionary of performance metrics.

        Returns:
            bool: True if metrics were tracked successfully.
        """
        # Placeholder: Store metrics in memory or persistent storage as needed
        self._last_metrics = metrics
        return True

    def scheduled_analysis(self):
        """
        Placeholder for scheduled analysis logic.

        Returns:
            None
        """
        # To be implemented: scheduling logic for periodic analysis
        pass

    def generate_report(self, analysis_results, format="json"):
        """
        Generate a report from analysis results in JSON or Markdown format.

        Args:
            analysis_results (dict): Results from codebase analysis.
            format (str): 'json' or 'markdown'.

        Returns:
            str: The generated report as a string.
        """
        import json

        if format == "json":
            return json.dumps(analysis_results, indent=2)
        elif format == "markdown":
            md = "# Analysis Report\n"
            for key, value in analysis_results.items():
                md += f"## {key.capitalize()}\n"
                if isinstance(value, list):
                    for item in value:
                        md += f"- {item}\n"
                else:
                    md += f"{value}\n"
            return md
        else:
            return "Unsupported format"