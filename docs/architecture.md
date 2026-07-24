# Architecture

The orchestrator is a coordination layer. It does not replace the API, Web, or Mobile frameworks.

## Core Concepts

- `Journey`: one cross-platform business flow.
- `JourneyStep`: one phase in that flow, owned by a platform such as `api`, `web`, or `mobile`.
- `ScenarioState`: JSON-safe shared state passed between phases.
- `FrameworkAdapter`: a small boundary object that runs a framework-specific phase without importing that framework's internals.
- `RunPlan`: the subprocess command used for real framework execution.
- `OrchestratorReport`: a neutral report built from journey results and rendered by `automation-core`.

## Process Boundary

The orchestrator prefers subprocess execution for real frameworks because the repositories intentionally have their own top-level packages and pytest fixtures. Running each target in its own working directory avoids module collisions and lets every framework keep its own virtual environment, browser/device setup, and config.

## Ownership Boundary

Environment-specific implementation stays with its framework:

- Web owns browser setup, page objects, flows, web screenshots, console logs, and network logs.
- Mobile owns Appium drivers, device setup, capabilities, native/hybrid/mobile-web screens, and mobile artifacts.
- API owns clients, services, request/response helpers, contracts, and sanitized payload artifacts.
- Core owns neutral models, helpers, reporting, history, exports, and quality analysis.
- Orchestrator owns sequencing, state handoff, preflight, subprocess execution, and cross-platform report aggregation.
