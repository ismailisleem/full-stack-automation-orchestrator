from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

VALID_PLATFORMS = {"api", "web", "mobile", "orchestrator"}
TERMINAL_STATUSES = {"passed", "failed", "skipped", "blocked"}


def utc_now() -> datetime:
    return datetime.now(UTC)


def duration_ms(started_at: datetime, ended_at: datetime | None = None) -> float:
    end = ended_at or utc_now()
    return max(0.0, (end - started_at).total_seconds() * 1000)


def normalize_status(status: str) -> str:
    normalized = status.strip().lower()
    if normalized not in TERMINAL_STATUSES:
        raise ValueError(f"Unsupported status: {status}")
    return normalized


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value):
        return json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [json_safe(item) for item in value]
    return str(value)


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 1
    delay_seconds: float = 0
    backoff: float = 1

    def __post_init__(self) -> None:
        if self.attempts < 1:
            raise ValueError("retry attempts must be at least 1")
        if self.delay_seconds < 0:
            raise ValueError("retry delay_seconds must be 0 or greater")
        if self.backoff < 1:
            raise ValueError("retry backoff must be at least 1")


@dataclass(frozen=True)
class ArtifactRef:
    name: str
    artifact_type: str = "other"
    path: str | Path | None = None
    href: str | None = None
    mime_type: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "artifact_type": self.artifact_type,
            "path": str(self.path) if self.path is not None else None,
            "href": self.href,
            "mime_type": self.mime_type,
            "metadata": json_safe(dict(self.metadata)),
        }


@dataclass(frozen=True)
class StepOutput:
    status: str = "passed"
    data: Any = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    artifacts: Sequence[ArtifactRef] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        normalize_status(self.status)


@dataclass(frozen=True)
class RetryRecord:
    attempt: int
    status: str
    reason: str
    started_at: datetime
    ended_at: datetime
    duration_ms: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StepResult:
    name: str
    platform: str
    status: str
    started_at: datetime
    ended_at: datetime
    duration_ms: float
    attempts: int = 1
    data: Any = None
    error: str = ""
    retry_records: Sequence[RetryRecord] = field(default_factory=tuple)
    artifacts: Sequence[ArtifactRef] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    depends_on: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class JourneyResult:
    journey_id: str
    name: str
    status: str
    started_at: datetime
    ended_at: datetime
    duration_ms: float
    steps: Sequence[StepResult]
    state: Mapping[str, Any]
    environment: str = "local"
    suite: str = "full-stack"
    domain: str = "cross-platform"
    metadata: Mapping[str, Any] = field(default_factory=dict)
    preflight: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == "passed"
