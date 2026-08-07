# Release Guide

## Versioning

The orchestrator follows semantic versioning while it remains independently usable from GitHub.

- Patch releases: documentation, compatibility, and focused bug fixes.
- Minor releases: new orchestration features, adapters, CLI commands, or reporting capabilities.
- Major releases: breaking public API or CLI changes.

## Dependency Rule

Pin `automation-core` to a public tag for user-facing releases. Avoid publishing release documentation that points users at an untagged feature branch commit.

Example:

```toml
"automation-core @ git+https://github.com/ismailisleem/automation-core.git@v0.13.1"
```

## Local Release Checklist

```bash
ruff check .
ruff format --check .
pytest --cov=full_stack_automation_orchestrator --cov-report=term-missing
python -m build
full-stack-orchestrator run-sample all --output reports/orchestrator
```

Also run at least one configured framework target when sibling repositories are available:

```bash
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target api-smoke
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target web-smoke
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target mobile-helper-smoke
```

## GitHub Release Checklist

- GitHub Actions CI is green on `main`.
- README and docs match the released behavior.
- The dependency on `automation-core` points to a tested public tag.
- Built-in samples generate a portfolio report.
- Known limitations are documented.
- Create a release tag matching `pyproject.toml`, such as `v0.1.0`.
