from __future__ import annotations

import sys

from full_stack_automation_orchestrator.adapters import AdapterRegistry, RunPlan, SubprocessFrameworkAdapter
from full_stack_automation_orchestrator.config import OrchestratorConfig
from full_stack_automation_orchestrator.context import ScenarioContext
from full_stack_automation_orchestrator.state import ScenarioState


def test_subprocess_adapter_captures_logs(tmp_path):
    adapter = SubprocessFrameworkAdapter("api")
    context = ScenarioContext(
        config=OrchestratorConfig(),
        state=ScenarioState(),
        adapters=AdapterRegistry({"api": adapter}),
        artifacts_dir=tmp_path / "artifacts",
    )

    result = adapter.run_plan(
        RunPlan(
            name="python-smoke",
            command=[sys.executable, "-S", "-c", "print('hello')"],
            cwd=tmp_path,
        ),
        context,
    )

    assert result.status == "passed"
    assert "hello" in (tmp_path / "artifacts" / "python-smoke" / "stdout.log").read_text(encoding="utf-8")
