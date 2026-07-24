from __future__ import annotations

import shlex
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from automation_core.config import load_yaml

from full_stack_automation_orchestrator.models import VALID_PLATFORMS, json_safe


@dataclass(frozen=True)
class TargetConfig:
    name: str
    platform: str
    repo_path: str = ""
    command: tuple[str, ...] = ()
    enabled: bool = True
    env: Mapping[str, str] = field(default_factory=dict)
    required_env: tuple[str, ...] = ()
    timeout_seconds: int = 900
    report_root: str = "reports/automation-report"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.platform not in VALID_PLATFORMS - {"orchestrator"}:
            raise ValueError(f"Target '{self.name}' has unsupported platform: {self.platform}")
        if self.timeout_seconds < 1:
            raise ValueError(f"Target '{self.name}' timeout_seconds must be greater than 0")


@dataclass(frozen=True)
class ReportingConfig:
    output_dir: str = "reports/orchestrator"
    history_dir: str | None = None
    safe_share: bool = True
    update_history_file: bool = True
    open_report: bool = False


@dataclass(frozen=True)
class OrchestratorConfig:
    project_name: str = "Full-Stack Automation Orchestrator"
    environment: str = "local"
    fail_fast: bool = True
    state: Mapping[str, Any] = field(default_factory=dict)
    targets: Mapping[str, TargetConfig] = field(default_factory=dict)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> OrchestratorConfig:
        targets = {
            name: _target_from_dict(name, value)
            for name, value in dict(data.get("targets", {})).items()
            if isinstance(value, Mapping)
        }
        reporting = _reporting_from_dict(data.get("reporting", {}))
        return cls(
            project_name=str(data.get("project_name", cls.project_name)),
            environment=str(data.get("environment", cls.environment)),
            fail_fast=bool(data.get("fail_fast", True)),
            state=json_safe(dict(data.get("state", {}))),
            targets=targets,
            reporting=reporting,
            metadata=json_safe(dict(data.get("metadata", {}))),
        )


def load_orchestrator_config(path: str | Path = "config/orchestrator.yaml") -> OrchestratorConfig:
    return OrchestratorConfig.from_dict(load_yaml(path))


def _target_from_dict(name: str, data: Mapping[str, Any]) -> TargetConfig:
    return TargetConfig(
        name=name,
        platform=str(data.get("platform", "")),
        repo_path=str(data.get("repo_path", "")),
        command=_as_command(data.get("command", ())),
        enabled=bool(data.get("enabled", True)),
        env={str(key): str(value) for key, value in dict(data.get("env", {})).items()},
        required_env=tuple(str(item) for item in _as_sequence(data.get("required_env", ()))),
        timeout_seconds=int(data.get("timeout_seconds", 900)),
        report_root=str(data.get("report_root", "reports/automation-report")),
        metadata=json_safe(dict(data.get("metadata", {}))),
    )


def _reporting_from_dict(data: Any) -> ReportingConfig:
    if not isinstance(data, Mapping):
        return ReportingConfig()
    return ReportingConfig(
        output_dir=str(data.get("output_dir", "reports/orchestrator")),
        history_dir=str(data["history_dir"]) if data.get("history_dir") else None,
        safe_share=bool(data.get("safe_share", True)),
        update_history_file=bool(data.get("update_history_file", True)),
        open_report=bool(data.get("open_report", False)),
    )


def _as_command(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(shlex.split(value))
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(str(item) for item in value)
    raise TypeError("target command must be a string or sequence")


def _as_sequence(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(value)
    return (value,)
