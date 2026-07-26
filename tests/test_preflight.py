from __future__ import annotations

import sys

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
                    "command": [sys.executable, "--version"],
                }
            }
        }
    )

    result = run_config_preflight(config, base_dir=tmp_path)

    assert result.ok


def test_preflight_reports_missing_relative_executable(tmp_path):
    repo = tmp_path / "web"
    repo.mkdir()
    config = OrchestratorConfig.from_dict(
        {
            "targets": {
                "web": {
                    "platform": "web",
                    "repo_path": str(repo),
                    "command": [".venv/bin/python", "framework.py", "run"],
                }
            }
        }
    )

    result = run_config_preflight(config, base_dir=tmp_path)

    assert not result.ok
    assert {check.name for check in result.failures} == {"web executable"}
