from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from automation_core.reporting import (
    Artifact,
    RetryAttempt,
    RunReport,
    StepRecord,
    TestCaseReport,
    generate_report_portfolio,
    generate_reporting_product,
    prepare_timestamped_report_dir,
)
from automation_core.reporting.validation import assert_valid_report

from full_stack_automation_orchestrator.models import ArtifactRef, JourneyResult, StepResult, json_safe, utc_now


@dataclass(frozen=True)
class OrchestratorReportPaths:
    portfolio_index: Path
    run_index: Path
    run_dir: Path
    report_data: Path


def build_run_report(
    results: JourneyResult | Sequence[JourneyResult],
    *,
    project_name: str = "Full-Stack Automation Orchestrator",
    run_id: str | None = None,
) -> RunReport:
    journey_results = (results,) if isinstance(results, JourneyResult) else tuple(results)
    generated_at = utc_now()
    report = RunReport(
        run_id=run_id or generated_at.strftime("RUN-%H%M%S-%f"),
        project_name=project_name,
        framework="full-stack-orchestrator",
        generated_at=generated_at,
        started_at=min((item.started_at for item in journey_results), default=generated_at),
        ended_at=max((item.ended_at for item in journey_results), default=generated_at),
        tests=[_test_case_from_journey(item) for item in journey_results],
        metadata={
            "orchestrator": {
                "journey_count": len(journey_results),
                "platforms": sorted({step.platform for item in journey_results for step in item.steps}),
            }
        },
        matrix_dimensions=["platform", "domain", "component", "environment", "profile", "owner"],
    )
    if report.started_at and report.ended_at:
        report.duration_ms = max(0, (report.ended_at - report.started_at).total_seconds() * 1000)
    return report


def generate_orchestrator_report(
    results: JourneyResult | Sequence[JourneyResult],
    output_dir: str | Path,
    *,
    project_name: str = "Full-Stack Automation Orchestrator",
    run_id: str | None = None,
    history_dir: str | Path | None = None,
    safe_share: bool = True,
    update_history_file: bool = True,
) -> OrchestratorReportPaths:
    output_path = Path(output_dir)
    report = build_run_report(results, project_name=project_name, run_id=run_id)
    assert_valid_report(report)
    run_dir = prepare_timestamped_report_dir(output_path, run_id=report.run_id, generated_at=report.generated_at)
    run_index = generate_reporting_product(
        report,
        run_dir,
        history_dir=history_dir,
        safe_share=safe_share,
        update_history_file=update_history_file,
    )
    portfolio_index = generate_report_portfolio(output_path, current_report_dir=run_dir)
    return OrchestratorReportPaths(
        portfolio_index=portfolio_index,
        run_index=run_index,
        run_dir=run_dir,
        report_data=run_dir / "report-data.json",
    )


def _test_case_from_journey(result: JourneyResult) -> TestCaseReport:
    platforms = sorted({step.platform for step in result.steps})
    test = TestCaseReport(
        id=result.journey_id,
        name=result.name,
        full_name=f"{result.suite}.{result.journey_id}",
        suite=result.suite,
        domain=result.domain,
        profile="full-stack",
        environment=result.environment,
        status=result.status,
        started_at=result.started_at,
        ended_at=result.ended_at,
        duration_ms=result.duration_ms,
        failure_message=_failure_message(result),
        failure_trace=_failure_trace(result),
        labels={"journey": result.journey_id, "framework": "full-stack-orchestrator"},
        capabilities={"platforms": platforms, "platform": "full-stack"},
        metadata={
            "platform": "full-stack",
            "platform_type": "full-stack",
            "component": result.domain,
            "journey_status": result.status,
            "state": json_safe(dict(result.state)),
            **json_safe(dict(result.metadata)),
        },
        steps=[_step_record(step) for step in result.steps],
    )
    return test


def _step_record(step: StepResult) -> StepRecord:
    return StepRecord(
        name=step.name,
        status=step.status,
        started_at=step.started_at,
        ended_at=step.ended_at,
        duration_ms=step.duration_ms,
        retries=[_retry_attempt(step, retry) for retry in step.retry_records],
        artifacts=[_artifact(artifact) for artifact in step.artifacts],
        metadata={
            "platform": step.platform,
            "attempts": step.attempts,
            "depends_on": list(step.depends_on),
            "data": json_safe(step.data),
            **json_safe(dict(step.metadata)),
        },
    )


def _artifact(artifact: ArtifactRef) -> Artifact:
    return Artifact(
        name=artifact.name,
        artifact_type=artifact.artifact_type,
        path=str(artifact.path) if artifact.path is not None else None,
        href=artifact.href,
        mime_type=artifact.mime_type,
        metadata=json_safe(dict(artifact.metadata)),
    )


def _retry_attempt(step: StepResult, retry: Any) -> RetryAttempt:
    return RetryAttempt(
        attempt=retry.attempt,
        status=retry.status,
        retry_type="action",
        started_at=retry.started_at,
        ended_at=retry.ended_at,
        duration_ms=retry.duration_ms,
        reason=retry.reason,
        action=step.name,
        metadata={"platform": step.platform, **json_safe(dict(retry.metadata))},
    )


def _failure_message(result: JourneyResult) -> str:
    for step in result.steps:
        if step.status == "failed":
            return f"{step.name} failed"
    return ""


def _failure_trace(result: JourneyResult) -> str:
    return "\n\n".join(step.error for step in result.steps if step.error)
