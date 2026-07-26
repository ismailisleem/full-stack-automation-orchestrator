# Feature Parity

The orchestrator should feel like part of the same framework family while keeping a different job.
It coordinates API, Web, and Mobile runs; it does not duplicate their internals.

## Shared User Experience

| Capability | Orchestrator Behavior | Owner |
| --- | --- | --- |
| CLI entry point | `full-stack-orchestrator` for doctor, samples, run plans, and report aggregation | Orchestrator |
| Configuration | YAML run plans with target repo, command, metadata, and reporting settings | Orchestrator |
| Reporting | Uses the shared automation-core report portfolio and retained timestamped runs | Core |
| Preflight | Checks target repo paths, commands, command executables, and required env vars | Orchestrator |
| State handoff | Shares JSON-safe journey state between phases | Orchestrator |
| Artifacts | Links subprocess output, framework report paths, and custom artifacts into the journey report | Orchestrator plus framework adapters |
| API behavior | Request clients, services, schemas, auth, contracts, and payload artifacts | API framework |
| Web behavior | Browser setup, page objects, flows, traces, screenshots, console and network artifacts | Web framework |
| Mobile behavior | Appium drivers, capabilities, screen objects, contexts, devices, screenshots, source dumps | Mobile framework |

## Design Rule

If a feature is neutral and useful across frameworks, it belongs in `automation-core`.
If it needs Playwright, Selenium, Appium, HTTP clients, devices, browsers, or framework fixtures, it stays in the dedicated framework repository.
If it connects multiple framework runs into one business flow, it belongs here.

## Release 0.1 Scope

- Built-in API+Web, API+Mobile, and API+Web+Mobile sample journeys.
- Subprocess target plans for real sibling framework runs.
- Shared report portfolio generation and report portfolio combination.
- Command readiness checks before running configured targets.
- Starter project template for product-specific cross-platform journeys.

## Deferred Scope

- Device CI and device-farm orchestration policies.
- Cross-framework secret management beyond environment-variable preflight.
- Distributed parallel orchestration across remote workers.
- Advanced quality gates that block release pipelines from orchestrator-level policies.
