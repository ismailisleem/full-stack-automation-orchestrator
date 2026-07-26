# Examples

The examples are split into two groups: infrastructure-free samples and configured framework runs.

## Built-In Samples

Built-in samples use in-process demo adapters so a new user can run them immediately.

```bash
full-stack-orchestrator run-sample api-web --output reports/orchestrator
full-stack-orchestrator run-sample api-mobile --output reports/orchestrator
full-stack-orchestrator run-sample full --output reports/orchestrator
full-stack-orchestrator run-sample all --output reports/orchestrator
```

Use these when validating the orchestrator package, report generation, state handoff, step retries,
and journey modeling without requiring browsers, devices, Appium, or live services.

## Real Framework Targets

The default `config/orchestrator.yaml` shows three sibling framework targets:

```bash
full-stack-orchestrator doctor --config config/orchestrator.yaml
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target api-smoke
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target web-smoke
full-stack-orchestrator run-plan --config config/orchestrator.yaml --target mobile-helper-smoke
```

Each target runs inside its own repository using its own virtual environment. The orchestrator records
subprocess output and links the framework report root as a journey artifact.

## Portfolio Combination

When framework runs already produced automation-core reports, combine their portfolios:

```bash
full-stack-orchestrator combine-reports \
  --source ../api-automation-framework/reports/automation-report \
  --source ../web-automation-framework/reports/automation-report \
  --source ../mobile-automation-framework/reports/automation-report \
  --output reports/combined
```

Use this when the API, Web, and Mobile suites run separately in CI but need one shared report
portfolio for review.

## Product Journey Pattern

```python
from full_stack_automation_orchestrator import Journey, JourneyStep

journey = Journey(
    name="Checkout works across API, Web, and Mobile",
    steps=[
        JourneyStep("Create order through API", create_order, platform="api"),
        JourneyStep("Verify order in Web", verify_web_order, platform="web", depends_on=("Create order through API",)),
        JourneyStep(
            "Verify order in Mobile",
            verify_mobile_order,
            platform="mobile",
            depends_on=("Create order through API",),
        ),
    ],
)
```

Keep the functions thin. They should call framework-owned clients, flows, page objects, or screen
objects instead of reimplementing those layers in the orchestrator.
