# Contributing to SIA

Thank you for your interest in contributing to SIA! This guide outlines the process for contributing code, reporting issues, and maintaining code quality.

---

## How to Contribute

1. **Fork the repository** and create a new branch for your feature or bugfix.
2. **Write clear, concise code** following the style guidelines below.
3. **Document your changes** with clear docstrings and comments.
4. **Add or update tests** to cover your changes.
5. **Submit a pull request** with a descriptive title and summary.

---

## Code Style

- Follow [PEP 8](https://pep8.org/) for Python code style.
- Use descriptive variable and function names.
- Write docstrings for all public classes and functions.
- Keep functions small and focused.
- Use type hints where appropriate.

---

## Testing

- Use `pytest` for writing and running tests.
- Place tests in a `tests/` directory or alongside modules as appropriate.
- Ensure all tests pass before submitting a pull request:
  ```bash
  pytest --cov=. --cov-report=term-missing --cov-fail-under=80
  ```
  - The `--cov-fail-under=80` flag enforces a minimum of 80% coverage.
  - Adjust the threshold as needed for your contribution.
- Add tests for new features and bug fixes.
- Test all CLI, API, and UI workflows relevant to your change.

---

## Security Guidelines

- Never commit secrets, API keys, or credentials.
- Use the provided API authentication and encryption mechanisms.
- All self-improvement PRs require human approval before merging.
- Use manual memory injection and retrieval endpoints/commands for safe, auditable memory management.
- Monitor PR status and rollback if necessary.

---

## Reporting Issues

- Use GitHub Issues to report bugs or request features.
- Provide clear steps to reproduce bugs and relevant context.

---

## Contribution Workflow

- Fork the repository and create a feature branch.
- Follow the code style and documentation standards.
- Add or update tests as appropriate.
- Submit a pull request with a clear description.
- For PRs involving self-improvement or automation, ensure human approval is required before merge.
- Use the CLI, API, or UI dashboard to monitor PR status and perform approval or rollback as needed.

---

## Code of Conduct

Be respectful and constructive in all interactions.

---

Thank you for helping improve SIA!