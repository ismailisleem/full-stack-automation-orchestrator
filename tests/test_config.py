from __future__ import annotations

import pytest

from full_stack_automation_orchestrator.config import OrchestratorConfig


def test_config_parses_targets():
    config = OrchestratorConfig.from_dict(
        {
            "project_name": "Demo",
            "targets": {
                "api": {
                    "platform": "api",
                    "repo_path": "../api",
                    "command": "python framework.py run --smoke",
                    "required_env": "API_TOKEN",
                }
            },
        }
    )

    assert config.project_name == "Demo"
    assert config.targets["api"].command == ("python", "framework.py", "run", "--smoke")
    assert config.targets["api"].required_env == ("API_TOKEN",)


def test_config_rejects_unknown_platform():
    with pytest.raises(ValueError):
        OrchestratorConfig.from_dict({"targets": {"bad": {"platform": "desktop", "command": ["pytest"]}}})
