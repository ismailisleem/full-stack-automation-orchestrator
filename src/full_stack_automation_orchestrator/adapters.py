from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from full_stack_automation_orchestrator.models import ArtifactRef, StepOutput, duration_ms, json_safe, utc_now
from full_stack_automation_orchestrator.preflight import PreflightCheck

if TYPE_CHECKING:
    from full_stack_automation_orchestrator.context import ScenarioContext


class AdapterError(RuntimeError):
    """Raised when an adapter cannot execute its assigned framework action."""


@runtime_checkable
class FrameworkAdapter(Protocol):
    platform: str
    name: str

    def doctor(self, context: ScenarioContext | None = None) -> Sequence[PreflightCheck]: ...


@dataclass(frozen=True)
class RunPlan:
    name: str
    command: Sequence[str]
    cwd: str | Path
    env: Mapping[str, str] = field(default_factory=dict)
    timeout_seconds: int = 900
    expected_exit_codes: Sequence[int] = (0,)
    report_path: str | Path | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FrameworkRunResult:
    name: str
    platform: str
    status: str
    exit_code: int
    command: Sequence[str]
    cwd: str
    duration_ms: float
    stdout_path: str
    stderr_path: str
    report_path: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_step_output(self) -> StepOutput:
        artifacts = [
            ArtifactRef(
                name=f"{self.name} stdout",
                artifact_type="log",
                path=self.stdout_path,
                mime_type="text/plain",
            ),
            ArtifactRef(
                name=f"{self.name} stderr",
                artifact_type="log",
                path=self.stderr_path,
                mime_type="text/plain",
            ),
        ]
        if self.report_path:
            artifacts.append(
                ArtifactRef(
                    name=f"{self.name} report",
                    artifact_type="html",
                    path=self.report_path,
                    mime_type="text/html",
                )
            )
        return StepOutput(
            status=self.status,
            data={
                "exit_code": self.exit_code,
                "command": list(self.command),
                "cwd": self.cwd,
            },
            metadata={
                "platform": self.platform,
                "duration_ms": self.duration_ms,
                **json_safe(dict(self.metadata)),
            },
            artifacts=artifacts,
        )


class AdapterRegistry:
    def __init__(self, adapters: Mapping[str, FrameworkAdapter] | None = None) -> None:
        self._adapters: dict[str, FrameworkAdapter] = {}
        for platform, adapter in dict(adapters or {}).items():
            self.register(platform, adapter)

    def register(self, platform: str, adapter: FrameworkAdapter) -> FrameworkAdapter:
        self._adapters[platform] = adapter
        return adapter

    def get(self, platform: str) -> FrameworkAdapter | None:
        return self._adapters.get(platform)

    def require(self, platform: str) -> FrameworkAdapter:
        adapter = self.get(platform)
        if adapter is None:
            raise AdapterError(f"No adapter registered for platform '{platform}'")
        return adapter

    def platforms(self) -> tuple[str, ...]:
        return tuple(sorted(self._adapters))


class FunctionAdapter:
    """In-process adapter for demos, tests, and user-provided lightweight actions."""

    def __init__(
        self,
        platform: str,
        *,
        name: str | None = None,
        actions: Mapping[str, Callable[..., Any]] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.platform = platform
        self.name = name or f"{platform}-adapter"
        self._actions = dict(actions or {})
        self.metadata = dict(metadata or {})

    def register(self, name: str, action: Callable[..., Any]) -> None:
        self._actions[name] = action

    def run_action(self, name: str, context: ScenarioContext, **kwargs: Any) -> StepOutput:
        if name not in self._actions:
            raise AdapterError(f"Adapter '{self.name}' has no action named '{name}'")
        result = self._actions[name](context, **kwargs)
        if isinstance(result, StepOutput):
            return result
        return StepOutput(data=result, metadata={"platform": self.platform, "adapter": self.name})

    def doctor(self, context: ScenarioContext | None = None) -> Sequence[PreflightCheck]:
        return [
            PreflightCheck(
                name=f"{self.name} registered",
                status="passed",
                message=f"{self.platform} function adapter is available",
                metadata={"actions": sorted(self._actions), **self.metadata},
            )
        ]


class SubprocessFrameworkAdapter:
    """Runs a framework in its own process so framework imports and fixtures stay isolated."""

    def __init__(self, platform: str, *, name: str | None = None) -> None:
        self.platform = platform
        self.name = name or f"{platform}-subprocess"

    def doctor(self, context: ScenarioContext | None = None) -> Sequence[PreflightCheck]:
        return [
            PreflightCheck(
                name=f"{self.name} ready",
                status="passed",
                message=f"{self.platform} subprocess adapter is available",
            )
        ]

    def run_plan(self, plan: RunPlan, context: ScenarioContext) -> FrameworkRunResult:
        if not plan.command:
            raise AdapterError(f"Run plan '{plan.name}' has no command")
        cwd = Path(plan.cwd).expanduser().resolve()
        if not cwd.exists():
            raise AdapterError(f"Run plan '{plan.name}' cwd does not exist: {cwd}")

        executable = plan.command[0]
        if os.sep not in executable and shutil.which(executable) is None:
            raise AdapterError(f"Executable not found for run plan '{plan.name}': {executable}")

        started_at = utc_now()
        log_dir = context.artifact_path(plan.name)
        log_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = log_dir / "stdout.log"
        stderr_path = log_dir / "stderr.log"
        env = {**os.environ, **dict(plan.env)}

        try:
            completed = subprocess.run(
                list(plan.command),
                cwd=cwd,
                env=env,
                text=True,
                capture_output=True,
                timeout=plan.timeout_seconds,
                check=False,
            )
            exit_code = completed.returncode
            stdout_path.write_text(completed.stdout, encoding="utf-8")
            stderr_path.write_text(completed.stderr, encoding="utf-8")
        except subprocess.TimeoutExpired as error:
            exit_code = 124
            stdout_path.write_text(error.stdout or "", encoding="utf-8")
            stderr_path.write_text(error.stderr or f"Timed out after {plan.timeout_seconds} seconds", encoding="utf-8")

        status = "passed" if exit_code in set(plan.expected_exit_codes) else "failed"
        return FrameworkRunResult(
            name=plan.name,
            platform=self.platform,
            status=status,
            exit_code=exit_code,
            command=tuple(plan.command),
            cwd=str(cwd),
            duration_ms=duration_ms(started_at),
            stdout_path=str(stdout_path),
            stderr_path=str(stderr_path),
            report_path=str(plan.report_path) if plan.report_path else None,
            metadata=plan.metadata,
        )
