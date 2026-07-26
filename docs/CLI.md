# CLI Guide

The orchestrator exposes one command:

```bash
full-stack-orchestrator
```

Use `python -m full_stack_automation_orchestrator` when you want to run the same CLI without relying on shell entry points.

## Doctor

Validate configured target paths, commands, and required environment variables:

```bash
full-stack-orchestrator doctor --config config/orchestrator.yaml
```

`doctor` does not start browsers, devices, or API calls. It checks whether the plan is structurally runnable from this machine.

## Built-In Samples

Run samples that demonstrate orchestration without external services, browsers, Appium, or devices:

```bash
full-stack-orchestrator run-sample api-web --output reports/orchestrator
full-stack-orchestrator run-sample api-mobile --output reports/orchestrator
full-stack-orchestrator run-sample full --output reports/orchestrator
full-stack-orchestrator run-sample all --output reports/orchestrator
```

Samples generate an automation-core portfolio report at `reports/orchestrator/index.html`.

## Run A Configured Plan

Run enabled framework targets from `config/orchestrator.yaml`:

```bash
full-stack-orchestrator run-plan --config config/orchestrator.yaml
```

Run one target:

```bash
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target api-smoke
```

Run more than one selected target:

```bash
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target api-smoke --target web-smoke
```

Real framework phases are executed from each target repository using its configured command. Prefer repo-local virtual environments such as `.venv/bin/python`.

## Combine Existing Report Portfolios

Build one portfolio from several framework report roots:

```bash
full-stack-orchestrator combine-reports \
  --source ../api-automation-framework/reports/automation-report \
  --source ../web-automation-framework/reports/automation-report \
  --source ../mobile-automation-framework/reports/automation-report \
  --output reports/combined
```

This is useful when API, Web, and Mobile frameworks already generated their own automation-core reports and you want a single cross-platform view.
