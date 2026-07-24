from __future__ import annotations

import json

import pytest

from full_stack_automation_orchestrator.samples import run_sample


@pytest.mark.e2e
def test_all_samples_generate_one_portfolio(tmp_path):
    sample = run_sample("all", output_dir=tmp_path / "report")

    assert all(result.passed for result in sample.results)
    report_data = json.loads(sample.report.report_data.read_text(encoding="utf-8"))
    assert report_data["run"]["summary"]["total"] == 3
    assert report_data["run"]["summary"]["passed"] == 3
    full_stack = next(item for item in report_data["test_index"] if item["test_id"] == "full-stack-checkout")
    assert full_stack["action_retry_count"] == 1
    assert (sample.report.run_dir / "exports" / "report-bundle.json").exists()
