# Samples

The built-in samples run without external infrastructure:

```bash
full-stack-orchestrator run-sample api-web --output reports/orchestrator
full-stack-orchestrator run-sample api-mobile --output reports/orchestrator
full-stack-orchestrator run-sample full --output reports/orchestrator
full-stack-orchestrator run-sample all --output reports/orchestrator
```

## API + Web

Creates an order through an API phase, completes checkout through a Web phase, then verifies final status through API.

## API + Mobile

Creates an order through API, confirms it in a Mobile phase, then verifies the mobile confirmation through API.

## Full Journey

Seeds a customer through API, builds a cart on Web, authorizes payment through API, and observes the Mobile confirmation. It includes one successful retry to demonstrate how orchestration-level retries appear in the shared report.
