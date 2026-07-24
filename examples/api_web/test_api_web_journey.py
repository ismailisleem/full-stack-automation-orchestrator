from __future__ import annotations

from full_stack_automation_orchestrator.samples import run_sample


def test_api_web_sample(tmp_path):
    sample = run_sample("api-web", output_dir=tmp_path / "report")

    assert sample.results[0].passed
    assert sample.report.portfolio_index.exists()
    assert sample.report.run_index.exists()
