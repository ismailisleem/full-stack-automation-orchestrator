from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from full_stack_automation_orchestrator.config import OrchestratorConfig
from full_stack_automation_orchestrator.state import ScenarioState

if TYPE_CHECKING:
    from full_stack_automation_orchestrator.adapters import AdapterRegistry, FrameworkAdapter


class ScenarioContext:
    def __init__(
        self,
        *,
        config: OrchestratorConfig,
        state: ScenarioState,
        adapters: AdapterRegistry,
        artifacts_dir: str | Path,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.config = config
        self.state = state
        self.adapters = adapters
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = metadata or {}

    def adapter(self, platform: str) -> FrameworkAdapter:
        return self.adapters.require(platform)

    @property
    def api(self) -> FrameworkAdapter:
        return self.adapter("api")

    @property
    def web(self) -> FrameworkAdapter:
        return self.adapter("web")

    @property
    def mobile(self) -> FrameworkAdapter:
        return self.adapter("mobile")

    def artifact_path(self, name: str) -> Path:
        safe_name = "".join(char if char.isalnum() or char in "._-" else "-" for char in name).strip("-")
        return self.artifacts_dir / (safe_name or "artifact")
