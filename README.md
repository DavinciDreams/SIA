# SIA (Synthetic Intelligence Assistant)

SIA is a modular Python framework for advanced AI-driven analysis, memory management, code generation, and integration workflows. Designed for extensibility and research, SIA enables automated reasoning, persistent memory, and seamless integration with external systems.

---

## Project Overview

SIA orchestrates multiple specialized modules to analyze code, generate new artifacts, manage long-term memory, and interact with external APIs and repositories. Its architecture supports research, automation, and integration scenarios for AI-assisted development.

---

## Architecture Summary

SIA is organized into the following core modules:

- **Analysis Module**: Extracts insights and patterns from input data, performs code analysis, and generates reports.
- **Memory Module**: Provides persistent and transient memory storage, semantic retrieval, and memory pruning.
- **Generation Module**: Produces code, responses, or artifacts based on analysis and memory context.
- **Integration Module**: Manages connections to external systems (e.g., Git, email, Slack), handles repository operations, and facilitates notifications.
- **Orchestrator**: Coordinates workflows between modules.
- **CLI & API**: Entry points for command-line and web-based interaction.

---

## Module Descriptions

### [`analysis_module.py`](analysis_module.py:1)
- Processes and interprets input data.
- Extracts insights, detects code smells, and identifies deprecated libraries.
- Interfaces with memory and generation modules.
- Generates analysis reports in JSON or Markdown.

### [`memory_module.py`](memory_module.py:7)
- Stores and retrieves persistent and transient data.
- Uses embeddings (optionally FAISS) for semantic memory search.
- Supports memory injection, pruning, and metadata management.

### [`generation_module.py`](generation_module.py:1)
- Generates code or artifacts based on analysis and memory.
- Supports iterative refinement and safety checks.
- Can run local tests (e.g., pytest) on generated code.

### [`integration_module.py`](integration_module.py:5)
- Manages external integrations (Git, email, Slack).
- Handles repository cloning, branching, commits, pushes, and notifications.
- Provides placeholders for PR creation and merge conflict handling.

### [`orchestrator.py`](orchestrator.py:1)
- Central coordinator for all modules.
- Manages workflow execution and module communication.

### [`sia_cli.py`](sia_cli.py:1)
- Command-line interface entry point.
- Provides user-friendly commands for memory operations, analysis, code generation, and PR submission.

### [`sia_api.py`](sia_api.py:1)
- FastAPI-based web API.
- Provides endpoints for memory operations, analysis, code generation, and PR submission.

---

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/sia.git
   cd sia
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Run tests:
   ```bash
   pytest
   ```

---

## Usage Examples

### CLI

Run the CLI with subcommands:

```bash
python sia_cli.py memory --store "Remember this fact." --meta "example"
python sia_cli.py memory --retrieve "fact" --topk 2
python sia_cli.py analyze --paths orchestrator.py analysis_module.py --format markdown
python sia_cli.py generate --prompt "Write a function to add two numbers." --file-path utils/add.py
python sia_cli.py pr --repo-url https://github.com/your-org/sia.git --file-path utils/add.py --branch-name feature/add-func --pr-title "Add addition function" --pr-description "Implements add function" --prompt "Write a function to add two numbers."
```

Each subcommand provides detailed help:
```bash
python sia_cli.py memory --help
python sia_cli.py analyze --help
python sia_cli.py generate --help
python sia_cli.py pr --help
```

### API

Start the API server:
```bash
uvicorn sia_api:app --reload
```

Example endpoints:

- `POST /memory/store` — Store text in memory.
  - Request body: `{"text": "Remember this fact.", "meta": "example"}`
- `POST /memory/retrieve` — Retrieve memories.
  - Request body: `{"query": "fact", "topk": 2}`
- `POST /analyze` — Run code analysis.
  - Request body: `{"paths": ["orchestrator.py"], "format": "markdown"}`
- `POST /generate` — Generate code for a prompt.
  - Request body: `{"prompt": "Write a function to add two numbers.", "file_path": "utils/add.py"}`
- `POST /pr` — Automate code generation and PR submission.
  - Request body: `{"repo_url": "...", "file_path": "...", "branch_name": "...", "pr_title": "...", "pr_description": "...", "prompt": "..."}`

---

## Contribution Guidelines

We welcome contributions! Please see [`CONTRIBUTING.md`](CONTRIBUTING.md:1) for detailed instructions.

- Fork the repository and create a feature branch.
- Follow the code style and documentation standards.
- Add or update tests as appropriate.
- Submit a pull request with a clear description.

---

## License

Distributed under the MIT License.