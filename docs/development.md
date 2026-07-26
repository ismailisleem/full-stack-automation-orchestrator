# Development

Run local validation before opening or merging a pull request:

```bash
ruff check .
ruff format --check .
pytest
python -m build
```

When report behavior changes, also generate sample reports:

```bash
full-stack-orchestrator run-sample all --output reports/orchestrator
```

When sibling framework repositories are available, run the configured smoke plan:

```bash
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target api-smoke
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target web-smoke
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target mobile-helper-smoke
```

For visual QA, use Playwright bundled Chromium or another non-system-Chrome renderer. Do not use the system Google Chrome app for screenshots or static report checks.

## Pull Request Checklist

- Scope is focused.
- No Web, Mobile, or API internals were copied into this repository.
- New shared-neutral behavior remains in `automation-core` when it belongs there.
- Unit tests and samples pass locally.
- GitHub checks pass.
