## What Changed

-

## Why

-

## Validation

- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `pytest --cov=full_stack_automation_orchestrator --cov-report=term-missing`
- [ ] `python -m build`
- [ ] `full-stack-orchestrator run-sample all --output reports/orchestrator`

## Boundaries

- [ ] No Web, Mobile, or API framework internals were copied into the orchestrator.
- [ ] Environment-specific behavior remains in the responsible framework.
- [ ] Shared neutral behavior remains in or belongs to `automation-core`.

## Notes

-
