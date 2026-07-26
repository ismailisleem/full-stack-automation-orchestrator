# Walkthrough

This walkthrough starts from a clean local checkout and ends with a retained report portfolio.

## 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## 2. Run Infrastructure-Free Samples

```bash
full-stack-orchestrator run-sample all --output reports/orchestrator
```

The sample run executes three journeys:

- API prepares state and Web verifies it.
- API prepares state and Mobile verifies it.
- API, Web, and Mobile complete one full journey.

## 3. Review The Report

Open the portfolio:

```bash
open reports/orchestrator/index.html
```

Important pages:

- `index.html`: portfolio dashboard across retained runs.
- `reports.html`: gallery of every retained run.
- `compare.html`: compare recent runs.
- `runs/<timestamp>-<run-id>/index.html`: detailed run overview.
- `runs/<timestamp>-<run-id>/tests/`: journey details with steps, retries, state, and artifacts.

See [Screenshot Index](SCREENSHOTS.md) for captured examples.

## 4. Check Real Framework Readiness

```bash
full-stack-orchestrator doctor --config config/orchestrator.yaml
```

`doctor` checks configured repo paths, target commands, command executables, and required
environment variables. Fix failed checks before running a real plan.

## 5. Run A Real Target

```bash
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target api-smoke
```

Then expand to Web and Mobile helper smoke runs:

```bash
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target web-smoke
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target mobile-helper-smoke
```

Device-dependent Android and iOS examples stay in `mobile-automation-framework`, where Appium,
capabilities, devices, simulators, and app fixtures are owned.

## 6. Combine Framework Portfolios

```bash
full-stack-orchestrator combine-reports \
  --source ../api-automation-framework/reports/automation-report \
  --source ../web-automation-framework/reports/automation-report \
  --source ../mobile-automation-framework/reports/automation-report \
  --output reports/combined
```

Use this after independent framework runs when reviewers need one dashboard.
