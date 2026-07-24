from __future__ import annotations

from full_stack_automation_orchestrator.config import OrchestratorConfig
from full_stack_automation_orchestrator.preflight import run_config_preflight


def test_preflight_reports_missing_repo_and_command(tmp_path):
    config = OrchestratorConfig.from_dict(
        {
            "targets": {
                "api": {
                    "platform": "api",
                    "repo_path": "missing",
                    "command": [],
                }
            }
        }
    )

    result = run_config_preflight(config, base_dir=tmp_path)

    assert not result.ok
    assert {check.name for check in result.failures} == {"api repo path", "api command"}


def test_preflight_passes_existing_target(tmp_path):
    repo = tmp_path / "api"
    repo.mkdir()
    config = OrchestratorConfig.from_dict(
        {
            "targets": {
                "api": {
                    "platform": "api",
                    "repo_path": str(repo),
                    "command": ["python", "--version"],
                }
            }
        }
    )

    result = run_config_preflight(config, base_dir=tmp_path)

    assert result.ok
