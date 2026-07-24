# Adapters

Adapters are intentionally thin.

## Subprocess Adapter

Use `SubprocessFrameworkAdapter` for real framework execution:

```python
from full_stack_automation_orchestrator import RunPlan, SubprocessFrameworkAdapter

adapter = SubprocessFrameworkAdapter("web")
result = adapter.run_plan(
    RunPlan(
        name="web-smoke",
        command=["python", "framework.py", "run", "--env", "qa", "--browser", "chromium"],
        cwd="../web-automation-framework",
    ),
    context,
)
```

The result contains exit code, logs, duration, and optional report path. The orchestrator converts it to a journey step artifact.

## Function Adapter

Use `FunctionAdapter` for demos, unit tests, and very small in-process actions. It should not be used to import all framework internals into one process.

```python
from full_stack_automation_orchestrator import FunctionAdapter

api = FunctionAdapter("api")
api.register("create_order", lambda context: {"order_id": "ORD-1001"})
```

## Adapter Rule

Adapters may call a framework. They should not copy framework code.
