from __future__ import annotations

from full_stack_automation_orchestrator.cli import main


def test_cli_run_sample_generates_report(tmp_path):
    exit_code = main(["run-sample", "api-web", "--output", str(tmp_path / "report")])

    assert exit_code == 0
    assert (tmp_path / "report" / "index.html").exists()


def test_cli_doctor_fails_for_missing_default_targets(tmp_path):
    config = tmp_path / "orchestrator.yaml"
    config.write_text(
        """
targets:
  web:
    platform: web
    repo_path: missing
    command: []
""",
        encoding="utf-8",
    )

    assert main(["doctor", "--config", str(config)]) == 1
