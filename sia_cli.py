#!/usr/bin/env python3

"""
SIA Command Line Interface

Provides user-friendly commands for memory operations, code analysis, code generation, and PR submission.
"""

import sys
from orchestrator import Orchestrator
def main():
    """
    SIA CLI entry point.
    Provides subcommands for memory, analysis, code generation, and PR submission.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="SIA CLI: Memory, Analysis, Generation, and PR workflows."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")

    # Memory operations
    mem_parser = subparsers.add_parser("memory", help="Memory operations: store or retrieve text.")
    mem_parser.add_argument("--store", type=str, help="Text to store in memory.")
    mem_parser.add_argument("--meta", type=str, help="Optional metadata for memory.")
    mem_parser.add_argument("--retrieve", type=str, help="Query to retrieve from memory.")
    mem_parser.add_argument("--topk", type=int, default=3, help="Number of top results to retrieve.")

    # Analysis
    ana_parser = subparsers.add_parser("analyze", help="Run code analysis and reporting.")
    ana_parser.add_argument("--paths", nargs="*", default=None, help="File paths to analyze.")
    ana_parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Report format.")

    # Code generation
    gen_parser = subparsers.add_parser("generate", help="Generate code for a specified task.")
    gen_parser.add_argument("--prompt", type=str, required=True, help="Prompt describing code to generate.")
    gen_parser.add_argument("--file-path", type=str, required=True, help="File path to write generated code.")

    # PR submission
    pr_parser = subparsers.add_parser("pr", help="Automate code generation and PR submission workflow.")
    pr_parser.add_argument("--repo-url", type=str, required=True, help="Remote repository URL.")
    pr_parser.add_argument("--file-path", type=str, required=True, help="File path for generated code.")
    pr_parser.add_argument("--branch-name", type=str, required=True, help="Feature branch name.")
    pr_parser.add_argument("--pr-title", type=str, required=True, help="Pull request title.")
    pr_parser.add_argument("--pr-description", type=str, required=True, help="Pull request description.")
    pr_parser.add_argument("--prompt", type=str, required=True, help="Prompt describing code to generate.")

    args = parser.parse_args()
    orchestrator = Orchestrator()

    if args.command == "memory":
        if args.store:
            """Store text in memory."""
            result = orchestrator.memory_store(args.store, meta=args.meta)
            print("Memory stored:", result)
        elif args.retrieve:
            """Retrieve from memory."""
            result = orchestrator.memory_retrieve(args.retrieve, topk=args.topk)
            print("Retrieved memories:")
            for i, (mem, meta, score) in enumerate(result, 1):
                print(f"  {i}. Text: {mem!r}, Metadata: {meta}, Score: {score:.4f}")
        else:
            print("Specify --store or --retrieve for memory operations.")
    elif args.command == "analyze":
        """Run code analysis and reporting."""
        report = orchestrator.run_self_analysis_cycle(
            code_paths=args.paths,
            report_format=args.format
        )
        print(report)
    elif args.command == "generate":
        """Generate code for a specified task."""
        result = orchestrator.generate_code(
            prompt=args.prompt,
            file_path=args.file_path
        )
        print("Generated code written to", args.file_path)
        print(result)
    elif args.command == "pr":
        """Automate code generation and PR submission workflow."""
        result = orchestrator.automate_code_and_pr_workflow(
            repo_url=args.repo_url,
            file_path=args.file_path,
            branch_name=args.branch_name,
            pr_title=args.pr_title,
            pr_description=args.pr_description,
            prompt=args.prompt
        )
        print(result)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()