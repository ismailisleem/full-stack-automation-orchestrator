from __future__ import annotations

import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from traceback import format_exception
from typing import Any

from full_stack_automation_orchestrator.adapters import AdapterRegistry
from full_stack_automation_orchestrator.config import OrchestratorConfig
from full_stack_automation_orchestrator.context import ScenarioContext
from full_stack_automation_orchestrator.models import (
    ArtifactRef,
    JourneyResult,
    RetryPolicy,
    RetryRecord,
    StepOutput,
    StepResult,
    duration_ms,
    json_safe,
    normalize_status,
    utc_now,
)
from full_stack_automation_orchestrator.state import ScenarioState


class StepFailed(RuntimeError):
    def __init__(self, output: StepOutput) -> None:
        super().__init__(str(output.data or "Step returned a failed status"))
        self.output = output


@dataclass(frozen=True)
class JourneyStep:
    name: str
    action: Callable[[ScenarioContext], StepOutput | Mapping[str, Any] | Any]
    platform: str = "orchestrator"
    retry: RetryPolicy = field(default_factory=RetryPolicy)
    depends_on: Sequence[str] = field(default_factory=tuple)
    required: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Journey:
    name: str
    steps: Sequence[JourneyStep]
    journey_id: str | None = None
    suite: str = "full-stack"
    domain: str = "cross-platform"
    environment: str | None = None
    fail_fast: bool | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def resolved_id(self) -> str:
        return self.journey_id or _slug(self.name)


class JourneyRunner:
    def __init__(
        self,
        *,
        config: OrchestratorConfig | None = None,
        adapters: AdapterRegistry | Mapping[str, Any] | None = None,
        state: ScenarioState | None = None,
        artifacts_dir: str = ".tmp/orchestrator-artifacts",
    ) -> None:
        self.config = config or OrchestratorConfig()
        self.adapters = adapters if isinstance(adapters, AdapterRegistry) else AdapterRegistry(adapters)
        self.state = state or ScenarioState(self.config.state)
        self.artifacts_dir = artifacts_dir

    def run(self, journey: Journey) -> JourneyResult:
        started_at = utc_now()
        context = ScenarioContext(
            config=self.config,
            state=self.state,
            adapters=self.adapters,
            artifacts_dir=self.artifacts_dir,
            metadata={"journey": journey.name},
        )
        step_results: list[StepResult] = []
        step_statuses: dict[str, str] = {}
        fail_fast = self.config.fail_fast if journey.fail_fast is None else journey.fail_fast

        for step in journey.steps:
            if _dependency_failed(step, step_statuses):
                result = _skipped_step(step, reason="Dependency failed or was skipped")
            else:
                result = self._run_step(step, context)
            step_results.append(result)
            step_statuses[step.name] = result.status
            if fail_fast and result.status in {"failed", "blocked"} and step.required:
                step_results.extend(_remaining_skipped_steps(journey.steps, step.name))
                break

        ended_at = utc_now()
        status = _journey_status(step_results)
        return JourneyResult(
            journey_id=journey.resolved_id(),
            name=journey.name,
            status=status,
            started_at=started_at,
            ended_at=ended_at,
            duration_ms=duration_ms(started_at, ended_at),
            steps=tuple(step_results),
            state=self.state.snapshot(),
            environment=journey.environment or self.config.environment,
            suite=journey.suite,
            domain=journey.domain,
            metadata={**json_safe(dict(self.config.metadata)), **json_safe(dict(journey.metadata))},
        )

    def _run_step(self, step: JourneyStep, context: ScenarioContext) -> StepResult:
        started_at = utc_now()
        retry_records: list[RetryRecord] = []
        artifacts: Sequence[ArtifactRef] = ()
        output_data: Any = None
        output_metadata: dict[str, Any] = {}
        delay = step.retry.delay_seconds
        final_error = ""
        attempts_used = 0

        for attempt in range(1, step.retry.attempts + 1):
            attempts_used = attempt
            attempt_started = utc_now()
            try:
                output = _normalize_output(step.action(context))
                if output.status in {"failed", "blocked"}:
                    raise StepFailed(output)
                ended_at = utc_now()
                return StepResult(
                    name=step.name,
                    platform=step.platform,
                    status=output.status,
                    started_at=started_at,
                    ended_at=ended_at,
                    duration_ms=duration_ms(started_at, ended_at),
                    attempts=attempts_used,
                    data=json_safe(output.data),
                    retry_records=tuple(retry_records),
                    artifacts=tuple(output.artifacts),
                    metadata={**json_safe(dict(step.metadata)), **json_safe(dict(output.metadata))},
                    depends_on=tuple(step.depends_on),
                )
            except Exception as error:
                attempt_ended = utc_now()
                final_error = "".join(format_exception(type(error), error, error.__traceback__))
                retry_records.append(
                    RetryRecord(
                        attempt=attempt,
                        status="failed",
                        reason=str(error),
                        started_at=attempt_started,
                        ended_at=attempt_ended,
                        duration_ms=duration_ms(attempt_started, attempt_ended),
                        metadata={"platform": step.platform},
                    )
                )
                if isinstance(error, StepFailed):
                    artifacts = error.output.artifacts
                    output_data = error.output.data
                    output_metadata.update(json_safe(dict(error.output.metadata)))
                if attempt == step.retry.attempts:
                    break
                if delay:
                    time.sleep(delay)
                    delay *= step.retry.backoff

        ended_at = utc_now()
        return StepResult(
            name=step.name,
            platform=step.platform,
            status="failed",
            started_at=started_at,
            ended_at=ended_at,
            duration_ms=duration_ms(started_at, ended_at),
            attempts=attempts_used,
            data=json_safe(output_data),
            error=final_error,
            retry_records=tuple(retry_records),
            artifacts=tuple(artifacts),
            metadata={**json_safe(dict(step.metadata)), **output_metadata},
            depends_on=tuple(step.depends_on),
        )


def _normalize_output(value: Any) -> StepOutput:
    if isinstance(value, StepOutput):
        normalize_status(value.status)
        return value
    if isinstance(value, Mapping):
        return StepOutput(data=dict(value))
    return StepOutput(data=value)


def _dependency_failed(step: JourneyStep, statuses: Mapping[str, str]) -> bool:
    return any(statuses.get(dependency) != "passed" for dependency in step.depends_on)


def _skipped_step(step: JourneyStep, *, reason: str) -> StepResult:
    started_at = utc_now()
    ended_at = utc_now()
    return StepResult(
        name=step.name,
        platform=step.platform,
        status="skipped",
        started_at=started_at,
        ended_at=ended_at,
        duration_ms=0,
        attempts=0,
        metadata={**json_safe(dict(step.metadata)), "skip_reason": reason},
        depends_on=tuple(step.depends_on),
    )


def _remaining_skipped_steps(steps: Sequence[JourneyStep], failed_step_name: str) -> tuple[StepResult, ...]:
    remaining: list[StepResult] = []
    after_failed = False
    for step in steps:
        if after_failed:
            remaining.append(_skipped_step(step, reason=f"Fail-fast after '{failed_step_name}'"))
        if step.name == failed_step_name:
            after_failed = True
    return tuple(remaining)


def _journey_status(step_results: Sequence[StepResult]) -> str:
    required_results = [result for result in step_results if result.status != "skipped"]
    if any(result.status in {"failed", "blocked"} for result in required_results):
        return "failed"
    if not required_results and step_results:
        return "skipped"
    return "passed"


def _slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    return "-".join(part for part in slug.split("-") if part)
