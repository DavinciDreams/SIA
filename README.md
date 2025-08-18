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
- **Orchestrator**: Coordinates workflows between modules, manages self-improvement cycles, and enforces safeguards.
- **CLI & API**: Entry points for command-line and web-based interaction.
- **UI Dashboard**: Terminal-based dashboard for real-time monitoring and control of SIA workflows.

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
- Handles repository cloning, branching, commits, pushes, notifications, PR creation, and merge conflict handling.

### [`orchestrator.py`](orchestrator.py:1)
- Central coordinator for all modules.
- Manages workflow execution and module communication.
- Enforces rate-limiting for self-improvement cycles.
- Requires human approval before merging PRs.
- Supports rollback of failed/problematic self-improvements.
### [`sia_cli.py`](sia_cli.py:1)
- Command-line interface entry point.
- Provides user-friendly commands for memory operations, analysis, code generation, and PR submission.
- Exposes `approve-pr` and `rollback-pr` commands for PR approval and rollback.
- Supports manual memory injection and retrieval, and PR status monitoring.

### [`sia_api.py`](sia_api.py:1)
- FastAPI-based web API.
- Provides endpoints for memory operations, analysis, code generation, and PR submission.
- Exposes `/pr/approve` and `/pr/rollback` endpoints for PR approval and rollback.
- Supports manual memory injection (`/memory/manual_inject`) and retrieval (`/memory/manual_retrieve`).
- Provides `/pr/status` endpoint for PR status monitoring.

### [`ui_dashboard.py`](ui_dashboard.py:1)
- Terminal dashboard for monitoring and controlling SIA.
- Exposes controls for PR approval, rollback, manual memory management, and PR status.
- Provides interactive panels for memory usage, analysis reports, and PR workflows.

---
---
## Security & Reliability Features

- **API Authentication**: All API endpoints require an API key via the `x-api-key` header. See [`config.py`](config.py:1) for configuration.
- **Encrypted Memory Storage**: All persistent memories are encrypted at rest using Fernet symmetric encryption. Set `SIA_ENCRYPTION_KEY` in your environment.
- **Audit Logging**: All memory and self-improvement operations are logged to `sia_audit.log` for traceability.
- **Automated Backups**: Use `MemoryModule.backup_memories()` to create timestamped encrypted backups of memory storage.
- **Test Coverage Enforcement**: Run tests with coverage and enforce a minimum threshold using `pytest --cov=. --cov-fail-under=80`.
- **Human-in-the-Loop Safeguards**: All self-improvement PRs require explicit human approval before merging. Rollback is supported for any problematic changes.
- **Rate Limiting**: Self-improvement cycles are rate-limited to prevent runaway automation.
- **Manual Memory Controls**: Manual injection and retrieval endpoints/commands are available for safe, auditable memory management.
- **PR Status Monitoring**: All PRs can be monitored and managed via CLI, API, and UI dashboard.



## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/sia.git
   cd sia
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Run tests with coverage:
   ```bash
   pytest --cov=. --cov-report=term-missing --cov-fail-under=80
   ```
   - The `--cov-fail-under=80` flag enforces a minimum of 80% coverage.
   - Adjust the threshold as needed for your project.

---

## Usage Examples

### CLI

Run the CLI with subcommands:

```bash
python sia_cli.py memory --store "Remember this fact." --meta "example"
python sia_cli.py memory --retrieve "fact" --topk 2
python sia_cli.py memory --help
python sia_cli.py analyze --paths orchestrator.py analysis_module.py --format markdown
python sia_cli.py generate --prompt "Write a function to add two numbers." --file-path src/utils/add.py
python sia_cli.py pr --repo-url https://github.com/your-organization/sia.git --file-path src/utils/add.py --branch-name feature/add-func --pr-title "Add addition function" --pr-description "Implements add function" --prompt "Write a function to add two numbers."
python sia_cli.py pr --repo-url https://github.com/your-organization/sia.git --file-path src/utils/add.py --branch-name feature/add-func --prompt "Write a function to add two numbers." --auto --reviewers alice bob --status
python sia_cli.py approve-pr --pr-id 1
python sia_cli.py rollback-pr --pr-id 1
```

Manual memory management via CLI:
```bash
python sia_cli.py memory --store "Fact" --meta "manual"
python sia_cli.py memory --retrieve "Fact" --topk 1
```

Each subcommand provides detailed help:
```bash
python sia_cli.py memory --help
python sia_cli.py analyze --help
python sia_cli.py generate --help
python sia_cli.py pr --help
python sia_cli.py approve-pr --help
python sia_cli.py rollback-pr --help
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
- `POST /memory/manual_inject` — Manually inject a memory.
  - Request body: `{"text": "Manual memory", "meta": {"source": "manual"}, "memory_type": "semantic"}`
- `GET /memory/manual_retrieve?idx=0` — Retrieve a memory by index.
- `POST /analyze` — Run code analysis.
  - Request body: `{"paths": ["orchestrator.py"], "format": "markdown"}`
- `POST /generate` — Generate code for a prompt.
  - Request body: `{"prompt": "Write a function to add two numbers.", "file_path": "utils/add.py"}`
- `POST /pr` — Automate code generation and PR submission.
  - Request body: `{"repo_url": "https://github.com/your-organization/sia.git", "file_path": "src/utils/add.py", "branch_name": "feature/add-func", "pr_title": "Add addition function", "pr_description": "Implements add function", "prompt": "Write a function to add two numbers.", "reviewers": ["alice"], "auto": true}`
- `POST /pr/approve` — Approve and merge a PR.
  - Request body: `{"pr_id": 1}`
- `POST /pr/rollback` — Rollback a PR's self-improvement.
  - Request body: `{"pr_id": 1}`
- `POST /pr/status` — Get PR status.
  - Request body: `{"repo_url": "https://github.com/your-organization/sia.git", "pr_id": 1}`

---

### UI Dashboard

Start the dashboard:
```bash
python ui_dashboard.py
```

Features:
- Real-time panels for memory usage, analysis reports, and PR status.
- Controls for triggering analysis, code generation, PR submission, manual memory inject/retrieve, PR approval, and rollback.
- Interactive prompts for all workflows.


## Contribution Guidelines

We welcome contributions! Please see [`CONTRIBUTING.md`](CONTRIBUTING.md:1) for detailed instructions.

- Fork the repository and create a feature branch.
- Follow the code style and documentation standards.
- Add or update tests as appropriate.
- Submit a pull request with a clear description.

---

## License

Distributed under the MIT License.