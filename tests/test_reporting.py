from __future__ import annotations

import json

from full_stack_automation_orchestrator import JourneyRunner
from full_stack_automation_orchestrator.reporting import build_run_report, generate_orchestrator_report
from full_stack_automation_orchestrator.samples import sample_journeys


def test_build_run_report_contains_journey_steps(tmp_path):
    result = JourneyRunner(artifacts_dir=str(tmp_path)).run(sample_journeys("api-web")[0])
    report = build_run_report(result, project_name="Demo", run_id="RUN-1")

    assert report.run_id == "RUN-1"
    assert report.tests[0].steps[0].metadata["platform"] == "api"


def test_generate_orchestrator_report_writes_portfolio_and_run(tmp_path):
    result = JourneyRunner(artifacts_dir=str(tmp_path / "artifacts")).run(sample_journeys("full")[0])
    paths = generate_orchestrator_report(result, tmp_path / "report", project_name="Demo", run_id="RUN-1")

    assert paths.portfolio_index.exists()
    assert paths.run_index.exists()
    data = json.loads(paths.report_data.read_text(encoding="utf-8"))
    assert data["run"]["summary"]["total"] == 1
    assert data["run"]["summary"]["passed"] == 1
