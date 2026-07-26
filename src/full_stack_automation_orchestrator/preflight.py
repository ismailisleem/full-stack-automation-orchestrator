from __future__ import annotations

import os
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from full_stack_automation_orchestrator.config import OrchestratorConfig


@dataclass(frozen=True)
class PreflightCheck:
    name: str
    status: str
    message: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == "passed"


@dataclass(frozen=True)
class PreflightResult:
    checks: Sequence[PreflightCheck]

    @property
    def ok(self) -> bool:
        return all(check.status in {"passed", "skipped"} for check in self.checks)

    @property
    def failures(self) -> tuple[PreflightCheck, ...]:
        return tuple(check for check in self.checks if check.status == "failed")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status,
                    "message": check.message,
                    "metadata": dict(check.metadata),
                }
                for check in self.checks
            ],
        }


def run_config_preflight(config: OrchestratorConfig, *, base_dir: str | Path | None = None) -> PreflightResult:
    checks: list[PreflightCheck] = []
    root = Path(base_dir or Path.cwd()).resolve()
    for target in config.targets.values():
        if not target.enabled:
            checks.append(PreflightCheck(target.name, "skipped", "Target is disabled"))
            continue

        repo_path = _resolve(root, target.repo_path)
        if target.repo_path:
            status = "passed" if repo_path.exists() else "failed"
            checks.append(
                PreflightCheck(
                    name=f"{target.name} repo path",
                    status=status,
                    message=str(repo_path),
                    metadata={"platform": target.platform},
                )
            )

        if target.command:
            checks.append(
                PreflightCheck(
                    name=f"{target.name} command",
                    status="passed",
                    message=" ".join(target.command),
                    metadata={"platform": target.platform},
                )
            )
            checks.append(_command_executable_check(target.name, target.platform, repo_path, target.command))
        else:
            checks.append(
                PreflightCheck(
                    name=f"{target.name} command",
                    status="failed",
                    message="Target command is empty",
                    metadata={"platform": target.platform},
                )
            )

        for env_name in target.required_env:
            checks.append(
                PreflightCheck(
                    name=f"{target.name} env {env_name}",
                    status="passed" if os.getenv(env_name) else "failed",
                    message="Environment variable is set" if os.getenv(env_name) else "Environment variable is missing",
                    metadata={"platform": target.platform},
                )
            )

    return PreflightResult(tuple(checks))


def _command_executable_check(
    target_name: str,
    platform: str,
    repo_path: Path,
    command: Sequence[str],
) -> PreflightCheck:
    executable = command[0]
    executable_path = Path(executable).expanduser()
    if executable_path.is_absolute() or executable_path.parent != Path("."):
        resolved = executable_path if executable_path.is_absolute() else repo_path / executable_path
        status = "passed" if resolved.exists() else "failed"
        message = str(resolved)
    else:
        resolved = shutil.which(executable)
        status = "passed" if resolved else "failed"
        message = resolved or f"{executable} was not found on PATH"
    return PreflightCheck(
        name=f"{target_name} executable",
        status=status,
        message=message,
        metadata={"platform": platform},
    )


def _resolve(root: Path, path: str) -> Path:
    candidate = Path(path).expanduser()
    return candidate if candidate.is_absolute() else root / candidate
