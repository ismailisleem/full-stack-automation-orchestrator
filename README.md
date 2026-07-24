# Full-Stack Automation Orchestrator

Cross-Platform E2E Automation Framework for teams that need one scenario to coordinate API, Web, and Mobile automation without copying framework-specific code into one large repository.

## What It Owns

- Journey orchestration across API, Web, and Mobile phases.
- Shared scenario state such as IDs, tokens, customer data, order references, and correlation metadata.
- Preflight checks for configured framework targets.
- Subprocess-first framework execution so each framework keeps its own dependencies and fixtures isolated.
- Shared reporting through `automation-core`, including retained timestamped runs, portfolio dashboard, compare view, test details, timeline, artifacts, and exports.

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

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
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

## Configured Framework Runs

The default config shows how to point the orchestrator at sibling framework repositories:

```bash
full-stack-orchestrator doctor --config config/orchestrator.yaml
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target api-smoke
```

Real framework phases are executed as subprocesses from each repository directory. This keeps `utils`, `flows`, `pages`, `screens`, fixtures, and dependency sets isolated.

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

## Documentation

- [Architecture](docs/architecture.md)
- [Adapters](docs/adapters.md)
- [Configuration](docs/configuration.md)
- [Reporting](docs/reporting.md)
- [Samples](docs/samples.md)
- [Development](docs/development.md)
