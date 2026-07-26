# Full-Stack Orchestrator Starter Project

Use this starter when one product flow needs API, Web, and Mobile phases in the same scenario.

## Copy

```bash
cp -R templates/starter_project/config ./config
cp -R templates/starter_project/journeys ./journeys
```

## Run

```bash
full-stack-orchestrator doctor --config config/orchestrator.yaml
pytest journeys
```

## Adapt

- Replace repo paths in `config/orchestrator.yaml`.
- Replace target commands with the smoke or e2e commands owned by each framework.
- Keep product-specific clients, page objects, and screen objects in their dedicated framework repos.
- Use the journey test as a thin state handoff layer.
