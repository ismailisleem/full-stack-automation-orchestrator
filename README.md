# Full-Stack Automation Orchestrator

[![CI](https://github.com/ismailisleem/full-stack-automation-orchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/ismailisleem/full-stack-automation-orchestrator/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-3776AB.svg)](#requirements)
[![Reports](https://img.shields.io/badge/reports-automation--core-2EAD33.svg)](https://github.com/ismailisleem/automation-core)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Cross-Platform E2E Automation Framework for teams that need one scenario to coordinate API, Web, and Mobile automation without copying framework-specific code into one large repository.

It is the coordination layer for the automation framework family:

- `automation-core`: shared neutral helpers and reporting.
- `api-automation-framework`: API clients, services, contracts, and API samples.
- `web-automation-framework`: browser automation, page objects, flows, and web samples.
- `mobile-automation-framework`: Appium automation, devices, contexts, screens, and mobile samples.

## What This Framework Gives You

- Journey orchestration across API, Web, and Mobile phases.
- Shared scenario state such as IDs, tokens, customer data, order references, and correlation metadata.
- Preflight checks for configured framework targets.
- Subprocess-first framework execution so each framework keeps its own dependencies and fixtures isolated.
- Shared reporting through `automation-core`, including retained timestamped runs, portfolio dashboard, compare view, test details, timeline, artifacts, and exports.
- Built-in API+Web, API+Mobile, and full-stack sample journeys.
- GitHub Actions workflow for linting, tests, package build, and wheel smoke validation.
- CLI commands for samples, configured framework plans, report portfolio aggregation, and readiness checks.

## Project Structure

```text
.
├── config/
│   └── orchestrator.yaml          # Example cross-framework target plan
├── docs/
│   ├── CLI.md                     # Unified command guide
│   ├── RELEASE.md                 # Release and dependency checklist
│   ├── TROUBLESHOOTING.md         # Common setup and execution issues
│   ├── adapters.md                # Adapter patterns and boundaries
│   ├── architecture.md            # Ownership and process model
│   ├── configuration.md           # Config file reference
│   ├── development.md             # Contributor validation
│   ├── reporting.md               # Report output and sidecar data
│   └── samples.md                 # Runnable sample walkthrough
├── examples/
│   ├── api_mobile/                # API + Mobile sample test
│   ├── api_web/                   # API + Web sample test
│   └── full_journey/              # API + Web + Mobile sample test
├── src/full_stack_automation_orchestrator/
│   ├── adapters.py                # Function and subprocess adapters
│   ├── cli.py                     # `full-stack-orchestrator`
│   ├── config.py                  # YAML config model
│   ├── journey.py                 # Journey runner and step execution
│   ├── reporting.py               # automation-core report bridge
│   └── state.py                   # JSON-safe scenario state
└── tests/
    └── e2e/                       # End-to-end sample validation
```

## What It Does Not Own

- Web pages, browser drivers, Selenium, or Playwright code.
- Mobile screens, Appium drivers, capabilities, or device setup.
- API clients, request builders, schema validators, or service objects.
- Shared neutral utilities that belong in `automation-core`.

Those stay in their own repositories:

- `web-automation-framework`
- `mobile-automation-framework`
- `api-automation-framework`
- `automation-core`

## Starter Template

A copyable product starter is available under `templates/starter_project/`.
It shows how a product repository can keep cross-platform orchestration code thin while delegating
browser, device, and API behavior back to the dedicated framework repositories.

Use it when a business flow spans multiple automation targets, for example:

- API creates or prepares data.
- Web validates the customer or admin experience.
- Mobile validates the same state on Android or iOS.
- The final report presents the whole journey as one run.

See [Starter Project](templates/starter_project/README.md) and
[Feature Parity](docs/FEATURE_PARITY.md).

## Requirements

- Python 3.11, 3.12, or 3.13.
- Git access to this repository and `automation-core`.
- For configured framework targets, each sibling framework should have its own virtual environment installed.
- For real Web or Mobile target runs, browser or Appium/device setup is owned by the Web or Mobile framework.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Install from GitHub for a released tag:

```bash
python -m pip install "full-stack-automation-orchestrator @ git+https://github.com/ismailisleem/full-stack-automation-orchestrator.git@v0.1.0"
```

Run the built-in examples. They use lightweight demo adapters, so they do not require browsers, devices, Appium, or live services.

```bash
full-stack-orchestrator run-sample api-web --output reports/orchestrator
full-stack-orchestrator run-sample api-mobile --output reports/orchestrator
full-stack-orchestrator run-sample full --output reports/orchestrator
full-stack-orchestrator run-sample all --output reports/orchestrator
```

Open the portfolio:

```bash
open reports/orchestrator/index.html
```

## Unified Orchestrator CLI

Check config readiness:

```bash
full-stack-orchestrator doctor --config config/orchestrator.yaml
```

Run built-in samples:

```bash
full-stack-orchestrator run-sample all --output reports/orchestrator
```

Run configured framework targets:

```bash
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target api-smoke
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target web-smoke
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target mobile-helper-smoke
```

Combine existing framework report portfolios:

```bash
full-stack-orchestrator combine-reports \
  --source ../api-automation-framework/reports/automation-report \
  --source ../web-automation-framework/reports/automation-report \
  --source ../mobile-automation-framework/reports/automation-report \
  --output reports/combined
```

See the [CLI Guide](docs/CLI.md) for all commands.

## Configured Framework Runs

The default config shows how to point the orchestrator at sibling framework repositories:

```bash
full-stack-orchestrator doctor --config config/orchestrator.yaml
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target api-smoke
```

Real framework phases are executed as subprocesses from each repository directory. This keeps `utils`, `flows`, `pages`, `screens`, fixtures, and dependency sets isolated.

`doctor` validates the configured repository paths, target commands, command executables, and required environment variables before a plan is executed.

## Reporting

Every sample or run plan can generate an automation-core report portfolio:

- `reports/orchestrator/index.html`: dashboard across retained runs.
- `reports/orchestrator/reports.html`: report gallery.
- `reports/orchestrator/compare.html`: run comparison.
- `reports/orchestrator/runs/<timestamp>-<run-id>/index.html`: individual run overview.
- `reports/orchestrator/runs/<timestamp>-<run-id>/tests/`: journey details.
- `reports/orchestrator/runs/<timestamp>-<run-id>/exports/`: CSV, XLSX, DOCX, SVG, and JSON exports.

The HTML is for people. The `report-data.json` sidecar is the stable validation target for tooling.

## Python Usage

```python
from full_stack_automation_orchestrator import Journey, JourneyRunner, JourneyStep, StepOutput


def create_order(context):
    context.state.set("order.id", "ORD-1001")
    return StepOutput(data={"order_id": "ORD-1001"}, metadata={"platform": "api"})


def verify_order_on_web(context):
    order_id = context.state.require("order.id")
    return StepOutput(data={"visible_order": order_id}, metadata={"platform": "web"})


journey = Journey(
    name="API creates order and Web verifies it",
    steps=[
        JourneyStep("Create order", create_order, platform="api"),
        JourneyStep("Verify on Web", verify_order_on_web, platform="web", depends_on=("Create order",)),
    ],
)

result = JourneyRunner().run(journey)
assert result.passed
```

## Validation

```bash
ruff check .
ruff format --check .
pytest
python -m build
```

Run samples and configured framework targets when validating release readiness:

```bash
full-stack-orchestrator run-sample all --output reports/orchestrator
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target api-smoke
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target web-smoke
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target mobile-helper-smoke
```

This repo does not publish a coverage number yet. CI runs linting, formatting, unit tests, package build, wheel smoke validation, and a sample report smoke.

## Known Limitations

- Real browser, Appium, simulator, device, and API-service readiness remains owned by the target framework.
- Built-in samples are intentionally infrastructure-free so new users can see orchestration and reporting immediately.
- Mobile device execution requires Appium and a prepared Android/iOS target; device CI is a future environment decision.
- The orchestrator coordinates existing frameworks. It does not replace their page objects, screen objects, service clients, fixtures, or helpers.

## Troubleshooting

See [Troubleshooting](docs/TROUBLESHOOTING.md).

## Documentation

- [Architecture](docs/architecture.md)
- [Adapters](docs/adapters.md)
- [CLI Guide](docs/CLI.md)
- [Configuration](docs/configuration.md)
- [Examples](docs/EXAMPLES.md)
- [Feature Parity](docs/FEATURE_PARITY.md)
- [Reporting](docs/reporting.md)
- [Release Guide](docs/RELEASE.md)
- [Samples](docs/samples.md)
- [Screenshot Index](docs/SCREENSHOTS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Walkthrough](docs/WALKTHROUGH.md)
- [Development](docs/development.md)
